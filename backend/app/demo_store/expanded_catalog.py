"""Extra DemoMart listings. Each row is a different product.

Brands are fictional. Pack sizes and prices follow common Indian shelves.
A fault omits a declaration the rule engine requires, or prints two MRPs.
The same studio photo may be shared by up to three different products.
"""

from __future__ import annotations

from typing import Any

# fault codes: "" clear, or origin, manufacturer, mrp, qty, dates, sparse, conflict
_FAULT_LABEL = {
    "": "Complete declarations (high score)",
    "origin": "Missing country of origin",
    "manufacturer": "Missing manufacturer / packer",
    "mrp": "Missing MRP declaration",
    "qty": "Missing net quantity",
    "dates": "Missing manufacturing and expiry dates",
    "sparse": "Several mandatory declarations missing",
    "conflict": "Page MRP and pack MRP disagree",
}

# One product per line. Three different goods may share one studio photo.
# brand|brand_slug|product|product_slug|size_slug|words|qty|price|mrp|category|sub|image|maker|origin|fault
_SPEC = """
NectarJar|nectarjar|Wild Forest Honey|wild-honey|500g|500 g|500 g|349|425|Grocery & Gourmet Foods|Honey|honey-2.jpg|NectarJar Apiaries, Mahabaleshwar, Maharashtra - 412806|India|
GroveHive|grovehive|Acacia Honey|acacia-honey|250g|250 g|250 g|189|240|Grocery & Gourmet Foods|Honey|honey-2.jpg|GroveHive Apiaries, Madikeri, Karnataka - 571201|India|origin
AmberComb|ambercomb|Eucalyptus Honey|eucalyptus-honey|400g|400 g|400 g|275|340|Grocery & Gourmet Foods|Honey|honey-2.jpg|AmberComb Farms, Canning, West Bengal - 743329|India|dates
WhiteCrystal|whitecrystal|Iodised Salt|iodised-salt|1kg|1 kg|1 kg|28|32|Grocery & Gourmet Foods|Salt|salt.jpg|WhiteCrystal Salt Works, Bhavnagar, Gujarat - 364002|India|
SeaPan|seapan|Rock Salt|rock-salt|500g|500 g|500 g|42|55|Grocery & Gourmet Foods|Salt|salt.jpg|SeaPan Minerals, Bhuj, Gujarat - 370001|India|mrp
PinkWell|pinkwell|Sendha Salt|sendha-salt|200g|200 g|200 g|35|48|Grocery & Gourmet Foods|Salt|salt.jpg|PinkWell Spices, Jaipur, Rajasthan - 302001|India|qty
OrchardGold|orchardgold|Mixed Fruit Juice|mixed-fruit-juice|1l|1 L|1 L|95|120|Grocery & Gourmet Foods|Beverages|juice.jpg|OrchardGold Beverages, Nashik, Maharashtra - 422001|India|
CanePress|canepress|Sugarcane Juice|sugarcane-juice|500ml|500 ml|500 ml|40|50|Grocery & Gourmet Foods|Beverages|juice.jpg|CanePress Drinks, Meerut, Uttar Pradesh - 250001|India|manufacturer
PulpLane|pulplane|Alphonso Mango Nectar|mango-nectar|1l|1 L|1 L|110|140|Grocery & Gourmet Foods|Beverages|juice.jpg|PulpLane Foods, Ratnagiri, Maharashtra - 415612|India|sparse
PaperDesk|paperdesk|Single Line Notebook|notebook|172p|172 pages|1 N|45|55|Home & Kitchen|Stationery|notebook.jpg|PaperDesk Stationery, Sivakasi, Tamil Nadu - 626123|India|
MarginLine|marginline|Long Notebook|long-notebook|240p|240 pages|1 N|70|85|Home & Kitchen|Stationery|notebook.jpg|MarginLine Paper, Rajahmundry, Andhra Pradesh - 533101|India|origin
ExamPad|exampad|Graph Notebook|graph-notebook|64p|64 pages|1 N|30|40|Home & Kitchen|Stationery|notebook.jpg|ExamPad Stationery, Dewas, Madhya Pradesh - 455001|India|dates
SoyaGold|soya-gold|Soybean Oil|soybean-oil|500ml|500 ml|500 ml|92|115|Grocery & Gourmet Foods|Cooking Oils|oil-2.jpg|SoyaGold Foods Pvt Ltd, Kheda, Gujarat - 387411|India|origin
MustardPress|mustardpress|Kachi Ghani Mustard Oil|mustard-oil|1l|1 L|1 L|165|199|Grocery & Gourmet Foods|Cooking Oils|oil-2.jpg|MustardPress Mills, Alwar, Rajasthan - 301001|India|mrp
GroundPot|groundpot|Filtered Groundnut Oil|groundnut-oil|1l|1 L|1 L|175|210|Grocery & Gourmet Foods|Cooking Oils|oil-2.jpg|GroundPot Expellers, Rajkot, Gujarat - 360001|India|dates
LeafKettle|leafkettle|Assam Leaf Tea|assam-tea|250g|250 g|250 g|145|180|Grocery & Gourmet Foods|Tea|tea-2.jpg|LeafKettle Tea Co, Jorhat, Assam - 785001|India|
HillDust|hilldust|CTC Dust Tea|dust-tea|250g|250 g|250 g|105|130|Grocery & Gourmet Foods|Tea|tea-2.jpg|HillDust Tea Co, Dibrugarh, Assam - 786001|India|manufacturer
MasalaPot|masalapot|Masala Chai Blend|masala-tea|100g|100 g|100 g|75|95|Grocery & Gourmet Foods|Tea|tea-2.jpg|MasalaPot Blenders, Nagpur, Maharashtra - 440001|India|sparse
MasalaCrunch|masalacrunch|Masala Potato Chips|masala-chips|50g|50 g|50 g|20|25|Grocery & Gourmet Foods|Snacks|chips-2.jpg|MasalaCrunch Snacks, Indore, Madhya Pradesh - 452001|India|dates
SaltRidge|saltridge|Classic Salted Chips|salted-chips|40g|40 g|40 g|18|20|Grocery & Gourmet Foods|Snacks|chips-2.jpg|SaltRidge Foods, Pune, Maharashtra - 411001|India|origin
RingBite|ringbite|Tomato Rings|tomato-rings|60g|60 g|60 g|20|30|Grocery & Gourmet Foods|Snacks|chips-2.jpg|RingBite Snacks, Hyderabad, Telangana - 500001|India|conflict
ToorMill|toormill|Arhar Dal|arhar-dal|1kg|1 kg|1 kg|155|185|Grocery & Gourmet Foods|Pulses|lentils.jpg|ToorMill Pulses, Akola, Maharashtra - 444001|India|
DalHouse|dalhouse|Masoor Dal|masoor-dal|1kg|1 kg|1 kg|135|165|Grocery & Gourmet Foods|Pulses|lentils.jpg|DalHouse Mills, Latur, Maharashtra - 413512|India|mrp
MoongYard|moongyard|Yellow Moong Dal|moong-dal|500g|500 g|500 g|78|95|Grocery & Gourmet Foods|Pulses|lentils.jpg|MoongYard Mills, Nagaur, Rajasthan - 341001|India|dates
MintPaste|mintpaste|Fluoride Toothpaste|toothpaste|100g|100 g|100 g|62|79|Beauty & Personal Care|Oral Care|toothpaste.jpg|MintPaste Hygiene, Baddi, Himachal Pradesh - 173205|India|mrp
NeemGum|neemgum|Herbal Toothpaste|herbal-toothpaste|150g|150 g|150 g|85|110|Beauty & Personal Care|Oral Care|toothpaste.jpg|NeemGum Care, Haridwar, Uttarakhand - 249401|India|origin
CalmMint|calmmint|Sensitive Toothpaste|sensitive-toothpaste|80g|80 g|80 g|95|125|Beauty & Personal Care|Oral Care|toothpaste.jpg|CalmMint Labs, Baddi, Himachal Pradesh - 173205|India|dates
NirmalWash|nirmalwash|Detergent Powder|detergent|1kg|1 kg|1 kg|99|125|Home & Kitchen|Laundry|detergent.jpg|NirmalWash Chemicals, Ankleshwar, Gujarat - 393002|India|manufacturer
BarClean|barclean|Detergent Bar|detergent-bar|250g|250 g|250 g|22|28|Home & Kitchen|Laundry|detergent.jpg|BarClean Soaps, Kanpur, Uttar Pradesh - 208001|India|sparse
LiquidTub|liquidtub|Matic Liquid Detergent|liquid-detergent|1l|1 L|1 L|189|249|Home & Kitchen|Laundry|detergent.jpg|LiquidTub Home Care, Vapi, Gujarat - 396191|India|conflict
GlucoseGold|glucosegold|Glucose Biscuits|glucose-biscuits|150g|150 g|150 g|20|25|Grocery & Gourmet Foods|Biscuits|biscuit.jpg|GlucoseGold Bakers, Malanpur, Madhya Pradesh - 477117|India|
CrunchBite|crunchbite|Marie Biscuits|marie-biscuits|200g|200 g|200 g|25|30|Grocery & Gourmet Foods|Biscuits|biscuit.jpg|CrunchBite Bakers, Malanpur, Madhya Pradesh - 477117|India|mrp
CreamFill|creamfill|Vanilla Sandwich Biscuits|sandwich-biscuits|300g|300 g|300 g|45|55|Grocery & Gourmet Foods|Biscuits|biscuit.jpg|CreamFill Bakery, Rudrapur, Uttarakhand - 263153|India|qty
GlycerinSoft|glycerinsoft|Transparent Soap|transparent-soap|100g|100 g|100 g|40|55|Beauty & Personal Care|Soap|soap.jpg|GlycerinSoft Soaps, Baddi, Himachal Pradesh - 173205|India|
NeemBar|neembar|Neem Bathing Soap|bathing-soap|125g|125 g|125 g|40|52|Beauty & Personal Care|Soap|soap.jpg|NeemBar Soaps, Baddi, Himachal Pradesh - 173205|India|dates
SandalBar|sandalbar|Sandal Soap|sandal-soap|150g|150 g|150 g|55|70|Beauty & Personal Care|Soap|soap.jpg|SandalBar Perfumers, Kannauj, Uttar Pradesh - 209725|India|sparse
FarmPouch|farmpouch|Toned Milk|toned-milk|500ml|500 ml|500 ml|28|34|Grocery & Gourmet Foods|Dairy|milk.jpg|FarmPouch Dairy, Anand, Gujarat - 388001|India|origin
CurdCup|curdcup|Set Dahi|set-dahi|400g|400 g|400 g|35|42|Grocery & Gourmet Foods|Dairy|milk.jpg|CurdCup Dairy, Anand, Gujarat - 388001|India|dates
PaneerBlock|paneerblock|Malai Paneer|malai-paneer|200g|200 g|200 g|90|110|Grocery & Gourmet Foods|Dairy|milk.jpg|PaneerBlock Dairy, Karnal, Haryana - 132001|India|mrp
TubeLite|tubelite|LED Batten|led-batten|20w|20 W|1 N|249|349|Electronics|Lighting|bulb.jpg|TubeLite Electricals, Noida, Uttar Pradesh - 201301|India|
BrightBulb|brightbulb|LED Bulb|led-bulb|9w|9 W|1 N|89|129|Electronics|Lighting|bulb.jpg|BrightBulb Electricals, Noida, Uttar Pradesh - 201301|India|origin
NightGlow|nightglow|Night Lamp|night-lamp|05w|0.5 W|1 N|99|149|Electronics|Lighting|bulb.jpg|NightGlow Lamps, Pune, Maharashtra - 411026|India|manufacturer
CopperLine|copperline|USB-C Charging Cable|usb-c-cable|1m|1 m|1 m|199|299|Electronics|Cables|cable.jpg|CopperLine Accessories, Shenzhen|China|mrp
AuxBeat|auxbeat|Audio Cable|audio-cable|1-5m|1.5 m|1.5 m|149|199|Electronics|Cables|cable.jpg|AuxBeat Accessories, Shenzhen|China|conflict
ChargeBrick|chargebrick|Micro-USB Cable|micro-usb-cable|1m|1 m|1 m|129|179|Electronics|Cables|cable.jpg|ChargeBrick Cables, Shenzhen|China|sparse
QuickBowl|quickbowl|Masala Instant Noodles|instant-noodles|70g|70 g|70 g|14|15|Grocery & Gourmet Foods|Noodles|noodles.jpg|QuickBowl Foods, Mysuru, Karnataka - 570016|India|qty
HakkaWok|hakkawok|Hakka Noodles|hakka-noodles|400g|400 g|400 g|55|70|Grocery & Gourmet Foods|Noodles|noodles.jpg|HakkaWok Foods, Bengaluru, Karnataka - 560001|India|origin
SoupCup|soupcup|Tomato Cup Noodles|cup-noodles|60g|60 g|60 g|25|30|Grocery & Gourmet Foods|Noodles|noodles.jpg|SoupCup Foods, Kolkata, West Bengal - 700001|India|dates
OrchardJar|orchardjar|Mixed Fruit Jam|mixed-fruit-jam|500g|500 g|500 g|175|220|Grocery & Gourmet Foods|Spreads|jam.jpg|OrchardJar Preserves, Pune, Maharashtra - 411001|India|manufacturer
BerryPot|berrypot|Strawberry Jam|strawberry-jam|300g|300 g|300 g|145|180|Grocery & Gourmet Foods|Spreads|jam.jpg|BerryPot Preserves, Mahabaleshwar, Maharashtra - 412806|India|mrp
OrangeMarm|orangemarm|Orange Marmalade|orange-marmalade|250g|250 g|250 g|130|165|Grocery & Gourmet Foods|Spreads|jam.jpg|OrangeMarm Foods, Nagpur, Maharashtra - 440001|India|origin
CreamTop|creamtop|Table Butter|table-butter|100g|100 g|100 g|55|68|Grocery & Gourmet Foods|Dairy|butter.jpg|CreamTop Dairy, Anand, Gujarat - 388001|India|
TableChurn|tablechurn|White Butter|white-butter|200g|200 g|200 g|105|130|Grocery & Gourmet Foods|Dairy|butter.jpg|TableChurn Dairy, Karnal, Haryana - 132001|India|dates
SliceDairy|slicedairy|Processed Cheese Slices|cheese-slices|200g|200 g|200 g|120|155|Grocery & Gourmet Foods|Dairy|butter.jpg|SliceDairy Foods, Palanpur, Gujarat - 385001|India|conflict
MumbaiMix|mumbaimix|Bhujia Namkeen|bhujia|400g|400 g|400 g|99|125|Grocery & Gourmet Foods|Snacks|namkeen.jpg|MumbaiMix Namkeen, Bikaner, Rajasthan - 334001|India|origin
SevCorner|sevcorner|Ratlami Sev|ratlami-sev|200g|200 g|200 g|70|90|Grocery & Gourmet Foods|Snacks|namkeen.jpg|SevCorner Snacks, Ratlam, Madhya Pradesh - 457001|India|qty
MixtureTin|mixturetin|Bombay Mixture|bombay-mixture|400g|400 g|400 g|110|140|Grocery & Gourmet Foods|Snacks|namkeen.jpg|MixtureTin Foods, Indore, Madhya Pradesh - 452001|India|manufacturer
Sunrise|sunrise|Tomato Ketchup|tomato-ketchup|1kg|1 kg|1 kg|195|249|Grocery & Gourmet Foods|Sauces|ketchup.jpg|Sunrise Foods, Kolkata, West Bengal - 700001|India|conflict
ChilliBowl|chillibowl|Red Chilli Sauce|chilli-sauce|200g|200 g|200 g|65|85|Grocery & Gourmet Foods|Sauces|ketchup.jpg|ChilliBowl Foods, Kolkata, West Bengal - 700001|India|mrp
SoyaDip|soyadip|Dark Soy Sauce|soy-sauce|200ml|200 ml|200 ml|75|95|Grocery & Gourmet Foods|Sauces|ketchup.jpg|SoyaDip Kitchens, Bengaluru, Karnataka - 560038|India|dates
MillRoad|millroad|Sulphurless Sugar|sugar|1kg|1 kg|1 kg|55|68|Grocery & Gourmet Foods|Sugar|sugar.jpg|MillRoad Sugars, Mandya, Karnataka - 571401|India|sparse
BrownMill|brownmill|Demerara Sugar|demerara-sugar|500g|500 g|500 g|70|90|Grocery & Gourmet Foods|Sugar|sugar.jpg|BrownMill Sugars, Kolhapur, Maharashtra - 416001|India|origin
RockCandy|rockcandy|Mishri Crystals|mishri|200g|200 g|200 g|45|60|Grocery & Gourmet Foods|Sugar|sugar.jpg|RockCandy Traders, Jaipur, Rajasthan - 302001|India|manufacturer
CocoShine|cocoshine|Coconut Hair Oil|coconut-hair-oil|200ml|200 ml|200 ml|95|120|Beauty & Personal Care|Hair Care|hairoil.jpg|CocoShine Oils, Kochi, Kerala - 682001|India|dates
AmlaDrop|amladrop|Amla Hair Oil|amla-hair-oil|150ml|150 ml|150 ml|80|99|Beauty & Personal Care|Hair Care|hairoil.jpg|AmlaDrop Oils, Indore, Madhya Pradesh - 452001|India|mrp
HerbRoot|herbroot|Bhringraj Hair Oil|bhringraj-oil|100ml|100 ml|100 ml|120|155|Beauty & Personal Care|Hair Care|hairoil.jpg|HerbRoot Ayurveda, Haridwar, Uttarakhand - 249401|India|origin
SoftDew|softdew|Daily Body Lotion|body-lotion|200ml|200 ml|200 ml|175|249|Beauty & Personal Care|Skin Care|lotion.jpg|SoftDew Personal Care, Haridwar, Uttarakhand - 249401|India|manufacturer
AloeGel|aloegel|Aloe Vera Gel|aloe-gel|100ml|100 ml|100 ml|99|149|Beauty & Personal Care|Skin Care|lotion.jpg|AloeGel Care, Jodhpur, Rajasthan - 342001|India|qty
WinterPalm|winterpalm|Hand Cream|hand-cream|50ml|50 ml|50 ml|85|120|Beauty & Personal Care|Skin Care|lotion.jpg|WinterPalm Care, Solan, Himachal Pradesh - 173212|India|dates
StepEase|stepease|Bathroom Slippers|slippers|uk7|UK 7|1 Pair|149|199|Footwear|Slippers|slippers.jpg|StepEase Footwear, Agra, Uttar Pradesh - 282001|India|origin
FlipWalk|flipwalk|Rubber Flip Flops|flip-flops|uk8|UK 8|1 Pair|199|299|Footwear|Slippers|slippers.jpg|FlipWalk Footwear, Bahadurgarh, Haryana - 124507|India|sparse
HomeSole|homesole|House Slippers|house-slippers|uk6|UK 6|1 Pair|249|349|Footwear|Slippers|slippers.jpg|HomeSole Footwear, Agra, Uttar Pradesh - 282001|India|mrp
DailyKnit|dailyknit|Ankle Socks|ankle-socks|3pair|Pack of 3|3 N|199|249|Clothing & Apparel|Socks|socks.jpg|DailyKnit Hosiery, Tiruppur, Tamil Nadu - 641601|India|dates
SportKnit|sportknit|Crew Sports Socks|sports-socks|1pair|1 Pair|1 Pair|129|179|Clothing & Apparel|Socks|socks.jpg|SportKnit Hosiery, Tiruppur, Tamil Nadu - 641601|India|manufacturer
FormalPair|formalpair|Formal Cotton Socks|formal-socks|1pair|1 Pair|1 Pair|99|149|Clothing & Apparel|Socks|socks.jpg|FormalPair Hosiery, Ludhiana, Punjab - 141001|India|qty
PlainLoom|plainloom|Cotton Crew T-Shirt|crew-tshirt|m|Medium|1 N|299|499|Clothing & Apparel|T-Shirts|tshirt.jpg|PlainLoom Apparel, Tiruppur, Tamil Nadu - 641601|India|origin
VestLoom|vestloom|Cotton Vest|cotton-vest|m|Medium|1 N|199|299|Clothing & Apparel|Vests|tshirt.jpg|VestLoom Knitwear, Tiruppur, Tamil Nadu - 641601|India|conflict
PoloYard|poloyard|Pique Polo|pique-polo|m|Medium|1 N|449|699|Clothing & Apparel|T-Shirts|tshirt.jpg|PoloYard Apparel, Tiruppur, Tamil Nadu - 641602|India|dates
CellPack|cellpack|AA Alkaline Batteries|aa-battery|4n|Pack of 4|4 N|110|145|Electronics|Batteries|battery.jpg|CellPack Energy, Penang|Malaysia|mrp
CoinCell|coincell|CR2032 Coin Cells|coin-cell|5n|Pack of 5|5 N|90|120|Electronics|Batteries|battery.jpg|CoinCell Energy, Penang|Malaysia|sparse
BlockCell|blockcell|9V Battery|9v-battery|1n|1 N|1 N|45|60|Electronics|Batteries|battery.jpg|BlockCell Energy, Penang|Malaysia|origin
SteelSip|steelsip|Steel Water Bottle|water-bottle|750ml|750 ml|750 ml|449|649|Home & Kitchen|Drinkware|bottle.jpg|SteelSip Housewares, Rajkot, Gujarat - 360001|India|
GlassSip|glasssip|Borosilicate Bottle|glass-bottle|500ml|500 ml|500 ml|299|399|Home & Kitchen|Drinkware|bottle.jpg|GlassSip Glassworks, Firozabad, Uttar Pradesh - 283203|India|dates
KidSip|kidsip|Kids Water Bottle|kids-bottle|400ml|400 ml|400 ml|199|279|Home & Kitchen|Drinkware|bottle.jpg|KidSip Plastics, Daman - 396210|India|qty
PressureHome|pressurehome|Aluminium Pressure Cooker|pressure-cooker|3l|3 L|1 N|1099|1599|Home & Kitchen|Cookware|cooker.jpg|PressureHome Metals, Rajkot, Gujarat - 360004|India|origin
TawaHome|tawahome|Non-stick Tawa|nonstick-tawa|26cm|26 cm|1 N|499|699|Home & Kitchen|Cookware|cooker.jpg|TawaHome Metals, Rajkot, Gujarat - 360004|India|mrp
SaucePot|saucepot|Aluminium Saucepan|saucepan|2l|2 L|1 N|399|549|Home & Kitchen|Cookware|cooker.jpg|SaucePot Metals, Jagadhri, Haryana - 135003|India|conflict
HandYard|handyard|Cotton Hand Towel|hand-towel|2n|Pack of 2|2 N|199|299|Home & Kitchen|Bath|towel.jpg|HandYard Textiles, Solapur, Maharashtra - 413001|India|
CottonYard|cottonyard|Cotton Bath Towel|bath-towel|1n|Single|1 N|249|399|Home & Kitchen|Bath|towel.jpg|CottonYard Textiles, Solapur, Maharashtra - 413001|India|dates
WipeYard|wipeyard|Kitchen Towels|kitchen-towel|3n|Pack of 3|3 N|179|249|Home & Kitchen|Bath|towel.jpg|WipeYard Textiles, Solapur, Maharashtra - 413001|India|manufacturer
"""


def _load_groups(spec: str) -> list[list[tuple]]:
    groups: list[list[tuple]] = []
    current: list[tuple] = []
    current_image = ""
    for raw in spec.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 15:
            raise ValueError(f"Expected 15 fields, got {len(parts)}: {line}")
        (
            brand, brand_slug, product, product_slug, size_slug, words, qty,
            price, mrp, ui, sub, image, maker, origin, fault,
        ) = parts
        row = (
            brand, brand_slug, product, product_slug, size_slug, words, qty,
            int(price), int(mrp), ui, sub, image, maker, origin, fault,
        )
        if image != current_image:
            if current:
                groups.append(current)
            current = [row]
            current_image = image
        else:
            current.append(row)
    if current:
        groups.append(current)
    return groups


_GROUPS = _load_groups(_SPEC)


def declaration_gaps(product: dict[str, Any]) -> list[str]:
    """Required lines that are absent, plus an MRP conflict when the pack disagrees."""
    if product.get("regex_blind"):
        return []
    fields = product.get("fields") or {}
    gaps: list[str] = []
    if product.get("ocr_conflict_note"):
        gaps.append("conflict")
    for name in ("mrp", "net_quantity", "manufacturer", "country_of_origin"):
        if not fields.get(name):
            gaps.append(name)
    if not fields.get("manufacturing_date") and not fields.get("expiry_date"):
        gaps.append("dates")
    return gaps


def is_declaration_faulty(product: dict[str, Any]) -> bool:
    return bool(declaration_gaps(product))


def _omit_set(fault: str) -> set[str]:
    if fault == "sparse":
        return {"mrp", "manufacturer", "dates"}
    if fault in {"origin", "manufacturer", "mrp", "qty", "dates"}:
        return {fault}
    return set()


def _product(
    *,
    index: int,
    brand: str,
    brand_slug: str,
    product: str,
    product_slug: str,
    ui_category: str,
    sub: str,
    image: str,
    maker: str,
    origin: str,
    fault: str,
    size_slug: str,
    size_words: str,
    qty: str,
    price: int,
    mrp: int,
) -> dict[str, Any]:
    slug = f"{brand_slug}-{product_slug}-{size_slug}"
    month = f"{(index % 12) + 1:02d}"
    mfg = f"{month}/2025"
    exp = f"{month}/2027"
    omit = _omit_set(fault)
    name_line = f"Product Name: {brand} {product} {size_words}"
    mrp_line = f"MRP Rs. {mrp} (Incl. of all taxes)"
    qty_line = f"Net Quantity: {qty}"
    maker_line = f"Manufactured by: {maker}"
    origin_line = f"Country of Origin: {origin}"
    mfg_line = f"Mfg Date: {mfg}"
    exp_line = f"Best Before: {exp}"
    care_line = f"Customer Care: care@{brand_slug}.demo | 1800-210-{index:04d}"

    fields: dict[str, Any] = {
        "product_name": name_line,
        "mrp": None if "mrp" in omit else mrp_line,
        "net_quantity": None if "qty" in omit else qty_line,
        "manufacturer": None if "manufacturer" in omit else maker_line,
        "country_of_origin": None if "origin" in omit else origin_line,
        "manufacturing_date": None if "dates" in omit else mfg_line,
        "expiry_date": None if "dates" in omit else exp_line,
        "customer_care": care_line,
    }
    lines = [value for value in fields.values() if value]
    description = f"{brand} {product}, {size_words}. " + " ".join(lines)
    record: dict[str, Any] = {
        "asin": f"B0DM{index:06d}",
        "slug": slug,
        "title": f"{brand} {product}, {size_words}",
        "brand": brand,
        "category": f"{ui_category} › {sub}",
        "ui_category": ui_category,
        "sub_category": sub,
        "price": price,
        "mrp": None if "mrp" in omit else mrp,
        "mrp_display": None if "mrp" in omit else f"Rs. {mrp}",
        "discount_note": "Inclusive of all taxes",
        "rating": round(3.8 + (index % 9) * 0.1, 1),
        "reviews": 180 + (index * 37) % 4200,
        "bought": f"{80 + (index * 13) % 900}+ bought in past month",
        "in_stock": True,
        "images": [image],
        "bullets": [
            f"{size_words} retail pack",
            f"Sold as a DemoMart educational listing for {sub.lower()}",
            "Declarations below are what the checker reads",
        ],
        "fields": fields,
        "description": description,
        "scenario": "mrp_conflict" if fault == "conflict" else (fault or "complete"),
        "scenario_label": _FAULT_LABEL[fault],
    }
    if fault == "conflict":
        other = mrp + 40
        record["ocr_conflict_note"] = f"MRP Rs. {other} (Incl. of all taxes)"
    return record


def expanded_products() -> list[dict[str, Any]]:
    """List distinct products, rotating photos so copies are not side by side."""
    width = max(len(group) for group in _GROUPS)
    rows: list[tuple] = []
    for slot in range(width):
        for group in _GROUPS:
            if slot < len(group):
                rows.append(group[slot])
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows, start=1):
        (
            brand, brand_slug, product, product_slug, size_slug, size_words,
            qty, price, mrp, ui, sub, image, maker, origin, fault,
        ) = row
        record = _product(
            index=index,
            brand=brand,
            brand_slug=brand_slug,
            product=product,
            product_slug=product_slug,
            ui_category=ui,
            sub=sub,
            image=image,
            maker=maker,
            origin=origin,
            fault=fault,
            size_slug=size_slug,
            size_words=size_words,
            qty=qty,
            price=price,
            mrp=mrp,
        )
        if record["slug"] in seen or record["title"] in seen:
            raise RuntimeError(f"Duplicate DemoMart listing: {record['title']}")
        seen.add(record["slug"])
        seen.add(record["title"])
        out.append(record)
    return out
