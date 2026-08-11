"""Demo samples for reliable presentations when live scrape/OCR is unavailable."""

from __future__ import annotations

from typing import Any

SAMPLES: dict[str, dict[str, Any]] = {
    "honey_complete": {
        "id": "sample_honey_complete",
        "name": "Organic Himalayan Honey 500g",
        "source_url": "demo://samples/honey_complete",
        "platform": "Demo",
        "page_text": (
            "Product Name: Organic Himalayan Honey 500g "
            "MRP Rs. 349 (Incl. of all taxes) "
            "Net Quantity: 500 g "
            "Manufactured by: Himalayan Bee Farms Pvt Ltd "
            "Country of Origin: India "
            "Mfg Date: 03/2024 "
            "Best Before: 03/2026"
        ),
        "ocr_text": (
            "MRP Rs. 349 Inclusive of all taxes Net Quantity 500 g "
            "Manufactured by Himalayan Bee Farms Pvt Ltd Made in India "
            "Mfg Date 03/2024 Best Before 03/2026"
        ),
        "description": "Complete declarations — should score high / few findings.",
    },
    "oil_missing_origin": {
        "id": "sample_oil_missing_origin",
        "name": "Pure Groundnut Oil 1L",
        "source_url": "demo://samples/oil_missing_origin",
        "platform": "Demo",
        "page_text": (
            "Pure Groundnut Oil "
            "MRP Rs. 150 "
            "Net Quantity: 1 L "
            "Manufactured by: Pure Oil Mills "
            "Mfg Date: Jan 2025 "
            "Best Before: 12 months from manufacture"
        ),
        "ocr_text": (
            "MRP Rs. 150 Net Quantity 1 L Manufactured by Pure Oil Mills "
            "Mfg Date Jan 2025 Best Before 12 months from manufacture"
        ),
        "description": "Country of origin missing — should flag potential issue.",
    },
    "chips_sparse": {
        "id": "sample_chips_sparse",
        "name": "Spicy Chips (listing incomplete)",
        "source_url": "demo://samples/chips_sparse",
        "platform": "Demo",
        "page_text": "Spicy Chips Family Pack Great taste Buy now Special price 99",
        "ocr_text": "Spicy Chips Enjoy!",
        "description": "Sparse data — multiple fields not detected.",
    },
    "conflict_mrp": {
        "id": "sample_conflict_mrp",
        "name": "Tea Bags — conflicting MRP",
        "source_url": "demo://samples/conflict_mrp",
        "platform": "Demo",
        "page_text": "Product Name: Classic Tea Bags MRP Rs. 100 Net Quantity 100 g Country of Origin India Manufactured by Assam Tea Co",
        "ocr_text": "MRP Rs. 120 Net Quantity 100 g Made in India Manufactured by Assam Tea Co",
        "description": "Page/OCR MRP conflict — ambiguous, needs human review.",
    },
}


def list_samples() -> list[dict[str, str]]:
    return [
        {"id": k, "name": v["name"], "description": v["description"]}
        for k, v in SAMPLES.items()
    ]


def get_sample(sample_id: str) -> dict[str, Any] | None:
    return SAMPLES.get(sample_id)
