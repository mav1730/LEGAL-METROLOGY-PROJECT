"""Precision-first field extraction from OCR / page text.

Public contract:
  extract_fields(text, source=...) -> ExtractionResult

Guarantees:
  - Never invents a value that is not supported by a labeled pattern match.
  - Returns NOT_DETECTED (confidence 0) when no safe match exists.
  - Attaches evidence (matched span + pattern_id) for every detection.
  - Fully free / offline / deterministic (stdlib + regex only).
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Iterable, Optional

from .models import (
    Evidence,
    ExtractedField,
    ExtractionResult,
    FieldStatus,
    SourceType,
    empty_field,
)
from .normalize import (
    normalize_amount_string,
    normalize_for_extraction,
    normalize_quantity,
)
from .patterns import (
    ALL_PATTERN_GROUPS,
    FIELD_ORDER,
    KNOWN_COUNTRIES,
    PatternSpec,
)


# ---------------------------------------------------------------------------
# Validation helpers (reject bad captures rather than pass them through)
# ---------------------------------------------------------------------------

_MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def _clean_capture(raw: str) -> str:
    return re.sub(r"\s+", " ", (raw or "").strip(" \t\n\r:;-|.,"))


def _title_country(name: str) -> str:
    # Keep small particles lowercase if multi-word
    parts = name.strip().split()
    out = []
    for i, p in enumerate(parts):
        low = p.lower()
        if low in {"of", "and", "the"} and i > 0:
            out.append(low)
        elif low in {"usa", "uk", "uae", "u.s.a", "u.s.a.", "u.k", "u.k.", "u.a.e"}:
            out.append(low.upper().replace(".", ""))
            if low.count(".") >= 2:
                # U.S.A. style
                out[-1] = low.upper()
        else:
            out.append(p[:1].upper() + p[1:].lower() if p else p)
    return " ".join(out)


def validate_mrp(raw_value: str) -> Optional[str]:
    amount = normalize_amount_string(raw_value)
    if not amount:
        return None
    # Reject absurd values for retail packaging demo range
    try:
        num = float(amount)
    except ValueError:
        return None
    if num <= 0 or num > 10_000_000:
        return None
    return amount


def validate_net_quantity(raw_value: str, raw_unit: str) -> Optional[tuple[str, str, str]]:
    num, unit = normalize_quantity(raw_value, raw_unit)
    if not num or not unit:
        return None
    try:
        n = float(num)
    except ValueError:
        return None
    if n <= 0 or n > 1_000_000:
        return None
    display = f"{num} {unit}"
    return num, unit, display


def validate_manufacturer(raw: str) -> Optional[str]:
    name = _clean_capture(raw)
    if len(name) < 3:
        return None
    # Must contain at least one letter
    if not re.search(r"[A-Za-z]", name):
        return None
    # Reject if it is only a next-field label that leaked
    banned = {
        "mrp",
        "net quantity",
        "country of origin",
        "india",
        "customer care",
    }
    if name.lower() in banned:
        return None
    # Truncate runaway captures
    if len(name) > 120:
        name = name[:120].rstrip()
    return name


def validate_country(raw: str) -> Optional[str]:
    name = _clean_capture(raw)
    if not name:
        return None
    # Strip trailing punctuation leftovers
    name = name.strip(" .,:;")
    key = re.sub(r"\s+", " ", name.lower())
    # Normalize common abbreviations
    aliases = {
        "u.s.a": "usa",
        "u.s.a.": "usa",
        "u.s": "usa",
        "united states of america": "united states",
        "u.k": "uk",
        "u.k.": "uk",
        "great britain": "united kingdom",
        "u.a.e": "uae",
        "u.a.e.": "uae",
        "bharat": "india",
        "hindustan": "india",
    }
    key = aliases.get(key, key)
    if key not in KNOWN_COUNTRIES:
        # Allow only known countries — precision over recall
        return None
    # Canonical display
    display_map = {
        "usa": "USA",
        "uk": "UK",
        "uae": "UAE",
        "united states": "United States",
        "united kingdom": "United Kingdom",
        "united arab emirates": "United Arab Emirates",
        "south korea": "South Korea",
        "sri lanka": "Sri Lanka",
        "new zealand": "New Zealand",
        "south africa": "South Africa",
        "saudi arabia": "Saudi Arabia",
        "hong kong": "Hong Kong",
        "czech republic": "Czech Republic",
    }
    if key in display_map:
        return display_map[key]
    return _title_country(key)


def _normalize_year(y: int) -> Optional[int]:
    if y < 100:
        # 00-79 → 2000-2079; 80-99 → 1980-1999
        y = 2000 + y if y < 80 else 1900 + y
    if 1980 <= y <= 2100:
        return y
    return None


def validate_date(raw: str) -> Optional[str]:
    """Return canonical display date or None if invalid.

    Accepts:
      DD/MM/YYYY, DD-MM-YY, MM/YYYY, Mon YYYY, DD Mon YYYY
    Relative phrases (best before N months...) are returned cleaned as-is.
    """
    s = _clean_capture(raw)
    if not s:
        return None

    # Relative duration phrases already validated by pattern
    if re.search(r"(?i)\bfrom\b", s) and re.search(
        r"(?i)\b(days?|months?|years?)\b", s
    ):
        return re.sub(r"\s+", " ", s)

    # DD Mon YYYY or Mon YYYY
    m = re.match(
        r"(?i)^(?:(\d{1,2})\s+)?"
        r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)\.?"
        r"[\s,./\-]*(\d{2,4})$",
        s,
    )
    if m:
        day_s, mon_s, year_s = m.group(1), m.group(2), m.group(3)
        mon = _MONTHS.get(mon_s.lower().rstrip("."))
        year = _normalize_year(int(year_s))
        if mon is None or year is None:
            return None
        if day_s:
            day = int(day_s)
            if not 1 <= day <= 31:
                return None
            return f"{day:02d}/{mon:02d}/{year}"
        return f"{mon:02d}/{year}"

    # Numeric dates
    m = re.match(r"^(\d{1,2})[./\-](\d{1,2})[./\-](\d{2,4})$", s)
    if m:
        a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
        year = _normalize_year(c)
        if year is None:
            return None
        # Prefer DD/MM/YYYY (India). If first > 12, must be day.
        if a > 31 or b > 31:
            return None
        if a > 12 and b <= 12:
            day, month = a, b
        elif b > 12 and a <= 12:
            # Ambiguous US-style — still accept as MM/DD only if day valid
            # Prefer India convention: if b > 12 then a is month? No — DD/MM:
            # if second > 12 it cannot be month under DD/MM.
            day, month = a, b  # invalid month → reject below
        else:
            # Both <= 12: interpret as DD/MM (Legal Metrology / India)
            day, month = a, b
        if not 1 <= month <= 12 or not 1 <= day <= 31:
            return None
        return f"{day:02d}/{month:02d}/{year}"

    m = re.match(r"^(\d{1,2})[./\-](\d{2,4})$", s)
    if m:
        month, year_s = int(m.group(1)), int(m.group(2))
        year = _normalize_year(year_s)
        if year is None or not 1 <= month <= 12:
            return None
        return f"{month:02d}/{year}"

    return None


def validate_product_name(raw: str) -> Optional[str]:
    name = _clean_capture(raw)
    if len(name) < 2 or len(name) > 80:
        return None
    if not re.search(r"[A-Za-z]", name):
        return None
    return name


# ---------------------------------------------------------------------------
# Core matching
# ---------------------------------------------------------------------------


def _apply_pattern(
    text: str,
    spec: PatternSpec,
    source: SourceType,
) -> Optional[ExtractedField]:
    match = spec.regex.search(text)
    if not match:
        return None

    raw_value = match.groupdict().get("value")
    if raw_value is None:
        return None

    unit = None
    normalized: Optional[str] = None
    display: Optional[str] = None
    confidence = spec.base_confidence

    if spec.field == "mrp":
        amount = validate_mrp(raw_value)
        if amount is None:
            return None
        normalized = amount
        display = f"Rs. {amount}"
    elif spec.field == "net_quantity":
        raw_unit = match.groupdict().get("unit") or ""
        parsed = validate_net_quantity(raw_value, raw_unit)
        if parsed is None:
            return None
        num, unit, display = parsed
        normalized = display
    elif spec.field == "manufacturer":
        name = validate_manufacturer(raw_value)
        if name is None:
            return None
        display = name
        normalized = name
    elif spec.field == "country_of_origin":
        country = validate_country(raw_value)
        if country is None:
            return None
        display = country
        normalized = country
    elif spec.field in ("manufacturing_date", "expiry_date"):
        date = validate_date(raw_value)
        if date is None:
            return None
        display = date
        normalized = date
    elif spec.field == "product_name":
        pname = validate_product_name(raw_value)
        if pname is None:
            return None
        display = pname
        normalized = pname
    else:
        display = _clean_capture(raw_value)
        normalized = display

    # Slight confidence penalty for very short / noisy matched spans
    span = match.group(0)
    if len(span) < 6:
        confidence = max(0.5, confidence - 0.05)

    evidence = Evidence(
        source=source,
        matched_text=span.strip(),
        start=match.start(),
        end=match.end(),
        pattern_id=spec.pattern_id,
    )

    status = FieldStatus.DETECTED
    if confidence < 0.80:
        status = FieldStatus.LOW_CONFIDENCE

    return ExtractedField(
        name=spec.field,
        value=display,
        normalized_value=normalized,
        unit=unit,
        status=status,
        confidence=confidence,
        evidence=evidence,
        reason=None,
    )


def _extract_one_field(
    text: str,
    field_name: str,
    patterns: Iterable[PatternSpec],
    source: SourceType,
) -> ExtractedField:
    """Try patterns in order; collect alternatives; pick best by confidence.

    If multiple *different* values match at high confidence → AMBIGUOUS
    (we do not silently pick one — that would be a mistake).
    """
    hits: list[ExtractedField] = []
    for spec in patterns:
        hit = _apply_pattern(text, spec, source)
        if hit is not None:
            hits.append(hit)

    if not hits:
        return empty_field(
            field_name,
            reason=(
                f"Required field not detected: no labeled "
                f"{field_name.replace('_', ' ')} declaration in available text"
            ),
        )

    # Group by normalized value
    by_value: dict[str, list[ExtractedField]] = {}
    for h in hits:
        key = (h.normalized_value or h.value or "").strip().lower()
        by_value.setdefault(key, []).append(h)

    if len(by_value) == 1:
        # All agree — take highest confidence evidence
        best = max(hits, key=lambda h: h.confidence)
        return best

    # Multiple conflicting values
    ranked = sorted(hits, key=lambda h: h.confidence, reverse=True)
    best = ranked[0]
    alts = []
    for h in ranked[1:]:
        v = h.normalized_value or h.value
        if v and v not in alts and v != best.value:
            alts.append(v)

    # If top two confidences are close → ambiguous, do not force a winner
    if len(ranked) >= 2 and abs(ranked[0].confidence - ranked[1].confidence) < 0.08:
        return ExtractedField(
            name=field_name,
            value=None,
            normalized_value=None,
            status=FieldStatus.AMBIGUOUS,
            confidence=max(h.confidence for h in hits),
            evidence=best.evidence,
            alternatives=[best.value, *alts] if best.value else alts,
            reason=(
                f"Conflicting values detected for {field_name.replace('_', ' ')}; "
                f"human review required"
            ),
        )

    # Clear winner
    return replace(best, alternatives=alts)


def extract_fields(
    text: str,
    source: SourceType | str = SourceType.UNKNOWN,
    fields: Optional[list[str]] = None,
) -> ExtractionResult:
    """Extract Legal Metrology fields from a single text blob.

    Parameters
    ----------
    text:
        Raw OCR output or scraped page text.
    source:
        ``page``, ``ocr``, ``merged``, or ``unknown``.
    fields:
        Optional subset of field names; default = all prototype fields.
    """
    if isinstance(source, str):
        try:
            source = SourceType(source.lower())
        except ValueError:
            source = SourceType.UNKNOWN

    warnings: list[str] = []
    if text is None or not str(text).strip():
        target = fields or FIELD_ORDER
        return ExtractionResult(
            fields={
                name: empty_field(name, reason="Empty input text")
                for name in target
            },
            raw_text="",
            source=source,
            warnings=["Empty input text — nothing to extract"],
        )

    normalized = normalize_for_extraction(text)
    if not normalized:
        target = fields or FIELD_ORDER
        return ExtractionResult(
            fields={
                name: empty_field(name, reason="Text empty after normalization")
                for name in target
            },
            raw_text="",
            source=source,
            warnings=["Input became empty after normalization"],
        )

    target_fields = fields or FIELD_ORDER
    extracted: dict[str, ExtractedField] = {}

    for name in target_fields:
        patterns = ALL_PATTERN_GROUPS.get(name)
        if not patterns:
            extracted[name] = empty_field(
                name, reason=f"No patterns registered for field '{name}'"
            )
            warnings.append(f"Unknown field requested: {name}")
            continue
        extracted[name] = _extract_one_field(normalized, name, patterns, source)

    return ExtractionResult(
        fields=extracted,
        raw_text=normalized,
        source=source,
        warnings=warnings,
    )


def extract_from_ocr(ocr_text: str) -> ExtractionResult:
    return extract_fields(ocr_text, source=SourceType.OCR)


def extract_from_page(page_text: str) -> ExtractionResult:
    return extract_fields(page_text, source=SourceType.PAGE)
