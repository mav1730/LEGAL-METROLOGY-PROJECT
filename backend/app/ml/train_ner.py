"""Train DistilBERT token classification for Legal Metrology field spans.

Usage (from backend/):
    python -m app.ml.make_dataset
    python -m app.ml.train_ner

CPU fallback is automatic when CUDA is absent. Heavy training is skipped
in CI / when SKIP_NER_TRAIN=1.

    python -m app.ml.train_ner --multilingual   # bert-base-multilingual-cased
    python -m app.ml.train_ner --eval-only      # score an existing model dir

Does not call hosted LLMs. Offline weights only after the first HF download
of the base checkpoint into the local cache.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

BACKEND = Path(__file__).resolve().parents[2]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.ml.labels import BIO_LABELS, ID2LABEL, LABEL2ID, labels_payload  # noqa: E402

DEFAULT_MODEL = "distilbert-base-uncased"
MULTILINGUAL_MODEL = "bert-base-multilingual-cased"
GOLD_DIR = BACKEND / "data" / "ner_gold"
OUTPUT_DIR = BACKEND / "app" / "ml" / "ner_model"
METRICS_PATH = BACKEND / "app" / "ml" / "metrics.json"
RESULTS_PATH = BACKEND / "app" / "ml" / "RESULTS.md"
MAX_LEN = 256
STRIDE = 64


CPU_FALLBACK_NOTE = """
No CUDA GPU detected. Training will run on CPU.

This is supported but slow (a DistilBERT run on ~400 short docs is typically
one Colab T4 evening-or-less on GPU, and tens of minutes on CPU).

Skip heavy train:
  set SKIP_NER_TRAIN=1
  python -m app.ml.train_ner --eval-only

Colab T4:
  !pip install -r requirements-ml.txt
  !python -m app.ml.make_dataset
  !python -m app.ml.train_ner
""".strip()


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def should_skip_train() -> bool:
    return _truthy("SKIP_NER_TRAIN") or _truthy("CI")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing {path}. Run: python -m app.ml.make_dataset"
        )
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _char_tags(text: str, ents: list[dict[str, Any]]) -> list[str]:
    tags = ["O"] * max(len(text), 1)
    for ent in ents or []:
        label = ent.get("label")
        start, end = int(ent.get("start", -1)), int(ent.get("end", -1))
        if not label or start < 0 or end > len(text) or start >= end:
            continue
        tags[start] = f"B-{label}"
        for i in range(start + 1, end):
            tags[i] = f"I-{label}"
    return tags


def windows_for_doc(
    text: str,
    ents: list[dict[str, Any]],
    tokenizer,
    max_len: int = MAX_LEN,
    stride: int = STRIDE,
) -> list[dict[str, Any]]:
    """BIO-align one document into (possibly overlapping) token windows."""
    char_tags = _char_tags(text, ents)
    enc = tokenizer(
        text,
        return_offsets_mapping=True,
        return_overflowing_tokens=True,
        truncation=True,
        max_length=max_len,
        stride=stride,
        padding="max_length",
    )
    input_ids = enc["input_ids"]
    attention = enc["attention_mask"]
    offsets = enc["offset_mapping"]
    # Single window → flat lists; overflowing → list of windows
    if input_ids and isinstance(input_ids[0], int):
        input_ids = [input_ids]
        attention = [attention]
        offsets = [offsets]

    windows: list[dict[str, Any]] = []
    for ids, mask, offs in zip(input_ids, attention, offsets):
        labels: list[int] = []
        for token_id, (a, b) in zip(ids, offs):
            # Special tokens / padding
            if a == b:
                labels.append(-100)
                continue
            tag = char_tags[a] if a < len(char_tags) else "O"
            labels.append(LABEL2ID.get(tag, LABEL2ID["O"]))
        windows.append(
            {
                "input_ids": list(ids),
                "attention_mask": list(mask),
                "labels": labels,
            }
        )
    return windows


def flatten_split(
    docs: list[dict[str, Any]],
    tokenizer,
    max_len: int,
    stride: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for doc in docs:
        rows.extend(
            windows_for_doc(
                doc.get("text") or "",
                doc.get("ents") or [],
                tokenizer,
                max_len=max_len,
                stride=stride,
            )
        )
    return rows


def seqeval_from_logits(predictions, labels) -> dict[str, Any]:
    import numpy as np

    pred_ids = np.argmax(predictions, axis=-1)
    true_seqs: list[list[str]] = []
    pred_seqs: list[list[str]] = []
    for pred_row, lab_row in zip(pred_ids, labels):
        t_seq, p_seq = [], []
        for p, lab in zip(pred_row, lab_row):
            if lab == -100:
                continue
            t_seq.append(ID2LABEL.get(int(lab), "O"))
            p_seq.append(ID2LABEL.get(int(p), "O"))
        true_seqs.append(t_seq)
        pred_seqs.append(p_seq)
    try:
        from seqeval.metrics import (
            classification_report,
            f1_score,
            precision_score,
            recall_score,
        )
    except ImportError:
        return _span_f1_fallback(true_seqs, pred_seqs)

    return {
        "precision": float(precision_score(true_seqs, pred_seqs)),
        "recall": float(recall_score(true_seqs, pred_seqs)),
        "f1": float(f1_score(true_seqs, pred_seqs)),
        "report": classification_report(true_seqs, pred_seqs, digits=4),
    }


def _span_f1_fallback(
    true_seqs: list[list[str]], pred_seqs: list[list[str]]
) -> dict[str, Any]:
    """Minimal entity F1 if seqeval is not installed."""

    def ents(seq: list[str]) -> set[tuple[str, int, int]]:
        out, i = set(), 0
        while i < len(seq):
            tag = seq[i]
            if tag.startswith("B-"):
                lab = tag[2:]
                j = i + 1
                while j < len(seq) and seq[j] == f"I-{lab}":
                    j += 1
                out.add((lab, i, j))
                i = j
            else:
                i += 1
        return out

    tp = fp = fn = 0
    for t, p in zip(true_seqs, pred_seqs):
        te, pe = ents(t), ents(p)
        tp += len(te & pe)
        fp += len(pe - te)
        fn += len(te - pe)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return {
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "report": "(seqeval not installed; used span-F1 fallback)",
    }


def _require_transformers():
    try:
        import torch  # noqa: F401
        from transformers import (  # noqa: F401
            AutoModelForTokenClassification,
            AutoTokenizer,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise SystemExit(
            "Missing ML extras. From backend/:\n"
            "  pip install torch --index-url https://download.pytorch.org/whl/cpu\n"
            "  pip install -r requirements-ml.txt\n"
            f"Original error: {exc}"
        ) from exc


def train(
    *,
    model_name: str,
    gold_dir: Path,
    output_dir: Path,
    epochs: float,
    batch_size: int,
    lr: float,
    max_len: int,
    stride: int,
    seed: int,
) -> dict[str, Any]:
    _require_transformers()
    import torch
    from datasets import Dataset
    from transformers import (
        AutoModelForTokenClassification,
        AutoTokenizer,
        DataCollatorForTokenClassification,
        Trainer,
        TrainingArguments,
        set_seed,
    )

    set_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        print(CPU_FALLBACK_NOTE)
        print()
    print(f"Device: {device}  base_model: {model_name}")

    train_docs = load_jsonl(gold_dir / "train.jsonl")
    val_docs = load_jsonl(gold_dir / "val.jsonl")
    test_docs = load_jsonl(gold_dir / "test.jsonl")
    print(
        f"Docs  train={len(train_docs)} val={len(val_docs)} test={len(test_docs)}"
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    train_rows = flatten_split(train_docs, tokenizer, max_len, stride)
    val_rows = flatten_split(val_docs, tokenizer, max_len, stride)
    print(f"Windows train={len(train_rows)} val={len(val_rows)}")

    model = AutoModelForTokenClassification.from_pretrained(
        model_name,
        num_labels=len(BIO_LABELS),
        id2label={i: l for i, l in ID2LABEL.items()},
        label2id=dict(LABEL2ID),
    )

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        scores = seqeval_from_logits(logits, labels)
        return {
            "precision": scores["precision"],
            "recall": scores["recall"],
            "f1": scores["f1"],
        }

    ta_kwargs = dict(
        output_dir=str(output_dir / "runs"),
        learning_rate=lr,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        num_train_epochs=epochs,
        weight_decay=0.01,
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=20,
        report_to=[],
        seed=seed,
        fp16=torch.cuda.is_available(),
        dataloader_num_workers=0,
        save_total_limit=1,
    )
    try:
        args = TrainingArguments(eval_strategy="epoch", **ta_kwargs)
    except TypeError:
        args = TrainingArguments(evaluation_strategy="epoch", **ta_kwargs)

    trainer_common = dict(
        model=model,
        args=args,
        train_dataset=Dataset.from_list(train_rows),
        eval_dataset=Dataset.from_list(val_rows),
        data_collator=DataCollatorForTokenClassification(tokenizer),
        compute_metrics=compute_metrics,
    )
    try:
        trainer = Trainer(processing_class=tokenizer, **trainer_common)
    except TypeError:
        trainer = Trainer(tokenizer=tokenizer, **trainer_common)
    trainer.train()

    output_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    (output_dir / "label2id.json").write_text(
        json.dumps(labels_payload(), indent=2), encoding="utf-8"
    )
    print(f"Saved model → {output_dir}")

    # Seqeval on TEST windows
    test_rows = flatten_split(test_docs, tokenizer, max_len, stride)
    test_metrics = trainer.evaluate(Dataset.from_list(test_rows))
    print("TEST (token windows):", test_metrics)
    return {
        "device": device,
        "base_model": model_name,
        "train_docs": len(train_docs),
        "val_docs": len(val_docs),
        "test_docs": len(test_docs),
        "trainer_test": {k: float(v) if isinstance(v, (int, float)) else v for k, v in test_metrics.items()},
    }


def run_extractor_eval(
    gold_dir: Path,
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    from app.ml.eval_extractors import compare_systems, load_jsonl, write_reports

    test_docs = load_jsonl(gold_dir / "test.jsonl")
    ner_predict = None
    try:
        from app.field_extractor.ner_extractor import extract_fields_ner, ner_available

        if ner_available():
            # Force a load once so the lazy singleton is warm
            extract_fields_ner("warmup")
            ner_predict = extract_fields_ner
        else:
            print("NER weights not found — scoring regex_only only.")
    except Exception as exc:  # noqa: BLE001
        print(f"NER unavailable ({exc}); scoring regex_only only.")

    metrics = compare_systems(test_docs, ner_predict=ner_predict)
    if extra:
        metrics["train_meta"] = extra
    # Attach seqeval from trainer if present
    if extra and extra.get("trainer_test"):
        tt = extra["trainer_test"]
        metrics["seqeval"] = {
            "precision": tt.get("eval_precision"),
            "recall": tt.get("eval_recall"),
            "f1": tt.get("eval_f1"),
            "report": None,
        }
    write_reports(metrics, METRICS_PATH, RESULTS_PATH)
    print(f"Wrote {METRICS_PATH}")
    print(f"Wrote {RESULTS_PATH}")
    print(metrics.get("note"))
    return metrics


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train Legal Metrology NER")
    p.add_argument(
        "--multilingual",
        action="store_true",
        help="Use bert-base-multilingual-cased instead of DistilBERT",
    )
    p.add_argument("--model", default=None, help="Override base checkpoint name")
    p.add_argument("--gold-dir", type=Path, default=GOLD_DIR)
    p.add_argument("--output", type=Path, default=OUTPUT_DIR)
    p.add_argument("--epochs", type=float, default=4.0)
    p.add_argument("--batch-size", type=int, default=8)
    p.add_argument("--lr", type=float, default=5e-5)
    p.add_argument("--max-len", type=int, default=MAX_LEN)
    p.add_argument("--stride", type=int, default=STRIDE)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument(
        "--eval-only",
        action="store_true",
        help="Skip training; score regex/ner/hybrid on TEST",
    )
    p.add_argument(
        "--skip-train",
        action="store_true",
        help="Skip heavy training (also honoured via SKIP_NER_TRAIN=1 or CI=1)",
    )
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    model_name = args.model or (
        MULTILINGUAL_MODEL if args.multilingual else DEFAULT_MODEL
    )
    skip = args.skip_train or args.eval_only or should_skip_train()

    extra: dict[str, Any] = {}
    if skip:
        print(
            "Skipping heavy NER training "
            f"(eval_only={args.eval_only}, SKIP_NER_TRAIN/CI={should_skip_train()})."
        )
        print(CPU_FALLBACK_NOTE)
        if args.eval_only or (args.output / "config.json").is_file():
            run_extractor_eval(args.gold_dir, extra={"skipped_train": True})
        else:
            print("No saved model at", args.output)
            print("Generate data with: python -m app.ml.make_dataset")
        return 0

    extra = train(
        model_name=model_name,
        gold_dir=args.gold_dir,
        output_dir=args.output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        max_len=args.max_len,
        stride=args.stride,
        seed=args.seed,
    )
    # Drop the in-process trainer model so eval uses the saved weights path
    run_extractor_eval(args.gold_dir, extra=extra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
