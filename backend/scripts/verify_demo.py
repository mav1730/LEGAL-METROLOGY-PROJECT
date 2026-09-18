"""End-to-end demo check. Run with the D: venv so NER loads.

    D:\\legal-metrology\\venv\\Scripts\\python.exe backend/scripts/verify_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.demo_store.regex_blind import REGEX_BLIND_DOCS
from app.field_extractor.extractors import extract_fields
from app.field_extractor.merge import extract_with_mode
from app.field_extractor.models import FieldStatus
from app.field_extractor.patterns import FIELD_ORDER
from app.main import create_app


def _detected(result) -> dict[str, str]:
    out = {}
    for name in FIELD_ORDER:
        f = result.fields[name]
        if f.status == FieldStatus.DETECTED and f.value:
            src = f.evidence.source.value if f.evidence else "?"
            out[name] = f"{f.value} [{src}]"
    return out


def main() -> int:
    print("== regex must miss every paraphrased DemoMart page ==")
    leaks = 0
    for doc in REGEX_BLIND_DOCS:
        rx = extract_fields(doc["text"])
        hit = _detected(rx)
        if hit:
            leaks += 1
            print(" LEAK", doc["id"], hit)
        else:
            print(" ok  ", doc["id"])
    if leaks:
        print("FAIL: regex saw paraphrased labels")
        return 1

    print("\n== hybrid NER should fill atta (needs torch + weights) ==")
    atta = next(d for d in REGEX_BLIND_DOCS if d["id"] == "golden-grain-atta-5kg")
    hybrid = extract_with_mode(page_text=atta["text"], mode="hybrid")
    filled = _detected(hybrid)
    print(" hybrid atta:", filled or "(empty — NER off?)")
    if "manufacturer" not in filled:
        print("WARN: manufacturer still empty — start D: venv with EXTRACTOR_MODE=hybrid")

    print("\n== Flask health + sample scans ==")
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        h = c.get("/api/health").get_json()
        print(" health", {k: h.get(k) for k in ("ok", "ner_available", "extractor_mode")})
        cat = c.get("/api/demo/catalog").get_json()["products"]
        print(" catalog", len(cat), "products,", sum(1 for p in cat if p["regex_blind"]), "regex-blind")
        honey = c.post("/api/scan/sample", json={"sample_id": "honey_complete"}).get_json()
        print(" honey score", honey.get("compliance_score"), "ok", honey.get("ok"))
        atta_s = c.post("/api/scan/sample", json={"sample_id": "golden-grain-atta-5kg"}).get_json()
        fields = {f["field_name"]: f for f in atta_s.get("fields") or []}
        mfg = fields.get("manufacturer") or {}
        print(
            " atta manufacturer",
            mfg.get("status"),
            mfg.get("value"),
            mfg.get("source"),
            "score",
            atta_s.get("compliance_score"),
        )
        if honey.get("compliance_score", 0) < 80:
            print("FAIL: honey score dropped")
            return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
