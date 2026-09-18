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

# NER-only acceptances are capped so they stay "medium" vs regex hits.
_NER_MEDIUM_CAP = 0.78


def _norm_key(field: ExtractedField) -> str:
    return (field.normalized_value or field.value or "").strip().lower()


def _same_value(a: ExtractedField, b: ExtractedField) -> bool:
    ka, kb = _norm_key(a), _norm_key(b)
    if not ka or not kb:
        return False
    if ka == kb:
        return True
    # "aerofit apparels ltd" vs the same name plus address
    shorter, longer = (ka, kb) if len(ka) <= len(kb) else (kb, ka)
    if len(shorter) >= 10 and shorter in longer:
        return True
    return False


def _prefer_richer(a: ExtractedField, b: ExtractedField) -> ExtractedField:
    ka, kb = _norm_key(a), _norm_key(b)
    return b if len(kb) > len(ka) else a


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


def merge_regex_ner(
    regex_result: ExtractionResult,
    ner_result: ExtractionResult,
    fields: Optional[list[str]] = None,
) -> ExtractionResult:
    """Hybrid merge: regex is precision-first; NER is a fallback, never a silent override.

    Policy:
      * regex already AMBIGUOUS → keep ambiguous (human review)
      * both DETECTED, same normalized value → keep, high confidence
      * regex miss + NER hit → accept NER, medium confidence
      * both DETECTED, different values → AMBIGUOUS, value None
      * regex hit + NER miss → keep regex
      * both miss → not_detected
    """
    target = fields or FIELD_ORDER
    merged: dict[str, ExtractedField] = {}
    warnings: list[str] = list(regex_result.warnings) + list(ner_result.warnings)

    for name in target:
        rx = regex_result.fields.get(name) or empty_field(
            name, "Missing from regex extraction"
        )
        nw = ner_result.fields.get(name) or empty_field(
            name, "Missing from NER extraction"
        )

        if rx.status == FieldStatus.AMBIGUOUS:
            merged[name] = rx
            continue

        rx_ok = _is_positive(rx)
        nw_ok = _is_positive(nw)

        if rx_ok and nw_ok:
            if _same_value(rx, nw):
                keep = _prefer_richer(rx, nw)
                boosted = min(0.99, max(rx.confidence, nw.confidence) + 0.04)
                evidence = Evidence(
                    source=SourceType.MERGED,
                    matched_text=(
                        f"regex: {rx.evidence.matched_text if rx.evidence else rx.value}"
                        f" | ner: {nw.evidence.matched_text if nw.evidence else nw.value}"
                    ),
                    start=keep.evidence.start if keep.evidence else 0,
                    end=keep.evidence.end if keep.evidence else 0,
                    pattern_id=(
                        f"hybrid_agree:"
                        f"{rx.evidence.pattern_id if rx.evidence else 'regex'}+"
                        f"{nw.evidence.pattern_id if nw.evidence else 'ner'}"
                    ),
                )
                merged[name] = ExtractedField(
                    name=name,
                    value=keep.value,
                    normalized_value=keep.normalized_value or rx.normalized_value or nw.normalized_value,
                    unit=keep.unit or rx.unit or nw.unit,
                    status=FieldStatus.DETECTED,
                    confidence=boosted,
                    evidence=evidence,
                    reason="Regex and NER agree",
                )
            else:
                alts = []
                for f in (rx, nw):
                    v = f.normalized_value or f.value
                    if v and v not in alts:
                        alts.append(v)
                merged[name] = ExtractedField(
                    name=name,
                    value=None,
                    normalized_value=None,
                    status=FieldStatus.AMBIGUOUS,
                    confidence=max(rx.confidence, nw.confidence),
                    evidence=rx.evidence or nw.evidence,
                    alternatives=alts,
                    reason=(
                        f"Regex and NER disagree for {name.replace('_', ' ')} "
                        f"(regex={rx.value!r}, ner={nw.value!r}); "
                        f"human review required"
                    ),
                )
            continue

        if rx_ok:
            merged[name] = rx
            continue

        if nw_ok:
            medium = min(_NER_MEDIUM_CAP, max(0.55, nw.confidence))
            evidence = nw.evidence
            if evidence is None:
                evidence = Evidence(
                    source=SourceType.NER,
                    matched_text=nw.value or "",
                    start=0,
                    end=0,
                    pattern_id="ner",
                )
            merged[name] = ExtractedField(
                name=name,
                value=nw.value,
                normalized_value=nw.normalized_value,
                unit=nw.unit,
                status=FieldStatus.DETECTED,
                confidence=medium,
                evidence=evidence,
                reason="Regex miss; accepted NER span",
            )
            continue

        if nw.status == FieldStatus.AMBIGUOUS:
            merged[name] = nw
            continue

        merged[name] = empty_field(
            name,
            reason=(
                f"Required field not detected by regex or NER "
                f"(regex: {rx.reason}; ner: {nw.reason})"
            ),
        )

    combined_raw = regex_result.raw_text or ner_result.raw_text
    return ExtractionResult(
        fields=merged,
        raw_text=combined_raw,
        source=SourceType.MERGED,
        warnings=warnings,
    )


def extract_with_mode(
    page_text: str = "",
    ocr_text: str = "",
    fields: Optional[list[str]] = None,
    mode: Optional[str] = None,
) -> ExtractionResult:
    """Run regex, NER, or hybrid based on EXTRACTOR_MODE.

    Missing NER weights → fall back to regex (with a warning). Never downloads.
    """
    try:
        from app.config import EXTRACTOR_MODE as CFG_MODE
    except Exception:  # noqa: BLE001
        CFG_MODE = "hybrid"

    mode_s = (mode or CFG_MODE or "hybrid").strip().lower()
    if mode_s not in {"regex", "ner", "hybrid"}:
        mode_s = "hybrid"

    regex_result = extract_and_merge(page_text, ocr_text, fields=fields)
    if mode_s == "regex":
        return regex_result

    from .ner_extractor import extract_fields_ner, ner_available

    combined = "\n".join(
        part for part in (page_text or "", ocr_text or "") if (part or "").strip()
    )
    if not ner_available():
        regex_result.warnings.append(
            "NER model not available; using regex only "
            f"(EXTRACTOR_MODE={mode_s})"
        )
        return regex_result

    ner_result = extract_fields_ner(combined, fields=fields)
    if mode_s == "ner":
        return ner_result
    return merge_regex_ner(regex_result, ner_result, fields=fields)
