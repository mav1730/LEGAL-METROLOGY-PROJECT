import { useState } from "react";

function StatusPill({ value }) {
  if (!value) return <span className="status-pill">—</span>;
  return <span className={`status-pill ${value}`}>{value.replaceAll("_", " ")}</span>;
}

export default function ProductDetail({
  product,
  onReviewFinding,
  onReviewProduct,
  onReport,
  busy,
}) {
  const [comment, setComment] = useState("");
  const [reportJson, setReportJson] = useState(null);

  if (!product) {
    return (
      <div className="panel">
        <div className="empty-state">
          <h2>Inspection detail</h2>
          <p>Select a scan or run a demo sample to inspect fields, findings, and evidence.</p>
        </div>
      </div>
    );
  }

  const fields = product.fields || [];
  const findings = product.findings || [];

  return (
    <div className="panel">
      <div className="detail-header">
        <div>
          <h2>{product.name || "Product"}</h2>
          <p className="muted mono" style={{ margin: "0.35rem 0 0" }}>
            {product.id}
            {product.source_url ? ` · ${product.source_url}` : ""}
          </p>
          <div className="row" style={{ marginTop: "0.55rem" }}>
            <StatusPill value={product.overall_status} />
            <StatusPill value={product.review_status} />
            <span className="badge">{product.platform || "—"}</span>
            <span className="badge">{product.input_type || "—"}</span>
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div className="muted">Compliance score (priority only)</div>
          <div className="score">{product.compliance_score ?? "—"}</div>
        </div>
      </div>

      <h3 style={{ margin: "0 0 0.5rem", fontSize: "0.95rem" }}>Extracted fields</h3>
      <table className="fields-table">
        <thead>
          <tr>
            <th>Field</th>
            <th>Value</th>
            <th>Status</th>
            <th>Evidence</th>
          </tr>
        </thead>
        <tbody>
          {fields.map((f) => (
            <tr key={f.id || f.field_name || f.name}>
              <td>{(f.field_name || f.name || "").replaceAll("_", " ")}</td>
              <td>{f.value || "—"}</td>
              <td>
                <StatusPill value={f.status} />
                {f.confidence != null && f.status === "detected" ? (
                  <div className="muted mono">{Number(f.confidence).toFixed(2)}</div>
                ) : null}
              </td>
              <td className="mono">
                {f.evidence?.matched_text || f.reason || "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3 style={{ margin: "0.5rem 0", fontSize: "0.95rem" }}>
        Findings ({findings.length})
      </h3>
      {!findings.length ? (
        <p className="muted">
          No configured potential issues in available data. This is{" "}
          <strong>not</strong> a legal clearance certificate.
        </p>
      ) : (
        findings.map((f) => (
          <div className="finding-card" key={f.id}>
            <h4>
              <StatusPill value={f.status} /> {f.rule_id}{" "}
              <span className="muted">· {f.field}</span>{" "}
              <span className="badge">{f.severity}</span>
            </h4>
            <p>{f.explanation}</p>
            {f.evidence?.matched_text ? (
              <p className="mono">Evidence: {f.evidence.matched_text}</p>
            ) : null}
            {f.alternatives?.length ? (
              <p className="mono">Alternatives: {f.alternatives.join(" | ")}</p>
            ) : null}
            {f.reviewer_action ? (
              <p>
                Reviewer: <strong>{f.reviewer_action}</strong>
                {f.reviewer_comment ? ` — ${f.reviewer_comment}` : ""}
              </p>
            ) : (
              <div className="row" style={{ marginTop: "0.5rem" }}>
                <button
                  type="button"
                  className="ok"
                  disabled={busy}
                  onClick={() => onReviewFinding(f.id, "confirm", comment)}
                >
                  Confirm
                </button>
                <button
                  type="button"
                  className="danger"
                  disabled={busy}
                  onClick={() => onReviewFinding(f.id, "reject", comment)}
                >
                  Reject
                </button>
                <button
                  type="button"
                  className="warn"
                  disabled={busy}
                  onClick={() => onReviewFinding(f.id, "needs_review", comment)}
                >
                  Needs review
                </button>
              </div>
            )}
          </div>
        ))
      )}

      <label htmlFor="rev-comment" style={{ marginTop: "0.75rem" }}>
        Reviewer comment (optional)
      </label>
      <textarea
        id="rev-comment"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder="Notes for the audit trail…"
      />

      <div className="row">
        <button
          type="button"
          className="secondary"
          disabled={busy}
          onClick={() => onReviewProduct(product.id, "confirmed", comment)}
        >
          Mark product confirmed
        </button>
        <button
          type="button"
          className="secondary"
          disabled={busy}
          onClick={() => onReviewProduct(product.id, "needs_review", comment)}
        >
          Mark needs review
        </button>
        <button
          type="button"
          disabled={busy}
          onClick={async () => {
            const r = await onReport(product.id, "json");
            setReportJson(r);
          }}
        >
          Generate JSON report
        </button>
        <button
          type="button"
          className="secondary"
          disabled={busy}
          onClick={() => onReport(product.id, "pdf")}
        >
          Generate PDF report
        </button>
      </div>

      {reportJson?.report ? (
        <pre
          className="mono"
          style={{
            marginTop: "1rem",
            maxHeight: 240,
            overflow: "auto",
            background: "var(--bg)",
            padding: "0.75rem",
            borderRadius: 10,
            border: "1px solid var(--border)",
            fontSize: "0.75rem",
          }}
        >
          {JSON.stringify(reportJson.report, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}
