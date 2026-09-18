"""Demo samples for reliable presentations when live scrape/OCR is unavailable."""

from __future__ import annotations

from typing import Any

from app.demo_store.catalog import PRODUCTS
from app.demo_store.regex_blind import REGEX_BLIND_DOCS

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
        "page_text": (
            "Product Name: Classic Tea Bags MRP Rs. 100 Net Quantity 100 g "
            "Country of Origin India Manufactured by Assam Tea Co"
        ),
        "ocr_text": (
            "MRP Rs. 120 Net Quantity 100 g Made in India Manufactured by Assam Tea Co"
        ),
        "description": "Page/OCR MRP conflict — ambiguous, needs human review.",
    },
}

for slug, prod in PRODUCTS.items():
    if slug in SAMPLES:
        continue
    fields = prod.get("fields", {})
    if prod.get("regex_blind"):
        continue
    page_lines = [
        f"Product Name: {prod.get('title')}",
        f"MRP: Rs. {prod.get('mrp')} (Inclusive of all taxes)",
    ]
    for _k, v in fields.items():
        if v and not str(v).startswith("Product Name:") and not str(v).startswith("MRP"):
            page_lines.append(str(v))
    page_text = "\n".join(page_lines) + f"\nDescription: {prod.get('description', '')}"
    ocr_text = "\n".join([str(v) for v in fields.values() if v])
    SAMPLES[slug] = {
        "id": f"sample_{slug}",
        "name": (prod.get("title") or slug)[:45]
        + ("..." if len(prod.get("title") or "") > 45 else ""),
        "source_url": f"http://127.0.0.1:5000/demo/dp/{slug}",
        "platform": "DemoMart",
        "page_text": page_text,
        "ocr_text": ocr_text,
        "description": prod.get("scenario_label", f"{prod.get('brand')} sample"),
    }

for _blind in REGEX_BLIND_DOCS:
    SAMPLES[_blind["id"]] = {
        "id": f"sample_{_blind['id'].replace('-', '_')}",
        "name": _blind["values"]["product_name"],
        "source_url": f"http://127.0.0.1:5000/demo/dp/{_blind['id']}",
        "platform": "DemoMart",
        "page_text": _blind["text"],
        "ocr_text": "",
        "description": (
            "Regex-blind paraphrased declarations — regex should miss; "
            "hybrid/NER may fill spans after training."
        ),
        "regex_blind": True,
    }


def list_samples() -> list[dict[str, str]]:
    return [
        {"id": k, "name": v["name"], "description": v["description"]}
        for k, v in SAMPLES.items()
    ]


def get_sample(sample_id: str) -> dict[str, Any] | None:
    return SAMPLES.get(sample_id)
