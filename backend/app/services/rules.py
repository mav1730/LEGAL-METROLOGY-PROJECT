"""Deterministic compliance rule engine.

AI/OCR extracts fields. This module only applies configured rules.
It never declares a final legal violation — findings are potential issues.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Optional

from app.config import RULES_PATH, SYSTEM_DISCLAIMER
from app.field_extractor.models import FieldStatus


DEFAULT_RULES: dict[str, Any] = {
    "version": "1.0.0-prototype",
    "name": "Built-in prototype rules",
    "disclaimer": SYSTEM_DISCLAIMER,
    "rules": [
        {
            "id": "REQ_MRP",
            "field": "mrp",
            "type": "presence",
            "required": True,
            "severity": "high",
            "explanation": "MRP was not detected in available sources.",
        },
        {
            "id": "REQ_NET_QTY",
            "field": "net_quantity",
            "type": "presence",
            "required": True,
            "severity": "high",
            "explanation": "Net quantity was not detected in available sources.",
        },
        {
            "id": "REQ_MANUFACTURER",
            "field": "manufacturer",
            "type": "presence",
            "required": True,
            "severity": "high",
            "explanation": "Manufacturer details were not detected in available sources.",
        },
        {
            "id": "REQ_COUNTRY",
            "field": "country_of_origin",
            "type": "presence",
            "required": True,
            "severity": "high",
            "explanation": "Country of origin was not detected in available sources.",
        },
        {
            "id": "REQ_MFG_OR_EXP",
            "field": "_mfg_or_exp",
            "type": "any_of",
            "required": True,
            "fields": ["manufacturing_date", "expiry_date"],
            "severity": "medium",
            "explanation": "Neither manufacturing/packing date nor expiry/best-before was detected.",
        },
        {
            "id": "AMB_ANY",
            "field": "*",
            "type": "ambiguous",
            "required": False,
            "severity": "review",
            "explanation": "Conflicting values detected — human review required.",
        },
    ],
}


def load_rules(path: Optional[Path] = None) -> dict[str, Any]:
    p = path or RULES_PATH
    if p.is_file():
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if "rules" in data:
            return data
    return DEFAULT_RULES


def _field_map(fields: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {f["name"]: f for f in fields if f.get("name")}


def _is_detected(field: Optional[dict[str, Any]]) -> bool:
    if not field:
        return False
    return field.get("status") == FieldStatus.DETECTED.value and bool(field.get("value"))


def evaluate_rules(
    fields: list[dict[str, Any]],
    rules_doc: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Run configured rules. Returns findings + score + overall status."""
    doc = rules_doc or load_rules()
    fmap = _field_map(fields)
    findings: list[dict[str, Any]] = []

    for rule in doc.get("rules") or []:
        rtype = rule.get("type")
        rid = rule.get("id", "UNKNOWN")
        severity = rule.get("severity", "review")
        explanation = rule.get("explanation", "Potential compliance issue.")

        if rtype == "presence":
            fname = rule["field"]
            f = fmap.get(fname)
            if rule.get("required") and not _is_detected(f):
                findings.append(
                    _finding(
                        rid,
                        fname,
                        "potential_issue",
                        severity,
                        explanation,
                        evidence=f.get("evidence") if f else None,
                        confidence=f.get("confidence", 0.0) if f else 0.0,
                        field_reason=f.get("reason") if f else "Field missing",
                    )
                )

        elif rtype == "any_of":
            names = rule.get("fields") or []
            if rule.get("required") and not any(_is_detected(fmap.get(n)) for n in names):
                findings.append(
                    _finding(
                        rid,
                        ",".join(names),
                        "potential_issue",
                        severity,
                        explanation,
                        confidence=0.0,
                    )
                )

        elif rtype == "confidence":
            fname = rule["field"]
            f = fmap.get(fname)
            min_c = float(rule.get("min_confidence", 0.8))
            if f and _is_detected(f) and float(f.get("confidence") or 0) < min_c:
                findings.append(
                    _finding(
                        rid,
                        fname,
                        "needs_review",
                        severity,
                        explanation,
                        evidence=f.get("evidence"),
                        confidence=float(f.get("confidence") or 0),
                    )
                )

        elif rtype == "ambiguous":
            # Flag every ambiguous field
            for fname, f in fmap.items():
                if f.get("status") == FieldStatus.AMBIGUOUS.value:
                    findings.append(
                        _finding(
                            rid,
                            fname,
                            "needs_review",
                            severity,
                            f.get("reason") or explanation,
                            evidence=f.get("evidence"),
                            confidence=float(f.get("confidence") or 0),
                            alternatives=f.get("alternatives") or [],
                        )
                    )

    score = _compute_score(fields, findings, doc)
    overall = _overall_status(findings, fields)

    return {
        "findings": findings,
        "compliance_score": score,
        "overall_status": overall,
        "rules_version": doc.get("version"),
        "rules_name": doc.get("name"),
        "disclaimer": doc.get("disclaimer") or SYSTEM_DISCLAIMER,
    }


def _finding(
    rule_id: str,
    field: str,
    status: str,
    severity: str,
    explanation: str,
    evidence: Any = None,
    confidence: float = 0.0,
    field_reason: str = "",
    alternatives: Optional[list] = None,
) -> dict[str, Any]:
    exp = explanation
    if field_reason:
        exp = f"{explanation} ({field_reason})"
    return {
        "id": f"fnd_{uuid.uuid4().hex[:12]}",
        "rule_id": rule_id,
        "field": field,
        "status": status,
        "severity": severity,
        "explanation": exp,
        "evidence": evidence,
        "confidence": confidence,
        "requires_human_review": True,
        "alternatives": alternatives or [],
        "action_recommended": "Manual verification recommended",
    }


def _compute_score(
    fields: list[dict[str, Any]],
    findings: list[dict[str, Any]],
    doc: dict[str, Any],
) -> float:
    """Simple prioritization score 0–100 (not a legal certification)."""
    required_fields = {
        r["field"]
        for r in doc.get("rules") or []
        if r.get("type") == "presence" and r.get("required")
    }
    # also count any_of as one required group
    any_of_groups = [
        r for r in doc.get("rules") or [] if r.get("type") == "any_of" and r.get("required")
    ]

    fmap = _field_map(fields)
    total_checks = len(required_fields) + len(any_of_groups)
    if total_checks == 0:
        return 100.0

    passed = 0
    for fname in required_fields:
        if _is_detected(fmap.get(fname)):
            passed += 1
    for r in any_of_groups:
        names = r.get("fields") or []
        if any(_is_detected(fmap.get(n)) for n in names):
            passed += 1

    base = 100.0 * passed / total_checks

    # Penalize open findings
    for f in findings:
        if f["severity"] == "high":
            base -= 8
        elif f["severity"] == "medium":
            base -= 5
        else:
            base -= 2

    return max(0.0, min(100.0, round(base, 2)))


def _overall_status(findings: list[dict[str, Any]], fields: list[dict[str, Any]]) -> str:
    if any(f.get("status") == "needs_review" for f in findings):
        return "needs_review"
    if any(f.get("status") == "potential_issue" for f in findings):
        return "potential_issues"
    if any(f.get("status") == FieldStatus.AMBIGUOUS.value for f in fields):
        return "needs_review"
    if any(f.get("status") == FieldStatus.LOW_CONFIDENCE.value for f in fields):
        return "needs_review"
    return "clear_in_available_data"
