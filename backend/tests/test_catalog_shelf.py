"""DemoMart shelf size, fault mix, and frontend lockstep."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from app.demo_store.catalog import PRODUCTS, get_product
from app.demo_store.expanded_catalog import is_declaration_faulty
from app.demo_store.regex_blind import REGEX_BLIND_SKUS
from app.field_extractor.models import FieldStatus
from app.services.rules import evaluate_rules


def test_shelf_has_at_least_112_and_mostly_faulty():
    products = list(PRODUCTS.values())
    assert len(products) >= 112
    faulty = [p for p in products if is_declaration_faulty(p)]
    assert len(faulty) / len(products) > 0.60
    titles = [p["title"].strip().lower() for p in products]
    assert len(titles) == len(set(titles))


def test_known_demo_slugs_stay():
    honey = get_product("hive-organic-honey-500g")
    assert honey and not is_declaration_faulty(honey)
    oil = get_product("pure-groundnut-oil-1l")
    assert oil and "origin" in (oil.get("scenario") or "")
    for sku in REGEX_BLIND_SKUS:
        assert sku in PRODUCTS
        assert not is_declaration_faulty(PRODUCTS[sku])


def test_new_faults_match_their_labels():
    missing_origin = get_product("soya-gold-soybean-oil-500ml")
    missing_mrp = get_product("crunchbite-marie-biscuits-200g")
    conflict = get_product("sunrise-tomato-ketchup-1kg")
    assert missing_origin["fields"]["country_of_origin"] is None
    assert missing_mrp["fields"]["mrp"] is None
    assert conflict.get("ocr_conflict_note")
    assert "MRP Rs." in conflict["fields"]["mrp"]


def test_every_image_exists_and_is_not_overused():
    image_dir = BACKEND / "app" / "demo_store" / "static" / "images"
    counts: Counter[str] = Counter()
    for product in PRODUCTS.values():
        names = list(dict.fromkeys(product.get("images") or []))
        assert names, product["slug"]
        for name in names:
            assert (image_dir / name).is_file(), name
            counts[name] += 1
    assert max(counts.values()) <= 3


def test_frontend_catalog_matches_backend_slugs():
    text = (ROOT / "frontend" / "src" / "data" / "demomartCatalog.js").read_text(encoding="utf-8")
    slugs = set(re.findall(r'"slug": "([^"]+)"', text))
    assert slugs == set(PRODUCTS)


@pytest.mark.parametrize(
    "slug, missing_field",
    [
        ("soya-gold-soybean-oil-500ml", "country_of_origin"),
        ("crunchbite-marie-biscuits-200g", "mrp"),
    ],
)
def test_faulty_pages_scan_as_potential_issues(slug, missing_field):
    from bs4 import BeautifulSoup

    from app.demo_store.render import render_product
    from app.field_extractor.merge import extract_with_mode

    product = get_product(slug)
    html = render_product(product, "http://127.0.0.1:5000")
    text = BeautifulSoup(html, "lxml").get_text(" ", strip=True)
    extraction = extract_with_mode(page_text=text, mode="regex")
    fields = [
        {
            "name": name,
            "status": field.status.value,
            "value": field.value,
            "confidence": field.confidence,
        }
        for name, field in extraction.fields.items()
    ]
    result = evaluate_rules(fields)
    assert extraction.fields[missing_field].status != FieldStatus.DETECTED
    assert result["overall_status"] == "potential_issues"


def test_mrp_conflict_page_needs_review():
    from app.demo_store.render import render_product
    from app.field_extractor.merge import extract_with_mode
    from app.services.scraper import parse_html_to_product

    product = get_product("sunrise-tomato-ketchup-1kg")
    html = render_product(product, "http://127.0.0.1:5000")
    parsed = parse_html_to_product(html, url="http://127.0.0.1:5000/demo/dp/sunrise-tomato-ketchup-1kg")
    extraction = extract_with_mode(
        page_text=parsed["page_text"],
        ocr_text=parsed["ocr_text"],
        mode="regex",
    )
    fields = [
        {
            "name": name,
            "status": field.status.value,
            "value": field.value,
            "confidence": field.confidence,
        }
        for name, field in extraction.fields.items()
    ]
    result = evaluate_rules(fields)
    assert extraction.fields["mrp"].status == FieldStatus.AMBIGUOUS
    assert result["overall_status"] == "needs_review"
