"""Demo samples for reliable presentations when live scrape/OCR is unavailable."""

from __future__ import annotations

from typing import Any
from app.demo_store.catalog import PRODUCTS

# Map all DemoMart products into pipeline sample format
SAMPLES: dict[str, dict[str, Any]] = {}

for slug, prod in PRODUCTS.items():
    fields = prod.get("fields", {})
    page_lines = [
        f"Product Name: {prod.get('title')}",
        f"MRP: Rs. {prod.get('mrp')} (Inclusive of all taxes)",
    ]
    for k, v in fields.items():
        if v and not str(v).startswith("Product Name:") and not str(v).startswith("MRP"):
            page_lines.append(str(v))
            
    page_text = "\n".join(page_lines) + f"\nDescription: {prod.get('description', '')}"
    ocr_text = "\n".join([str(v) for v in fields.values() if v])
    
    SAMPLES[slug] = {
        "id": f"sample_{slug}",
        "name": prod.get("title", slug)[:45] + ("..." if len(prod.get("title", "")) > 45 else ""),
        "source_url": f"http://127.0.0.1:5000/demo/dp/{slug}",
        "platform": "DemoMart",
        "page_text": page_text,
        "ocr_text": ocr_text,
        "description": prod.get("scenario_label", f"{prod.get('brand')} {prod.get('category')} sample"),
    }


def list_samples() -> list[dict[str, str]]:
    return [
        {"id": k, "name": v["name"], "description": v["description"]}
        for k, v in SAMPLES.items()
    ]


def get_sample(sample_id: str) -> dict[str, Any] | None:
    # Accept either slug or 'sample_' prefix
    if sample_id in SAMPLES:
        return SAMPLES[sample_id]
    cleaned = sample_id.replace("sample_", "")
    return SAMPLES.get(cleaned)
