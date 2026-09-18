"""Regex-blind DemoMart SKUs — paraphrased declarations, no canonical LM labels.

These pages contain every required field in wording that the precision-first
regex extractor is designed to miss. Do not add these phrases as aliases in
normalize.py — that would destroy the regex vs NER comparison.

SKUs:
  golden-grain-atta-5kg
  mediterra-olive-oil-500ml
  vaidya-triphala-churna-100g
  foamchem-active-wash-1kg
"""

from __future__ import annotations

from typing import Any

REGEX_BLIND_SKUS: tuple[str, ...] = (
    "golden-grain-atta-5kg",
    "mediterra-olive-oil-500ml",
    "vaidya-triphala-churna-100g",
    "foamchem-active-wash-1kg",
    "malabar-black-pepper-100g",
    "kerala-coconut-oil-500ml",
    "rajasthan-gram-flour-1kg",
    "goa-cane-jaggery-500g",
    "punjab-desi-ghee-1l",
    "darjeeling-leaf-tea-250g",
)

# value = exact substring labeled as the entity in `text`
REGEX_BLIND_DOCS: list[dict[str, Any]] = [
    {
        "id": "golden-grain-atta-5kg",
        "text": (
            "Name of the food article Golden Grain Chakki Atta. "
            "Stated consumer price Rs. 275. "
            "Fill weight 5 kg. "
            "Plant operator Golden Mills Co-op Society Ltd. "
            "Harvested in India. "
            "DOM 04/2025. "
            "Consume before 04/2026."
        ),
        "values": {
            "product_name": "Golden Grain Chakki Atta",
            "mrp": "Rs. 275",
            "net_quantity": "5 kg",
            "manufacturer": "Golden Mills Co-op Society Ltd",
            "country_of_origin": "India",
            "manufacturing_date": "04/2025",
            "expiry_date": "04/2026",
        },
        "lm_lines": [
            "Name of the food article Golden Grain Chakki Atta",
            "Stated consumer price Rs. 275",
            "Fill weight 5 kg",
            "Plant operator Golden Mills Co-op Society Ltd",
            "Harvested in India",
            "DOM 04/2025",
            "Consume before 04/2026",
        ],
        "title": "Golden Grain Chakki Atta, 5 kg Whole Wheat Flour | Stone Ground",
        "brand": "Golden Grain",
        "price": 275,
        "category": "Grocery & Gourmet Foods › Flour",
        "images": ["atta.jpg", "atta.jpg"],
        "bullets": [
            "Stone-ground whole wheat atta",
            "5 kg family sack",
            "Suitable for roti and paratha",
        ],
        "asin": "B0DEMOATTA01",
    },
    {
        "id": "mediterra-olive-oil-500ml",
        "text": (
            "Article: Mediterra Extra Virgin Olive Oil. "
            "Pack price 649. "
            "Jar holds 500 ml. "
            "Imported by Mediterra Imports Pvt Ltd. "
            "Sourced from Italy. "
            "Lot dated 11/2024. "
            "Discard after 11/2026."
        ),
        "values": {
            "product_name": "Mediterra Extra Virgin Olive Oil",
            "mrp": "649",
            "net_quantity": "500 ml",
            "manufacturer": "Mediterra Imports Pvt Ltd",
            "country_of_origin": "Italy",
            "manufacturing_date": "11/2024",
            "expiry_date": "11/2026",
        },
        "lm_lines": [
            "Article: Mediterra Extra Virgin Olive Oil",
            "Pack price 649",
            "Jar holds 500 ml",
            "Imported by Mediterra Imports Pvt Ltd",
            "Sourced from Italy",
            "Lot dated 11/2024",
            "Discard after 11/2026",
        ],
        "title": "Mediterra Extra Virgin Olive Oil, 500 ml Glass Bottle | Cold Pressed",
        "brand": "Mediterra",
        "price": 649,
        "category": "Grocery & Gourmet Foods › Cooking Oils",
        "images": ["olive.jpg", "olive.jpg"],
        "bullets": [
            "Cold pressed extra virgin olive oil",
            "500 ml glass bottle",
            "Imported Mediterranean packing",
        ],
        "asin": "B0DEMOOIL500",
    },
    {
        "id": "vaidya-triphala-churna-100g",
        "text": (
            "Name of the food article Vaidya Triphala Churna. "
            "Stated consumer price Rs. 180. "
            "Fill weight 100 g. "
            "Packer: Vaidya Ayurvedic Works. "
            "COO India. "
            "DOM 02/2025. "
            "Shelf life ends 02/2028."
        ),
        "values": {
            "product_name": "Vaidya Triphala Churna",
            "mrp": "Rs. 180",
            "net_quantity": "100 g",
            "manufacturer": "Vaidya Ayurvedic Works",
            "country_of_origin": "India",
            "manufacturing_date": "02/2025",
            "expiry_date": "02/2028",
        },
        "lm_lines": [
            "Name of the food article Vaidya Triphala Churna",
            "Stated consumer price Rs. 180",
            "Fill weight 100 g",
            "Packer: Vaidya Ayurvedic Works",
            "COO India",
            "DOM 02/2025",
            "Shelf life ends 02/2028",
        ],
        "title": "Vaidya Triphala Churna, 100 g | Classic Ayurvedic Blend",
        "brand": "Vaidya",
        "price": 180,
        "category": "Grocery & Gourmet Foods › Ayurveda",
        "images": ["triphala.jpg", "triphala.jpg"],
        "bullets": [
            "Triphala churna in a 100 g jar",
            "Traditional three-fruit blend",
            "Packed for household use",
        ],
        "asin": "B0DEMOTRIP01",
    },
    {
        "id": "foamchem-active-wash-1kg",
        "text": (
            "Article: FoamChem Active Wash. "
            "Pack price Rs. 220. "
            "Fill weight 1 kg. "
            "Plant operator FoamChem Industries. "
            "Sourced from India. "
            "Lot dated 08/2024. "
            "Consume before 08/2027."
        ),
        "values": {
            "product_name": "FoamChem Active Wash",
            "mrp": "Rs. 220",
            "net_quantity": "1 kg",
            "manufacturer": "FoamChem Industries",
            "country_of_origin": "India",
            "manufacturing_date": "08/2024",
            "expiry_date": "08/2027",
        },
        "lm_lines": [
            "Article: FoamChem Active Wash",
            "Pack price Rs. 220",
            "Fill weight 1 kg",
            "Plant operator FoamChem Industries",
            "Sourced from India",
            "Lot dated 08/2024",
            "Consume before 08/2027",
        ],
        "title": "FoamChem Active Wash Powder, 1 kg | Household Detergent",
        "brand": "FoamChem",
        "price": 220,
        "category": "Home & Kitchen › Detergent",
        "images": ["wash.jpg", "wash.jpg"],
        "bullets": [
            "Active wash powder for daily laundry",
            "1 kg carton",
            "Household detergent pack",
        ],
        "asin": "B0DEMOWASH01",
    },
    {
        "id": "malabar-black-pepper-100g",
        "text": (
            "Name of the food article Malabar Black Pepper. "
            "Stated consumer price Rs. 95. "
            "Fill weight 100 g. "
            "Packer: Malabar Spice House. "
            "COO India. "
            "DOM 07/2024. "
            "Shelf life ends 07/2027."
        ),
        "values": {
            "product_name": "Malabar Black Pepper",
            "mrp": "Rs. 95",
            "net_quantity": "100 g",
            "manufacturer": "Malabar Spice House",
            "country_of_origin": "India",
            "manufacturing_date": "07/2024",
            "expiry_date": "07/2027",
        },
        "lm_lines": [
            "Name of the food article Malabar Black Pepper",
            "Stated consumer price Rs. 95",
            "Fill weight 100 g",
            "Packer: Malabar Spice House",
            "COO India",
            "DOM 07/2024",
            "Shelf life ends 07/2027",
        ],
        "title": "Malabar Black Pepper, 100 g | Whole Peppercorns",
        "brand": "Malabar Spice",
        "price": 95,
        "category": "Grocery & Gourmet Foods › Spices",
        "images": ["pepper.jpg", "pepper.jpg"],
        "bullets": [
            "Whole black peppercorns from the Malabar coast",
            "100 g refill pouch",
            "For daily tempering and grinding",
        ],
        "asin": "B0DEMOPPR001",
    },
    {
        "id": "kerala-coconut-oil-500ml",
        "text": (
            "Article: Kerala Coconut Oil. "
            "Pack price 240. "
            "Jar holds 500 ml. "
            "Imported by Malabar Copra Board. "
            "Sourced from India. "
            "Lot dated 09/2025. "
            "Discard after 09/2026."
        ),
        "values": {
            "product_name": "Kerala Coconut Oil",
            "mrp": "240",
            "net_quantity": "500 ml",
            "manufacturer": "Malabar Copra Board",
            "country_of_origin": "India",
            "manufacturing_date": "09/2025",
            "expiry_date": "09/2026",
        },
        "lm_lines": [
            "Article: Kerala Coconut Oil",
            "Pack price 240",
            "Jar holds 500 ml",
            "Imported by Malabar Copra Board",
            "Sourced from India",
            "Lot dated 09/2025",
            "Discard after 09/2026",
        ],
        "title": "Kerala Coconut Oil, 500 ml | Cold Pressed Cooking Oil",
        "brand": "Malabar Copra",
        "price": 240,
        "category": "Grocery & Gourmet Foods › Cooking Oils",
        "images": ["coconut.jpg", "coconut.jpg"],
        "bullets": [
            "Cold pressed coconut oil",
            "500 ml bottle",
            "For tadka and hair care demos",
        ],
        "asin": "B0DEMOCoco01",
    },
    {
        "id": "rajasthan-gram-flour-1kg",
        "text": (
            "Name of the food article Rajasthan Gram Flour. "
            "Stated consumer price Rs. 88. "
            "Fill weight 1 kg. "
            "Plant operator Marwar Mills Ltd. "
            "Harvested in India. "
            "DOM 11/2025. "
            "Consume before 11/2026."
        ),
        "values": {
            "product_name": "Rajasthan Gram Flour",
            "mrp": "Rs. 88",
            "net_quantity": "1 kg",
            "manufacturer": "Marwar Mills Ltd",
            "country_of_origin": "India",
            "manufacturing_date": "11/2025",
            "expiry_date": "11/2026",
        },
        "lm_lines": [
            "Name of the food article Rajasthan Gram Flour",
            "Stated consumer price Rs. 88",
            "Fill weight 1 kg",
            "Plant operator Marwar Mills Ltd",
            "Harvested in India",
            "DOM 11/2025",
            "Consume before 11/2026",
        ],
        "title": "Rajasthan Gram Flour (Besan), 1 kg | Fine Milled",
        "brand": "Marwar Mills",
        "price": 88,
        "category": "Grocery & Gourmet Foods › Flour",
        "images": ["besan.jpg", "besan.jpg"],
        "bullets": [
            "Fine gram flour for pakora and kadhi",
            "1 kg family pack",
            "Milled in Rajasthan (demo listing)",
        ],
        "asin": "B0DEMOBESN01",
    },
    {
        "id": "goa-cane-jaggery-500g",
        "text": (
            "Article: Goa Cane Jaggery. "
            "Pack price Rs. 72. "
            "Fill weight 500 g. "
            "Plant operator Konkan Agro Packers. "
            "Harvested in India. "
            "DOM 12/2024. "
            "Consume before 12/2025."
        ),
        "values": {
            "product_name": "Goa Cane Jaggery",
            "mrp": "Rs. 72",
            "net_quantity": "500 g",
            "manufacturer": "Konkan Agro Packers",
            "country_of_origin": "India",
            "manufacturing_date": "12/2024",
            "expiry_date": "12/2025",
        },
        "lm_lines": [
            "Article: Goa Cane Jaggery",
            "Pack price Rs. 72",
            "Fill weight 500 g",
            "Plant operator Konkan Agro Packers",
            "Harvested in India",
            "DOM 12/2024",
            "Consume before 12/2025",
        ],
        "title": "Goa Cane Jaggery, 500 g | Unrefined Blocks",
        "brand": "Konkan Agro",
        "price": 72,
        "category": "Grocery & Gourmet Foods › Sweeteners",
        "images": ["jaggery.jpg", "jaggery.jpg"],
        "bullets": [
            "Unrefined cane jaggery blocks",
            "500 g pack",
            "For chai and traditional sweets",
        ],
        "asin": "B0DEMOJAG001",
    },
    {
        "id": "punjab-desi-ghee-1l",
        "text": (
            "Article: Punjab Desi Ghee. "
            "Pack price 560. "
            "Jar holds 1 L. "
            "Packer: Doaba Dairy Co-op. "
            "COO India. "
            "Lot dated 06/2025. "
            "DOE 06/2026."
        ),
        "values": {
            "product_name": "Punjab Desi Ghee",
            "mrp": "560",
            "net_quantity": "1 L",
            "manufacturer": "Doaba Dairy Co-op",
            "country_of_origin": "India",
            "manufacturing_date": "06/2025",
            "expiry_date": "06/2026",
        },
        "lm_lines": [
            "Article: Punjab Desi Ghee",
            "Pack price 560",
            "Jar holds 1 L",
            "Packer: Doaba Dairy Co-op",
            "COO India",
            "Lot dated 06/2025",
            "DOE 06/2026",
        ],
        "title": "Punjab Desi Ghee, 1 L | Cultured Butter Ghee",
        "brand": "Doaba Dairy",
        "price": 560,
        "category": "Grocery & Gourmet Foods › Dairy",
        "images": ["ghee.jpg", "ghee.jpg"],
        "bullets": [
            "Cultured desi ghee",
            "1 litre jar",
            "For tadka and sweets",
        ],
        "asin": "B0DEMOGHEE01",
    },
    {
        "id": "darjeeling-leaf-tea-250g",
        "text": (
            "Name of the food article Darjeeling Leaf Tea. "
            "Stated consumer price Rs. 420. "
            "Fill weight 250 g. "
            "Plant operator Hillside Tea Estate. "
            "Sourced from India. "
            "DOM 03/2025. "
            "Consume before 03/2027."
        ),
        "values": {
            "product_name": "Darjeeling Leaf Tea",
            "mrp": "Rs. 420",
            "net_quantity": "250 g",
            "manufacturer": "Hillside Tea Estate",
            "country_of_origin": "India",
            "manufacturing_date": "03/2025",
            "expiry_date": "03/2027",
        },
        "lm_lines": [
            "Name of the food article Darjeeling Leaf Tea",
            "Stated consumer price Rs. 420",
            "Fill weight 250 g",
            "Plant operator Hillside Tea Estate",
            "Sourced from India",
            "DOM 03/2025",
            "Consume before 03/2027",
        ],
        "title": "Darjeeling Leaf Tea, 250 g | First Flush Style",
        "brand": "Hillside Tea",
        "price": 420,
        "category": "Grocery & Gourmet Foods › Tea",
        "images": ["darjeeling.jpg", "darjeeling.jpg"],
        "bullets": [
            "Orthodox leaf tea",
            "250 g caddy",
            "Morning cup demo listing",
        ],
        "asin": "B0DEMODARJ01",
    },
]


def _ents_for(doc: dict[str, Any]) -> list[dict[str, Any]]:
    text: str = doc["text"]
    ents: list[dict[str, Any]] = []
    used: list[tuple[int, int]] = []
    for label, value in doc["values"].items():
        start = 0
        found = -1
        while True:
            idx = text.find(value, start)
            if idx < 0:
                break
            end = idx + len(value)
            overlap = any(not (end <= a or idx >= b) for a, b in used)
            if not overlap:
                found = idx
                break
            start = idx + 1
        if found < 0:
            raise ValueError(
                f"Value {value!r} for {label} not found uniquely in {doc['id']}"
            )
        end = found + len(value)
        used.append((found, end))
        ents.append(
            {"start": found, "end": end, "label": label, "text": text[found:end]}
        )
    ents.sort(key=lambda e: e["start"])
    return ents


def gold_records() -> list[dict[str, Any]]:
    """JSONL-ready gold documents (one per regex-blind SKU)."""
    out = []
    for doc in REGEX_BLIND_DOCS:
        out.append(
            {
                "id": f"regex_blind:{doc['id']}",
                "text": doc["text"],
                "ents": _ents_for(doc),
            }
        )
    return out


def get_blind_doc(slug: str) -> dict[str, Any] | None:
    for doc in REGEX_BLIND_DOCS:
        if doc["id"] == slug:
            return doc
    return None
