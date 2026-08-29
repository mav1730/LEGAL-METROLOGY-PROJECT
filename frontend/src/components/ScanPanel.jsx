import { useState } from "react";
import { Scan } from "lucide-react";

const DEMO_PRODUCTS = [
  {
    label: "Honey (complete → score ~100)",
    url: "http://127.0.0.1:5000/demo/dp/hive-organic-honey-500g",
  },
  {
    label: "Oil (missing origin)",
    url: "http://127.0.0.1:5000/demo/dp/pure-groundnut-oil-1l",
  },
  {
    label: "Chips (sparse listing)",
    url: "http://127.0.0.1:5000/demo/dp/crunchyco-spicy-chips-50g",
  },
  {
    label: "Tea bags (complete)",
    url: "http://127.0.0.1:5000/demo/dp/assam-classic-tea-bags-100g",
  },
];

export default function ScanPanel({ samples, onScan, loading }) {
  const [tab, setTab] = useState("url");
  const [url, setUrl] = useState("");
  const [pageHtml, setPageHtml] = useState("");
  const [pageText, setPageText] = useState("");
  const [ocrText, setOcrText] = useState("");
  const [file, setFile] = useState(null);

  const submit = async () => {
    if (tab === "url") await onScan({ type: "url", url, html: pageHtml });
    else if (tab === "text")
      await onScan({ type: "text", page_text: pageText, ocr_text: ocrText });
    else if (tab === "image") await onScan({ type: "image", file });
  };

  return (
    <div className="panel">
      <h2>
        <Scan size={20} style={{ marginRight: "0.5rem" }} />
        New Scan
      </h2>
      <div className="tabs">
        {[
          ["url", "Product URL"],
          ["text", "Paste text"],
          ["image", "Image OCR"],
          ["sample", "Built-in samples"],
        ].map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={tab === id ? "active" : ""}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "url" && (
        <div className="stack">
          <label htmlFor="url">Real product URL (Amazon / Flipkart / DemoMart)</label>
          <input
            id="url"
            type="url"
            placeholder="https://www.amazon.in/.../dp/XXXXXXXX  or  http://127.0.0.1:5000/demo/dp/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />

          <p className="muted" style={{ marginTop: 0 }}>
            <b>DemoMart (always works — Amazon-style pages with images):</b>
          </p>
          <div className="sample-grid" style={{ marginBottom: "0.75rem" }}>
            {DEMO_PRODUCTS.map((d) => (
              <button
                key={d.url}
                type="button"
                className="sample-btn"
                disabled={loading}
                onClick={() => {
                  setUrl(d.url);
                  onScan({ type: "url", url: d.url, html: "" });
                }}
              >
                <strong>{d.label}</strong>
                <span className="mono" style={{ fontSize: "0.72rem" }}>
                  {d.url}
                </span>
              </button>
            ))}
          </div>
          <p className="muted">
            <a href="http://127.0.0.1:5000/demo/" target="_blank" rel="noreferrer">
              Open DemoMart storefront ↗
            </a>
          </p>

          <label htmlFor="html">
            Optional: paste page HTML / product details (if Amazon blocks the server)
          </label>
          <textarea
            id="html"
            value={pageHtml}
            onChange={(e) => setPageHtml(e.target.value)}
            placeholder={
              "If auto-fetch fails: open the real Amazon product in Chrome →\n" +
              "copy Product details / Important information text (or Save Page HTML) → paste here.\n" +
              "Keep the real product URL above for the report."
            }
          />

          <button
            type="button"
            onClick={submit}
            disabled={loading || (!url.trim() && !pageHtml.trim())}
          >
            {loading ? <span className="spinner" /> : null}
            Scan product URL
          </button>
          <p className="muted" style={{ fontSize: "0.8rem" }}>
            Amazon/Flipkart often block data-centre scrapers with CAPTCHA. That is their
            anti-bot system — not a broken demo. Use DemoMart for reliable viva demos, or
            paste details from a real page to still test real product content.
          </p>
        </div>
      )}

      {tab === "sample" && (
        <div className="sample-grid">
          <p className="muted">
            Offline text samples (no URL). Prefer <b>Product URL + DemoMart</b> for URL demos.
          </p>
          {(samples || []).map((s) => (
            <button
              key={s.id}
              type="button"
              className="sample-btn"
              disabled={loading}
              onClick={() => onScan({ type: "sample", sample_id: s.id })}
            >
              <strong>{s.name}</strong>
              <span>{s.description}</span>
            </button>
          ))}
        </div>
      )}

      {tab === "text" && (
        <div className="stack">
          <label htmlFor="page">Page / listing text</label>
          <textarea
            id="page"
            value={pageText}
            onChange={(e) => setPageText(e.target.value)}
            placeholder="Paste product page text, specs, description from a real Amazon/Flipkart listing…"
          />
          <label htmlFor="ocr">OCR / packaging text (optional)</label>
          <textarea
            id="ocr"
            value={ocrText}
            onChange={(e) => setOcrText(e.target.value)}
            placeholder="Paste text read from packaging…"
          />
          <button
            type="button"
            onClick={submit}
            disabled={loading || (!pageText.trim() && !ocrText.trim())}
          >
            {loading ? <span className="spinner" /> : null}
            Extract &amp; check
          </button>
        </div>
      )}

      {tab === "image" && (
        <div className="stack">
          <label htmlFor="img">Packaging image</label>
          <input
            id="img"
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <p className="muted">
            Requires free Tesseract OCR on the server. Without it, use paste-text or DemoMart.
          </p>
          <button type="button" onClick={submit} disabled={loading || !file}>
            {loading ? <span className="spinner" /> : null}
            OCR &amp; check
          </button>
        </div>
      )}
    </div>
  );
}
