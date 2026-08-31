import React, { useState, useMemo } from "react";
import DEMOMART_CATALOG from "../data/demomartCatalog";

const CATEGORIES = [
  "All",
  "Electronics",
  "Footwear",
  "Clothing & Apparel",
  "Grocery & Gourmet Foods",
  "Beauty & Personal Care",
];

function formatDateTime(isoString) {
  if (!isoString) return null;
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
    });
  } catch {
    return isoString;
  }
}

export default function CatalogHistoryPage({
  products = [],
  onSelectProduct,
  onScanUrl,
  onReport,
  onNavigateToScanner,
  onNavigateToHome,
  busy,
}) {
  const [activeTab, setActiveTab] = useState("catalog"); // 'catalog' | 'history'
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [downloadingId, setDownloadingId] = useState(null);

  // Map database scanned products by source_url or slug for instant lookup
  const scannedMap = useMemo(() => {
    const map = {};
    products.forEach((p) => {
      if (p.source_url) {
        map[p.source_url.toLowerCase()] = p;
      }
      if (p.name) {
        map[p.name.toLowerCase()] = p;
      }
    });
    return map;
  }, [products]);

  // Filter Catalog items
  const filteredCatalog = useMemo(() => {
    return DEMOMART_CATALOG.filter((item) => {
      const matchesCategory =
        selectedCategory === "All" || item.category === selectedCategory;

      const q = searchTerm.toLowerCase();
      const matchesSearch =
        item.title.toLowerCase().includes(q) ||
        item.brand.toLowerCase().includes(q) ||
        item.asin.toLowerCase().includes(q) ||
        item.subCategory.toLowerCase().includes(q) ||
        item.scenarioLabel.toLowerCase().includes(q) ||
        (item.countryOfOrigin && item.countryOfOrigin.toLowerCase().includes(q));

      return matchesCategory && matchesSearch;
    });
  }, [searchTerm, selectedCategory]);

  // Filter Live DB History items
  const filteredHistory = useMemo(() => {
    return products.filter((p) => {
      const q = searchTerm.toLowerCase();
      return (
        (p.name && p.name.toLowerCase().includes(q)) ||
        (p.id && p.id.toLowerCase().includes(q)) ||
        (p.source_url && p.source_url.toLowerCase().includes(q)) ||
        (p.overall_status && p.overall_status.toLowerCase().includes(q)) ||
        (p.platform && p.platform.toLowerCase().includes(q))
      );
    });
  }, [products, searchTerm]);

  const handleDownloadPdf = async (productId, itemUrl) => {
    if (productId) {
      setDownloadingId(productId);
      try {
        await onReport(productId, "pdf");
      } finally {
        setDownloadingId(null);
      }
    } else if (itemUrl) {
      setDownloadingId(itemUrl);
      try {
        // Trigger a scan and then generate PDF
        const res = await onScanUrl(itemUrl);
        const newId = res?.id || res?.product?.id;
        if (newId) {
          await onReport(newId, "pdf");
        }
      } finally {
        setDownloadingId(null);
      }
    }
  };

  const handleInspect = async (item) => {
    const existing = scannedMap[item.url.toLowerCase()];
    if (existing?.id) {
      onSelectProduct(existing.id);
      if (onNavigateToScanner) onNavigateToScanner();
    } else {
      await onScanUrl(item.url);
      if (onNavigateToScanner) onNavigateToScanner();
    }
  };

  return (
    <div className="history-page-container">
      {/* Top Breadcrumb & Hero */}
      <div className="history-hero-header">
        <div className="breadcrumb-nav">
          {onNavigateToHome && (
            <button type="button" className="breadcrumb-link" onClick={onNavigateToHome}>
              ← Back to Home
            </button>
          )}
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-current">Scan History &amp; Verified Catalog</span>
        </div>

        <div className="history-hero-title-row">
          <div>
            <h1 className="history-main-title">DemoMart Verified Catalog &amp; Scan History</h1>
            <p className="history-subtitle">
              Browse pre-audited product listings with full metrology metadata, inspect historical scan results with timestamps, and download official PDF compliance reports.
            </p>
          </div>

          <div className="history-stats-badge-group">
            <div className="history-stat-mini">
              <span className="mini-num">{DEMOMART_CATALOG.length}</span>
              <span className="mini-lbl">Catalog Items</span>
            </div>
            <div className="history-stat-mini">
              <span className="mini-num">{products.length}</span>
              <span className="mini-lbl">Scanned Audits</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Tab Switcher */}
      <div className="history-tabs-nav">
        <button
          type="button"
          className={`history-tab-btn ${activeTab === "catalog" ? "active" : ""}`}
          onClick={() => setActiveTab("catalog")}
        >
          <span className="material-symbols-outlined tab-icon">verified</span>
          DemoMart Verified Catalog ({DEMOMART_CATALOG.length})
        </button>
        <button
          type="button"
          className={`history-tab-btn ${activeTab === "history" ? "active" : ""}`}
          onClick={() => setActiveTab("history")}
        >
          <span className="material-symbols-outlined tab-icon">history</span>
          All Scanned Inspection Records ({products.length})
        </button>
      </div>

      {/* Search & Category Filter Bar */}
      <div className="history-controls-card">
        <div className="history-search-row">
          <div className="history-search-box">
            <span className="material-symbols-outlined search-icon">search</span>
            <input
              type="text"
              className="history-search-input"
              placeholder={
                activeTab === "catalog"
                  ? "Search by Title, ASIN, Brand, Country of Origin, or Sub-Category..."
                  : "Search scanned audit history by Name, ID, URL, or Compliance Status..."
              }
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            {searchTerm && (
              <button
                type="button"
                className="search-clear-btn"
                onClick={() => setSearchTerm("")}
              >
                ×
              </button>
            )}
          </div>
        </div>

        {activeTab === "catalog" && (
          <div className="category-pills-row" style={{ marginTop: "1rem" }}>
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                type="button"
                className={`category-pill-btn ${selectedCategory === cat ? "active" : ""}`}
                onClick={() => setSelectedCategory(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        )}

        <div className="search-meta-row" style={{ padding: "0.75rem 0 0" }}>
          <p className="search-result-count">
            Showing{" "}
            <strong className="highlight-count">
              {activeTab === "catalog" ? filteredCatalog.length : filteredHistory.length}
            </strong>{" "}
            {activeTab === "catalog" ? "verified products" : "scanned audit records"}
            {searchTerm && ` for "${searchTerm}"`}
            {selectedCategory !== "All" && activeTab === "catalog" && ` in [${selectedCategory}]`}
          </p>
          <a
            href="http://127.0.0.1:5000/demo/"
            target="_blank"
            rel="noreferrer"
            className="demomart-store-link"
          >
            Open Live DemoMart Storefront ↗
          </a>
        </div>
      </div>

      {/* Tab 1: DemoMart Verified Catalog Grid */}
      {activeTab === "catalog" && (
        <div className="catalog-grid">
          {filteredCatalog.length === 0 ? (
            <div className="panel empty-search-state" style={{ gridColumn: "1 / -1" }}>
              <span className="material-symbols-outlined empty-icon">search_off</span>
              <h3>No catalog products match your search</h3>
              <p className="muted">Try clearing the search query or selecting 'All' categories.</p>
              <button
                type="button"
                className="btn-back-scanner"
                style={{ marginTop: "1rem" }}
                onClick={() => {
                  setSearchTerm("");
                  setSelectedCategory("All");
                }}
              >
                Reset Filters
              </button>
            </div>
          ) : (
            filteredCatalog.map((item) => {
              const matchedScan = scannedMap[item.url.toLowerCase()];
              const isScanned = !!matchedScan;
              const scanDate = matchedScan ? formatDateTime(matchedScan.created_at) : null;
              const score = matchedScan ? matchedScan.compliance_score : item.expectedScore;
              const status = matchedScan ? matchedScan.overall_status : item.status;
              const isDownloading = downloadingId === (matchedScan?.id || item.url);

              return (
                <div key={item.asin} className="catalog-card">
                  <div className="catalog-card-top">
                    <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start", marginBottom: "0.75rem" }}>
                      {item.image && (
                        <div style={{
                          width: "72px",
                          height: "72px",
                          flexShrink: 0,
                          borderRadius: "10px",
                          overflow: "hidden",
                          background: "#181824",
                          border: "1px solid rgba(255,255,255,0.08)",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center"
                        }}>
                          <img
                            src={item.image}
                            alt={item.title}
                            style={{ width: "100%", height: "100%", objectFit: "cover" }}
                            onError={(e) => {
                              e.currentTarget.style.display = "none";
                            }}
                          />
                        </div>
                      )}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div className="catalog-badge-row" style={{ marginBottom: "0.4rem" }}>
                          <span className="catalog-category-tag">{item.category}</span>
                          <span className="catalog-asin-pill mono">{item.asin}</span>
                        </div>
                        <h3 className="catalog-item-title" style={{ fontSize: "0.98rem", lineHeight: "1.35", margin: 0 }}>
                          {item.title}
                        </h3>
                      </div>
                    </div>

                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                      <span
                        className={`status-pill ${
                          status === "clear_in_available_data"
                            ? "detected"
                            : "potential_issues"
                        }`}
                      >
                        {status === "clear_in_available_data" ? "PASSED (100%)" : "POTENTIAL ISSUE"}
                      </span>
                      <span className="catalog-brand" style={{ fontSize: "0.85rem" }}>Brand: <strong>{item.brand}</strong></span>
                      <span className="catalog-mrp" style={{ fontSize: "0.95rem" }}>MRP: <strong>₹{item.mrp.toLocaleString()}</strong></span>
                    </div>
                  </div>

                  {/* Metadata Specs */}
                  <div className="catalog-specs-box">
                    <div className="spec-item">
                      <span className="spec-label">Net Qty:</span>
                      <span className="spec-val mono">{item.netQuantity || "— (Missing)"}</span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Origin:</span>
                      <span className={`spec-val ${!item.countryOfOrigin ? "text-danger" : ""}`}>
                        {item.countryOfOrigin || "⚠️ Missing Origin"}
                      </span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Dates:</span>
                      <span className="spec-val">
                        {item.mfgDate ? `Mfg: ${item.mfgDate}` : "⚠️ Missing Mfg Date"}
                      </span>
                    </div>
                    <div className="spec-item">
                      <span className="spec-label">Care:</span>
                      <span className={`spec-val ${!item.customerCare ? "text-danger" : ""}`}>
                        {item.customerCare ? "✓ Declared" : "⚠️ Missing Contact"}
                      </span>
                    </div>
                  </div>

                  {/* Scanned Timestamp Info */}
                  <div className="catalog-scan-timestamp-box">
                    <div className="timestamp-left">
                      <span className="material-symbols-outlined timestamp-icon">
                        {isScanned ? "event_available" : "schedule"}
                      </span>
                      <div>
                        <span className="timestamp-label">
                          {isScanned ? "Last Scanned Timestamp:" : "Verification Status:"}
                        </span>
                        <span className="timestamp-val">
                          {isScanned ? scanDate : "Verified Test Baseline"}
                        </span>
                      </div>
                    </div>
                    <div className="score-badge-compact">
                      Score: <strong>{score != null ? `${score}%` : "—"}</strong>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="catalog-actions-row">
                    <button
                      type="button"
                      className="btn-download-pdf-card"
                      disabled={busy || isDownloading}
                      onClick={() => handleDownloadPdf(matchedScan?.id, item.url)}
                    >
                      {isDownloading ? (
                        <span className="spinner" style={{ margin: 0, width: 14, height: 14 }} />
                      ) : (
                        <span className="material-symbols-outlined" style={{ fontSize: "1rem" }}>
                          picture_as_pdf
                        </span>
                      )}
                      <span>Download PDF</span>
                    </button>

                    <button
                      type="button"
                      className="btn-inspect-card"
                      onClick={() => handleInspect(item)}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: "1rem" }}>
                        search_check
                      </span>
                      <span>Inspect</span>
                    </button>

                    <a
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-store-link"
                      title="Open Live Product Page"
                    >
                      ↗
                    </a>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Tab 2: Live Scanned History Table */}
      {activeTab === "history" && (
        <div className="history-table-container">
          {!filteredHistory.length ? (
            <div className="panel empty-search-state">
              <span className="material-symbols-outlined empty-icon">history_toggle_off</span>
              <h3>No scan records found</h3>
              <p className="muted">
                Run a product scan via Product URL, Raw Text, or Image OCR to populate the audit log.
              </p>
              {onNavigateToScanner && (
                <button
                  type="button"
                  className="btn-scan-main"
                  style={{ marginTop: "1rem" }}
                  onClick={onNavigateToScanner}
                >
                  ⚡ Open Scanner
                </button>
              )}
            </div>
          ) : (
            <div className="table-responsive">
              <table className="fields-table history-table">
                <thead>
                  <tr>
                    <th style={{ width: "28%" }}>Product Name &amp; ID</th>
                    <th style={{ width: "20%" }}>Scanned Date &amp; Time</th>
                    <th style={{ width: "12%" }}>Compliance Score</th>
                    <th style={{ width: "14%" }}>Audit Status</th>
                    <th style={{ width: "12%" }}>Input Source</th>
                    <th style={{ width: "14%", textAlign: "right" }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.map((p) => {
                    const isDownloading = downloadingId === p.id;
                    const dateFormatted = formatDateTime(p.created_at) || "Recent";
                    const score = p.compliance_score;

                    return (
                      <tr key={p.id}>
                        <td>
                          <div className="history-prod-name">
                            <strong>{p.name || p.id}</strong>
                          </div>
                          <span className="mono history-prod-id">ID: {p.id}</span>
                          {p.source_url && (
                            <div className="history-prod-url">
                              <a href={p.source_url} target="_blank" rel="noreferrer">
                                {p.source_url}
                              </a>
                            </div>
                          )}
                        </td>
                        <td>
                          <div className="history-time-cell">
                            <span className="material-symbols-outlined time-icon">
                              calendar_today
                            </span>
                            <div>
                              <div className="time-primary">{dateFormatted}</div>
                              <span className="muted" style={{ fontSize: "0.74rem" }}>
                                {p.updated_at && p.updated_at !== p.created_at
                                  ? `Updated: ${formatDateTime(p.updated_at)}`
                                  : "Initial Inspection"}
                              </span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="history-score-pill">
                            <span
                              className={`score-tag ${
                                score >= 90
                                  ? "score-pass"
                                  : score >= 60
                                  ? "score-warn"
                                  : "score-fail"
                              }`}
                            >
                              {score != null ? `${score}%` : "—"}
                            </span>
                          </div>
                        </td>
                        <td>
                          <span className={`status-pill ${p.overall_status || ""}`}>
                            {(p.overall_status || "Pending").replaceAll("_", " ")}
                          </span>
                          {p.review_status && (
                            <div className="review-sub-status">
                              Review: <strong>{p.review_status}</strong>
                            </div>
                          )}
                        </td>
                        <td>
                          <span className="badge">{p.platform || p.input_type || "Direct URL"}</span>
                        </td>
                        <td style={{ textAlign: "right" }}>
                          <div className="history-action-btn-group">
                            <button
                              type="button"
                              className="btn-download-pdf-sm"
                              disabled={busy || isDownloading}
                              title="Download PDF Audit Report"
                              onClick={() => handleDownloadPdf(p.id, null)}
                            >
                              {isDownloading ? (
                                <span className="spinner" style={{ margin: 0, width: 12, height: 12 }} />
                              ) : (
                                "📄 PDF"
                              )}
                            </button>

                            <button
                              type="button"
                              className="btn-inspect-sm"
                              title="View Full Inspection Details"
                              onClick={() => {
                                onSelectProduct(p.id);
                                if (onNavigateToScanner) onNavigateToScanner();
                              }}
                            >
                              🔍 Inspect
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
