"""Build NER JSONL splits from gold + DemoMart samples + template paraphrases.

Usage (from backend/):
    python -m app.ml.make_dataset

Writes:
    backend/data/ner_gold/regex_blind.jsonl
    backend/data/ner_gold/train.jsonl
    backend/data/ner_gold/val.jsonl
    backend/data/ner_gold/test.jsonl

Split is by DOCUMENT (70/15/15), never by token.
All regex-blind SKUs are forced into TEST.
Does not scrape Amazon. Does not invent legal conclusions.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

BACKEND = Path(__file__).resolve().parents[2]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.demo_store.regex_blind import (  # noqa: E402
    REGEX_BLIND_DOCS,
    REGEX_BLIND_SKUS,
    gold_records,
)
from app.ml.labels import ENTITY_LABELS  # noqa: E402
from app.services.samples import SAMPLES  # noqa: E402

GOLD_DIR = BACKEND / "data" / "ner_gold"
DEFAULT_SEED = 42
DEFAULT_SYNTH = 480

# Fixed paraphrase templates — these MUST stay off normalize.py aliases.
PRODUCT_NAME_TEMPLATES = (
    "Article: {product_name}",
    "Name of the food article {product_name}",
)
MRP_TEMPLATES = (
    "Pack price Rs. {mrp}",
    "Stated consumer price Rs. {mrp}",
    "Pack price {mrp}",
    "Stated consumer price {mrp}",
)
QTY_TEMPLATES = (
    "Jar holds {net_quantity}",
    "Fill weight {net_quantity}",
    "Weight of commodity {net_quantity}",
)
MFG_TEMPLATES = (
    "Imported by {manufacturer}",
    "Packer: {manufacturer}",
    "Plant operator {manufacturer}",
)
ORIGIN_TEMPLATES = (
    "Harvested in {country_of_origin}",
    "Sourced from {country_of_origin}",
    "COO {country_of_origin}",
)
MFG_DATE_TEMPLATES = (
    "DOM {manufacturing_date}",
    "Lot dated {manufacturing_date}",
)
EXP_TEMPLATES = (
    "Consume before {expiry_date}",
    "Discard after {expiry_date}",
    "Shelf life ends {expiry_date}",
    "DOE {expiry_date}",
)

# Canonical templates so NER also sees regex-visible wording (train/val only).
CANONICAL_TEMPLATES = {
    "product_name": ("Product Name: {product_name}",),
    "mrp": ("MRP Rs. {mrp}", "MRP: {mrp}"),
    "net_quantity": ("Net Quantity: {net_quantity}",),
    "manufacturer": ("Manufactured by: {manufacturer}", "Manufacturer: {manufacturer}"),
    "country_of_origin": ("Country of Origin: {country_of_origin}", "Made in {country_of_origin}"),
    "manufacturing_date": ("Mfg Date: {manufacturing_date}",),
    "expiry_date": ("Best Before: {expiry_date}", "Exp Date: {expiry_date}"),
}

PARA_TEMPLATES = {
    "product_name": PRODUCT_NAME_TEMPLATES,
    "mrp": MRP_TEMPLATES,
    "net_quantity": QTY_TEMPLATES,
    "manufacturer": MFG_TEMPLATES,
    "country_of_origin": ORIGIN_TEMPLATES,
    "manufacturing_date": MFG_DATE_TEMPLATES,
    "expiry_date": EXP_TEMPLATES,
}

FILLERS = (
    "Keep in a cool dry place.",
    "For household consumption.",
    "Batch as marked on pack.",
    "This is a DemoMart educational listing.",
    "Packed for retail sale in India.",
)

# Synthetic product records (field VALUES only — not legal verdicts).
SEED_PRODUCTS: list[dict[str, str]] = [
    {
        "product_name": "Himalayan Multi Flora Honey",
        "mrp": "349",
        "net_quantity": "500 g",
        "manufacturer": "Himalayan Bee Farms Pvt Ltd",
        "country_of_origin": "India",
        "manufacturing_date": "03/2024",
        "expiry_date": "03/2026",
    },
    {
        "product_name": "Pure Groundnut Oil",
        "mrp": "150",
        "net_quantity": "1 L",
        "manufacturer": "Pure Oil Mills",
        "country_of_origin": "India",
        "manufacturing_date": "01/2025",
        "expiry_date": "01/2026",
    },
    {
        "product_name": "Classic Assam Tea Bags",
        "mrp": "100",
        "net_quantity": "100 g",
        "manufacturer": "Assam Tea Co",
        "country_of_origin": "India",
        "manufacturing_date": "01/2025",
        "expiry_date": "01/2027",
    },
    {
        "product_name": "Golden Grain Chakki Atta",
        "mrp": "275",
        "net_quantity": "5 kg",
        "manufacturer": "Golden Mills Co-op Society Ltd",
        "country_of_origin": "India",
        "manufacturing_date": "04/2025",
        "expiry_date": "04/2026",
    },
    {
        "product_name": "Mediterra Extra Virgin Olive Oil",
        "mrp": "649",
        "net_quantity": "500 ml",
        "manufacturer": "Mediterra Imports Pvt Ltd",
        "country_of_origin": "Italy",
        "manufacturing_date": "11/2024",
        "expiry_date": "11/2026",
    },
    {
        "product_name": "Vaidya Triphala Churna",
        "mrp": "180",
        "net_quantity": "100 g",
        "manufacturer": "Vaidya Ayurvedic Works",
        "country_of_origin": "India",
        "manufacturing_date": "02/2025",
        "expiry_date": "02/2028",
    },
    {
        "product_name": "FoamChem Active Wash",
        "mrp": "220",
        "net_quantity": "1 kg",
        "manufacturer": "FoamChem Industries",
        "country_of_origin": "India",
        "manufacturing_date": "08/2024",
        "expiry_date": "08/2027",
    },
    {
        "product_name": "Coastal Rock Salt",
        "mrp": "45",
        "net_quantity": "1 kg",
        "manufacturer": "Konkan Salt Works",
        "country_of_origin": "India",
        "manufacturing_date": "06/2025",
        "expiry_date": "06/2028",
    },
    {
        "product_name": "Nile Red Lentils",
        "mrp": "132",
        "net_quantity": "1 kg",
        "manufacturer": "Deccan Pulses Ltd",
        "country_of_origin": "India",
        "manufacturing_date": "09/2024",
        "expiry_date": "09/2026",
    },
    {
        "product_name": "Sakura Soy Sauce",
        "mrp": "210",
        "net_quantity": "250 ml",
        "manufacturer": "Sakura Foods KK",
        "country_of_origin": "Japan",
        "manufacturing_date": "05/2025",
        "expiry_date": "05/2027",
    },
    {
        "product_name": "Andes Dark Cocoa Powder",
        "mrp": "399",
        "net_quantity": "200 g",
        "manufacturer": "Andes Cocoa SA",
        "country_of_origin": "Brazil",
        "manufacturing_date": "12/2024",
        "expiry_date": "12/2026",
    },
    {
        "product_name": "Alpine Milk Chocolate",
        "mrp": "120",
        "net_quantity": "80 g",
        "manufacturer": "Alpine Confectioners AG",
        "country_of_origin": "Switzerland",
        "manufacturing_date": "03/2025",
        "expiry_date": "03/2026",
    },
    {
        "product_name": "Malabar Black Pepper",
        "mrp": "95",
        "net_quantity": "100 g",
        "manufacturer": "Malabar Spice House",
        "country_of_origin": "India",
        "manufacturing_date": "07/2024",
        "expiry_date": "07/2027",
    },
    {
        "product_name": "Saigon Cinnamon Sticks",
        "mrp": "160",
        "net_quantity": "50 g",
        "manufacturer": "Mekong Spice Export",
        "country_of_origin": "Vietnam",
        "manufacturing_date": "10/2024",
        "expiry_date": "10/2027",
    },
    {
        "product_name": "Nile Valley Dates",
        "mrp": "280",
        "net_quantity": "400 g",
        "manufacturer": "Valley Date Packers",
        "country_of_origin": "Egypt",
        "manufacturing_date": "01/2025",
        "expiry_date": "01/2026",
    },
    {
        "product_name": "Patagonia Quinoa Grain",
        "mrp": "310",
        "net_quantity": "500 g",
        "manufacturer": "Andes Grain Co",
        "country_of_origin": "Argentina",
        "manufacturing_date": "04/2024",
        "expiry_date": "04/2026",
    },
    {
        "product_name": "Seoul Kimchi Paste",
        "mrp": "175",
        "net_quantity": "200 g",
        "manufacturer": "Han Foods Ltd",
        "country_of_origin": "South Korea",
        "manufacturing_date": "02/2025",
        "expiry_date": "08/2025",
    },
    {
        "product_name": "Tuscany Tomato Passata",
        "mrp": "145",
        "net_quantity": "700 ml",
        "manufacturer": "Tuscan Pantry SRL",
        "country_of_origin": "Italy",
        "manufacturing_date": "08/2025",
        "expiry_date": "08/2027",
    },
    {
        "product_name": "Bengal Mustard Oil",
        "mrp": "198",
        "net_quantity": "1 L",
        "manufacturer": "Hooghly Oil Mills",
        "country_of_origin": "India",
        "manufacturing_date": "05/2025",
        "expiry_date": "05/2026",
    },
    {
        "product_name": "Kerala Coconut Oil",
        "mrp": "240",
        "net_quantity": "500 ml",
        "manufacturer": "Malabar Copra Board",
        "country_of_origin": "India",
        "manufacturing_date": "09/2025",
        "expiry_date": "09/2026",
    },
    {
        "product_name": "Punjab Desi Ghee",
        "mrp": "560",
        "net_quantity": "1 L",
        "manufacturer": "Doaba Dairy Co-op",
        "country_of_origin": "India",
        "manufacturing_date": "06/2025",
        "expiry_date": "06/2026",
    },
    {
        "product_name": "Darjeeling Leaf Tea",
        "mrp": "420",
        "net_quantity": "250 g",
        "manufacturer": "Hillside Tea Estate",
        "country_of_origin": "India",
        "manufacturing_date": "03/2025",
        "expiry_date": "03/2027",
    },
    {
        "product_name": "Rajasthan Gram Flour",
        "mrp": "88",
        "net_quantity": "1 kg",
        "manufacturer": "Marwar Mills Ltd",
        "country_of_origin": "India",
        "manufacturing_date": "11/2025",
        "expiry_date": "11/2026",
    },
    {
        "product_name": "Goa Cane Jaggery",
        "mrp": "72",
        "net_quantity": "500 g",
        "manufacturer": "Konkan Agro Packers",
        "country_of_origin": "India",
        "manufacturing_date": "12/2024",
        "expiry_date": "12/2025",
    },
]


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1
    return n


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _find_span(text: str, value: str, occupied: list[tuple[int, int]]) -> Optional[tuple[int, int]]:
    start = 0
    while True:
        idx = text.find(value, start)
        if idx < 0:
            return None
        end = idx + len(value)
        if not any(not (end <= a or idx >= b) for a, b in occupied):
            return idx, end
        start = idx + 1


def _ents_from_values(text: str, values: dict[str, str]) -> list[dict[str, Any]]:
    occupied: list[tuple[int, int]] = []
    ents: list[dict[str, Any]] = []
    # Longer values first so "South Korea" wins over accidental shorts
    items = sorted(values.items(), key=lambda kv: len(kv[1] or ""), reverse=True)
    for label, value in items:
        if not value or label not in ENTITY_LABELS:
            continue
        span = _find_span(text, value, occupied)
        if span is None:
            continue
        occupied.append(span)
        ents.append(
            {
                "start": span[0],
                "end": span[1],
                "label": label,
                "text": text[span[0] : span[1]],
            }
        )
    ents.sort(key=lambda e: e["start"])
    return ents


def _render_line(template: str, values: dict[str, str]) -> tuple[str, Optional[str], str]:
    """Return (rendered_line, entity_label or None, entity_substring)."""
    label = None
    for key in ENTITY_LABELS:
        token = "{" + key + "}"
        if token in template:
            label = key
            break
    rendered = template.format(**values)
    entity_text = values[label] if label else ""
    return rendered, label, entity_text


def render_document(
    doc_id: str,
    values: dict[str, str],
    rng: random.Random,
    paraphrased: bool = True,
    drop_fields: Optional[set[str]] = None,
    extra_filler: bool = True,
) -> dict[str, Any]:
    drop_fields = drop_fields or set()
    present = {
        k: v
        for k, v in values.items()
        if k in ENTITY_LABELS and v and k not in drop_fields
    }
    lines: list[str] = []
    if extra_filler and rng.random() < 0.7:
        lines.append(rng.choice(FILLERS))

    order = list(present.keys())
    rng.shuffle(order)
    for field in order:
        bank = PARA_TEMPLATES[field] if paraphrased else CANONICAL_TEMPLATES[field]
        tmpl = rng.choice(bank)
        line, _, _ = _render_line(tmpl, present)
        lines.append(line)

    if extra_filler and rng.random() < 0.4:
        lines.append(rng.choice(FILLERS))

    joiner = rng.choice((". ", " | ", "\n", ". "))
    text = joiner.join(lines).strip()
    # For mrp templates that already include "Rs. ", the value substring is still "349"
    ents = _ents_from_values(text, present)
    return {"id": doc_id, "text": text, "ents": ents}


def records_from_samples() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    # honey_complete — all 7 fields, canonical labels
    honey = SAMPLES["honey_complete"]["page_text"]
    honey_vals = {
        "product_name": "Organic Himalayan Honey 500g",
        "mrp": "349",
        "net_quantity": "500 g",
        "manufacturer": "Himalayan Bee Farms Pvt Ltd",
        "country_of_origin": "India",
        "manufacturing_date": "03/2024",
        "expiry_date": "03/2026",
    }
    out.append(
        {
            "id": "sample:honey_complete",
            "text": honey,
            "ents": _ents_from_values(honey, honey_vals),
        }
    )
    oil = SAMPLES["oil_missing_origin"]["page_text"]
    oil_vals = {
        "product_name": "Pure Groundnut Oil",
        "mrp": "150",
        "net_quantity": "1 L",
        "manufacturer": "Pure Oil Mills",
        "manufacturing_date": "Jan 2025",
        # expiry is a relative phrase in the sample; label the date-like tail only
        # if present as a clean span. Skip relative "12 months from manufacture"
        # as expiry_date gold — NER is trained on dated spans.
    }
    out.append(
        {
            "id": "sample:oil_missing_origin",
            "text": oil,
            "ents": _ents_from_values(oil, oil_vals),
        }
    )
    chips = SAMPLES["chips_sparse"]["page_text"]
    out.append({"id": "sample:chips_sparse", "text": chips, "ents": []})
    tea_page = SAMPLES["conflict_mrp"]["page_text"]
    tea_vals = {
        "product_name": "Classic Tea Bags",
        "mrp": "100",
        "net_quantity": "100 g",
        "manufacturer": "Assam Tea Co",
        "country_of_origin": "India",
    }
    out.append(
        {
            "id": "sample:conflict_mrp_page",
            "text": tea_page,
            "ents": _ents_from_values(tea_page, tea_vals),
        }
    )
    return out


def synthesize(n: int, rng: random.Random) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for i in range(n):
        prod = rng.choice(SEED_PRODUCTS)
        paraphrased = rng.random() < 0.82
        drop: set[str] = set()
        if rng.random() < 0.12:
            drop.add(rng.choice(["expiry_date", "manufacturing_date", "country_of_origin"]))
        docs.append(
            render_document(
                doc_id=f"synth:{i:04d}",
                values=prod,
                rng=rng,
                paraphrased=paraphrased,
                drop_fields=drop,
            )
        )
    # A handful of long docs so stride-64 training is exercised
    for j in range(6):
        prod = rng.choice(SEED_PRODUCTS)
        base = render_document(
            doc_id=f"synth_long:{j:02d}",
            values=prod,
            rng=rng,
            paraphrased=True,
        )
        pad = " ".join(rng.choice(FILLERS) for _ in range(80))
        base["text"] = pad + " " + base["text"] + " " + pad
        # Recompute ents after padding
        shift = len(pad) + 1
        new_ents = []
        for ent in base["ents"]:
            new_ents.append(
                {
                    "start": ent["start"] + shift,
                    "end": ent["end"] + shift,
                    "label": ent["label"],
                    "text": ent["text"],
                }
            )
        base["ents"] = new_ents
        docs.append(base)
    return docs


def is_regex_blind_id(doc_id: str) -> bool:
    return any(sku in doc_id for sku in REGEX_BLIND_SKUS)


def split_docs(
    docs: list[dict[str, Any]],
    seed: int = DEFAULT_SEED,
    ratios: tuple[float, float, float] = (0.70, 0.15, 0.15),
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Document-level split. Regex-blind SKUs always land in TEST."""
    blind, rest = [], []
    for d in docs:
        (blind if is_regex_blind_id(d.get("id", "")) else rest).append(d)
    rng = random.Random(seed)
    rng.shuffle(rest)
    n = len(rest)
    n_train = int(n * ratios[0])
    n_val = int(n * ratios[1])
    train = rest[:n_train]
    val = rest[n_train : n_train + n_val]
    test = rest[n_train + n_val :] + blind
    return train, val, test


def build_dataset(
    gold_dir: Path = GOLD_DIR,
    n_synth: int = DEFAULT_SYNTH,
    seed: int = DEFAULT_SEED,
) -> dict[str, int]:
    gold_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    blind = gold_records()
    existing_seed = load_jsonl(gold_dir / "regex_blind.jsonl")
    # Prefer freshly computed gold (offsets stay in sync with source texts)
    seed_docs = blind or existing_seed
    _write_jsonl(gold_dir / "regex_blind.jsonl", seed_docs)

    samples = records_from_samples()
    synth = synthesize(n_synth, rng)

    # Deduplicate by id
    by_id: dict[str, dict[str, Any]] = {}
    for row in [*seed_docs, *samples, *synth]:
        by_id[row["id"]] = row
    docs = list(by_id.values())

    train, val, test = split_docs(docs, seed=seed)
    counts = {
        "gold_blind": _write_jsonl(gold_dir / "regex_blind.jsonl", seed_docs),
        "train": _write_jsonl(gold_dir / "train.jsonl", train),
        "val": _write_jsonl(gold_dir / "val.jsonl", val),
        "test": _write_jsonl(gold_dir / "test.jsonl", test),
        "total": len(docs),
        "synth": len(synth),
    }
    return counts


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build NER JSONL dataset")
    parser.add_argument("--out-dir", type=Path, default=GOLD_DIR)
    parser.add_argument("--n-synth", type=int, default=DEFAULT_SYNTH)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args(argv)

    n_synth = max(300, min(600, args.n_synth))
    counts = build_dataset(gold_dir=args.out_dir, n_synth=n_synth, seed=args.seed)
    print("Wrote NER gold splits:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"  dir: {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
