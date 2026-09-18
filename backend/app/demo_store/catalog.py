"""DemoMart catalog — Amazon-style demo products with Legal Metrology fields."""

from __future__ import annotations

from typing import Any

from app.demo_store.regex_blind import REGEX_BLIND_DOCS

# All product pages include labeled declarations so the compliance scraper
# can extract them the same way it would from a real listing + packaging text.
# Regex-blind SKUs keep paraphrased wording for the NER demo.

PRODUCTS: dict[str, dict[str, Any]] = {
    # 1. Organic Honey
    "hive-organic-honey-500g": {
        "asin": "B0DEMOHONEY1",
        "slug": "hive-organic-honey-500g",
        "title": "HIVE Organic Himalayan Honey, 500g Glass Jar | 100% Pure Raw Unprocessed Honey | No Added Sugar",
        "brand": "HIVE Naturals",
        "category": "Grocery & Gourmet Foods › Honey",
        "price": 454,
        "mrp": 454,
        "mrp_display": "Rs. 454",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.5,
        "reviews": 1284,
        "bought": "2K+ bought in past month",
        "in_stock": True,
        "images": ["honey.jpg"],
        "bullets": [
            "100% pure multi-flora Himalayan honey",
            "No added sugar, no artificial flavour",
            "Packed in food-grade glass jar",
            "Ideal for tea, toast and daily wellness routines",
        ],
        "fields": {
            "product_name": "Product Name: Organic Himalayan Honey 500g",
            "mrp": "MRP Rs. 454 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 500 g",
            "manufacturer": "Manufactured by: Himalayan Bee Farms Pvt Ltd, Solan, HP - 173212",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Mfg Date: 03/2024",
            "expiry_date": "Best Before: 03/2026",
            "customer_care": "Customer Care: care@hivenaturals.demo | 1800-000-0000",
            "fssai": "FSSAI Lic. No.: 10000000000000",
        },
        "description": (
            "HIVE Organic Himalayan Honey is carefully collected and packed to preserve natural enzymes and flavour. "
            "Product Name: Organic Himalayan Honey 500g. "
            "MRP Rs. 454 (Incl. of all taxes). Net Quantity: 500 g. "
            "Manufactured by: Himalayan Bee Farms Pvt Ltd, Solan, HP - 173212. Country of Origin: India. "
            "Mfg Date: 03/2024. Best Before: 03/2026. Customer Care: care@hivenaturals.demo | 1800-000-0000."
        ),
        "scenario": "complete",
        "scenario_label": "Complete declarations (high score)",
    },

    # 2. Groundnut Oil (Missing Origin)
    "pure-groundnut-oil-1l": {
        "asin": "B0DEMOOIL001",
        "slug": "pure-groundnut-oil-1l",
        "title": "PureGold Groundnut Oil, 1 L Bottle | Cold Filtered Cooking Oil | Rich Aroma",
        "brand": "PureGold",
        "category": "Grocery & Gourmet Foods › Cooking Oils",
        "price": 195,
        "mrp": 195,
        "mrp_display": "Rs. 195",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.2,
        "reviews": 856,
        "bought": "1K+ bought in past month",
        "in_stock": True,
        "images": ["oil.jpg"],
        "bullets": [
            "Pure groundnut oil for everyday cooking",
            "Cold filtered traditional extraction",
            "1 litre convenient food-grade bottle",
            "Rich authentic peanut aroma",
        ],
        "fields": {
            "product_name": "Pure Groundnut Oil 1L",
            "mrp": "MRP Rs. 195 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 1 L",
            "manufacturer": "Manufactured by: Pure Oil Mills, Rajkot, Gujarat - 360001",
            "country_of_origin": None,  # Intentionally missing
            "manufacturing_date": "Mfg Date: Jan 2025",
            "expiry_date": "Best Before: 12 months from manufacture",
            "customer_care": "Customer Care: help@puregold.demo",
            "fssai": "FSSAI Lic. No.: 10000000000001",
        },
        "description": (
            "Pure Groundnut Oil for home kitchens. "
            "MRP Rs. 195. Net Quantity: 1 L. "
            "Manufactured by: Pure Oil Mills, Rajkot, Gujarat - 360001. "
            "Mfg Date: Jan 2025. Best Before: 12 months from manufacture. Customer Care: help@puregold.demo. "
            "Note: This demo listing intentionally omits Country of Origin."
        ),
        "scenario": "missing_origin",
        "scenario_label": "Missing country of origin (potential issue)",
    },

    # 3. Spicy Chips (Sparse Listing)
    "crunchyco-spicy-chips-50g": {
        "asin": "B0DEMOCHIP01",
        "slug": "crunchyco-spicy-chips-50g",
        "title": "CrunchyCo Spicy Masala Chips, Family Pack | Crunchy Potato Snack",
        "brand": "CrunchyCo",
        "category": "Grocery & Gourmet Foods › Snacks",
        "price": 129,
        "mrp": 129,
        "mrp_display": "Rs. 129",
        "discount_note": "Special price",
        "rating": 3.9,
        "reviews": 412,
        "bought": "500+ bought in past month",
        "in_stock": True,
        "images": ["chips.jpg"],
        "bullets": [
            "Spicy masala flavour",
            "Family pack for sharing",
            "Crispy potato chips",
        ],
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
            "CrunchyCo Spicy Masala Chips Family Pack Great taste. Buy now Special price 129. "
            "Crunchy snack for parties. Incomplete demo listing for compliance testing."
        ),
        "scenario": "sparse",
        "scenario_label": "Sparse listing (many fields missing)",
    },

    # 4. Assam Tea Bags
    "assam-classic-tea-bags-100g": {
        "asin": "B0DEMOTEA001",
        "slug": "assam-classic-tea-bags-100g",
        "title": "Assam Valley Classic Tea Bags, 100 g | Strong Morning Chai | 50 Bags",
        "brand": "Assam Valley",
        "category": "Grocery & Gourmet Foods › Tea",
        "price": 130,
        "mrp": 130,
        "mrp_display": "Rs. 130",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.3,
        "reviews": 2201,
        "bought": "3K+ bought in past month",
        "in_stock": True,
        "images": ["tea.jpg"],
        "bullets": [
            "Strong single origin Assam blend",
            "50 tea bags, 100 g net content",
            "Fresh aroma lock foil pouch",
        ],
        "fields": {
            "product_name": "Product Name: Classic Tea Bags",
            "mrp": "MRP Rs. 130 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 100 g",
            "manufacturer": "Manufactured by: Assam Tea Co, Dibrugarh, Assam - 786001",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Mfg Date: 01/2025",
            "expiry_date": "Best Before: 01/2027",
            "customer_care": "Customer Care: support@assamvalley.demo",
        },
        "description": (
            "Product Name: Classic Tea Bags. "
            "MRP Rs. 130 (Incl. of all taxes). Net Quantity: 100 g. "
            "Manufactured by: Assam Tea Co, Dibrugarh, Assam - 786001. Country of Origin: India. "
            "Mfg Date: 01/2025. Best Before: 01/2027. Customer Care: support@assamvalley.demo."
        ),
        "scenario": "complete",
        "scenario_label": "Complete tea listing",
    },

    # 5. Basmati Rice 5kg
    "royal-basmati-rice-5kg": {
        "asin": "B0DEMORICE05",
        "slug": "royal-basmati-rice-5kg",
        "title": "Royal Heritage Premium Basmati Rice, 5 kg Bag | Aged Long Grain Biryani Rice | Royal Fragrance",
        "brand": "Royal Heritage",
        "category": "Grocery & Gourmet Foods › Rice & Grains",
        "price": 715,
        "mrp": 715,
        "mrp_display": "Rs. 715",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.7,
        "reviews": 3410,
        "bought": "4K+ bought in past month",
        "in_stock": True,
        "images": ["rice.jpg"],
        "bullets": [
            "2 years aged authentic Himalayan basmati",
            "Extra long grain with fluffy texture",
            "Ideal for royal biryanis, pulao and steamed rice",
            "Hygienically packed 5 kg master bag",
        ],
        "fields": {
            "product_name": "Product Name: Royal Heritage Premium Basmati Rice",
            "mrp": "MRP Rs. 715 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 5 kg",
            "manufacturer": "Manufactured by: Royal Heritage Agro Foods Pvt Ltd, GT Road, Karnal, Haryana - 132001",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Mfg Date: 02/2025",
            "expiry_date": "Best Before: 02/2027",
            "customer_care": "Customer Care: care@royalheritage.demo | 1800-444-5555",
            "fssai": "FSSAI Lic. No.: 10014064000321",
        },
        "description": (
            "Royal Heritage Premium Basmati Rice 5kg. "
            "MRP Rs. 715 (Incl. of all taxes). Net Quantity: 5 kg. "
            "Manufactured by: Royal Heritage Agro Foods Pvt Ltd, GT Road, Karnal, Haryana - 132001. "
            "Country of Origin: India. Mfg Date: 02/2025. Best Before: 02/2027. "
            "Customer Care: care@royalheritage.demo | 1800-444-5555."
        ),
        "scenario": "complete",
        "scenario_label": "Complete standard grain pack (score ~100)",
    },

    # 6. California Almonds 500g (Missing Care)
    "nutrinut-california-almonds-500g": {
        "asin": "B0DEMOALMD50",
        "slug": "nutrinut-california-almonds-500g",
        "title": "NutriNut California Raw Almonds, 500g Pouch | Premium Whole Badam Giri | 100% Natural & Crunchy",
        "brand": "NutriNut",
        "category": "Grocery & Gourmet Foods › Dry Fruits & Nuts",
        "price": 546,
        "mrp": 546,
        "mrp_display": "Rs. 546",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.4,
        "reviews": 978,
        "bought": "1K+ bought in past month",
        "in_stock": True,
        "images": ["almonds.jpg"],
        "bullets": [
            "100% California raw whole almonds",
            "High protein, rich in dietary fiber and vitamin E",
            "Vacuum packed for lasting crunchiness",
        ],
        "fields": {
            "product_name": "Product Name: California Raw Almonds",
            "mrp": "MRP Rs. 546 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 500 g",
            "manufacturer": "Packed by: NutriNut Foods Ltd, Plot 42, Turbhe MIDC, Navi Mumbai - 400705",
            "country_of_origin": "Country of Origin: USA",
            "manufacturing_date": "Mfg Date: 01/2025",
            "expiry_date": "Best Before: 09/2025",
            "customer_care": None,  # Intentionally missing
        },
        "description": (
            "NutriNut California Raw Almonds 500g. "
            "MRP Rs. 546 (Incl. of all taxes). Net Quantity: 500 g. "
            "Packed by: NutriNut Foods Ltd, Navi Mumbai - 400705. Country of Origin: USA. "
            "Mfg Date: 01/2025. Best Before: 09/2025. "
            "Note: Missing customer care details for compliance test."
        ),
        "scenario": "missing_care",
        "scenario_label": "Missing customer care details (potential issue)",
    },

    # 7. Whole Wheat Atta 10kg (Missing Dates)
    "shudhkhet-whole-wheat-atta-10kg": {
        "asin": "B0DEMOATTA10",
        "slug": "shudhkhet-whole-wheat-atta-10kg",
        "title": "ShudhKhet Chakki Fresh 100% Whole Wheat Atta, 10 kg Bag | Traditional Stone Ground Flour",
        "brand": "ShudhKhet",
        "category": "Grocery & Gourmet Foods › Flours",
        "price": 572,
        "mrp": 572,
        "mrp_display": "Rs. 572",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.1,
        "reviews": 1540,
        "bought": "3K+ bought in past month",
        "in_stock": True,
        "images": ["atta.jpg"],
        "bullets": [
            "100% whole wheat grain Chakki ground",
            "Zero maida addition with natural bran retention",
            "Makes soft and fluffy rotis",
        ],
        "fields": {
            "product_name": "Product Name: ShudhKhet Whole Wheat Atta",
            "mrp": "MRP Rs. 572 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 10 kg",
            "manufacturer": "Manufactured by: ShudhKhet Flour Mills, Sector 3, Sanwer Road, Indore, MP - 452015",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": None,  # Intentionally missing
            "expiry_date": None,         # Intentionally missing
            "customer_care": "Customer Care: help@shudhkhet.demo",
        },
        "description": (
            "ShudhKhet Chakki Fresh Whole Wheat Atta 10kg. "
            "MRP Rs. 572 (Incl. of all taxes). Net Quantity: 10 kg. "
            "Manufactured by: ShudhKhet Flour Mills, Indore, MP - 452015. Country of Origin: India. "
            "Customer Care: help@shudhkhet.demo. "
            "Note: Missing manufacturing and expiry dates for compliance test."
        ),
        "scenario": "missing_dates",
        "scenario_label": "Missing manufacturing / expiry dates",
    },

    # 8. Dark Chocolate (Imported)
    "swissdelight-dark-chocolate-125g": {
        "asin": "B0DEMOCHOC12",
        "slug": "swissdelight-dark-chocolate-125g",
        "title": "SwissDelight 70% Dark Chocolate Bar, 125 g | Single Origin Swiss Alpine Cocoa Confectionery",
        "brand": "SwissDelight",
        "category": "Grocery & Gourmet Foods › Chocolates",
        "price": 273,
        "mrp": 273,
        "mrp_display": "Rs. 273",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.6,
        "reviews": 1120,
        "bought": "2K+ bought in past month",
        "in_stock": True,
        "images": ["chocolate.jpg"],
        "bullets": [
            "70% rich Swiss dark chocolate",
            "Single origin Alpine cocoa blend",
            "Smooth velvety gourmet finish",
        ],
        "fields": {
            "product_name": "Product Name: 70% Dark Chocolate Bar",
            "mrp": "MRP Rs. 273 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 125 g",
            "manufacturer": "Manufactured by: Chocolatier Suisse SA, Zurich, Switzerland. Imported by: Global Treats India Pvt Ltd, Andheri East, Mumbai, Maharashtra - 400069",
            "country_of_origin": "Country of Origin: Switzerland",
            "manufacturing_date": "Mfg Date: 11/2024",
            "expiry_date": "Best Before: 11/2025",
            "customer_care": "Customer Care: imports@globaltreat.demo | 1800-222-3344",
        },
        "description": (
            "SwissDelight 70% Dark Chocolate Bar 125g. "
            "MRP Rs. 273 (Incl. of all taxes). Net Quantity: 125 g. "
            "Manufactured by: Chocolatier Suisse SA, Zurich, Switzerland. "
            "Imported by: Global Treats India Pvt Ltd, Mumbai, Maharashtra - 400069. Country of Origin: Switzerland. "
            "Mfg Date: 11/2024. Best Before: 11/2025. Customer Care: imports@globaltreat.demo | 1800-222-3344."
        ),
        "scenario": "complete_imported",
        "scenario_label": "Imported commodity with complete declarations",
    },

    # 9. Herbal Shampoo 400ml
    "keshveda-herbal-shampoo-400ml": {
        "asin": "B0DEMOSHAMP4",
        "slug": "keshveda-herbal-shampoo-400ml",
        "title": "KeshVeda Ayurvedic Anti-Dandruff Herbal Shampoo, 400 ml Bottle | Bhringraj, Neem & Amla",
        "brand": "KeshVeda",
        "category": "Beauty & Personal Care › Hair Care",
        "price": 389,
        "mrp": 389,
        "mrp_display": "Rs. 389",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.5,
        "reviews": 2180,
        "bought": "3K+ bought in past month",
        "in_stock": True,
        "images": ["shampoo.jpg"],
        "bullets": [
            "Ayurvedic herbal blend with Bhringraj and Amla",
            "Natural scalp protection with pure Neem extracts",
            "Paraben and sulphate free formula",
        ],
        "fields": {
            "product_name": "Product Name: KeshVeda Herbal Shampoo",
            "mrp": "MRP Rs. 389 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 400 ml",
            "manufacturer": "Manufactured by: Veda Care Herbal Labs, Industrial Area, Haridwar, Uttarakhand - 249401",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Mfg Date: 01/2025",
            "expiry_date": "Best Before: 01/2028",
            "customer_care": "Customer Care: support@keshveda.demo | 1800-888-9999",
        },
        "description": (
            "KeshVeda Ayurvedic Anti-Dandruff Herbal Shampoo 400ml. "
            "MRP Rs. 389 (Incl. of all taxes). Net Quantity: 400 ml. "
            "Manufactured by: Veda Care Herbal Labs, Haridwar, Uttarakhand - 249401. Country of Origin: India. "
            "Mfg Date: 01/2025. Best Before: 01/2028. Customer Care: support@keshveda.demo | 1800-888-9999."
        ),
        "scenario": "complete_liquid",
        "scenario_label": "Personal care liquid volume (400 ml)",
    },

    # 10. Filter Coffee 200g
    "malabar-filter-coffee-200g": {
        "asin": "B0DEMOCOFF20",
        "slug": "malabar-filter-coffee-200g",
        "title": "Malabar Roast Pure Filter Coffee Powder, 200 g | 80:20 Coffee & Chicory South Indian Blend",
        "brand": "Malabar Roast",
        "category": "Grocery & Gourmet Foods › Coffee",
        "price": 208,
        "mrp": 208,
        "mrp_display": "Rs. 208",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.6,
        "reviews": 1890,
        "bought": "2K+ bought in past month",
        "in_stock": True,
        "images": ["coffee.jpg"],
        "bullets": [
            "Authentic South Indian 80:20 filter coffee blend",
            "Dark roast Plantation A Arabica & Robusta beans",
            "Intense decoction aroma",
        ],
        "fields": {
            "product_name": "Product Name: Malabar Roast Pure Filter Coffee Powder",
            "mrp": "MRP Rs. 208 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 200 g",
            "manufacturer": "Manufactured by: Malabar Coffee Works, Kalpetta, Wayanad, Kerala - 673121",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Mfg Date: 02/2025",
            "expiry_date": "Best Before: 11/2025",
            "customer_care": "Customer Care: hello@malabarroast.demo | 1800-333-7788",
            "fssai": "FSSAI Lic. No.: 11319008000452",
        },
        "description": (
            "Malabar Roast Pure Filter Coffee Powder 200g. "
            "MRP Rs. 208 (Incl. of all taxes). Net Quantity: 200 g. "
            "Manufactured by: Malabar Coffee Works, Wayanad, Kerala - 673121. Country of Origin: India. "
            "Mfg Date: 02/2025. Best Before: 11/2025. Customer Care: hello@malabarroast.demo | 1800-333-7788."
        ),
        "scenario": "complete",
        "scenario_label": "Complete beverage listing",
    },

    # 11. StridePro Running Shoes
    "stride-pro-running-shoes-uk8": {
        "asin": "B0DEMOSHOE01",
        "slug": "stride-pro-running-shoes-uk8",
        "title": "StridePro AeroGlide Men's Running Shoes | Ultra-Light Breathable Athletic Sneakers | Size UK 8",
        "brand": "StridePro",
        "category": "Shoes & Footwear › Men's Running Shoes",
        "price": 3899,
        "mrp": 3899,
        "mrp_display": "Rs. 3,899",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.6,
        "reviews": 2450,
        "bought": "1K+ bought in past month",
        "in_stock": True,
        "images": ["shoes.jpg"],
        "bullets": [
            "Engineered responsive cloud-cushion sole",
            "Breathable jacquard mesh upper",
            "Standard fit men's athletic sizing UK 8",
        ],
        "fields": {
            "product_name": "Product Name: StridePro AeroGlide Men's Running Shoes",
            "mrp": "MRP Rs. 3899 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 1 Pair",
            "dimensions": "Size: UK 8 (Euro 42 / 26.5 cm)",
            "manufacturer": "Manufactured by: StridePro Footwear Industries Ltd, Sikandra Industrial Area, Agra, UP - 282007",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Month & Year of Mfg: 01/2025",
            "customer_care": "Customer Care: care@stridepro.demo | 1800-222-7890",
        },
        "description": (
            "StridePro AeroGlide Men's Running Shoes. "
            "MRP Rs. 3899 (Incl. of all taxes). Net Quantity: 1 Pair. Size: UK 8. "
            "Manufactured by: StridePro Footwear Industries Ltd, Agra, UP - 282007. Country of Origin: India. "
            "Month & Year of Mfg: 01/2025. Customer Care: care@stridepro.demo | 1800-222-7890."
        ),
        "scenario": "complete_footwear",
        "scenario_label": "Complete footwear declarations (1 Pair, Size UK 8)",
    },

    # 12. Oxford Leather Shoes (Missing Origin)
    "urbanwalk-leather-oxford-shoes": {
        "asin": "B0DEMOOXFD02",
        "slug": "urbanwalk-leather-oxford-shoes",
        "title": "UrbanWalk Classic Handcrafted Genuine Leather Oxford Formal Shoes | Tan Brown | Size UK 9",
        "brand": "UrbanWalk",
        "category": "Shoes & Footwear › Men's Formal Shoes",
        "price": 4549,
        "mrp": 4549,
        "mrp_display": "Rs. 4,549",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.3,
        "reviews": 780,
        "bought": "400+ bought in past month",
        "in_stock": True,
        "images": ["oxford.jpg"],
        "bullets": [
            "100% genuine full-grain leather upper",
            "Hand-stitched Goodyear welted construction",
            "Size UK 9 / Tan Brown colour",
        ],
        "fields": {
            "product_name": "Product Name: UrbanWalk Leather Oxford Shoes",
            "mrp": "MRP Rs. 4549 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 1 Pair",
            "dimensions": "Size: UK 9",
            "manufacturer": "Manufactured by: UrbanWalk Leather Crafts, Jajmau, Kanpur, UP - 208010",
            "country_of_origin": None,  # Intentionally missing
            "manufacturing_date": "Month & Year of Mfg: 12/2024",
            "customer_care": "Customer Care: support@urbanwalk.demo",
        },
        "description": (
            "UrbanWalk Classic Leather Oxford Shoes. "
            "MRP Rs. 4549. Net Quantity: 1 Pair. Size: UK 9. "
            "Manufactured by: UrbanWalk Leather Crafts, Kanpur, UP - 208010. "
            "Month & Year of Mfg: 12/2024. Customer Care: support@urbanwalk.demo. "
            "Note: Intentionally missing Country of Origin declaration."
        ),
        "scenario": "missing_origin_footwear",
        "scenario_label": "Footwear with missing country of origin",
    },

    # 13. Denim Jeans Size 32
    "denimx-slim-stretch-jeans-32": {
        "asin": "B0DEMOJEAN32",
        "slug": "denimx-slim-stretch-jeans-32",
        "title": "DenimX Men's Slim Fit Stretch Cotton Jeans | Dark Indigo Whiskered Denim Trousers | Size 32",
        "brand": "DenimX",
        "category": "Clothing & Apparel › Men's Jeans",
        "price": 2469,
        "mrp": 2469,
        "mrp_display": "Rs. 2,469",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.5,
        "reviews": 3120,
        "bought": "2K+ bought in past month",
        "in_stock": True,
        "images": ["jeans.jpg"],
        "bullets": [
            "98% Cotton, 2% Elastane comfort stretch denim",
            "Slim fit with tapered leg opening",
            "Waist Size: 32 inches (81.2 cm), Length: 32 inches",
        ],
        "fields": {
            "product_name": "Product Name: DenimX Men's Slim Fit Jeans",
            "mrp": "MRP Rs. 2469 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 1 Piece",
            "dimensions": "Size: 32 (Waist: 81.2 cm, Inseam: 81.2 cm)",
            "manufacturer": "Manufactured by: DenimX Garments India Pvt Ltd, SIDCO Industrial Estate, Tirupur, TN - 641603",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Month & Year of Packing: 02/2025",
            "customer_care": "Customer Care: help@denimx.demo | 1800-444-1234",
        },
        "description": (
            "DenimX Men's Slim Fit Jeans. "
            "MRP Rs. 2469 (Incl. of all taxes). Net Quantity: 1 Piece. Size: 32 (81.2 cm). "
            "Manufactured by: DenimX Garments India Pvt Ltd, Tirupur, TN - 641603. Country of Origin: India. "
            "Month & Year of Packing: 02/2025. Customer Care: help@denimx.demo | 1800-444-1234."
        ),
        "scenario": "complete_apparel",
        "scenario_label": "Complete apparel declarations (1 Piece, Size 32)",
    },

    # 14. Cotton Polo T-Shirt (Missing Care)
    "aerofit-cotton-polo-tshirt-l": {
        "asin": "B0DEMOPOLO01",
        "slug": "aerofit-cotton-polo-tshirt-l",
        "title": "AeroFit Premium Pique 100% Combed Cotton Regular Fit Polo T-Shirt | Crimson Red | Size L",
        "brand": "AeroFit",
        "category": "Clothing & Apparel › Men's Polos",
        "price": 1169,
        "mrp": 1169,
        "mrp_display": "Rs. 1,169",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.4,
        "reviews": 1820,
        "bought": "1K+ bought in past month",
        "in_stock": True,
        "images": ["polo.jpg"],
        "bullets": [
            "220 GSM heavy pique combed cotton",
            "Ribbed collar and sleeve hems",
            "Size L (Chest: 106.7 cm, Length: 73.6 cm)",
        ],
        "fields": {
            "product_name": "Product Name: AeroFit Cotton Polo T-Shirt",
            "mrp": "MRP Rs. 1169 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 1 Piece",
            "dimensions": "Size: L (Chest: 106.7 cm)",
            "manufacturer": "Manufactured by: AeroFit Apparels Ltd, Pandesara GIDC, Surat, Gujarat - 394221",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Month & Year of Packing: 01/2025",
            "customer_care": None,  # Intentionally missing
        },
        "description": (
            "AeroFit Premium Cotton Polo T-Shirt. "
            "MRP Rs. 1169. Net Quantity: 1 Piece. Size: L. "
            "Manufactured by: AeroFit Apparels Ltd, Surat, Gujarat - 394221. Country of Origin: India. "
            "Month & Year of Packing: 01/2025. "
            "Note: Missing customer care details for test."
        ),
        "scenario": "missing_care_apparel",
        "scenario_label": "Branded clothing with missing customer care",
    },

    # 15. TWS Wireless Earbuds
    "soundwave-pulse-pro-earbuds": {
        "asin": "B0DEMOTWS450",
        "slug": "soundwave-pulse-pro-earbuds",
        "title": "SoundWave Pulse Pro True Wireless Earbuds (TWS) | 45dB Hybrid ANC | 40H Battery | Fast Charging",
        "brand": "SoundWave",
        "category": "Electronics › Headphones & Earbuds",
        "price": 3249,
        "mrp": 3249,
        "mrp_display": "Rs. 3,249",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.6,
        "reviews": 5600,
        "bought": "5K+ bought in past month",
        "in_stock": True,
        "images": ["earbuds.jpg"],
        "bullets": [
            "45dB Hybrid Active Noise Cancellation",
            "10mm Titanium drivers with spatial audio",
            "Up to 40 hours playtime with Type-C fast charging case",
            "IPX5 sweat and water resistance",
        ],
        "fields": {
            "product_name": "Product Name: SoundWave Pulse Pro TWS Earbuds",
            "mrp": "MRP Rs. 3249 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 1 Set (Contains: 1 Pair Earbuds, 1 Charging Case, 1 Type-C Cable, 2 Pairs Ear Tips)",
            "manufacturer": "Manufactured by: SoundWave Audio Tech Pvt Ltd, Electronics City Phase 1, Bengaluru, Karnataka - 560100",
            "country_of_origin": "Country of Origin: India",
            "manufacturing_date": "Month & Year of Mfg: 02/2025",
            "customer_care": "Customer Care: support@soundwave.demo | 1800-999-0011",
        },
        "description": (
            "SoundWave Pulse Pro True Wireless Earbuds (TWS). "
            "MRP Rs. 3249 (Incl. of all taxes). "
            "Net Quantity: 1 Set (Contains: 1 Pair Earbuds, 1 Charging Case, 1 Type-C Cable, 2 Pairs Ear Tips). "
            "Manufactured by: SoundWave Audio Tech Pvt Ltd, Electronics City Phase 1, Bengaluru, Karnataka - 560100. "
            "Country of Origin: India. Month & Year of Mfg: 02/2025. Customer Care: support@soundwave.demo | 1800-999-0011."
        ),
        "scenario": "complete_electronics",
        "scenario_label": "Complete electronics declarations (TWS Earbuds Set)",
    },

    # 16. 65W GaN Fast Charger (Imported)
    "voltmax-65w-gan-fast-charger": {
        "asin": "B0DEMOGAN065",
        "slug": "voltmax-65w-gan-fast-charger",
        "title": "VoltMax 65W GaN Dual USB-C Fast Wall Charger | Multi-Protocol PD PPS Power Adapter for Laptops & Phones",
        "brand": "VoltMax",
        "category": "Electronics › Mobile Accessories",
        "price": 2079,
        "mrp": 2079,
        "mrp_display": "Rs. 2,079",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.7,
        "reviews": 1940,
        "bought": "3K+ bought in past month",
        "in_stock": True,
        "images": ["charger.jpg"],
        "bullets": [
            "65W high speed GaN technology",
            "Dual USB-C Power Delivery 3.0 & PPS ports",
            "Universal charging for laptops, tablets and smartphones",
        ],
        "fields": {
            "product_name": "Product Name: VoltMax 65W GaN Fast Wall Charger",
            "mrp": "MRP Rs. 2079 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 1 Unit",
            "manufacturer": "Manufactured by: VoltMax Power Ltd, Que Vo Industrial Zone, Bac Ninh, Vietnam. Imported by: VoltMax India Technologies Pvt Ltd, Cyber City, Gurugram, Haryana - 122002",
            "country_of_origin": "Country of Origin: Vietnam",
            "manufacturing_date": "Month & Year of Import: 01/2025",
            "customer_care": "Customer Care: help@voltmax.demo | 1800-333-8888",
        },
        "description": (
            "VoltMax 65W GaN Fast Wall Charger. "
            "MRP Rs. 2079 (Incl. of all taxes). Net Quantity: 1 Unit. "
            "Manufactured by: VoltMax Power Ltd, Bac Ninh, Vietnam. "
            "Imported by: VoltMax India Technologies Pvt Ltd, Cyber City, Gurugram, Haryana - 122002. "
            "Country of Origin: Vietnam. Month & Year of Import: 01/2025. Customer Care: help@voltmax.demo | 1800-333-8888."
        ),
        "scenario": "complete_imported_electronics",
        "scenario_label": "Imported electronics with complete importer & origin declarations",
    },

    # 17. Smartwatch (Missing Import Date)
    "pulsefit-horizon-smartwatch": {
        "asin": "B0DEMOWATCH1",
        "slug": "pulsefit-horizon-smartwatch",
        "title": "PulseFit Horizon 1.96\" AMOLED Bluetooth Calling Smartwatch | Zinc Alloy Metal Frame | AI Voice Assistant",
        "brand": "PulseFit",
        "category": "Electronics › Smartwatches & Wearables",
        "price": 4289,
        "mrp": 4289,
        "mrp_display": "Rs. 4,289",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.2,
        "reviews": 1150,
        "bought": "800+ bought in past month",
        "in_stock": True,
        "images": ["smartwatch.jpg"],
        "bullets": [
            "1.96\" HD AMOLED display with 60Hz refresh rate",
            "Advanced Bluetooth 5.3 calling with built-in mic",
            "Heart rate, SpO2 and sleep health monitoring",
        ],
        "fields": {
            "product_name": "Product Name: PulseFit Horizon Smartwatch",
            "mrp": "MRP Rs. 4289 (Incl. of all taxes)",
            "net_quantity": "Net Quantity: 1 Unit",
            "manufacturer": "Manufactured by: PulseFit Electronics Co, Bao'an District, Shenzhen, China. Imported by: PulseFit India Retail Pvt Ltd, Okhla Phase 3, New Delhi - 110020",
            "country_of_origin": "Country of Origin: China",
            "manufacturing_date": None,  # Intentionally missing
            "customer_care": "Customer Care: support@pulsefit.demo",
        },
        "description": (
            "PulseFit Horizon Smartwatch. "
            "MRP Rs. 4289. Net Quantity: 1 Unit. "
            "Manufactured by: PulseFit Electronics Co, Shenzhen, China. "
            "Imported by: PulseFit India Retail Pvt Ltd, New Delhi - 110020. Country of Origin: China. "
            "Customer Care: support@pulsefit.demo. "
            "Note: Intentionally missing month & year of import."
        ),
        "scenario": "missing_import_date",
        "scenario_label": "Smartwatch with missing month & year of import",
    },
}


def _regex_blind_catalog_entry(doc: dict[str, Any]) -> dict[str, Any]:
    slug = doc["id"]
    values = doc["values"]
    return {
        "asin": doc["asin"],
        "slug": slug,
        "title": doc["title"],
        "brand": doc["brand"],
        "category": doc["category"],
        "price": doc["price"],
        "mrp": doc["price"],
        "mrp_display": f"Rs. {doc['price']}",
        "discount_note": "Inclusive of all taxes",
        "rating": 4.1,
        "reviews": 640,
        "bought": "400+ bought in past month",
        "in_stock": True,
        "images": list(doc["images"]),
        "bullets": list(doc["bullets"]),
        "fields": {
            "product_name": values["product_name"],
            "mrp": values["mrp"],
            "net_quantity": values["net_quantity"],
            "manufacturer": values["manufacturer"],
            "country_of_origin": values["country_of_origin"],
            "manufacturing_date": values["manufacturing_date"],
            "expiry_date": values["expiry_date"],
        },
        "lm_lines": list(doc["lm_lines"]),
        "description": doc["text"],
        "regex_blind": True,
        "scenario": "regex_blind",
        "scenario_label": "Paraphrased declarations (regex-blind)",
    }


for _blind in REGEX_BLIND_DOCS:
    PRODUCTS[_blind["id"]] = _regex_blind_catalog_entry(_blind)


def list_products() -> list[dict[str, Any]]:
    return list(PRODUCTS.values())


def get_product(slug: str) -> dict[str, Any] | None:
    return PRODUCTS.get(slug)


def public_catalog(base_url: str = "http://127.0.0.1:5000") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in PRODUCTS.values():
        out.append(
            {
                "slug": p["slug"],
                "title": p["title"],
                "brand": p.get("brand"),
                "url": f"{base_url.rstrip('/')}/demo/dp/{p['slug']}",
                "price": p["price"],
                "scenario": p.get("scenario"),
                "scenario_label": p.get("scenario_label"),
                "regex_blind": bool(p.get("regex_blind")),
            }
        )
    return out
