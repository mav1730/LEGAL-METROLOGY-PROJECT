"""OCR service with free Tesseract when available, safe fallback otherwise."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union


def tesseract_available() -> bool:
    try:
        import pytesseract
        from PIL import Image  # noqa: F401

        # Probe binary
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def run_ocr(image_path: Union[str, Path]) -> dict[str, Any]:
    """OCR a local image file.

    Returns {ok, text, engine, error, confidence_hint}
    Never invents packaging text — empty text if OCR fails.
    """
    path = Path(image_path)
    out: dict[str, Any] = {
        "ok": False,
        "text": "",
        "engine": None,
        "error": None,
        "confidence_hint": None,
    }
    if not path.is_file():
        out["error"] = f"Image not found: {path}"
        return out

    try:
        import pytesseract
        from PIL import Image, ImageOps, ImageFilter
    except ImportError:
        out["error"] = (
            "pytesseract/Pillow not installed. "
            "pip install pytesseract pillow and install Tesseract engine. "
            "You can still scan using page text or demo samples."
        )
        return out

    try:
        img = Image.open(path)
        # Light preprocessing — free, local
        gray = ImageOps.grayscale(img)
        gray = ImageOps.autocontrast(gray)
        gray = gray.filter(ImageFilter.SHARPEN)

        config = "--psm 6"
        text = pytesseract.image_to_string(gray, config=config) or ""
        text = text.strip()

        # Optional mean confidence from detailed data
        conf_hint: Optional[float] = None
        try:
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            confs = [int(c) for c in data.get("conf", []) if str(c).lstrip("-").isdigit() and int(c) >= 0]
            if confs:
                conf_hint = round(sum(confs) / len(confs) / 100.0, 3)
        except Exception:
            conf_hint = None

        out["ok"] = bool(text)
        out["text"] = text
        out["engine"] = "tesseract"
        out["confidence_hint"] = conf_hint
        if not text:
            out["error"] = "OCR returned empty text (blurry/low-contrast image?)"
        return out
    except Exception as exc:  # noqa: BLE001
        out["error"] = f"OCR failed: {exc.__class__.__name__}: {exc}"
        return out
