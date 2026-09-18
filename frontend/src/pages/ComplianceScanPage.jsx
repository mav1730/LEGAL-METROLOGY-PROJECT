import React, { useState } from "react";
import StatsBar from "../components/StatsBar";
import ScanPanel from "../components/ScanPanel";
import ProductDetail from "../components/ProductDetail";

export default function ComplianceScanPage({
  stats,
  samples,
  selectedId,
  setSelectedId,
  product,
  loading,
  busy,
  error,
  disclaimer,
  health,
  handleScan,
  handleReviewFinding,
  handleReviewProduct,
  handleReport,
  onBackToHome,
}) {
  const [showScanner, setShowScanner] = useState(false);

  return (
    <div className="compliance-scan-container">
      {/* Top Header */}
      <div className="scanner-top-header">
        <div>
          <div className="breadcrumb-nav">
            {onBackToHome && (
              <button type="button" className="breadcrumb-link" onClick={onBackToHome}>
                ← Back to Home
              </button>
            )}
            <span className="breadcrumb-sep">/</span>
            <span className="breadcrumb-current">
              {product && !showScanner ? "Inspection Details" : "Compliance Scanner"}
            </span>
          </div>
          <h2 className="section-title">
            {product && !showScanner
              ? `Inspection: ${product.name || product.id}`
              : "Legal Metrology Inspection Workspace"}
          </h2>
          <p className="section-subtitle">
            {product && !showScanner
              ? "Comprehensive statutory metrology assessment, extracted declarations, and rule findings."
              : "Verify e-commerce product listings, extract declarations, and cross-match statutory metrology rules in real-time."}
          </p>
        </div>

        <div className="badge-row">
          {product && (
            <button
              type="button"
              className={`mode-toggle-btn ${showScanner ? "active" : ""}`}
              onClick={() => setShowScanner(!showScanner)}
            >
              {showScanner ? "📋 View Inspection" : "🔍 Scan Another Product"}
            </button>
          )}
          <span className="badge">
            OCR: {health?.ocr_tesseract_available ? "Tesseract ready" : "Text / Demo mode"}
          </span>
        </div>
      </div>

      {error ? <div className="error-box">{error}</div> : null}

      <div className="scanner-workspace-layout">
        <div className="scanner-main-col">
          <ScanPanel samples={samples} onScan={handleScan} loading={loading} />
          {product ? (
            <div className="full-width-inspection-wrap" style={{ marginTop: "1.25rem" }}>
              <ProductDetail
                product={product}
                busy={busy}
                onReviewFinding={handleReviewFinding}
                onReviewProduct={handleReviewProduct}
                onReport={handleReport}
                onScanAnother={() => {
                  setShowScanner(true);
                  window.scrollTo({ top: 0, behavior: "smooth" });
                }}
              />
            </div>
          ) : null}
        </div>
        <aside className="scanner-sidebar-col">
          <StatsBar stats={stats} />
        </aside>
      </div>
    </div>
  );
}
