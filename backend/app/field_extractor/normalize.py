"""OCR / page-text normalization.

Goal: fix *mechanical* OCR noise without inventing product content.
We never rewrite values into different meanings — only spacing, currency
glyphs, common OCR confusions next to numbers, and label aliases.
"""

from __future__ import annotations

import re
import unicodedata


# Common OCR / keyboard substitutes for Indian packaging currency
_CURRENCY_MAP = {
    "₹": "Rs.",
    "rs.": "Rs.",
    "rs ": "Rs. ",
    "rs:": "Rs.:",
    "inr": "Rs.",
    "inr.": "Rs.",
    "mrp rs": "MRP Rs.",
    "m.r.p": "MRP",
    "m r p": "MRP",
    "m.r.p.": "MRP",
}

# Label aliases → canonical tokens (applied case-insensitively on whole text)
_LABEL_ALIASES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bmaximum\s+retail\s+price\b", re.I), "MRP"),
    (re.compile(r"\bm\.?\s*r\.?\s*p\.?\b", re.I), "MRP"),
    (re.compile(r"\bnet\s*(?:wt|weight)\.?\b", re.I), "Net Quantity"),
    (re.compile(r"\bnet\s*(?:qty|quantity|content|contents)\.?\b", re.I), "Net Quantity"),
    (re.compile(r"\bnet\s*wt\.?\b", re.I), "Net Quantity"),
    (re.compile(r"\bmfg\.?\s*by\b", re.I), "Manufactured by"),
    (re.compile(r"\bmfd\.?\s*by\b", re.I), "Manufactured by"),
    (re.compile(r"\bmfr\.?\s*by\b", re.I), "Manufactured by"),
    (re.compile(r"\bmanufactured\s*&\s*marketed\s*by\b", re.I), "Manufactured by"),
    (re.compile(r"\bmanufactured\s+and\s+marketed\s+by\b", re.I), "Manufactured by"),
    (re.compile(r"\bpacked\s+by\b", re.I), "Packed by"),
    (re.compile(r"\bpkd\.?\s*by\b", re.I), "Packed by"),
    (re.compile(r"\bmarketed\s+by\b", re.I), "Marketed by"),
    (re.compile(r"\bcountry\s+of\s+origin\b", re.I), "Country of Origin"),
    (re.compile(r"\bcountry\s+of\s+manufacture\b", re.I), "Country of Origin"),
    (re.compile(r"\bmfg\.?\s*date\b", re.I), "Mfg Date"),
    (re.compile(r"\bmfd\.?\s*(?:date|on)?\b", re.I), "Mfg Date"),
    (re.compile(r"\bmanufacturing\s+date\b", re.I), "Mfg Date"),
    (re.compile(r"\bdate\s+of\s+manufacture\b", re.I), "Mfg Date"),
    (re.compile(r"\bpkd\.?\s*(?:date|on)?\b", re.I), "Pkd Date"),
    (re.compile(r"\bpacked\s+on\b", re.I), "Pkd Date"),
    (re.compile(r"\bexp\.?\s*(?:date|iry)?\b", re.I), "Exp Date"),
    (re.compile(r"\bexpiry\s+date\b", re.I), "Exp Date"),
    (re.compile(r"\buse\s+by\b", re.I), "Exp Date"),
    (re.compile(r"\bbest\s+before\b", re.I), "Best Before"),
    (re.compile(r"\bbest\s+before\s+date\b", re.I), "Best Before"),
]


def unicode_normalize(text: str) -> str:
    if not text:
        return ""
    # NFKC folds compatibility forms (fullwidth digits, etc.)
    return unicodedata.normalize("NFKC", text)


def fix_line_noise(text: str) -> str:
    """Collapse OCR line junk without deleting product words."""
    t = unicode_normalize(text)
    # Normalize newlines and pipes often used as separators on labels
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[|¦]+", " | ", t)
    t = re.sub(r"[•●▪◦]+", " ", t)
    # Soft hyphen / zero-width
    t = t.replace("\u00ad", "").replace("\u200b", "").replace("\ufeff", "")
    # Multiple spaces / tabs
    t = re.sub(r"[ \t]+", " ", t)
    # Spaces around newlines
    t = re.sub(r" *\n *", "\n", t)
    return t.strip()


def normalize_currency_tokens(text: str) -> str:
    t = text
    t = t.replace("₹", "Rs.")
    # Rs variants with no space: Rs499 → Rs. 499
    t = re.sub(r"(?i)\b(?:rs|inr)\.?\s*([0-9])", r"Rs. \1", t)
    # Bare rupee word
    t = re.sub(r"(?i)\brupees?\s*([0-9])", r"Rs. \1", t)
    return t


def normalize_labels(text: str) -> str:
    t = text
    for pattern, replacement in _LABEL_ALIASES:
        t = pattern.sub(replacement, t)
    return t


def fix_common_ocr_digit_noise(text: str) -> str:
    """Conservative digit/letter fixes only in numeric contexts.

    We do NOT globally map O→0 or l→1 (that corrupts words like 'Gold').
    """
    t = text
    # Letter O between digits: 1O0 → 100
    t = re.sub(r"(?<=\d)[Oo](?=\d)", "0", t)
    # Letter l/I between digits: 49l → 491 (rare but seen)
    t = re.sub(r"(?<=\d)[lI](?=\d)", "1", t)
    # Trailing OCR slash price: 99/- → 99
    # (kept as display later; amount parser strips this)
    return t


def join_broken_lines(text: str) -> str:
    """Join hyphenated line breaks: 'Manufac-\ntured' → 'Manufactured'."""
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def normalize_for_extraction(text: str) -> str:
    """Full pipeline applied before field patterns.

    Pure functions only — free, offline, deterministic.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    t = fix_line_noise(text)
    t = join_broken_lines(t)
    t = normalize_currency_tokens(t)
    t = normalize_labels(t)
    t = fix_common_ocr_digit_noise(t)
    # Final whitespace collapse (preserve newlines as spaces for span search)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def normalize_amount_string(raw: str) -> str:
    """Normalize a money amount string. Returns empty if invalid."""
    if not raw:
        return ""
    s = raw.strip()
    s = s.replace(",", "")
    s = re.sub(r"(?i)^(rs\.?|inr|₹)\s*", "", s)
    s = re.sub(r"[/\-]+$", "", s).strip()
    s = re.sub(r"\s+", "", s)
    if not re.fullmatch(r"\d+(?:\.\d{1,2})?", s):
        return ""
    # Canonical: strip trailing .00 noise carefully
    if "." in s:
        whole, frac = s.split(".", 1)
        if frac == "00":
            return whole
        return f"{whole}.{frac}"
    return s


def normalize_quantity(value: str, unit: str) -> tuple[str, str]:
    """Return (numeric_string, canonical_unit). Empty value if invalid."""
    v = (value or "").strip().replace(",", "")
    u = (unit or "").strip().lower()
    if not re.fullmatch(r"\d+(?:\.\d+)?", v):
        return "", ""
    unit_map = {
        "g": "g",
        "gm": "g",
        "gms": "g",
        "gram": "g",
        "grams": "g",
        "kg": "kg",
        "kgs": "kg",
        "kilogram": "kg",
        "kilograms": "kg",
        "mg": "mg",
        "ml": "ml",
        "mL": "ml",
        "millilitre": "ml",
        "millilitres": "ml",
        "milliliter": "ml",
        "milliliters": "ml",
        "l": "L",
        "lt": "L",
        "ltr": "L",
        "ltrs": "L",
        "litre": "L",
        "litres": "L",
        "liter": "L",
        "liters": "L",
        "pcs": "pcs",
        "pc": "pcs",
        "piece": "pcs",
        "pieces": "pcs",
        "nos": "pcs",
        "no": "pcs",
        "n": "pcs",
        "units": "pcs",
        "unit": "pcs",
    }
    canon = unit_map.get(u, unit_map.get(u.rstrip("."), ""))
    if not canon:
        return "", ""
    # Drop trailing zeros: 1.00 → 1
    if "." in v:
        v = v.rstrip("0").rstrip(".")
    return v, canon
