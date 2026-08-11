"""Free, offline Legal Metrology field extraction from OCR / page text."""

from .extractors import extract_fields, extract_from_ocr, extract_from_page
from .merge import extract_and_merge, merge_fields
from .models import (
    Evidence,
    ExtractedField,
    ExtractionResult,
    FieldStatus,
    SourceType,
)
from .patterns import FIELD_ORDER

__all__ = [
    "Evidence",
    "ExtractedField",
    "ExtractionResult",
    "FieldStatus",
    "SourceType",
    "FIELD_ORDER",
    "extract_fields",
    "extract_from_ocr",
    "extract_from_page",
    "extract_and_merge",
    "merge_fields",
]

__version__ = "1.0.0"
