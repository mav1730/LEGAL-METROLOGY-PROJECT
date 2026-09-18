import { useState } from "react";

export default function ScanPanel({ samples, onScan, loading }) {
  const [tab, setTab] = useState("url");
  const [url, setUrl] = useState("");
  const [pageHtml, setPageHtml] = useState("");
  const [pageText, setPageText] = useState("");
  const [ocrText, setOcrText] = useState("");
  const [file, setFile] = useState(null);

  const normalizeUrl = (raw) => {
    const u = (raw || "").trim().replace(/^['"]|['"]$/g, "");
    if (!u) return "";
    if (u.startsWith("/demo/")) return `http://127.0.0.1:5000${u}`;
    if (/^(127\.0\.0\.1|localhost)/i.test(u)) return `http://${u}`;
    if (!/^https?:\/\//i.test(u)) return `https://${u}`;
    return u;
  };

  const submit = async () => {
    if (tab === "url") await onScan({ type: "url", url: normalizeUrl(url), html: pageHtml });
    else if (tab === "text")
      await onScan({ type: "text", page_text: pageText, ocr_text: ocrText });
    else if (tab === "image") await onScan({ type: "image", file });
  };

  return (
    <div className="panel scanner-centered-panel">
      <div className="scanner-header-center">
        <h2>Automated Compliance Inspection</h2>
        <p className="muted" style={{ margin: 0 }}>
          Select your inspection method to extract mandatory declarations and check statutory metrology rules.
        </p>
      </div>

      <div className="tabs tabs-centered">
        {[
          ["url", "🔗 Product URL"],
          ["text", "📝 Paste Text"],
          ["image", "📷 Image OCR"],
        ].map(([id, label]) => (
          <button
            key={id}
            type="button"
            className={`tab-btn ${tab === id ? "active" : ""}`}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "url" && (
        <div className="stack scanner-form-stack">
          <label htmlFor="url" className="form-label-highlight">
            Product Listing URL (Amazon / Flipkart / DemoMart)
          </label>
          <div className="url-input-wrapper">
            <input
              id="url"
              type="text"
              className="url-input-large"
              placeholder="Paste a DemoMart / Amazon / Flipkart product link"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  submit();
                }
              }}
            />
            <button
              type="button"
              className="btn-scan-main"
              onClick={submit}
              disabled={loading || (!url.trim() && !pageHtml.trim())}
            >
              {loading ? <span className="spinner" /> : "⚡ "}
              {loading ? "Inspecting..." : "Scan Product URL"}
            </button>
          </div>

          <details className="advanced-html-toggle">
            <summary className="muted" style={{ cursor: "pointer", fontSize: "0.85rem" }}>
              ▶ Optional: Paste raw HTML / product specifications (if website blocks automated fetch)
            </summary>
            <div style={{ marginTop: "0.65rem" }}>
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
            </div>
          </details>
        </div>
      )}

      {tab === "text" && (
        <div className="stack scanner-form-stack">
          <label htmlFor="page" className="form-label-highlight">
            Page / Listing Raw Text
          </label>
          <textarea
            id="page"
            rows="6"
            value={pageText}
            onChange={(e) => setPageText(e.target.value)}
            placeholder="Paste product page text, specifications, description from an Amazon, Flipkart, or brand store listing…"
          />

          <label htmlFor="ocr" className="form-label-highlight">
            OCR / Packaging Text (Optional)
          </label>
          <textarea
            id="ocr"
            rows="4"
            value={ocrText}
            onChange={(e) => setOcrText(e.target.value)}
            placeholder="Paste packaging label text or OCR transcript here…"
          />

          <button
            type="button"
            className="btn-scan-main"
            onClick={submit}
            disabled={loading || (!pageText.trim() && !ocrText.trim())}
          >
            {loading ? <span className="spinner" /> : "⚡ "}
            {loading ? "Inspecting Text..." : "Inspect Raw Text"}
          </button>
        </div>
      )}

      {tab === "image" && (
        <div className="stack scanner-form-stack">
          <label htmlFor="image" className="form-label-highlight">
            Packaging Image / Label Photo
          </label>
          <p className="muted" style={{ margin: "0 0 0.5rem", fontSize: "0.85rem" }}>
            Upload a clear photo of the product packaging (PDP, side panel, or MRP sticker).
          </p>
          <input
            id="image"
            type="file"
            accept="image/*"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />

          <button
            type="button"
            className="btn-scan-main"
            onClick={submit}
            disabled={loading || !file}
          >
            {loading ? <span className="spinner" /> : "📷 "}
            {loading ? "Performing OCR..." : "Scan Image (OCR)"}
          </button>
        </div>
      )}
    </div>
  );
}
