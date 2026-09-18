"""BIO label set for Legal Metrology span tagging.

7 entity types × (B, I) + O = 15 tags.
"""

from __future__ import annotations

from typing import Any

# Must stay aligned with field_extractor.patterns.FIELD_ORDER
ENTITY_LABELS: list[str] = [
    "product_name",
    "mrp",
    "net_quantity",
    "manufacturer",
    "country_of_origin",
    "manufacturing_date",
    "expiry_date",
]

BIO_LABELS: list[str] = ["O"] + [
    f"{prefix}-{name}" for name in ENTITY_LABELS for prefix in ("B", "I")
]

LABEL2ID: dict[str, int] = {label: i for i, label in enumerate(BIO_LABELS)}
ID2LABEL: dict[int, str] = {i: label for label, i in LABEL2ID.items()}

assert len(BIO_LABELS) == 15, f"expected 15 BIO tags, got {len(BIO_LABELS)}"


def labels_payload() -> dict[str, Any]:
    return {
        "entity_labels": list(ENTITY_LABELS),
        "bio_labels": list(BIO_LABELS),
        "label2id": dict(LABEL2ID),
        "id2label": {str(k): v for k, v in ID2LABEL.items()},
        "scheme": "BIO",
        "num_labels": len(BIO_LABELS),
    }
