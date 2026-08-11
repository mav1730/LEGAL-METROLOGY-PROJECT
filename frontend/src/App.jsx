import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client";
import StatsBar from "./components/StatsBar";
import ScanPanel from "./components/ScanPanel";
import ProductList from "./components/ProductList";
import ProductDetail from "./components/ProductDetail";

export default function App() {
  const [stats, setStats] = useState(null);
  const [samples, setSamples] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [health, setHealth] = useState(null);
  const [disclaimer, setDisclaimer] = useState(
    "Decision-support only — not a legal authority."
  );

  const flash = (message) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 3500);
  };

  const refreshLists = useCallback(async () => {
    const [s, p, h, sm] = await Promise.all([
      api.stats(),
      api.products(),
      api.health(),
      api.samples(),
    ]);
    setStats(s.stats);
    setProducts(p.products || []);
    setHealth(h);
    setSamples(sm.samples || []);
    if (s.disclaimer) setDisclaimer(s.disclaimer);
  }, []);

  const loadProduct = useCallback(async (id) => {
    if (!id) {
      setProduct(null);
      return;
    }
    const res = await api.product(id);
    setProduct(res.product);
    if (res.disclaimer) setDisclaimer(res.disclaimer);
  }, []);

  useEffect(() => {
    refreshLists().catch((e) => setError(e.message));
  }, [refreshLists]);

  useEffect(() => {
    loadProduct(selectedId).catch((e) => setError(e.message));
  }, [selectedId, loadProduct]);

  const handleScan = async (payload) => {
    setLoading(true);
    setError("");
    try {
      let res;
      if (payload.type === "sample") {
        res = await api.scanSample(payload.sample_id);
      } else if (payload.type === "url") {
        res = await api.scanUrl(payload.url, payload.html || "");
      } else if (payload.type === "text") {
        res = await api.scanText({
          page_text: payload.page_text,
          ocr_text: payload.ocr_text,
        });
      } else if (payload.type === "image") {
        res = await api.scanImage(payload.file);
      } else {
        throw new Error("Unknown scan type");
      }

      const id = res.id || res.product?.id;
      if (id) {
        setSelectedId(id);
        await refreshLists();
        await loadProduct(id);
        if (res.ok !== false) {
          const n = res.findings?.length ?? 0;
          const score = res.compliance_score ?? "—";
          flash(
            n === 0
              ? `Scan complete · score ${score} · no potential issues`
              : `Scan complete · score ${score} · ${n} finding(s)`
          );
        }
      }
      if (res.ok === false && res.error) {
        setError(res.error + (res.hint ? ` — ${res.hint}` : ""));
      }
      if (res.disclaimer) setDisclaimer(res.disclaimer);
    } catch (e) {
      const msg = e.data?.error || e.message;
      const hint = e.data?.hint ? ` — ${e.data.hint}` : "";
      setError(msg + hint);
      if (e.data?.id) {
        setSelectedId(e.data.id);
        await refreshLists();
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReviewFinding = async (id, action, comment) => {
    setBusy(true);
    setError("");
    try {
      await api.reviewFinding(id, action, comment);
      await refreshLists();
      await loadProduct(selectedId);
      flash(`Finding marked as ${action.replaceAll("_", " ")}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const handleReviewProduct = async (id, status, comment) => {
    setBusy(true);
    setError("");
    try {
      await api.reviewProduct(id, status, comment);
      await refreshLists();
      await loadProduct(id);
      flash(`Product review: ${status.replaceAll("_", " ")}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const handleReport = async (id, format) => {
    setBusy(true);
    setError("");
    try {
      const res = await api.report(id, format);
      if (format === "pdf" && res.meta?.id) {
        window.open(`/api/reports/${res.meta.id}`, "_blank");
        flash("PDF report generated");
      } else {
        flash("JSON report generated");
      }
      return res;
    } catch (e) {
      setError(e.message);
      return null;
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <h1>Legal Metrology Compliance Checker</h1>
          <p>
            AI/OCR-assisted first-pass screening for e-commerce product
            declarations — evidence-backed, human-reviewed.
          </p>
        </div>
        <div className="badge-row">
          <span className={`badge ${health?.ok ? "live" : ""}`}>
            API {health?.ok ? "online" : "offline"}
          </span>
          <span className="badge">
            OCR{" "}
            {health?.ocr_tesseract_available
              ? "Tesseract ready"
              : "text/samples mode"}
          </span>
          <span className="badge">Decision-support</span>
        </div>
      </header>

      <div className="disclaimer">{disclaimer}</div>

      {error ? <div className="error-box">{error}</div> : null}

      <StatsBar stats={stats} />

      {loading ? (
        <div className="panel" style={{ marginBottom: "1rem" }}>
          <h2>Processing pipeline</h2>
          <p className="muted" style={{ margin: 0 }}>
            <span className="spinner" />
            Collecting data → extracting fields → applying rules → attaching
            evidence…
          </p>
        </div>
      ) : null}

      <div className="layout">
        <div>
          <ScanPanel samples={samples} onScan={handleScan} loading={loading} />
          <ProductList
            products={products}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </div>
        <ProductDetail
          product={product}
          onReviewFinding={handleReviewFinding}
          onReviewProduct={handleReviewProduct}
          onReport={handleReport}
          busy={busy}
        />
      </div>

      {toast ? (
        <div className="toast toast-info" role="status">
          <span>{toast}</span>
          <button type="button" className="toast-close" onClick={() => setToast("")}>
            ×
          </button>
        </div>
      ) : null}
    </div>
  );
}
