"""REST API for the compliance checker."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, jsonify, request, send_file

from app.config import EXTRACTOR_MODE, SYSTEM_DISCLAIMER
from app.demo_store.catalog import public_catalog
from app.services import samples as sample_store
from app.field_extractor.ner_extractor import ner_available
from app.services.ocr_service import tesseract_available
from app.services.pipeline import scan_image, scan_raw_text, scan_sample, scan_url
from app.services.reports import generate_json_report, generate_pdf_report
from app.services.rules import load_rules
from app.services.scraper import playwright_available
from app.services.storage import (
    dashboard_stats,
    get_product,
    get_report,
    list_products,
    update_finding_review,
    update_product_review,
)

api_bp = Blueprint("api", __name__)


def _ok(data, status=200):
    if isinstance(data, dict):
        data.setdefault("disclaimer", SYSTEM_DISCLAIMER)
    return jsonify(data), status


def _err(message: str, status: int = 400, **extra):
    payload = {"ok": False, "error": message, "disclaimer": SYSTEM_DISCLAIMER}
    payload.update(extra)
    return jsonify(payload), status


@api_bp.get("/health")
def health():
    return _ok(
        {
            "ok": True,
            "service": "legal-metrology-compliance-checker",
            "ocr_tesseract_available": tesseract_available(),
            "playwright_available": playwright_available(),
            "ner_available": ner_available(),
            "extractor_mode": EXTRACTOR_MODE,
            "demomart": "http://127.0.0.1:5000/demo/",
            "version": "1.0.0",
        }
    )


@api_bp.get("/stats")
def stats():
    return _ok({"ok": True, "stats": dashboard_stats()})


@api_bp.get("/rules")
def rules():
    return _ok({"ok": True, "rules": load_rules()})


@api_bp.get("/samples")
def samples_list():
    return _ok({"ok": True, "samples": sample_store.list_samples()})


@api_bp.get("/demo/catalog")
def demo_catalog():
    """DemoMart product URLs + regex-blind flags for the dashboard."""
    return _ok({"ok": True, "products": public_catalog()})


@api_bp.post("/scan/url")
def api_scan_url():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    html = (data.get("html") or data.get("page_html") or "").strip()
    use_browser = data.get("use_browser", True)
    if not url and not html:
        return _err("url or html is required")
    result = scan_url(url, html=html, use_browser=bool(use_browser))
    status = 200 if result.get("ok") else 422
    return _ok(result, status)


@api_bp.post("/scan/image")
def api_scan_image():
    if "image" not in request.files and "file" not in request.files:
        return _err("multipart field 'image' (or 'file') is required")
    f = request.files.get("image") or request.files.get("file")
    if not f or not f.filename:
        return _err("empty upload")
    result = scan_image(f, original_name=f.filename)
    status = 200 if result.get("ok") else 422
    return _ok(result, status)


@api_bp.post("/scan/text")
def api_scan_text():
    data = request.get_json(silent=True) or {}
    result = scan_raw_text(
        page_text=data.get("page_text") or "",
        ocr_text=data.get("ocr_text") or "",
        name=data.get("name") or "",
    )
    status = 200 if result.get("ok") else 400
    return _ok(result, status)


@api_bp.post("/scan/sample")
def api_scan_sample():
    data = request.get_json(silent=True) or {}
    sample_id = (data.get("sample_id") or data.get("id") or "").strip()
    if not sample_id:
        return _err("sample_id is required", available=[s["id"] for s in sample_store.list_samples()])
    result = scan_sample(sample_id)
    status = 200 if result.get("ok") else 404
    return _ok(result, status)


@api_bp.get("/products")
def api_list_products():
    limit = min(int(request.args.get("limit", 50)), 200)
    offset = int(request.args.get("offset", 0))
    return _ok({"ok": True, "products": list_products(limit=limit, offset=offset)})


@api_bp.get("/products/<product_id>")
def api_get_product(product_id: str):
    product = get_product(product_id)
    if not product:
        return _err("Product not found", 404)
    return _ok({"ok": True, "product": product})


@api_bp.post("/findings/<finding_id>/review")
def api_review_finding(finding_id: str):
    data = request.get_json(silent=True) or {}
    action = (data.get("action") or "").strip()
    comment = data.get("comment") or ""
    try:
        updated = update_finding_review(finding_id, action, comment)
    except ValueError as exc:
        return _err(str(exc))
    if not updated:
        return _err("Finding not found", 404)
    return _ok({"ok": True, "finding": updated})


@api_bp.post("/products/<product_id>/review")
def api_review_product(product_id: str):
    data = request.get_json(silent=True) or {}
    status = (data.get("status") or data.get("action") or "").strip()
    comment = data.get("comment") or ""
    try:
        product = update_product_review(product_id, status, comment)
    except ValueError as exc:
        return _err(str(exc))
    if not product:
        return _err("Product not found", 404)
    return _ok({"ok": True, "product": product})


@api_bp.post("/products/<product_id>/report")
def api_generate_report(product_id: str):
    data = request.get_json(silent=True) or {}
    fmt = (data.get("format") or "json").lower()
    if not get_product(product_id):
        return _err("Product not found", 404)
    try:
        if fmt == "pdf":
            result = generate_pdf_report(product_id)
        else:
            result = generate_json_report(product_id)
    except Exception as exc:  # noqa: BLE001
        return _err(f"Report generation failed: {exc}", 500)
    return _ok({"ok": True, **result})


@api_bp.get("/reports/<report_id>")
def api_get_report(report_id: str):
    report = get_report(report_id)
    if not report:
        return _err("Report not found", 404)
    if report.get("format") == "pdf" and report.get("file_path"):
        path = Path(report["file_path"])
        if path.is_file():
            return send_file(path, mimetype="application/pdf", as_attachment=True,
                             download_name=path.name)
    return _ok({"ok": True, "report": report})
