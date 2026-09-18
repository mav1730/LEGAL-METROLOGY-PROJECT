import React, { useState } from "react";

function StatusPill({ value }) {
  if (value == null || value === "") return <span className="status-pill">—</span>;
  const label = String(value);
  return <span className={`status-pill ${label}`}>{label.replaceAll("_", " ")}</span>;
}

function evidenceText(evidence) {
  if (evidence == null || evidence === "") return "";
  if (typeof evidence === "string") return evidence;
  if (typeof evidence === "object") {
    return evidence.matched_text || evidence.text || "";
  }
  return String(evidence);
}

export default function ProductDetail({
  product,
  onReviewFinding,
  onReviewProduct,
  onReport,
  onScanAnother,
  busy,
}) {
  const [comment, setComment] = useState("");

  if (!product) {
    return (
      <div className="panel inspection-empty-panel">
        <div className="empty-state">
          <span className="material-symbols-outlined empty-search-icon">search_insights</span>
          <h2>Inspection Details</h2>
          <p className="muted">
            Select a scan or enter a product URL/text above to inspect extracted declarations, legal rule findings, and evidence.
          </p>
        </div>
      </div>
    );
  }

  const fields = product.fields || [];
  const findings = product.findings || [];

  return (
    <div className="panel inspection-full-panel">
      {/* Top Header & Actions Bar */}
      <div className="inspection-top-bar">
        {onScanAnother && (
          <button
            type="button"
            className="btn-back-scanner"
            onClick={onScanAnother}
          >
            ← Scan Another Product
          </button>
        )}

        <div className="report-actions-row">
          <button
            type="button"
            className="btn-pdf-export"
            disabled={busy}
            onClick={() => onReport(product.id, "pdf")}
          >
            📄 Download Official PDF Report
          </button>
          <button
            type="button"
            className="btn-json-export"
            disabled={busy}
            onClick={() => onReport(product.id, "json")}
          >
            { } Export JSON
          </button>
        </div>
      </div>

      {/* Main Product Info & Score Summary Card */}
      <div className="product-summary-card">
        <div className="summary-left">
          <span className="platform-pill">{product.platform || product.input_type || "Direct URL"}</span>
          <h1 className="inspection-product-title">{product.name || "Product Inspection Record"}</h1>

          <div className="product-metadata-row">
            <span className="mono text-muted">ID: {product.id}</span>
            {product.source_url && (
              <>
                <span className="dot-sep">·</span>
                <a
                  href={product.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="source-url-link"
                >
                  {product.source_url} ↗
                </a>
              </>
            )}
          </div>

          <div className="status-badges-group">
            <StatusPill value={product.overall_status} />
            <StatusPill value={product.review_status} />
          </div>
        </div>

        <div className="compliance-score-box">
          <div className="score-label">Compliance Score</div>
          <div
            className={`score-value-large ${
              (product.compliance_score ?? 100) >= 90
                ? "score-high"
                : (product.compliance_score ?? 100) >= 60
                ? "score-mid"
                : "score-low"
            }`}
          >
            {product.compliance_score != null ? `${product.compliance_score}%` : "—"}
          </div>
          <div className="score-desc">Deterministic Metrology Rating</div>
        </div>
      </div>

      {/* Two Column Layout: Extracted Declarations & Rule Engine Findings */}
      <div className="inspection-grid">
        {/* Left Column: Extracted Mandatory Declarations */}
        <div className="inspection-col">
          <div className="col-header">
            <h3>Mandatory Statutory Declarations</h3>
            <span className="badge">{fields.length} Field{fields.length === 1 ? "" : "s"}</span>
          </div>

          {!fields.length ? (
            <p className="muted" style={{ padding: "1rem" }}>
              No declarations extracted yet for this item.
            </p>
          ) : (
            <div className="table-responsive">
              <table className="fields-table">
                <thead>
                  <tr>
                    <th>Statutory Field</th>
                    <th>Extracted Value</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {fields.map((f) => (
                    <tr key={f.id || f.field_name}>
                      <td className="field-name-cell">
                        <strong>{f.field_name}</strong>
                        {f.reason && <span className="field-reason">{f.reason}</span>}
                      </td>
                      <td className="mono field-val-cell">
                        {f.value || <span className="text-muted">Not Declared</span>}
                      </td>
                      <td>
                        <StatusPill value={f.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right Column: Rule Engine Findings */}
        <div className="inspection-col">
          <div className="col-header">
            <h3>Rule Engine Audit Findings</h3>
            <span className={`badge ${findings.length > 0 ? "badge-warn" : "badge-ok"}`}>
              {findings.length} Finding{findings.length === 1 ? "" : "s"}
            </span>
          </div>

          {!findings.length ? (
            <div className="clean-findings-box">
              <div className="clean-icon">✅</div>
              <div className="clean-text">
                <strong>No Metrology Violations Detected</strong>
                <p className="muted" style={{ margin: "0.25rem 0 0" }}>
                  All mandatory Legal Metrology rule checks passed for available declarations.
                </p>
              </div>
            </div>
          ) : (
            <div className="findings-list">
              {findings.map((f) => (
                <div className="finding-card" key={f.id}>
                  <div className="finding-card-header">
                    <div className="finding-header-left">
                      <span className={`severity-tag ${f.severity || "medium"}`}>
                        {f.severity || "Rule Violation"}
                      </span>
                      <strong className="finding-field-title">{f.field || f.rule_id}</strong>
                    </div>
                    <span className="mono rule-id-badge">{f.rule_id}</span>
                  </div>

                  <p className="finding-explanation">{f.explanation}</p>

                  {evidenceText(f.evidence) ? (
                    <div className="finding-evidence-box">
                      <span className="evidence-label">Observed Evidence:</span>
                      <span className="mono evidence-text">{evidenceText(f.evidence)}</span>
                    </div>
                  ) : null}

                  {/* Reviewer Action Bar */}
                  <div className="finding-review-bar">
                    <span className="review-label">Auditor Verdict:</span>
                    <button
                      type="button"
                      className="btn-verdict-confirm"
                      disabled={busy}
                      onClick={() => onReviewFinding(f.id, "confirm", comment)}
                    >
                      ✓ Confirm Violation
                    </button>
                    <button
                      type="button"
                      className="btn-verdict-reject"
                      disabled={busy}
                      onClick={() => onReviewFinding(f.id, "reject", comment)}
                    >
                      ✕ False Positive
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Product Level Reviewer Actions */}
          <div className="product-review-panel">
            <h4>Inspector Final Clearance</h4>
            <div className="review-input-row">
              <input
                type="text"
                className="review-comment-input"
                placeholder="Optional inspection notes, case ID, or remark…"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
              />
            </div>
            <div className="review-buttons-row">
              <button
                type="button"
                className="btn-action-pass"
                disabled={busy}
                onClick={() => onReviewProduct(product.id, "confirmed", comment)}
              >
                Approve Compliance
              </button>
              <button
                type="button"
                className="btn-action-flag"
                disabled={busy}
                onClick={() => onReviewProduct(product.id, "needs_review", comment)}
              >
                Flag for Enforcement
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
