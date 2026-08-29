import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Activity, CheckCircle, AlertTriangle, ShieldCheck } from "lucide-react";
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

  const titleText = "Legal Metrology".split(" ");
  const titleText2 = "Compliance Checker".split(" ");

  return (
    <motion.div className="app-shell" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
      <header className="topbar">
        <div className="brand">
          <h1>
            {titleText.map((word, i) => (
              <motion.span
                key={i}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
                style={{ display: "inline-block", marginRight: "0.25em" }}
              >
                {word}
              </motion.span>
            ))}
            <br />
            {titleText2.map((word, i) => (
              <motion.span
                key={i}
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: (titleText.length + i) * 0.1, duration: 0.5 }}
                style={{ display: "inline-block", marginRight: "0.25em" }}
              >
                {word}
              </motion.span>
            ))}
          </h1>
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}>
            AI/OCR-assisted first-pass screening for e-commerce product declarations — evidence-backed, human-reviewed.
          </motion.p>
        </div>
        <div className="badge-row">
          <span className={`badge ${health?.ok ? "live" : ""}`}>
            {health?.ok ? <CheckCircle size={14} style={{display:'inline', verticalAlign:'text-bottom', marginRight:'4px'}}/> : <AlertTriangle size={14} style={{display:'inline', verticalAlign:'text-bottom', marginRight:'4px'}}/>}
            API {health?.ok ? "ONLINE" : "OFFLINE"}
          </span>
          <span className="badge">
            <Activity size={14} style={{display:'inline', verticalAlign:'text-bottom', marginRight:'4px'}}/>
            OCR {health?.ocr_tesseract_available ? "READY" : "TEXT MODE"}
          </span>
          <span className="badge">
            <ShieldCheck size={14} style={{display:'inline', verticalAlign:'text-bottom', marginRight:'4px'}}/>
            DECISION-SUPPORT
          </span>
        </div>
      </header>

      <motion.div 
        className="disclaimer"
        initial={{ y: 10, opacity: 0 }} 
        animate={{ y: 0, opacity: 1 }} 
        transition={{ delay: 0.7 }}
      >
        {disclaimer}
      </motion.div>

      {error ? (
        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="error-box">
          {error}
        </motion.div>
      ) : null}

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }}>
        <StatsBar stats={stats} />
      </motion.div>

      {loading ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="panel" style={{ marginBottom: "2rem" }}>
          <h2>Processing pipeline</h2>
          <p className="muted" style={{ margin: 0 }}>
            <span className="spinner" />
            Collecting data → extracting fields → applying rules → attaching
            evidence…
          </p>
        </motion.div>
      ) : null}

      <div className="layout">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.9 }}>
          <ScanPanel samples={samples} onScan={handleScan} loading={loading} />
          <ProductList
            products={products}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
        </motion.div>
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 1.0 }}>
          <ProductDetail
            product={product}
            onReviewFinding={handleReviewFinding}
            onReviewProduct={handleReviewProduct}
            onReport={handleReport}
            busy={busy}
          />
        </motion.div>
      </div>

      {toast ? (
        <div className="toast toast-info" role="status">
          <span>{toast}</span>
          <button type="button" className="toast-close" onClick={() => setToast("")}>
            ×
          </button>
        </div>
      ) : null}
    </motion.div>
  );
}
