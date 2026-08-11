"""Structured compliance report generation (JSON + PDF)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import DATA_DIR, SYSTEM_DISCLAIMER, ensure_dirs
from app.services.storage import get_product, save_report


def build_report_dict(product: dict[str, Any]) -> dict[str, Any]:
    return {
        "report_type": "Legal Metrology Compliance Screening Report",
        "disclaimer": SYSTEM_DISCLAIMER,
        "product": {
            "id": product.get("id"),
            "name": product.get("name"),
            "source_url": product.get("source_url"),
            "platform": product.get("platform"),
            "input_type": product.get("input_type"),
            "compliance_score": product.get("compliance_score"),
            "overall_status": product.get("overall_status"),
            "review_status": product.get("review_status"),
            "created_at": product.get("created_at"),
        },
        "extracted_fields": [
            {
                "field": f.get("field_name") or f.get("name"),
                "value": f.get("value"),
                "status": f.get("status"),
                "confidence": f.get("confidence"),
                "source": f.get("source"),
                "evidence": f.get("evidence"),
                "reason": f.get("reason"),
            }
            for f in product.get("fields") or []
        ],
        "findings": [
            {
                "id": f.get("id"),
                "rule_id": f.get("rule_id"),
                "field": f.get("field"),
                "status": f.get("status"),
                "severity": f.get("severity"),
                "explanation": f.get("explanation"),
                "requires_human_review": f.get("requires_human_review"),
                "reviewer_action": f.get("reviewer_action"),
                "reviewer_comment": f.get("reviewer_comment"),
            }
            for f in product.get("findings") or []
        ],
        "notes": [
            "Score is a prioritization metric for reviewers, not a legal certification.",
            "not_detected means the field was not found in available sources — not proof of illegality.",
            "Human review is required for enforcement or final compliance decisions.",
        ],
    }


def generate_json_report(product_id: str) -> dict[str, Any]:
    product = get_product(product_id)
    if not product:
        raise ValueError("Product not found")
    report = build_report_dict(product)
    content = json.dumps(report, indent=2, ensure_ascii=False)
    meta = save_report(product_id, "json", content, file_path="")
    return {"meta": meta, "report": report}


def generate_pdf_report(product_id: str) -> dict[str, Any]:
    product = get_product(product_id)
    if not product:
        raise ValueError("Product not found")

    ensure_dirs()
    reports_dir = DATA_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    file_path = reports_dir / f"{product_id}.pdf"

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=8,
    )
    body = styles["BodyText"]
    small = ParagraphStyle("Small", parent=body, fontSize=8, textColor=colors.grey)

    story = [
        Paragraph("Legal Metrology Compliance Screening Report", title_style),
        Paragraph(SYSTEM_DISCLAIMER, small),
        Spacer(1, 0.2 * inch),
        Paragraph(f"<b>Product:</b> {product.get('name') or '—'}", body),
        Paragraph(f"<b>ID:</b> {product.get('id')}", body),
        Paragraph(f"<b>Source:</b> {product.get('source_url') or '—'}", body),
        Paragraph(f"<b>Platform:</b> {product.get('platform') or '—'}", body),
        Paragraph(
            f"<b>Score:</b> {product.get('compliance_score')} &nbsp; "
            f"<b>Status:</b> {product.get('overall_status')} &nbsp; "
            f"<b>Review:</b> {product.get('review_status')}",
            body,
        ),
        Spacer(1, 0.15 * inch),
        Paragraph("<b>Extracted Fields</b>", styles["Heading2"]),
    ]

    field_rows = [[Paragraph("<b>Field</b>", body), Paragraph("<b>Value</b>", body),
                   Paragraph("<b>Status</b>", body), Paragraph("<b>Conf.</b>", body)]]
    for f in product.get("fields") or []:
        field_rows.append(
            [
                Paragraph(str(f.get("field_name") or f.get("name") or ""), body),
                Paragraph(str(f.get("value") or "—"), body),
                Paragraph(str(f.get("status") or ""), body),
                Paragraph(str(f.get("confidence") if f.get("confidence") is not None else ""), body),
            ]
        )

    table = Table(field_rows, colWidths=[1.6 * inch, 2.6 * inch, 1.3 * inch, 0.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.92, 0.94, 0.97)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>Findings (potential issues)</b>", styles["Heading2"]))

    findings = product.get("findings") or []
    if not findings:
        story.append(
            Paragraph(
                "No configured potential issues in available data. "
                "This is not a legal clearance certificate.",
                body,
            )
        )
    else:
        for f in findings:
            story.append(
                Paragraph(
                    f"<b>[{f.get('severity')}] {f.get('rule_id')}</b> — "
                    f"field <i>{f.get('field')}</i>: {f.get('explanation')}",
                    body,
                )
            )
            if f.get("reviewer_action"):
                story.append(
                    Paragraph(
                        f"Reviewer: {f.get('reviewer_action')} — {f.get('reviewer_comment') or ''}",
                        small,
                    )
                )
            story.append(Spacer(1, 0.06 * inch))

    story.append(Spacer(1, 0.2 * inch))
    story.append(
        Paragraph(
            "End of report. Automated screening only — human verification required.",
            small,
        )
    )

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch,
    )
    doc.build(story)

    report_dict = build_report_dict(product)
    meta = save_report(
        product_id,
        "pdf",
        json.dumps({"pdf_path": str(file_path)}),
        file_path=str(file_path),
    )
    return {"meta": meta, "file_path": str(file_path), "report": report_dict}
