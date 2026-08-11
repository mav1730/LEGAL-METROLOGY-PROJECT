const STEPS = [
  { id: "input", label: "Input received" },
  { id: "collect", label: "Data collection" },
  { id: "ocr", label: "OCR / text prep" },
  { id: "extract", label: "Field extraction" },
  { id: "rules", label: "Rule engine" },
  { id: "report", label: "Evidence & score" },
];

export default function ScanProgress({ active }) {
  if (!active) return null;

  return (
    <div className="panel scan-progress" style={{ marginBottom: "1rem" }}>
      <h2>Processing pipeline</h2>
      <div className="pipeline">
        {STEPS.map((step, i) => (
          <div key={step.id} className="pipeline-step active">
            <div className="pipeline-dot">
              <span className="spinner" style={{ margin: 0, borderWidth: 2 }} />
            </div>
            <div className="pipeline-label">{step.label}</div>
            {i < STEPS.length - 1 ? <div className="pipeline-line" /> : null}
          </div>
        ))}
      </div>
      <p className="muted" style={{ marginTop: "0.75rem", marginBottom: 0 }}>
        Extracting declarations and applying compliance rules…
      </p>
    </div>
  );
}
