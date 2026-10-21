"""Write frontend/src/data/demomartCatalog.js from the Flask catalog."""

from __future__ import annotations

import json
from pathlib import Path

from app.demo_store.catalog import list_products
from app.demo_store.expanded_catalog import declaration_gaps

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "frontend" / "src" / "data" / "demomartCatalog.js"
LOCAL = "http://127.0.0.1:5000"


def ui_category(product: dict) -> str:
    if product.get("ui_category"):
        return product["ui_category"]
    text = (product.get("category") or "").lower()
    if "electronic" in text or "smartwatch" in text:
        return "Electronics"
    if "footwear" in text or "shoe" in text:
        return "Footwear"
    if any(word in text for word in ("apparel", "clothing", "jean", "t-shirt", "polo")):
        return "Clothing & Apparel"
    if any(word in text for word in ("shampoo", "personal", "beauty", "soap", "skin", "hair")):
        return "Beauty & Personal Care"
    if "home" in text or "kitchen" in text:
        return "Home & Kitchen"
    return "Grocery & Gourmet Foods"


def _after_label(value: str | None, labels: tuple[str, ...]) -> str:
    if not value:
        return ""
    text = str(value).strip()
    lowered = text.lower()
    for label in labels:
        if lowered.startswith(label.lower()):
            return text[len(label):].lstrip(" :")
    return text


def card_status(product: dict) -> tuple[str, int]:
    gaps = declaration_gaps(product)
    if not gaps:
        return ("clear_in_available_data", 90 if product.get("regex_blind") else 100)
    missed = [gap for gap in gaps if gap != "conflict"]
    score = round(100 * max(5 - len(missed), 0) / 5)
    if "conflict" in gaps:
        return ("needs_review", min(score, 72))
    return ("potential_issues", score)


def to_frontend(product: dict) -> dict:
    fields = product.get("fields") or {}
    status, score = card_status(product)
    image_name = (product.get("images") or ["honey.jpg"])[0]
    category = product.get("category") or ""
    sub = product.get("sub_category") or (category.split("›")[-1].strip() if "›" in category else category)
    return {
        "asin": product["asin"],
        "slug": product["slug"],
        "title": product["title"],
        "brand": product["brand"],
        "category": ui_category(product),
        "subCategory": sub,
        "image": f"{LOCAL}/demo/static/images/{image_name}",
        "price": product.get("price"),
        "mrp": product.get("mrp"),
        "rating": product.get("rating"),
        "reviews": product.get("reviews"),
        "netQuantity": _after_label(fields.get("net_quantity"), ("Net Quantity",)),
        "manufacturer": _after_label(fields.get("manufacturer"), ("Manufactured by", "Packed by")),
        "countryOfOrigin": _after_label(fields.get("country_of_origin"), ("Country of Origin",)),
        "mfgDate": _after_label(fields.get("manufacturing_date"), ("Mfg Date", "DOM")),
        "expiryDate": _after_label(fields.get("expiry_date"), ("Best Before", "Exp Date")),
        "customerCare": fields.get("customer_care") or "",
        "scenarioLabel": product.get("scenario_label") or "",
        "expectedScore": score,
        "status": status,
        "url": f"{LOCAL}/demo/dp/{product['slug']}",
    }


def render_js(items: list[dict]) -> str:
    body = json.dumps(items, indent=2, ensure_ascii=False)
    return (
        'import { backendOrigin } from "../site";\n\n'
        f"const RAW_CATALOG = {body};\n\n"
        'const LOCAL = "http://127.0.0.1:5000";\n\n'
        "export const DEMOMART_CATALOG = RAW_CATALOG.map((item) => ({\n"
        "  ...item,\n"
        "  image: String(item.image || \"\").replace(LOCAL, backendOrigin()),\n"
        "  url: String(item.url || \"\").replace(LOCAL, backendOrigin()),\n"
        "}));\n\n"
        "export default DEMOMART_CATALOG;\n"
    )


def main() -> None:
    items = [to_frontend(product) for product in list_products()]
    OUT.write_text(render_js(items), encoding="utf-8")
    print(f"Wrote {len(items)} products to {OUT}")


if __name__ == "__main__":
    main()
