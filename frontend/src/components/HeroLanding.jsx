import React from "react";

export default function HeroLanding({ onRunCheck }) {
  return (
    <section className="hero-section">
      <div className="hero-glow-bg"></div>
      <div className="hero-container">
        {/* Left Column: Headline & Value Prop */}
        <div className="hero-content">
          <h1 className="hero-title">
            MetroCheck AI: Legal Metrology Compliance for E-Commerce.
          </h1>

          <p className="hero-description">
            Our AI-powered platform helps e-commerce sellers automate and ensure
            complete legal metrology compliance for all packaged commodities,
            covering rules, product listings, and instant verification across
            multi-regional standards.
          </p>

          <ul className="hero-features">
            <li>
              <span className="feature-check">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </span>
              <span>Automated Listing Analysis (Check: SKU/Product Name/Weight/Details)</span>
            </li>
            <li>
              <span className="feature-check">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </span>
              <span>Real-time Compliance Reports &amp; Risk Assessment</span>
            </li>
            <li>
              <span className="feature-check">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </span>
              <span>Generated Verified Listing Labels &amp; Data Sheets</span>
            </li>
            <li>
              <span className="feature-check">
                <svg viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
              </span>
              <span>Rules-Based Matching for Multi-Regional Standards</span>
            </li>
          </ul>

          <div className="hero-cta-wrap">
            <button
              type="button"
              className="hero-cta-btn"
              onClick={onRunCheck}
            >
              Run Compliance Check
            </button>
          </div>
        </div>

        {/* Right Column: 3D Perspective Tablet UI Mockup */}
        <div className="hero-mockup-wrap">
          <div className="tablet-frame">
            {/* Sidebar */}
            <div className="mockup-sidebar">
              <div className="mockup-logo-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
              </div>
              <div className="mockup-nav-icons">
                <div className="nav-icon active">
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <rect x="3" y="3" width="7" height="7" rx="1.5" />
                    <rect x="14" y="3" width="7" height="7" rx="1.5" />
                    <rect x="14" y="14" width="7" height="7" rx="1.5" />
                    <rect x="3" y="14" width="7" height="7" rx="1.5" />
                  </svg>
                </div>
                <div className="nav-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z" />
                    <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                    <line x1="12" y1="22.08" x2="12" y2="12" />
                  </svg>
                </div>
                <div className="nav-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                    <polyline points="10 9 9 9 8 9" />
                  </svg>
                </div>
                <div className="nav-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Main Content Area */}
            <div className="mockup-content">
              {/* Top bar inside mockup */}
              <div className="mockup-topbar">
                <div className="mockup-search">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <circle cx="11" cy="11" r="8" />
                    <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  </svg>
                  <span>Search Legal Metrology Rules, SKU, or ASIN...</span>
                </div>
                <div className="mockup-user-avatar">
                  <span>LM</span>
                </div>
              </div>

              {/* KPI Cards Row */}
              <div className="mockup-kpi-row">
                <div className="mockup-kpi-card">
                  <div className="kpi-label">Active Listings</div>
                  <div className="kpi-value">1,429</div>
                  <div className="kpi-sub green">+12% this week</div>
                </div>
                <div className="mockup-kpi-card">
                  <div className="kpi-label">Compliance Rate</div>
                  <div className="kpi-value">98.4%</div>
                  <div className="kpi-sub green">Optimal Standard</div>
                </div>
                <div className="mockup-kpi-card">
                  <div className="kpi-label">Flagged Issues</div>
                  <div className="kpi-value warning">3</div>
                  <div className="kpi-sub orange">Pending Review</div>
                </div>
              </div>

              {/* Table Preview */}
              <div className="mockup-table-wrap">
                <div className="mockup-table-header">
                  <span>Recent Listing Audits</span>
                  <span className="live-badge">Live Monitor</span>
                </div>
                <div className="mockup-table-row header">
                  <span>SKU / Product</span>
                  <span>Category</span>
                  <span>Declarations</span>
                  <span>Status</span>
                </div>
                <div className="mockup-table-row">
                  <span className="product-cell">
                    <strong>HIVE-HONEY-500G</strong>
                    <small>Organic Honey 500g</small>
                  </span>
                  <span>Packaged Food</span>
                  <span>MRP, Net Qty, FSSAI</span>
                  <span className="status-pill pass">Verified 100%</span>
                </div>
                <div className="mockup-table-row">
                  <span className="product-cell">
                    <strong>SOUNDWAVE-TWS</strong>
                    <small>Pulse Pro Earbuds</small>
                  </span>
                  <span>Electronics</span>
                  <span>Importer, Country of Origin</span>
                  <span className="status-pill pass">Verified 100%</span>
                </div>
                <div className="mockup-table-row">
                  <span className="product-cell">
                    <strong>URBAN-OXFORD-9</strong>
                    <small>Leather Oxford Shoes</small>
                  </span>
                  <span>Footwear</span>
                  <span>Size UK 9, Net Qty</span>
                  <span className="status-pill warn">Missing Origin</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
