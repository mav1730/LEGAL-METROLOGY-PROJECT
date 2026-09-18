"""Offline DistilBERT token-classification extractor (lazy singleton).

Never downloads weights at request time: `local_files_only=True` against
`backend/app/ml/ner_model/`. If files or torch/transformers are missing,
every field is `not_detected` — we do not invent values.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional

from .extractors import (
    validate_country,
    validate_date,
    validate_manufacturer,
    validate_mrp,
    validate_net_quantity,
    validate_product_name,
)
from .models import (
    Evidence,
    ExtractedField,
    ExtractionResult,
    FieldStatus,
    SourceType,
    empty_field,
)
from .patterns import FIELD_ORDER

_LOCK = threading.Lock()
_STATE: Any = None  # None = not tried, False = failed, dict = loaded

MAX_LEN = 256
STRIDE = 64


def _model_dir() -> Path:
    try:
        from app.config import NER_MODEL_DIR

        return Path(NER_MODEL_DIR)
    except Exception:  # noqa: BLE001
        return Path(__file__).resolve().parents[1] / "ml" / "ner_model"


def ner_files_present() -> bool:
    d = _model_dir()
    has_cfg = (d / "config.json").is_file()
    has_labels = (d / "label2id.json").is_file()
    has_weights = (d / "model.safetensors").is_file() or (
        d / "pytorch_model.bin"
    ).is_file()
    has_tok = (d / "tokenizer.json").is_file() or (d / "vocab.txt").is_file() or (
        d / "tokenizer_config.json"
    ).is_file()
    return has_cfg and has_labels and has_weights and has_tok


def transformers_importable() -> bool:
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except ImportError:
        return False
    return True


def ner_available() -> bool:
    """True when local weights exist and the ML extra is importable.

    Does not load the model (health checks must stay cheap).
    """
    return ner_files_present() and transformers_importable()


def _load_state() -> Optional[dict[str, Any]]:
    global _STATE
    if _STATE is False:
        return None
    if isinstance(_STATE, dict):
        return _STATE
    with _LOCK:
        if isinstance(_STATE, dict):
            return _STATE
        if _STATE is False:
            return None
        try:
            import torch
            from transformers import AutoModelForTokenClassification, AutoTokenizer
        except ImportError:
            _STATE = False
            return None
        d = _model_dir()
        if not ner_files_present():
            _STATE = False
            return None
        payload = json.loads((d / "label2id.json").read_text(encoding="utf-8"))
        id2label = {int(k): v for k, v in payload.get("id2label", {}).items()}
        if not id2label:
            raw = payload.get("label2id") or {}
            id2label = {int(v): k for k, v in raw.items()}
        tokenizer = AutoTokenizer.from_pretrained(str(d), local_files_only=True)
        model = AutoModelForTokenClassification.from_pretrained(
            str(d), local_files_only=True
        )
        model.eval()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        _STATE = {
            "tokenizer": tokenizer,
            "model": model,
            "id2label": id2label,
            "device": device,
            "torch": torch,
        }
        return _STATE


def reset_ner_singleton() -> None:
    """Test helper — drop the cached model."""
    global _STATE
    with _LOCK:
        _STATE = None


def _decode_window(
    text: str,
    offsets: list[tuple[int, int]],
    pred_ids: list[int],
    probs: list[float],
    id2label: dict[int, str],
) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    current: Optional[dict[str, Any]] = None

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        start, end = current["start"], current["end"]
        if 0 <= start < end <= len(text):
            spans.append(
                {
                    "start": start,
                    "end": end,
                    "label": current["label"],
                    "text": text[start:end],
                    "confidence": (
                        sum(current["scores"]) / len(current["scores"])
                        if current["scores"]
                        else 0.0
                    ),
                }
            )
        current = None

    for (a, b), pid, score in zip(offsets, pred_ids, probs):
        if a == b:
            continue
        tag = id2label.get(int(pid), "O")
        if tag == "O" or "-" not in tag:
            flush()
            continue
        prefix, label = tag.split("-", 1)
        if prefix == "B" or current is None or current["label"] != label:
            flush()
            current = {
                "label": label,
                "start": a,
                "end": b,
                "scores": [float(score)],
            }
        else:
            current["end"] = b
            current["scores"].append(float(score))
    flush()
    return spans


def _merge_spans(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Precision-first: keep highest-confidence non-overlapping spans."""
    spans = sorted(spans, key=lambda s: s.get("confidence", 0.0), reverse=True)
    kept: list[dict[str, Any]] = []
    for span in spans:
        overlap = False
        for other in kept:
            if not (span["end"] <= other["start"] or span["start"] >= other["end"]):
                overlap = True
                break
        if not overlap:
            kept.append(span)
    kept.sort(key=lambda s: s["start"])
    return kept


def _validate_span(field: str, raw: str) -> Optional[dict[str, Any]]:
    raw = (raw or "").strip()
    if not raw:
        return None
    if field == "mrp":
        amount = validate_mrp(raw)
        if amount is None:
            return None
        return {"value": f"Rs. {amount}", "normalized": amount, "unit": None}
    if field == "net_quantity":
        import re

        m = re.match(
            r"(?i)^\s*(\d+(?:\.\d+)?)\s*"
            r"(kgs?|kilograms?|gms?|grams?|g|mg|ml|millilitres?|milliliters?"
            r"|ltrs?|litres?|liters?|lt|l|pcs?|pieces?|nos?|units?|n)\.?\s*$",
            raw,
        )
        if not m:
            return None
        parsed = validate_net_quantity(m.group(1), m.group(2))
        if parsed is None:
            return None
        num, unit, display = parsed
        return {"value": display, "normalized": display, "unit": unit}
    if field == "manufacturer":
        name = validate_manufacturer(raw)
        if name is None:
            return None
        return {"value": name, "normalized": name, "unit": None}
    if field == "country_of_origin":
        country = validate_country(raw)
        if country is None:
            return None
        return {"value": country, "normalized": country, "unit": None}
    if field in ("manufacturing_date", "expiry_date"):
        date = validate_date(raw)
        if date is None:
            return None
        return {"value": date, "normalized": date, "unit": None}
    if field == "product_name":
        name = validate_product_name(raw)
        if name is None:
            return None
        return {"value": name, "normalized": name, "unit": None}
    return {"value": raw, "normalized": raw, "unit": None}


def extract_fields_ner(
    text: str,
    fields: Optional[list[str]] = None,
) -> ExtractionResult:
    """BIO decode → ExtractedField. Missing span ⇒ not_detected (never invent)."""
    target = fields or FIELD_ORDER
    warnings: list[str] = []
    raw = text or ""
    if not raw.strip():
        return ExtractionResult(
            fields={n: empty_field(n, "Empty input text") for n in target},
            raw_text="",
            source=SourceType.NER,
            warnings=["Empty input text — nothing to extract"],
        )

    state = _load_state()
    if state is None:
        warnings.append("NER model not available (offline weights missing or ML extra not installed)")
        return ExtractionResult(
            fields={
                n: empty_field(n, "NER model not available")
                for n in target
            },
            raw_text=raw,
            source=SourceType.NER,
            warnings=warnings,
        )

    torch = state["torch"]
    tokenizer = state["tokenizer"]
    model = state["model"]
    id2label = state["id2label"]
    device = state["device"]

    enc = tokenizer(
        raw,
        return_offsets_mapping=True,
        return_overflowing_tokens=True,
        truncation=True,
        max_length=MAX_LEN,
        stride=STRIDE,
        padding=True,
        return_tensors="pt",
    )
    offsets_all = enc.pop("offset_mapping")
    overflow = enc.pop("overflow_to_sample_mapping", None)  # unused; one doc
    _ = overflow
    enc = {k: v.to(device) for k, v in enc.items()}

    with torch.no_grad():
        logits = model(**enc).logits
        probs = torch.softmax(logits, dim=-1)
        pred_ids = torch.argmax(probs, dim=-1)
        pred_scores = probs.gather(-1, pred_ids.unsqueeze(-1)).squeeze(-1)

    all_spans: list[dict[str, Any]] = []
    n_win = pred_ids.shape[0]
    for w in range(n_win):
        offs = [(int(a), int(b)) for a, b in offsets_all[w].tolist()]
        ids = pred_ids[w].tolist()
        scores = pred_scores[w].tolist()
        all_spans.extend(_decode_window(raw, offs, ids, scores, id2label))
    spans = _merge_spans(all_spans)

    best: dict[str, dict[str, Any]] = {}
    for span in spans:
        lab = span["label"]
        if lab not in target:
            continue
        prev = best.get(lab)
        if prev is None or span["confidence"] > prev["confidence"]:
            best[lab] = span

    extracted: dict[str, ExtractedField] = {}
    for name in target:
        span = best.get(name)
        if not span:
            extracted[name] = empty_field(
                name,
                reason=(
                    f"Required field not detected: no NER span for "
                    f"{name.replace('_', ' ')}"
                ),
            )
            continue
        parsed = _validate_span(name, span["text"])
        if parsed is None:
            extracted[name] = empty_field(
                name,
                reason=(
                    f"NER span rejected by validator for {name.replace('_', ' ')}"
                ),
            )
            continue
        conf = float(span["confidence"])
        extracted[name] = ExtractedField(
            name=name,
            value=parsed["value"],
            normalized_value=parsed["normalized"],
            unit=parsed["unit"],
            status=FieldStatus.DETECTED,
            confidence=conf,
            evidence=Evidence(
                source=SourceType.NER,
                matched_text=span["text"],
                start=int(span["start"]),
                end=int(span["end"]),
                pattern_id=f"ner:{name}",
            ),
            reason=None,
        )

    return ExtractionResult(
        fields=extracted,
        raw_text=raw,
        source=SourceType.NER,
        warnings=warnings,
    )
