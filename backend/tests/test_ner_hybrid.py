"""NER / hybrid merge tests — must pass without a trained model or torch."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.demo_store.regex_blind import REGEX_BLIND_DOCS, REGEX_BLIND_SKUS
from app.field_extractor.extractors import extract_fields
from app.field_extractor.merge import extract_with_mode, merge_regex_ner
from app.field_extractor.models import (
    Evidence,
    ExtractedField,
    ExtractionResult,
    FieldStatus,
    SourceType,
    empty_field,
)
from app.field_extractor.patterns import FIELD_ORDER
from app.main import create_app
from app.ml.make_dataset import split_docs
from app.services.storage import init_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    import app.config as cfg
    import app.services.storage as storage

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
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


def _empty_result(source: SourceType = SourceType.PAGE) -> ExtractionResult:
    return ExtractionResult(
        fields={name: empty_field(name, "none") for name in FIELD_ORDER},
        raw_text="",
        source=source,
    )


def _hit(
    name: str,
    value: str,
    source: SourceType,
    confidence: float = 0.93,
) -> ExtractedField:
    return ExtractedField(
        name=name,
        value=value,
        normalized_value=value,
        status=FieldStatus.DETECTED,
        confidence=confidence,
        evidence=Evidence(
            source=source,
            matched_text=value,
            start=0,
            end=len(value),
            pattern_id="test",
        ),
    )


def _with_field(base: ExtractionResult, field: ExtractedField) -> ExtractionResult:
    fields = dict(base.fields)
    fields[field.name] = field
    return ExtractionResult(
        fields=fields, raw_text=base.raw_text, source=base.source
    )


def test_regex_misses_four_paraphrased_texts():
    """DemoMart regex-blind SKUs must stay invisible to the regex extractor."""
    assert len(REGEX_BLIND_DOCS) >= 4
    assert set(REGEX_BLIND_SKUS) == {d["id"] for d in REGEX_BLIND_DOCS}
    for doc in REGEX_BLIND_DOCS:
        result = extract_fields(doc["text"], source=SourceType.PAGE)
        detected = [
            name
            for name in FIELD_ORDER
            if result.fields[name].status == FieldStatus.DETECTED
            and result.fields[name].value
        ]
        assert detected == [], (
            f"{doc['id']} leaked to regex: {detected} "
            f"values={[result.fields[n].value for n in detected]}"
        )
        for name in FIELD_ORDER:
            assert result.fields[name].value is None
            assert result.fields[name].status == FieldStatus.NOT_DETECTED


def test_hybrid_merge_regex_miss_ner_hit():
    regex = _empty_result(SourceType.PAGE)
    ner = _with_field(
        _empty_result(SourceType.NER),
        _hit("manufacturer", "Golden Mills Co-op Society Ltd", SourceType.NER, 0.91),
    )
    merged = merge_regex_ner(regex, ner)
    f = merged.fields["manufacturer"]
    assert f.status == FieldStatus.DETECTED
    assert f.value == "Golden Mills Co-op Society Ltd"
    assert f.evidence and f.evidence.source == SourceType.NER
    assert f.confidence <= 0.78
    assert f.reason and "Regex miss" in f.reason
    assert merged.fields["mrp"].status == FieldStatus.NOT_DETECTED
    assert merged.fields["mrp"].value is None


def test_hybrid_merge_agreement_boosts_confidence():
    regex = _with_field(
        _empty_result(SourceType.PAGE),
        _hit("country_of_origin", "India", SourceType.PAGE, 0.95),
    )
    ner = _with_field(
        _empty_result(SourceType.NER),
        _hit("country_of_origin", "India", SourceType.NER, 0.88),
    )
    merged = merge_regex_ner(regex, ner)
    f = merged.fields["country_of_origin"]
    assert f.status == FieldStatus.DETECTED
    assert f.value == "India"
    assert f.confidence >= 0.95
    assert f.evidence and f.evidence.source == SourceType.MERGED


def test_hybrid_merge_conflict_is_ambiguous():
    regex = _with_field(
        _empty_result(SourceType.PAGE),
        _hit("mrp", "Rs. 100", SourceType.PAGE, 0.96),
    )
    regex.fields["mrp"].normalized_value = "100"
    ner = _with_field(
        _empty_result(SourceType.NER),
        _hit("mrp", "Rs. 120", SourceType.NER, 0.90),
    )
    ner.fields["mrp"].normalized_value = "120"
    merged = merge_regex_ner(regex, ner)
    f = merged.fields["mrp"]
    assert f.status == FieldStatus.AMBIGUOUS
    assert f.value is None
    assert "100" in f.alternatives and "120" in f.alternatives


def test_hybrid_merge_preserves_regex_ambiguous():
    regex = _empty_result(SourceType.PAGE)
    regex.fields["mrp"] = ExtractedField(
        name="mrp",
        value=None,
        status=FieldStatus.AMBIGUOUS,
        confidence=0.9,
        alternatives=["100", "120"],
        reason="page/ocr conflict",
    )
    ner = _with_field(
        _empty_result(SourceType.NER),
        _hit("mrp", "Rs. 100", SourceType.NER, 0.99),
    )
    merged = merge_regex_ner(regex, ner)
    assert merged.fields["mrp"].status == FieldStatus.AMBIGUOUS
    assert merged.fields["mrp"].value is None


def test_hybrid_merge_both_miss():
    merged = merge_regex_ner(
        _empty_result(SourceType.PAGE), _empty_result(SourceType.NER)
    )
    for name in FIELD_ORDER:
        assert merged.fields[name].status == FieldStatus.NOT_DETECTED
        assert merged.fields[name].value is None


def test_extract_with_mode_hybrid_mocked_fills_regex_blind(monkeypatch):
    doc = REGEX_BLIND_DOCS[0]
    values = doc["values"]

    def fake_available() -> bool:
        return True

    def fake_ner(text: str, fields=None):
        target = fields or FIELD_ORDER
        out = {n: empty_field(n, "none") for n in target}
        for name, val in values.items():
            if name in out:
                out[name] = _hit(name, val, SourceType.NER, 0.92)
                if name == "mrp":
                    out[name].normalized_value = "275"
                    out[name].value = "Rs. 275"
        return ExtractionResult(
            fields=out, raw_text=text, source=SourceType.NER
        )

    monkeypatch.setattr(
        "app.field_extractor.ner_extractor.ner_available", fake_available
    )
    monkeypatch.setattr(
        "app.field_extractor.ner_extractor.extract_fields_ner", fake_ner
    )

    regex_only = extract_with_mode(page_text=doc["text"], mode="regex")
    assert regex_only.fields["manufacturer"].status == FieldStatus.NOT_DETECTED

    hybrid = extract_with_mode(page_text=doc["text"], mode="hybrid")
    assert hybrid.fields["manufacturer"].status == FieldStatus.DETECTED
    assert "Golden Mills" in (hybrid.fields["manufacturer"].value or "")
    assert hybrid.fields["manufacturer"].evidence.source == SourceType.NER


def test_demo_catalog_lists_regex_blind(client):
    r = client.get("/api/demo/catalog")
    assert r.status_code == 200
    data = r.get_json()
    products = data["products"]
    slugs = {p["slug"] for p in products}
    for sku in REGEX_BLIND_SKUS:
        assert sku in slugs
    blind = [p for p in products if p.get("regex_blind")]
    assert len(blind) == len(REGEX_BLIND_SKUS)
    honey = next(p for p in products if p["slug"] == "hive-organic-honey-500g")
    assert honey["regex_blind"] is False


def test_health_exposes_ner_keys(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.get_json()
    assert "ner_available" in data
    assert data["ner_available"] in (True, False)
    assert "extractor_mode" in data
    assert data["extractor_mode"] in {"regex", "ner", "hybrid"}


def test_split_keeps_regex_blind_in_test():
    docs = [{"id": f"x{i}", "text": "t", "ents": []} for i in range(40)]
    docs += [{"id": f"regex_blind:{s}", "text": "t", "ents": []} for s in REGEX_BLIND_SKUS]
    train, val, test = split_docs(docs, seed=42)
    test_ids = {d["id"] for d in test}
    for sku in REGEX_BLIND_SKUS:
        assert any(sku in i for i in test_ids)
    train_ids = {d["id"] for d in train}
    val_ids = {d["id"] for d in val}
    for sku in REGEX_BLIND_SKUS:
        assert not any(sku in i for i in train_ids)
        assert not any(sku in i for i in val_ids)


def test_scan_honey_complete_still_high_without_model(client):
    r = client.post("/api/scan/sample", json={"sample_id": "honey_complete"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["ok"] is True
    assert data["compliance_score"] >= 80
    fields = {f["field_name"]: f for f in data["fields"]}
    assert fields["mrp"]["value"]
    assert fields["country_of_origin"]["value"] == "India"
