"""SQLite persistence — free, local, no MongoDB required for the MVP.

Schema mirrors the concept document collections:
  products, extracted_fields, findings, reviews, reports
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator, Optional

from app.config import DB_PATH, ensure_dirs


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    ensure_dirs()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    ensure_dirs()
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT,
                source_url TEXT,
                platform TEXT,
                input_type TEXT,
                image_paths TEXT,
                page_text TEXT,
                ocr_text TEXT,
                raw_payload TEXT,
                compliance_score REAL,
                overall_status TEXT,
                review_status TEXT DEFAULT 'pending',
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS extracted_fields (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                value TEXT,
                normalized_value TEXT,
                source TEXT,
                confidence REAL,
                status TEXT,
                evidence TEXT,
                reason TEXT,
                alternatives TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS findings (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                rule_id TEXT,
                field TEXT,
                status TEXT,
                severity TEXT,
                explanation TEXT,
                evidence TEXT,
                confidence REAL,
                requires_human_review INTEGER DEFAULT 1,
                reviewer_action TEXT,
                reviewer_comment TEXT,
                reviewed_at TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                product_id TEXT NOT NULL,
                format TEXT,
                content TEXT,
                file_path TEXT,
                created_at TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_fields_product ON extracted_fields(product_id);
            CREATE INDEX IF NOT EXISTS idx_findings_product ON findings(product_id);
            CREATE INDEX IF NOT EXISTS idx_products_status ON products(overall_status);
            """
        )


def save_scan_result(payload: dict[str, Any]) -> dict[str, Any]:
    """Persist a full scan pipeline result. Returns product record with ids."""
    product_id = payload.get("id") or _uid("prod_")
    now = _now()

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO products (
                id, name, source_url, platform, input_type, image_paths,
                page_text, ocr_text, raw_payload, compliance_score,
                overall_status, review_status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_id,
                payload.get("name"),
                payload.get("source_url"),
                payload.get("platform"),
                payload.get("input_type"),
                json.dumps(payload.get("image_paths") or []),
                payload.get("page_text"),
                payload.get("ocr_text"),
                json.dumps(payload.get("raw_payload") or {}),
                payload.get("compliance_score"),
                payload.get("overall_status"),
                payload.get("review_status", "pending"),
                now,
                now,
            ),
        )

        for field in payload.get("fields") or []:
            conn.execute(
                """
                INSERT INTO extracted_fields (
                    id, product_id, field_name, value, normalized_value,
                    source, confidence, status, evidence, reason, alternatives
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _uid("fld_"),
                    product_id,
                    field.get("name"),
                    field.get("value"),
                    field.get("normalized_value"),
                    field.get("source"),
                    field.get("confidence"),
                    field.get("status"),
                    json.dumps(field.get("evidence")),
                    field.get("reason"),
                    json.dumps(field.get("alternatives") or []),
                ),
            )

        for finding in payload.get("findings") or []:
            conn.execute(
                """
                INSERT INTO findings (
                    id, product_id, rule_id, field, status, severity,
                    explanation, evidence, confidence, requires_human_review
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    finding.get("id") or _uid("fnd_"),
                    product_id,
                    finding.get("rule_id"),
                    finding.get("field"),
                    finding.get("status"),
                    finding.get("severity"),
                    finding.get("explanation"),
                    json.dumps(finding.get("evidence")),
                    finding.get("confidence"),
                    1 if finding.get("requires_human_review", True) else 0,
                ),
            )

    return get_product(product_id)  # type: ignore[return-value]


def get_product(product_id: str) -> Optional[dict[str, Any]]:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if not row:
            return None
        product = dict(row)
        product["image_paths"] = json.loads(product.get("image_paths") or "[]")
        product["raw_payload"] = json.loads(product.get("raw_payload") or "{}")

        fields = conn.execute(
            "SELECT * FROM extracted_fields WHERE product_id = ?", (product_id,)
        ).fetchall()
        product["fields"] = [_field_row(r) for r in fields]

        findings = conn.execute(
            "SELECT * FROM findings WHERE product_id = ? ORDER BY severity DESC",
            (product_id,),
        ).fetchall()
        product["findings"] = [_finding_row(r) for r in findings]

        reports = conn.execute(
            "SELECT id, format, file_path, created_at FROM reports WHERE product_id = ?",
            (product_id,),
        ).fetchall()
        product["reports"] = [dict(r) for r in reports]
        return product


def list_products(limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT id, name, source_url, platform, input_type, compliance_score,
                   overall_status, review_status, created_at, updated_at
            FROM products
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]


def dashboard_stats() -> dict[str, Any]:
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
        issues = conn.execute(
            "SELECT COUNT(*) AS c FROM products WHERE overall_status IN ('potential_issues', 'needs_review')"
        ).fetchone()["c"]
        needs = conn.execute(
            "SELECT COUNT(*) AS c FROM products WHERE review_status IN ('pending', 'needs_review')"
        ).fetchone()["c"]
        confirmed = conn.execute(
            "SELECT COUNT(*) AS c FROM products WHERE review_status = 'confirmed'"
        ).fetchone()["c"]
        avg = conn.execute(
            "SELECT AVG(compliance_score) AS a FROM products WHERE compliance_score IS NOT NULL"
        ).fetchone()["a"]
        return {
            "products_scanned": total,
            "potential_issues": issues,
            "needs_review": needs,
            "confirmed": confirmed,
            "average_score": round(float(avg), 2) if avg is not None else None,
        }


def update_finding_review(
    finding_id: str,
    action: str,
    comment: str = "",
) -> Optional[dict[str, Any]]:
    action = action.lower().strip()
    if action not in ("confirm", "reject", "needs_review"):
        raise ValueError("action must be confirm | reject | needs_review")

    now = _now()
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM findings WHERE id = ?", (finding_id,)
        ).fetchone()
        if not row:
            return None
        conn.execute(
            """
            UPDATE findings
            SET reviewer_action = ?, reviewer_comment = ?, reviewed_at = ?
            WHERE id = ?
            """,
            (action, comment, now, finding_id),
        )
        product_id = row["product_id"]
        _refresh_product_review_status(conn, product_id)
        return _finding_row(
            conn.execute("SELECT * FROM findings WHERE id = ?", (finding_id,)).fetchone()
        )


def update_product_review(product_id: str, status: str, comment: str = "") -> Optional[dict[str, Any]]:
    status = status.lower().strip()
    if status not in ("pending", "confirmed", "rejected", "needs_review"):
        raise ValueError("invalid review status")
    with connect() as conn:
        row = conn.execute("SELECT id FROM products WHERE id = ?", (product_id,)).fetchone()
        if not row:
            return None
        conn.execute(
            """
            UPDATE products SET review_status = ?, updated_at = ? WHERE id = ?
            """,
            (status, _now(), product_id),
        )
    return get_product(product_id)


def save_report(product_id: str, format_: str, content: str, file_path: str = "") -> dict[str, Any]:
    report_id = _uid("rep_")
    created = _now()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO reports (id, product_id, format, content, file_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (report_id, product_id, format_, content, file_path, created),
        )
    return {
        "id": report_id,
        "product_id": product_id,
        "format": format_,
        "file_path": file_path,
        "created_at": created,
    }


def get_report(report_id: str) -> Optional[dict[str, Any]]:
    with connect() as conn:
        row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
        return dict(row) if row else None


def _refresh_product_review_status(conn: sqlite3.Connection, product_id: str) -> None:
    findings = conn.execute(
        "SELECT reviewer_action FROM findings WHERE product_id = ?", (product_id,)
    ).fetchall()
    if not findings:
        return
    actions = [f["reviewer_action"] for f in findings]
    if all(a is not None for a in actions) and all(a == "confirm" for a in actions):
        status = "confirmed"
    elif any(a == "needs_review" for a in actions):
        status = "needs_review"
    elif any(a is None for a in actions):
        status = "pending"
    elif all(a == "reject" for a in actions):
        status = "rejected"
    else:
        status = "needs_review"
    conn.execute(
        "UPDATE products SET review_status = ?, updated_at = ? WHERE id = ?",
        (status, _now(), product_id),
    )


def _field_row(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["evidence"] = json.loads(d["evidence"]) if d.get("evidence") else None
    d["alternatives"] = json.loads(d["alternatives"]) if d.get("alternatives") else []
    return d


def _finding_row(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    d["evidence"] = json.loads(d["evidence"]) if d.get("evidence") else None
    d["requires_human_review"] = bool(d.get("requires_human_review"))
    return d
