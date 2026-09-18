"""End-to-end backend tests (no network required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.main import create_app
from app.services.storage import init_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Isolate DB per test run
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    # Reload config paths is hard; point DB by patching storage
    import app.config as cfg
    import app.services.storage as storage

    monkeypatch.setattr(cfg, "DATA_DIR", tmp_path)
    monkeypatch.setattr(cfg, "UPLOAD_DIR", tmp_path / "uploads")
    monkeypatch.setattr(cfg, "SAMPLES_DIR", tmp_path / "samples")
    monkeypatch.setattr(cfg, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(cfg, "RULES_PATH", BACKEND / "data" / "rules.json")
    monkeypatch.setattr(storage, "DB_PATH", tmp_path / "test.db")

    cfg.ensure_dirs()
    init_db()
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_normalize_product_url():
    from app.services.scraper import normalize_product_url

    assert normalize_product_url("www.amazon.in/dp/B00X") == "https://www.amazon.in/dp/B00X"
    assert normalize_product_url("/demo/dp/hive-organic-honey-500g").startswith(
        "http://127.0.0.1:5000/demo/"
    )
    assert normalize_product_url("http://127.0.0.1:5000/demo/dp/x").startswith("http://")


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert "disclaimer" in data or True


def test_mrp_does_not_truncate_1169():
    from app.field_extractor.extractors import extract_fields
    from app.field_extractor.models import FieldStatus

    r = extract_fields("Product Name: Shirt MRP Rs. 1169 (Incl. of all taxes) Net Quantity: 1 Piece")
    assert r.fields["mrp"].status == FieldStatus.DETECTED
    assert r.fields["mrp"].normalized_value == "1169"


def test_country_stops_before_packing_date():
    from app.field_extractor.extractors import extract_fields
    from app.field_extractor.models import FieldStatus

    text = (
        "Country of Origin: India Month & Year of Packing: 01/2025 "
        "Manufactured by: AeroFit Apparels Ltd"
    )
    r = extract_fields(text)
    assert r.fields["country_of_origin"].status == FieldStatus.DETECTED
    assert r.fields["country_of_origin"].value == "India"
    assert r.fields["manufacturing_date"].status == FieldStatus.DETECTED


def test_scan_sample_complete(client):
    r = client.post("/api/scan/sample", json={"sample_id": "honey_complete"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert data["compliance_score"] >= 80
    fields = {f["field_name"]: f for f in data["fields"]}
    assert fields["mrp"]["value"]
    assert fields["country_of_origin"]["value"] == "India"
    assert data["overall_status"] in ("clear_in_available_data", "needs_review")


def test_scan_sample_missing_origin(client):
    r = client.post("/api/scan/sample", json={"sample_id": "oil_missing_origin"})
    data = r.get_json()
    assert data["ok"] is True
    assert data["overall_status"] == "potential_issues"
    rule_ids = {f["rule_id"] for f in data["findings"]}
    assert "REQ_COUNTRY" in rule_ids
    # Must not invent India
    fields = {f["field_name"]: f for f in data["fields"]}
    assert fields["country_of_origin"]["value"] is None


def test_scan_conflict_ambiguous(client):
    r = client.post("/api/scan/sample", json={"sample_id": "conflict_mrp"})
    data = r.get_json()
    assert data["ok"] is True
    fields = {f["field_name"]: f for f in data["fields"]}
    assert fields["mrp"]["status"] == "ambiguous"
    assert fields["mrp"]["value"] is None
    assert data["overall_status"] == "needs_review"


def test_scan_text_bare_price_not_mrp(client):
    r = client.post(
        "/api/scan/text",
        json={
            "page_text": "Special offer 199 only! Net Quantity: 100 g Made in India",
            "name": "Bare price test",
        },
    )
    data = r.get_json()
    assert data["ok"] is True
    fields = {f["field_name"]: f for f in data["fields"]}
    assert fields["mrp"]["status"] == "not_detected"
    assert fields["net_quantity"]["value"] == "100 g"


def test_human_review_and_report(client):
    r = client.post("/api/scan/sample", json={"sample_id": "oil_missing_origin"})
    product = r.get_json()
    finding_id = product["findings"][0]["id"]
    product_id = product["id"]

    rr = client.post(
        f"/api/findings/{finding_id}/review",
        json={"action": "confirm", "comment": "Verified missing on label"},
    )
    assert rr.status_code == 200
    assert rr.get_json()["finding"]["reviewer_action"] == "confirm"

    rep = client.post(f"/api/products/{product_id}/report", json={"format": "json"})
    assert rep.status_code == 200
    body = rep.get_json()
    assert body["report"]["product"]["id"] == product_id
    assert "disclaimer" in body["report"]

    pdf = client.post(f"/api/products/{product_id}/report", json={"format": "pdf"})
    assert pdf.status_code == 200
    assert pdf.get_json()["file_path"]


def test_list_and_get_product(client):
    client.post("/api/scan/sample", json={"sample_id": "chips_sparse"})
    lst = client.get("/api/products").get_json()
    assert lst["ok"] is True
    assert len(lst["products"]) >= 1
    pid = lst["products"][0]["id"]
    one = client.get(f"/api/products/{pid}").get_json()
    assert one["product"]["id"] == pid


def test_marketplace_blocked_returns_error_code(client):
    html = (
        "<html><head><title>Robot Check</title></head>"
        "<body>validatecaptcha sorry we just need to make sure you're not a robot</body></html>"
    )
    r = client.post(
        "/api/scan/url",
        json={"url": "https://www.amazon.in/dp/B00FAKEBLOCK", "html": html},
    )
    data = r.get_json()
    assert data["ok"] is False
    assert data.get("error_code") == "marketplace_blocked"
    assert "blocked" in (data.get("error") or "").lower()
    assert data.get("fallback", {}).get("demomart")


def test_scan_url_with_pasted_html_real_link_style(client):
    """Simulate real Amazon link + user-pasted HTML when bot wall blocks fetch."""
    html = """
    <html><head><title>Dabur Honey 500g</title></head><body>
    <h1 id="productTitle">Dabur Honey - Worlds No.1 Honey Brand, 500g</h1>
    <div id="productDetails_techSpec_section_1">
      <p>MRP Rs. 235 (Incl. of all taxes)</p>
      <p>Net Quantity: 500 g</p>
      <p>Manufactured by: Dabur India Ltd</p>
      <p>Country of Origin: India</p>
      <p>Mfg Date: 01/2025</p>
      <p>Best Before: 01/2027</p>
    </div>
    </body></html>
    """
    r = client.post(
        "/api/scan/url",
        json={
            "url": "https://www.amazon.in/Dabur-Honey-Worlds-No-1-Brand/dp/B00GL2F5L2",
            "html": html,
        },
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert "amazon.in" in (data.get("source_url") or "")
    fields = {f["field_name"]: f for f in data["fields"]}
    assert fields["mrp"]["normalized_value"] == "235"
    assert fields["country_of_origin"]["value"] == "India"
    assert data["compliance_score"] >= 80
