"""Merge page-text and OCR extractions without inventing values.

Policy (precision-first):
  1. Prefer higher-confidence DETECTed value.
  2. If both sources detect the same normalized value → boost confidence.
  3. If both detect *different* values at high confidence → AMBIGUOUS.
  4. If only one source has a value → keep it (tag source in evidence).
  5. Never fill a field from thin air when both are NOT_DETECTED.
"""

from __future__ import annotations

from typing import Optional

from .extractors import extract_fields
from .models import (
    Evidence,
    ExtractedField,
    ExtractionResult,
    FieldStatus,
    SourceType,
    empty_field,
)
from .patterns import FIELD_ORDER


def _norm_key(field: ExtractedField) -> str:
    return (field.normalized_value or field.value or "").strip().lower()


def _is_positive(field: ExtractedField) -> bool:
    return (
        field.status == FieldStatus.DETECTED
        and bool(field.value)
        and field.confidence > 0
    )


def merge_fields(
    page_result: ExtractionResult,
    ocr_result: ExtractionResult,
    fields: Optional[list[str]] = None,
) -> ExtractionResult:
    target = fields or FIELD_ORDER
    merged: dict[str, ExtractedField] = {}
    warnings: list[str] = list(page_result.warnings) + list(ocr_result.warnings)

    for name in target:
        page_f = page_result.fields.get(name) or empty_field(
            name, "Missing from page extraction"
        )
        ocr_f = ocr_result.fields.get(name) or empty_field(
            name, "Missing from OCR extraction"
        )

        page_ok = _is_positive(page_f)
        ocr_ok = _is_positive(ocr_f)

        if page_ok and ocr_ok:
            if _norm_key(page_f) == _norm_key(ocr_f):
                # Agreement — boost confidence, keep richer evidence
                base = page_f if page_f.confidence >= ocr_f.confidence else ocr_f
                boosted = min(0.99, max(page_f.confidence, ocr_f.confidence) + 0.04)
                evidence = Evidence(
                    source=SourceType.MERGED,
                    matched_text=(
                        f"page: {page_f.evidence.matched_text if page_f.evidence else page_f.value}"
                        f" | ocr: {ocr_f.evidence.matched_text if ocr_f.evidence else ocr_f.value}"
                    ),
                    start=0,
                    end=0,
                    pattern_id=(
                        f"merge_agree:"
                        f"{page_f.evidence.pattern_id if page_f.evidence else 'page'}+"
                        f"{ocr_f.evidence.pattern_id if ocr_f.evidence else 'ocr'}"
                    ),
                )
                merged[name] = ExtractedField(
                    name=name,
                    value=base.value,
                    normalized_value=base.normalized_value,
                    unit=base.unit,
                    status=FieldStatus.DETECTED,
                    confidence=boosted,
                    evidence=evidence,
                    reason="Page and OCR agree",
                )
            else:
                # Conflict — do not pick silently
                alts = []
                for f in (page_f, ocr_f):
                    v = f.normalized_value or f.value
                    if v and v not in alts:
                        alts.append(v)
                top = page_f if page_f.confidence >= ocr_f.confidence else ocr_f
                merged[name] = ExtractedField(
                    name=name,
                    value=None,
                    normalized_value=None,
                    status=FieldStatus.AMBIGUOUS,
                    confidence=max(page_f.confidence, ocr_f.confidence),
                    evidence=top.evidence,
                    alternatives=alts,
                    reason=(
                        f"Page and OCR disagree for {name.replace('_', ' ')} "
                        f"(page={page_f.value!r}, ocr={ocr_f.value!r}); "
                        f"human review required"
                    ),
                )
            continue

        if page_ok:
            merged[name] = page_f
            continue
        if ocr_ok:
            merged[name] = ocr_f
            continue

        # Neither detected positively — surface ambiguity/low-confidence if any
        if page_f.status == FieldStatus.AMBIGUOUS or ocr_f.status == FieldStatus.AMBIGUOUS:
            amb = page_f if page_f.status == FieldStatus.AMBIGUOUS else ocr_f
            alts = list(dict.fromkeys((page_f.alternatives or []) + (ocr_f.alternatives or [])))
            merged[name] = ExtractedField(
                name=name,
                value=None,
                status=FieldStatus.AMBIGUOUS,
                confidence=max(page_f.confidence, ocr_f.confidence),
                evidence=amb.evidence,
                alternatives=alts,
                reason=amb.reason or "Ambiguous across sources",
            )
            continue

        # Both missing
        merged[name] = empty_field(
            name,
            reason=(
                f"Required field not detected in page text or OCR "
                f"(page: {page_f.reason}; ocr: {ocr_f.reason})"
            ),
        )

    combined_raw = (
        f"[PAGE]\n{page_result.raw_text}\n\n[OCR]\n{ocr_result.raw_text}"
    ).strip()

    return ExtractionResult(
        fields=merged,
        raw_text=combined_raw,
        source=SourceType.MERGED,
        warnings=warnings,
    )


def extract_and_merge(
    page_text: str = "",
    ocr_text: str = "",
    fields: Optional[list[str]] = None,
) -> ExtractionResult:
    """Convenience: extract from both sources and merge."""
    page_r = extract_fields(page_text or "", source=SourceType.PAGE, fields=fields)
    ocr_r = extract_fields(ocr_text or "", source=SourceType.OCR, fields=fields)

    if not (page_text or "").strip() and (ocr_text or "").strip():
        return ocr_r
    if (page_text or "").strip() and not (ocr_text or "").strip():
        return page_r
    if not (page_text or "").strip() and not (ocr_text or "").strip():
        return extract_fields("", source=SourceType.MERGED, fields=fields)

    return merge_fields(page_r, ocr_r, fields=fields)
