export default function ProductList({ products, selectedId, onSelect }) {
  return (
    <div className="panel" style={{ marginTop: "1rem" }}>
      <h2>Recent scans</h2>
      {!products?.length ? (
        <p className="muted">No scans yet. Run a demo sample to get started.</p>
      ) : (
        <ul className="product-list">
          {products.map((p) => (
            <li
              key={p.id}
              className={selectedId === p.id ? "active" : ""}
              onClick={() => onSelect(p.id)}
            >
              <div className="name">{p.name || p.id}</div>
              <div className="meta">
                <span className={`status-pill ${p.overall_status || ""}`}>
                  {p.overall_status || "—"}
                </span>{" "}
                score {p.compliance_score ?? "—"} · {p.input_type} ·{" "}
                {p.review_status}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
