"""Structured result types for Legal Metrology field extraction.

Design principle: never invent values. A missing field is null with a reason,
not a guessed string.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


class FieldStatus(str, Enum):
    DETECTED = "detected"
    NOT_DETECTED = "not_detected"
    AMBIGUOUS = "ambiguous"
    LOW_CONFIDENCE = "low_confidence"


class SourceType(str, Enum):
    PAGE = "page"
    OCR = "ocr"
    MERGED = "merged"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Evidence:
    """Exact span that produced a field value — required for explainability."""

    source: SourceType
    matched_text: str
    start: int
    end: int
    pattern_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.value,
            "matched_text": self.matched_text,
            "start": self.start,
            "end": self.end,
            "pattern_id": self.pattern_id,
        }


@dataclass
class ExtractedField:
    """One structured product declaration field."""

    name: str
    value: Optional[str]
    status: FieldStatus
    confidence: float
    evidence: Optional[Evidence] = None
    normalized_value: Optional[str] = None
    unit: Optional[str] = None
    reason: Optional[str] = None
    alternatives: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "normalized_value": self.normalized_value,
            "unit": self.unit,
            "status": self.status.value,
            "confidence": round(self.confidence, 4),
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "reason": self.reason,
            "alternatives": list(self.alternatives),
        }


@dataclass
class ExtractionResult:
    """Full extraction output for one text source or multi-source merge."""

    fields: dict[str, ExtractedField]
    raw_text: str
    source: SourceType
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.value,
            "fields": {k: v.to_dict() for k, v in self.fields.items()},
            "warnings": list(self.warnings),
            "summary": self.summary(),
        }

    def summary(self) -> dict[str, Any]:
        detected = [
            name
            for name, f in self.fields.items()
            if f.status == FieldStatus.DETECTED and f.value
        ]
        missing = [
            name
            for name, f in self.fields.items()
            if f.status == FieldStatus.NOT_DETECTED
        ]
        review = [
            name
            for name, f in self.fields.items()
            if f.status in (FieldStatus.AMBIGUOUS, FieldStatus.LOW_CONFIDENCE)
        ]
        return {
            "detected_fields": detected,
            "not_detected_fields": missing,
            "needs_review_fields": review,
            "detected_count": len(detected),
            "not_detected_count": len(missing),
        }

    def as_json_ready(self) -> dict[str, Any]:
        """Shape close to the project concept document."""
        out: dict[str, Any] = {}
        for name, f in self.fields.items():
            out[name] = {
                "value": f.normalized_value or f.value,
                "raw_value": f.value,
                "source": f.evidence.source.value if f.evidence else None,
                "confidence": round(f.confidence, 4),
                "status": f.status.value,
                "evidence": f.evidence.matched_text if f.evidence else None,
                "reason": f.reason,
            }
        return out


def empty_field(name: str, reason: str) -> ExtractedField:
    return ExtractedField(
        name=name,
        value=None,
        status=FieldStatus.NOT_DETECTED,
        confidence=0.0,
        reason=reason,
    )


def result_to_plain_dict(result: ExtractionResult) -> dict[str, Any]:
    return result.to_dict()
