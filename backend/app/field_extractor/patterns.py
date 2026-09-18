"""Precision-first regex patterns for Indian Legal Metrology packaging fields.

Rules of engagement:
1. Prefer labeled matches (MRP, Net Quantity, …) over bare values.
2. Never match a bare price as MRP without an MRP-like label nearby.
3. Every pattern returns a named group `value` (and optional `unit`).
4. pattern_id is stable for evidence trails.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PatternSpec:
    field: str
    pattern_id: str
    regex: re.Pattern[str]
    # Base confidence when this pattern hits cleanly
    base_confidence: float = 0.92
    # Optional group names beyond value
    unit_group: Optional[str] = None


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

# Money amount: 499 | 499.00 | 1,299.50 | 99/-
# First branch used to be \d{1,3} which captured "116" out of "1169".
_AMOUNT = r"(?P<value>(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?)(?!\d)"
_AMOUNT_TRAIL = r"(?:\s*/\s*-)?"

# Quantity number
_QTY_NUM = r"(?P<value>\d+(?:\.\d+)?)"
_QTY_UNIT = (
    r"(?P<unit>"
    r"kgs?|kilograms?|gms?|grams?|g|mg|"
    r"ml|millilitres?|milliliters?|"
    r"ltrs?|litres?|liters?|lt|l|"
    r"pcs?|pieces?|nos?|units?|n"
    r")\.?"
)

# Date fragments (validated later)
_DATE_DMY = (
    r"(?P<value>"
    r"\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4}"  # 01/03/2024
    r"|"
    r"\d{1,2}[./\-]\d{2,4}"  # 03/2024 or 03/24
    r"|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
    r"[\s,./\-]*\d{2,4}"  # Jan 2024 / January, 2024
    r"|"
    r"\d{1,2}\s+"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?"
    r"[\s,./\-]*\d{2,4}"  # 15 Jan 2024
    r")"
)

# Manufacturer capture: stop at common next-label boundaries
_MFG_STOP = (
    r"(?="
    r"\s*(?:,?\s*)?(?:"
    r"MRP|Net Quantity|Country of Origin|Mfg Date|Pkd Date|Exp Date|Best Before|"
    r"Customer Care|FSSAI|Lic|Licence|License|Email|Phone|Tel|Helpline|"
    r"Ingredients|Nutrition|Batch|Lot|PIN|Pincode|Pin Code|"
    r"Marketed by|Packed by|Manufactured by|Manufacturer|"
    r"Made in|Product of|Item Weight|Brand|Technical Details|"
    r"www\.|http"
    r")\b"
    r"|$"
    r")"
)
_MFG_VALUE = rf"(?P<value>[A-Za-z0-9][A-Za-z0-9 &.,'()/\-]{{2,120}}?){_MFG_STOP}"

# Country list used for validation + "Made in X"
KNOWN_COUNTRIES = frozenset(
    {
        "india",
        "china",
        "usa",
        "u.s.a",
        "u.s.a.",
        "united states",
        "united states of america",
        "uk",
        "u.k",
        "u.k.",
        "united kingdom",
        "germany",
        "france",
        "italy",
        "japan",
        "south korea",
        "korea",
        "taiwan",
        "vietnam",
        "thailand",
        "indonesia",
        "malaysia",
        "singapore",
        "bangladesh",
        "sri lanka",
        "nepal",
        "pakistan",
        "uae",
        "u.a.e",
        "united arab emirates",
        "australia",
        "canada",
        "brazil",
        "mexico",
        "turkey",
        "spain",
        "netherlands",
        "belgium",
        "switzerland",
        "sweden",
        "norway",
        "denmark",
        "poland",
        "russia",
        "ukraine",
        "egypt",
        "south africa",
        "new zealand",
        "philippines",
        "myanmar",
        "cambodia",
        "hong kong",
        "macau",
        "saudi arabia",
        "qatar",
        "oman",
        "kuwait",
        "bahrain",
        "israel",
        "iran",
        "iraq",
        "argentina",
        "chile",
        "colombia",
        "peru",
        "portugal",
        "greece",
        "austria",
        "ireland",
        "finland",
        "czech republic",
        "romania",
        "hungary",
        "slovakia",
        "croatia",
        "serbia",
        "morocco",
        "tunisia",
        "kenya",
        "nigeria",
        "ghana",
        "ethiopia",
    }
)


def _compile(pattern: str, flags: int = re.IGNORECASE) -> re.Pattern[str]:
    return re.compile(pattern, flags)


# ---------------------------------------------------------------------------
# Field patterns (ordered: higher precision first within each field)
# ---------------------------------------------------------------------------

MRP_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        field="mrp",
        pattern_id="mrp_rs_amount_incl",
        regex=_compile(
            rf"\bMRP\b\s*[:\-]?\s*(?:Rs\.?\s*)?{_AMOUNT}{_AMOUNT_TRAIL}"
            rf"(?:\s*(?:\(|\[)?\s*incl(?:usive)?\.?\s*of\s*all\s*taxes\s*(?:\)|\])?)?"
        ),
        base_confidence=0.96,
    ),
    PatternSpec(
        field="mrp",
        pattern_id="mrp_currency_symbol",
        regex=_compile(rf"\bMRP\b\s*[:\-]?\s*Rs\.\s*{_AMOUNT}{_AMOUNT_TRAIL}"),
        base_confidence=0.95,
    ),
    PatternSpec(
        field="mrp",
        pattern_id="mrp_plain_amount",
        regex=_compile(rf"\bMRP\b\s*[:\-]?\s*{_AMOUNT}{_AMOUNT_TRAIL}"),
        base_confidence=0.90,
    ),
]

NET_QTY_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        field="net_quantity",
        pattern_id="net_qty_labeled",
        regex=_compile(
            rf"\bNet Quantity\b\s*[:\-]?\s*{_QTY_NUM}\s*{_QTY_UNIT}"
        ),
        base_confidence=0.96,
        unit_group="unit",
    ),
    PatternSpec(
        field="net_quantity",
        pattern_id="net_content_e_mark",
        # e-mark style: 500 g e
        regex=_compile(
            rf"\bNet Quantity\b\s*[:\-]?\s*{_QTY_NUM}\s*{_QTY_UNIT}\s*e\b"
        ),
        base_confidence=0.97,
        unit_group="unit",
    ),
    PatternSpec(
        field="net_quantity",
        pattern_id="qty_short_label",
        regex=_compile(rf"\b(?:Qty|Quantity)\b\s*[:\-]?\s*{_QTY_NUM}\s*{_QTY_UNIT}"),
        base_confidence=0.88,
        unit_group="unit",
    ),
]

MANUFACTURER_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        field="manufacturer",
        pattern_id="manufactured_by",
        regex=_compile(rf"\bManufactured by\b\s*[:\-]?\s*{_MFG_VALUE}"),
        base_confidence=0.93,
    ),
    PatternSpec(
        field="manufacturer",
        pattern_id="manufacturer_label",
        # E-commerce specs often use "Manufacturer: Nestle India Ltd" (no "by")
        regex=_compile(rf"\bManufacturer\b\s*[:\-]?\s*{_MFG_VALUE}"),
        base_confidence=0.90,
    ),
    PatternSpec(
        field="manufacturer",
        pattern_id="packed_by",
        regex=_compile(rf"\bPacked by\b\s*[:\-]?\s*{_MFG_VALUE}"),
        base_confidence=0.88,
    ),
    PatternSpec(
        field="manufacturer",
        pattern_id="marketed_by",
        regex=_compile(rf"\bMarketed by\b\s*[:\-]?\s*{_MFG_VALUE}"),
        base_confidence=0.86,
    ),
]

# Stop tokens after a country name (non-greedy value + lookahead)
_COUNTRY_STOP = (
    r"(?=\s*(?:MRP|Net Quantity|Mfg Date|Pkd Date|Exp Date|Best Before|"
    r"Manufactured by|Packed by|Marketed by|Manufacturer|Customer Care|"
    r"Month|Packed|Packing|Imported|Scenario|"
    r"FSSAI|PIN|Batch|Lot|Item Weight|Brand|Ingredients|Nutrition|"
    r",|\||$|\.))"
)
# 1–5 words; non-greedy so we stop at the first valid boundary
# (greedy would run to end-of-string via `$` in the lookahead)
_COUNTRY_VALUE = (
    rf"(?P<value>[A-Za-z][A-Za-z.'\-]*(?:\s+[A-Za-z][A-Za-z.'\-]*){{0,4}}?)"
    rf"{_COUNTRY_STOP}"
)

COUNTRY_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        field="country_of_origin",
        pattern_id="country_of_origin_label",
        regex=_compile(rf"\bCountry of Origin\b\s*[:\-]?\s*{_COUNTRY_VALUE}"),
        base_confidence=0.95,
    ),
    PatternSpec(
        field="country_of_origin",
        pattern_id="made_in",
        regex=_compile(rf"\bMade in\b\s+{_COUNTRY_VALUE}"),
        base_confidence=0.93,
    ),
    PatternSpec(
        field="country_of_origin",
        pattern_id="product_of",
        regex=_compile(rf"\bProduct of\b\s+{_COUNTRY_VALUE}"),
        base_confidence=0.90,
    ),
    PatternSpec(
        field="country_of_origin",
        pattern_id="origin_label",
        # Negative lookbehind: do not match the "Origin" inside "Country of Origin"
        regex=_compile(rf"(?<!Country of )\bOrigin\b\s*[:\-]?\s*{_COUNTRY_VALUE}"),
        base_confidence=0.85,
    ),
]

MFG_DATE_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        field="manufacturing_date",
        pattern_id="mfg_date_labeled",
        regex=_compile(rf"\bMfg Date\b\s*[:\-]?\s*{_DATE_DMY}"),
        base_confidence=0.93,
    ),
    PatternSpec(
        field="manufacturing_date",
        pattern_id="pkd_date_labeled",
        regex=_compile(rf"\bPkd Date\b\s*[:\-]?\s*{_DATE_DMY}"),
        base_confidence=0.90,
    ),
]

EXPIRY_PATTERNS: list[PatternSpec] = [
    PatternSpec(
        field="expiry_date",
        pattern_id="exp_date_labeled",
        regex=_compile(rf"\bExp Date\b\s*[:\-]?\s*{_DATE_DMY}"),
        base_confidence=0.93,
    ),
    PatternSpec(
        field="expiry_date",
        pattern_id="best_before_date",
        regex=_compile(rf"\bBest Before\b\s*[:\-]?\s*{_DATE_DMY}"),
        base_confidence=0.92,
    ),
    PatternSpec(
        field="expiry_date",
        pattern_id="best_before_relative",
        # "Best Before 6 months from manufacture" — keep full phrase as value
        regex=_compile(
            r"\bBest Before\b\s*[:\-]?\s*"
            r"(?P<value>\d+\s*(?:days?|months?|years?)\s+from\s+"
            r"(?:mfg|manufacture|manufacturing|packing|pkd)(?:\s*date)?)"
        ),
        base_confidence=0.90,
    ),
]

PRODUCT_NAME_PATTERNS: list[PatternSpec] = [
    # Only when explicitly labeled — never guess from first line
    PatternSpec(
        field="product_name",
        pattern_id="product_name_labeled",
        regex=_compile(
            r"\b(?:Product\s+Name|Item\s+Name|Commodity)\b\s*[:\-]?\s*"
            r"(?P<value>[A-Za-z0-9][A-Za-z0-9 &.,'()/\-]{1,80}?)"
            r"(?=\s*(?:MRP|Net Quantity|Manufactured by|Country of Origin|"
            r"Mfg Date|Exp Date|Brand|,|\||$))"
        ),
        base_confidence=0.88,
    ),
]


ALL_PATTERN_GROUPS: dict[str, list[PatternSpec]] = {
    "mrp": MRP_PATTERNS,
    "net_quantity": NET_QTY_PATTERNS,
    "manufacturer": MANUFACTURER_PATTERNS,
    "country_of_origin": COUNTRY_PATTERNS,
    "manufacturing_date": MFG_DATE_PATTERNS,
    "expiry_date": EXPIRY_PATTERNS,
    "product_name": PRODUCT_NAME_PATTERNS,
}

# Canonical field order for reports / dashboards
FIELD_ORDER: list[str] = [
    "product_name",
    "mrp",
    "net_quantity",
    "manufacturer",
    "country_of_origin",
    "manufacturing_date",
    "expiry_date",
]
