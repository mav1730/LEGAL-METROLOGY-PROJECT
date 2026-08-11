"""DemoMart catalog — Amazon-style demo products with Legal Metrology fields."""

from __future__ import annotations

from typing import Any

# All product pages include labeled declarations so the compliance scraper
# can extract them the same way it would from a real listing + packaging text.

PRODUCTS: dict[str, dict[str, Any]] = {
    "hive-organic-honey-500g": {
        "asin": "B0DEMOHONEY1",
        "slug": "hive-organic-honey-500g",
        "title": "HIVE Organic Himalayan Honey, 500g Glass Jar | 100% Pure Raw Unprocessed Honey | No Added Sugar",
        "brand": "HIVE Naturals",
        "category": "Grocery & Gourmet Foods › Honey",
        "price": 349,
        "mrp": 349,
        "mrp_display": "Rs. 349",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.5,
        "reviews": 1284,
        "bought": "2K+ bought in past month",
        "in_stock": True,
        "images": ["honey.jpg", "honey-2.jpg"],
        "bullets": [
            "100% pure multi-flora Himalayan honey",
            "No added sugar, no artificial flavour",
            "Packed in food-grade glass jar",
            "Ideal for tea, toast and immunity routines",
        ],
        # Legal Metrology / packaging declarations (explicit labels for extractor)
        "fields": {
            "product_name": "Product Name: Organic Himalayan Honey 500g",
            "mrp": "MRP Rs. 349 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 500 g",
            "manufacturer": "Manufactured by: Himalayan Bee Farms Pvt Ltd",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Mfg Date: 03/2024",
            "expiry_date": "Best Before: 03/2026",
            "customer_care": "Customer Care: care@hivenaturals.demo | 1800-000-0000",
            "fssai": "FSSAI Lic. No.: 10000000000000",
        },
        "description": (
            "HIVE Organic Himalayan Honey is carefully collected and packed to preserve "
            "natural enzymes and flavour. "
            "Product Name: Organic Himalayan Honey 500g. "
            "MRP Rs. 349 (Incl. of all taxes). Net Quantity: 500 g. "
            "Manufactured by: Himalayan Bee Farms Pvt Ltd. Country of Origin: India. "
            "Mfg Date: 03/2024. Best Before: 03/2026."
        ),
        "scenario": "complete",
        "scenario_label": "Complete declarations (should score high)",
    },
    "pure-groundnut-oil-1l": {
        "asin": "B0DEMOOIL001",
        "slug": "pure-groundnut-oil-1l",
        "title": "PureGold Groundnut Oil, 1 L Bottle | Cold Filtered Cooking Oil | Rich Aroma",
        "brand": "PureGold",
        "category": "Grocery & Gourmet Foods › Cooking Oils",
        "price": 150,
        "mrp": 150,
        "mrp_display": "Rs. 150",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.2,
        "reviews": 856,
        "bought": "1K+ bought in past month",
        "in_stock": True,
        "images": ["oil.jpg", "oil-2.jpg"],
        "bullets": [
            "Pure groundnut oil for everyday cooking",
            "Cold filtered process",
            "1 litre convenient bottle",
            "Suitable for frying and tadka",
        ],
        "fields": {
            "product_name": "Pure Groundnut Oil 1L",
            "mrp": "MRP Rs. 150",
            "net_quantity": "Net Quantity: 1 L",
            "manufacturer": "Manufactured by: Pure Oil Mills",
            "country_of_origin": None,  # intentionally missing for demo finding
            "manufacturing_date": "Mfg Date: Jan 2025",
            "expiry_date": "Best Before: 12 months from manufacture",
            "customer_care": "Customer Care: help@puregold.demo",
            "fssai": "FSSAI Lic. No.: 10000000000001",
        },
        "description": (
            "Pure Groundnut Oil for home kitchens. "
            "MRP Rs. 150. Net Quantity: 1 L. "
            "Manufactured by: Pure Oil Mills. "
            "Mfg Date: Jan 2025. Best Before: 12 months from manufacture. "
            "Note: This demo listing intentionally omits Country of Origin."
        ),
        "scenario": "missing_origin",
        "scenario_label": "Missing country of origin (potential issue)",
    },
    "crunchyco-spicy-chips-50g": {
        "asin": "B0DEMOCHIP01",
        "slug": "crunchyco-spicy-chips-50g",
        "title": "CrunchyCo Spicy Masala Chips, Family Pack | Crunchy Potato Snack",
        "brand": "CrunchyCo",
        "category": "Grocery & Gourmet Foods › Snacks",
        "price": 99,
        "mrp": 99,
        "mrp_display": "Rs. 99",
        "discount_note": "Special price",
        "rating": 3.9,
        "reviews": 412,
        "bought": "500+ bought in past month",
        "in_stock": True,
        "images": ["chips.jpg", "chips-2.jpg"],
        "bullets": [
            "Spicy masala flavour",
            "Family pack for sharing",
            "Crispy potato chips",
        ],
        # Sparse listing — many LM fields missing on purpose
        "fields": {
            "product_name": None,
            "mrp": None,
            "net_quantity": None,
            "manufacturer": None,
            "country_of_origin": None,
            "manufacturing_date": None,
            "expiry_date": None,
        },
        "description": (
            "Spicy Chips Family Pack Great taste. Buy now Special price 99. "
            "Crunchy snack for parties. Incomplete demo listing for compliance testing."
        ),
        "scenario": "sparse",
        "scenario_label": "Sparse listing (many fields missing)",
    },
    "assam-classic-tea-bags-100g": {
        "asin": "B0DEMOTEA001",
        "slug": "assam-classic-tea-bags-100g",
        "title": "Assam Valley Classic Tea Bags, 100 g | Strong Morning Chai | 50 Bags",
        "brand": "Assam Valley",
        "category": "Grocery & Gourmet Foods › Tea",
        "price": 100,
        "mrp": 100,
        "mrp_display": "Rs. 100",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.3,
        "reviews": 2201,
        "bought": "3K+ bought in past month",
        "in_stock": True,
        "images": ["tea.jpg", "tea-2.jpg"],
        "bullets": [
            "Strong Assam blend",
            "50 tea bags, 100 g net",
            "Fresh aroma lock pouch",
        ],
        # Page shows Rs.100 — OCR gallery text elsewhere can conflict in dual-source tests
        "fields": {
            "product_name": "Product Name: Classic Tea Bags",
            "mrp": "MRP Rs. 100",
            "net_quantity": "Net Quantity: 100 g",
            "manufacturer": "Manufactured by: Assam Tea Co",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Mfg Date: 01/2025",
            "expiry_date": "Best Before: 01/2027",
            "customer_care": "Customer Care: support@assamvalley.demo",
        },
        "description": (
            "Product Name: Classic Tea Bags. "
            "MRP Rs. 100. Net Quantity: 100 g. "
            "Manufactured by: Assam Tea Co. Country of Origin: India. "
            "Mfg Date: 01/2025. Best Before: 01/2027."
        ),
        "ocr_conflict_note": "MRP Rs. 120",  # shown only in hidden OCR demo block
        "scenario": "complete",
        "scenario_label": "Complete tea listing",
    },
}


def list_products() -> list[dict[str, Any]]:
    return list(PRODUCTS.values())


def get_product(slug: str) -> dict[str, Any] | None:
    return PRODUCTS.get(slug)
