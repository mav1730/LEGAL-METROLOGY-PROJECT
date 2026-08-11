"""End-to-end scan pipeline: input → extract → rules → persist."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Any, Optional

from app.config import SYSTEM_DISCLAIMER, UPLOAD_DIR, ensure_dirs
from app.field_extractor import extract_and_merge
from app.field_extractor.patterns import FIELD_ORDER
from app.services import samples as sample_store
from app.services.ocr_service import run_ocr
from app.services.rules import evaluate_rules
from app.services.scraper import (
    guess_name_from_text,
    scrape_from_html,
    scrape_product_url,
)
from app.services.storage import save_scan_result


def _fields_as_list(extraction) -> list[dict[str, Any]]:
    out = []
    for name in FIELD_ORDER:
        f = extraction.fields.get(name)
        if not f:
            continue
        d = f.to_dict()
        d["source"] = f.evidence.source.value if f.evidence else extraction.source.value
        out.append(d)
    return out


def run_text_scan(
    page_text: str = "",
    ocr_text: str = "",
    name: str = "",
    source_url: str = "",
    platform: str = "manual",
    input_type: str = "text",
    image_paths: Optional[list[str]] = None,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Core path used by URL / image / sample / raw-text scans."""
    extraction = extract_and_merge(page_text=page_text or "", ocr_text=ocr_text or "")
    fields = _fields_as_list(extraction)
    evaluation = evaluate_rules(fields)

    product_name = name or guess_name_from_text(page_text or ocr_text, None)
    # Prefer extracted product_name if present
    for f in fields:
        if f["name"] == "product_name" and f.get("value"):
            product_name = f["value"]
            break

    payload = {
        "name": product_name,
        "source_url": source_url or None,
        "platform": platform,
        "input_type": input_type,
        "image_paths": image_paths or [],
        "page_text": page_text or "",
        "ocr_text": ocr_text or "",
        "raw_payload": {
            "warnings": extraction.warnings,
            "extraction_summary": extraction.summary(),
            "extra": extra or {},
            "disclaimer": SYSTEM_DISCLAIMER,
        },
        "fields": fields,
        "findings": evaluation["findings"],
        "compliance_score": evaluation["compliance_score"],
        "overall_status": evaluation["overall_status"],
        "review_status": "pending",
    }

    saved = save_scan_result(payload)
    saved["disclaimer"] = SYSTEM_DISCLAIMER
    saved["rules_version"] = evaluation.get("rules_version")
    saved["extraction_summary"] = extraction.summary()
    return saved


def scan_url(
    url: str,
    html: str = "",
    use_browser: bool = True,
) -> dict[str, Any]:
    """Scan a product URL.

    Optional ``html``: if the marketplace blocks the server, the user can paste
    View-Source / saved page HTML from their browser and still attach the real URL.
    """
    url = (url or "").strip()
    html = (html or "").strip()

    if html:
        scraped = scrape_from_html(html, url=url or "pasted://html")
    elif url:
        scraped = scrape_product_url(url, use_browser=use_browser)
    else:
        return {
            "ok": False,
            "error": "Provide a product url and/or page html",
            "disclaimer": SYSTEM_DISCLAIMER,
        }

    if not scraped.get("ok"):
        return {
            "ok": False,
            "error": scraped.get("error") or "Scrape failed",
            "scrape": {
                "ok": False,
                "platform": scraped.get("platform"),
                "title": scraped.get("title"),
                "error": scraped.get("error"),
                "raw_meta": scraped.get("raw_meta"),
            },
            "hint": (
                "If Amazon/Flipkart blocked the server: open the product in Chrome → "
                "select Product details text (or Save page HTML) → paste in the "
                "URL tab 'Page HTML / details' box with the real product URL. "
                "Or use DemoMart links (always work): http://127.0.0.1:5000/demo/"
            ),
            "fallback": {
                "demomart": "http://127.0.0.1:5000/demo/",
                "paste_html": True,
                "paste_text_tab": True,
            },
            "disclaimer": SYSTEM_DISCLAIMER,
        }

    result = run_text_scan(
        page_text=scraped.get("page_text") or "",
        ocr_text="",
        name=scraped.get("title") or "",
        source_url=url or scraped.get("source_url"),
        platform=scraped.get("platform") or "web",
        input_type="url" if not html else "url_html",
        image_paths=scraped.get("image_urls") or [],
        extra={
            "scrape_ok": True,
            "image_urls": scraped.get("image_urls"),
            "method": (scraped.get("raw_meta") or {}).get("method"),
            "methods_tried": (scraped.get("raw_meta") or {}).get("methods_tried"),
        },
    )
    result["ok"] = True
    result["scrape"] = {
        "ok": True,
        "platform": scraped.get("platform"),
        "title": scraped.get("title"),
        "image_count": len(scraped.get("image_urls") or []),
        "method": (scraped.get("raw_meta") or {}).get("method"),
        "text_chars": len(scraped.get("page_text") or ""),
    }
    return result


def scan_image(file_storage, original_name: str = "") -> dict[str, Any]:
    ensure_dirs()
    ext = Path(original_name or "upload.jpg").suffix.lower() or ".jpg"
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}:
        return {
            "ok": False,
            "error": f"Unsupported image type: {ext}",
            "disclaimer": SYSTEM_DISCLAIMER,
        }

    filename = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / filename
    file_storage.save(str(dest))

    ocr = run_ocr(dest)
    if not ocr.get("ok"):
        # Still persist a scan with empty OCR so UI can show the failure honestly
        result = run_text_scan(
            page_text="",
            ocr_text="",
            name=original_name or filename,
            source_url=None,
            platform="upload",
            input_type="image",
            image_paths=[str(dest)],
            extra={"ocr_error": ocr.get("error"), "ocr_engine": ocr.get("engine")},
        )
        result["ok"] = False
        result["error"] = ocr.get("error") or "OCR produced no text"
        result["ocr"] = ocr
        return result

    result = run_text_scan(
        page_text="",
        ocr_text=ocr.get("text") or "",
        name=original_name or filename,
        source_url=None,
        platform="upload",
        input_type="image",
        image_paths=[str(dest)],
        extra={
            "ocr_engine": ocr.get("engine"),
            "ocr_confidence_hint": ocr.get("confidence_hint"),
        },
    )
    result["ok"] = True
    result["ocr"] = {
        "ok": True,
        "engine": ocr.get("engine"),
        "confidence_hint": ocr.get("confidence_hint"),
        "text_preview": (ocr.get("text") or "")[:500],
    }
    return result


def scan_raw_text(page_text: str = "", ocr_text: str = "", name: str = "") -> dict[str, Any]:
    if not (page_text or "").strip() and not (ocr_text or "").strip():
        return {
            "ok": False,
            "error": "Provide page_text and/or ocr_text",
            "disclaimer": SYSTEM_DISCLAIMER,
        }
    result = run_text_scan(
        page_text=page_text,
        ocr_text=ocr_text,
        name=name or "Manual text scan",
        platform="manual",
        input_type="text",
    )
    result["ok"] = True
    return result


def scan_sample(sample_id: str) -> dict[str, Any]:
    sample = sample_store.get_sample(sample_id)
    if not sample:
        return {
            "ok": False,
            "error": f"Unknown sample id: {sample_id}",
            "available": [s["id"] for s in sample_store.list_samples()],
            "disclaimer": SYSTEM_DISCLAIMER,
        }
    result = run_text_scan(
        page_text=sample.get("page_text") or "",
        ocr_text=sample.get("ocr_text") or "",
        name=sample.get("name") or sample_id,
        source_url=sample.get("source_url") or f"demo://samples/{sample_id}",
        platform=sample.get("platform") or "Demo",
        input_type="sample",
        extra={"sample_id": sample_id, "description": sample.get("description")},
    )
    result["ok"] = True
    result["sample_id"] = sample_id
    return result


def save_upload_copy(src: Path, dest_name: str) -> Path:
    ensure_dirs()
    dest = UPLOAD_DIR / dest_name
    shutil.copy2(src, dest)
    return dest
