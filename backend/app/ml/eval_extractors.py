"""Field-level regex / NER / hybrid comparison on the same JSONL texts.

Used by train_ner.py to write metrics.json and RESULTS.md.
Never fabricates scores — empty predictions count as misses.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Optional

from app.field_extractor.extractors import extract_fields
from app.field_extractor.merge import merge_regex_ner
from app.field_extractor.models import ExtractionResult, FieldStatus, SourceType
from app.field_extractor.normalize import normalize_amount_string
from app.ml.labels import ENTITY_LABELS

FOCUS_RECALL_FIELDS = (
    "manufacturer",
    "country_of_origin",
    "manufacturing_date",
    "expiry_date",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def gold_by_field(doc: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for ent in doc.get("ents") or []:
        lab = ent.get("label")
        if lab in ENTITY_LABELS and lab not in out:
            out[lab] = ent.get("text") or ""
    return out


def _norm(field: str, raw: Optional[str]) -> str:
    s = re.sub(r"\s+", " ", (raw or "").strip().lower())
    if field == "mrp":
        amt = normalize_amount_string(s)
        return amt or s.replace("rs.", "").replace("rs", "").strip()
    if field == "net_quantity":
        return s.replace("kilograms", "kg").replace("kilogram", "kg").replace(
            "grams", "g"
        ).replace("gram", "g").replace("millilitres", "ml").replace("milliliters", "ml")
    return s


def values_match(field: str, gold: str, pred: Optional[str]) -> bool:
    g = _norm(field, gold)
    p = _norm(field, pred)
    if not g or not p:
        return False
    if g == p:
        return True
    # Amount-only gold vs "rs. 349" pred (or reverse)
    if field == "mrp":
        return bool(g) and g == p
    if len(g) >= 4 and (g in p or p in g):
        return True
    return False


def pred_value(result: ExtractionResult, field: str) -> Optional[str]:
    f = result.fields.get(field)
    if not f or f.status != FieldStatus.DETECTED or not f.value:
        return None
    return f.normalized_value or f.value


def score_system(
    docs: list[dict[str, Any]],
    predict: Callable[[str], ExtractionResult],
) -> dict[str, Any]:
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    for doc in docs:
        gold = gold_by_field(doc)
        result = predict(doc.get("text") or "")
        for field in ENTITY_LABELS:
            g = gold.get(field)
            p = pred_value(result, field)
            if g and p and values_match(field, g, p):
                tp[field] += 1
            elif g and not (p and values_match(field, g, p)):
                fn[field] += 1
                if p:
                    fp[field] += 1
            elif p and not g:
                fp[field] += 1

    per_field: dict[str, dict[str, float]] = {}
    tp_all = fp_all = fn_all = 0
    for field in ENTITY_LABELS:
        t, fpp, fnn = tp[field], fp[field], fn[field]
        tp_all += t
        fp_all += fpp
        fn_all += fnn
        prec = t / (t + fpp) if (t + fpp) else 0.0
        rec = t / (t + fnn) if (t + fnn) else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
        per_field[field] = {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "tp": t,
            "fp": fpp,
            "fn": fnn,
            "support": t + fnn,
        }

    micro_p = tp_all / (tp_all + fp_all) if (tp_all + fp_all) else 0.0
    micro_r = tp_all / (tp_all + fn_all) if (tp_all + fn_all) else 0.0
    micro_f1 = (
        (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) else 0.0
    )
    return {
        "micro_precision": round(micro_p, 4),
        "micro_recall": round(micro_r, 4),
        "micro_f1": round(micro_f1, 4),
        "tp": tp_all,
        "fp": fp_all,
        "fn": fn_all,
        "per_field": per_field,
    }


def regex_predict(text: str) -> ExtractionResult:
    return extract_fields(text, source=SourceType.PAGE)


def compare_systems(
    docs: list[dict[str, Any]],
    ner_predict: Optional[Callable[[str], ExtractionResult]] = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "n_docs": len(docs),
        "regex_only": score_system(docs, regex_predict),
    }
    if ner_predict is None:
        out["ner_only"] = None
        out["hybrid"] = None
        out["note"] = "NER model not available — ner_only / hybrid not scored."
        return out

    def ner_only(text: str) -> ExtractionResult:
        return ner_predict(text)

    def hybrid(text: str) -> ExtractionResult:
        return merge_regex_ner(regex_predict(text), ner_predict(text))

    out["ner_only"] = score_system(docs, ner_only)
    out["hybrid"] = score_system(docs, hybrid)
    out["note"] = _hybrid_recall_note(out)
    return out


def _hybrid_recall_note(metrics: dict[str, Any]) -> str:
    regex = metrics.get("regex_only") or {}
    hybrid = metrics.get("hybrid") or {}
    if not hybrid:
        return "Hybrid not scored."
    misses: list[str] = []
    for field in FOCUS_RECALL_FIELDS:
        r = (regex.get("per_field") or {}).get(field, {}).get("recall", 0.0)
        h = (hybrid.get("per_field") or {}).get(field, {}).get("recall", 0.0)
        if h <= r:
            misses.append(f"{field} (hybrid {h:.4f} vs regex {r:.4f})")
    if misses:
        return (
            "Hybrid did NOT beat regex recall on: "
            + ", ".join(misses)
            + ". Report this honestly — do not inflate."
        )
    return (
        "Hybrid recall is higher than regex on manufacturer / origin / dates "
        "on this test split."
    )


def render_results_md(metrics: dict[str, Any]) -> str:
    lines = [
        "# NER vs regex vs hybrid (same test texts)",
        "",
        "Field-level precision / recall / F1. A predicted field counts as a hit",
        "only when status is `detected` and the normalized value matches gold.",
        "Numbers are computed by `python -m app.ml.train_ner`, not hand-written.",
        "",
        f"Test documents: **{metrics.get('n_docs', 0)}**",
        "",
        "## Micro scores",
        "",
        "| system | precision | recall | F1 |",
        "|---|---:|---:|---:|",
    ]
    for name in ("regex_only", "ner_only", "hybrid"):
        block = metrics.get(name)
        if not block:
            lines.append(f"| {name} | — | — | — |")
            continue
        lines.append(
            f"| {name} | {block['micro_precision']:.4f} | "
            f"{block['micro_recall']:.4f} | {block['micro_f1']:.4f} |"
        )
    lines += [
        "",
        "## Recall on manufacturer / origin / dates",
        "",
        "| system | manufacturer | country_of_origin | manufacturing_date | expiry_date |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("regex_only", "ner_only", "hybrid"):
        block = metrics.get(name)
        if not block:
            lines.append(f"| {name} | — | — | — | — |")
            continue
        pf = block["per_field"]
        cells = " | ".join(f"{pf[f]['recall']:.4f}" for f in FOCUS_RECALL_FIELDS)
        lines.append(f"| {name} | {cells} |")

    lines += ["", "## Per-field F1 (hybrid)", ""]
    hybrid = metrics.get("hybrid") or metrics.get("regex_only") or {}
    pf = hybrid.get("per_field") or {}
    lines += ["| field | P | R | F1 | support |", "|---|---:|---:|---:|---:|"]
    for field in ENTITY_LABELS:
        row = pf.get(field) or {}
        lines.append(
            f"| {field} | {row.get('precision', 0):.4f} | "
            f"{row.get('recall', 0):.4f} | {row.get('f1', 0):.4f} | "
            f"{row.get('support', 0)} |"
        )
    lines += ["", "## Note", "", metrics.get("note") or "", ""]
    if metrics.get("seqeval"):
        seq = metrics["seqeval"]
        lines += [
            "## Token/entity seqeval (NER model on TEST)",
            "",
            f"- precision: {seq.get('precision', 0):.4f}",
            f"- recall: {seq.get('recall', 0):.4f}",
            f"- f1: {seq.get('f1', 0):.4f}",
            "",
        ]
        if seq.get("report"):
            lines += ["```", str(seq["report"]).rstrip(), "```", ""]
    return "\n".join(lines) + "\n"


def write_reports(
    metrics: dict[str, Any],
    metrics_path: Path,
    results_path: Path,
) -> None:
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    results_path.write_text(render_results_md(metrics), encoding="utf-8")
