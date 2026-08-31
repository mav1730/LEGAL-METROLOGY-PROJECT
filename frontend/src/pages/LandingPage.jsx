import React from "react";
import HeroLanding from "../components/HeroLanding";

export default function LandingPage({ onNavigateToScanner, stats, health }) {
  return (
    <div className="landing-page-container">
      <HeroLanding onRunCheck={onNavigateToScanner} />

      {/* Overview Stats bar */}
      {stats && (
        <section className="landing-stats-section">
          <div className="stats-container-grid">
            <div className="stat-card">
              <span className="stat-num">{stats.products_scanned ?? 0}</span>
              <span className="stat-label">Products Audited</span>
            </div>
            <div className="stat-card">
              <span className="stat-num stat-highlight">
                {stats.average_score != null ? `${stats.average_score}%` : "—"}
              </span>
              <span className="stat-label">Average Compliance Score</span>
            </div>
            <div className="stat-card">
              <span className="stat-num stat-warn">{stats.potential_issues ?? 0}</span>
              <span className="stat-label">Potential Issues Flagged</span>
            </div>
            <div className="stat-card">
              <span className="stat-num stat-ok">{stats.confirmed ?? 0}</span>
              <span className="stat-label">Reviewed &amp; Cleared</span>
            </div>
          </div>
        </section>
      )}

      {/* Feature Pillars */}
      <section className="features-grid-section">
        <div className="feature-card">
          <div className="feature-icon">🔍</div>
          <h3>Multi-Source Extraction</h3>
          <p className="muted">
            Seamlessly scan live Amazon/Flipkart URLs, extract text with local scraper, or perform OCR on packaging photos with Tesseract OCR.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">⚖️</div>
          <h3>Deterministic Legal Metrology Engine</h3>
          <p className="muted">
            Evaluates 21 statutory rules under The Legal Metrology Act, 2009 and Packaged Commodities (LMPC) Rules, 2011 including Rule 6(10) for E-Commerce.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📄</div>
          <h3>Automated Audit PDF Reports</h3>
          <p className="muted">
            Generate printable, court-ready compliance audit sheets complete with exact rule citations, extracted declarations, and review states.
          </p>
        </div>
      </section>
    </div>
  );
}
