"""Optional free OCR bridge (Tesseract).

Install (free):
  - Tesseract OCR engine: https://github.com/tesseract-ocr/tesseract
  - pip install pytesseract pillow

This module is optional. Core field extraction works without it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

from .extractors import extract_fields
from .merge import extract_and_merge
from .models import ExtractionResult, SourceType


def ocr_image_to_text(image_path: Union[str, Path]) -> str:
    """Run free Tesseract OCR on an image. Raises ImportError if deps missing."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise ImportError(
            "OCR bridge requires free packages: pip install pytesseract pillow\n"
            "Also install the Tesseract engine from "
            "https://github.com/tesseract-ocr/tesseract"
        ) from exc

    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    img = Image.open(path)
    # PSM 6 = assume a single uniform block of text (good for packaging panels)
    config = "--psm 6"
    text = pytesseract.image_to_string(img, config=config)
    return text or ""


def extract_from_image(image_path: Union[str, Path]) -> ExtractionResult:
    """OCR an image, then run precision-first field extraction."""
    text = ocr_image_to_text(image_path)
    return extract_fields(text, source=SourceType.OCR)


def extract_from_page_and_image(
    page_text: str = "",
    image_path: Union[str, Path, None] = None,
) -> ExtractionResult:
    """Merge page text with OCR from a packaging image."""
    ocr_text = ocr_image_to_text(image_path) if image_path else ""
    return extract_and_merge(page_text=page_text or "", ocr_text=ocr_text)
