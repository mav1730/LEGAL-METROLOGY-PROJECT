import { useCallback, useEffect, useState } from "react";
import { api } from "./api/client";
import LandingPage from "./pages/LandingPage";
import ComplianceScanPage from "./pages/ComplianceScanPage";
import RulesPage from "./pages/RulesPage";
import CatalogHistoryPage from "./pages/CatalogHistoryPage";

export default function App() {
  // Page routing state: 'home' | 'scanner' | 'rules' | 'history'
  const [currentPage, setCurrentPage] = useState(() => {
    if (window.location.hash === "#scanner") return "scanner";
    if (window.location.hash === "#rules") return "rules";
    if (window.location.hash === "#history" || window.location.hash === "#catalog") return "history";
    return "home";
  });

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
  const [disclaimer, setDisclaimer] = useState("");

  // Sync hash with browser history
  useEffect(() => {
    const handleHashChange = () => {
      if (window.location.hash === "#scanner") {
        setCurrentPage("scanner");
      } else if (window.location.hash === "#rules") {
        setCurrentPage("rules");
      } else if (window.location.hash === "#history" || window.location.hash === "#catalog") {
        setCurrentPage("history");
      } else {
        setCurrentPage("home");
      }
    };
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigateTo = (page) => {
    setCurrentPage(page);
    if (page === "scanner") {
      window.location.hash = "#scanner";
    } else if (page === "rules") {
      window.location.hash = "#rules";
    } else if (page === "history") {
      window.location.hash = "#history";
    } else {
      window.location.hash = "";
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const flash = (message) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 3500);
  };

  const refreshLists = useCallback(async () => {
    try {
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
    } catch (err) {
      console.warn("Initial data load error:", err);
    }
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
      return res;
    } catch (e) {
      const msg = e.data?.error || e.message;
      const hint = e.data?.hint ? ` — ${e.data.hint}` : "";
      setError(msg + hint);
      if (e.data?.id) {
        setSelectedId(e.data.id);
        await refreshLists();
      }
      return null;
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

  const handleReport = async (id, format = "pdf") => {
    setBusy(true);
    setError("");
    try {
      const res = await api.report(id, format);
      if (res?.meta?.id) {
        window.open(`/api/reports/${res.meta.id}`, "_blank");
      }
      flash("PDF report generated successfully");
      return res;
    } catch (e) {
      setError(e.message);
      return null;
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="main-wrapper">
      {/* Top Global Navigation Bar */}
      <header className="global-navbar">
        <div className="nav-brand" onClick={() => navigateTo("home")} style={{ cursor: "pointer" }}>
          <div className="brand-logo-mark">
            <span>M</span>
          </div>
          <div className="brand-text">
            <span className="brand-title">MetroCheck AI</span>
            <span className="brand-tag">Legal Metrology</span>
          </div>
        </div>

        <nav className="nav-links">
          <button
            type="button"
            className={`nav-link-btn ${currentPage === "home" ? "active" : ""}`}
            onClick={() => navigateTo("home")}
          >
            Home
          </button>
          <button
            type="button"
            className={`nav-link-btn ${currentPage === "scanner" ? "active" : ""}`}
            onClick={() => navigateTo("scanner")}
          >
            Compliance Scanner
          </button>
          <button
            type="button"
            className={`nav-link-btn ${currentPage === "history" ? "active" : ""}`}
            onClick={() => navigateTo("history")}
          >
            📦 Catalog &amp; Scan History
          </button>
          <button
            type="button"
            className={`nav-link-btn ${currentPage === "rules" ? "active" : ""}`}
            onClick={() => navigateTo("rules")}
          >
            📜 Metrology Rules
          </button>
          <a
            href="http://127.0.0.1:5000/demo/"
            target="_blank"
            rel="noreferrer"
            className="nav-link-btn external"
          >
            DemoMart Storefront ↗
          </a>
        </nav>
      </header>

      {/* Separate Pages */}
      {currentPage === "home" ? (
        <LandingPage
          onNavigateToScanner={() => navigateTo("scanner")}
          stats={stats}
          health={health}
        />
      ) : currentPage === "rules" ? (
        <RulesPage
          onNavigateToScanner={() => navigateTo("scanner")}
          onNavigateToHome={() => navigateTo("home")}
        />
      ) : currentPage === "history" ? (
        <CatalogHistoryPage
          products={products}
          onSelectProduct={(id) => {
            setSelectedId(id);
            navigateTo("scanner");
          }}
          onScanUrl={async (url) => {
            const res = await handleScan({ type: "url", url, html: "" });
            return res;
          }}
          onReport={handleReport}
          onNavigateToScanner={() => navigateTo("scanner")}
          onNavigateToHome={() => navigateTo("home")}
          busy={busy}
        />
      ) : (
        <ComplianceScanPage
          stats={stats}
          samples={samples}
          selectedId={selectedId}
          setSelectedId={setSelectedId}
          product={product}
          loading={loading}
          busy={busy}
          error={error}
          disclaimer={disclaimer}
          health={health}
          handleScan={handleScan}
          handleReviewFinding={handleReviewFinding}
          handleReviewProduct={handleReviewProduct}
          handleReport={handleReport}
          onBackToHome={() => navigateTo("home")}
        />
      )}

      {/* Toast alert */}
      {toast ? (
        <div className="toast toast-info" role="status">
          <span>{toast}</span>
          <button
            type="button"
            className="toast-close"
            onClick={() => setToast("")}
          >
            ×
          </button>
        </div>
      ) : null}
    </div>
  );
}
