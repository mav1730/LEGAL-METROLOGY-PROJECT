import React, { useState } from "react";
import rulesData from "../data/rulesData";

const CATEGORIES = [
  "All",
  "Mandatory Declarations",
  "E-Commerce Regulation",
  "Display & Typography",
  "Pricing & Sale",
  "Quantity Measurement",
  "Inspection & Enforcement",
  "Registration & Licensing",
  "General & Scope",
];

export default function RulesPage({ onNavigateToScanner, onNavigateToHome }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [expandedRules, setExpandedRules] = useState({});
  const [isFocused, setIsFocused] = useState(false);

  const filteredRules = rulesData.filter((rule) => {
    const matchesSearch =
      rule.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.section.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (rule.keyPoints &&
        rule.keyPoints.some((kp) => kp.toLowerCase().includes(searchTerm.toLowerCase())));

    const matchesCategory =
      selectedCategory === "All" || rule.category === selectedCategory;

    return matchesSearch && matchesCategory;
  });

  const toggleRule = (index) => {
    setExpandedRules((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  const toggleAll = (expand) => {
    if (!expand) {
      setExpandedRules({});
    } else {
      const all = {};
      filteredRules.forEach((_, idx) => {
        all[idx] = true;
      });
      setExpandedRules(all);
    }
  };

  return (
    <div className="rules-page-container">
      {/* Top Header / Breadcrumbs */}
      <div className="rules-hero-header">
        <div className="breadcrumb-nav">
          {onNavigateToHome && (
            <button type="button" className="breadcrumb-link" onClick={onNavigateToHome}>
              ← Back to Home
            </button>
          )}
          <span className="breadcrumb-sep">/</span>
          <span className="breadcrumb-current">Statutory Regulations</span>
        </div>

        <div className="rules-hero-title-row">
          <div>
            <div className="hero-badge">
              <span className="material-symbols-outlined" style={{ fontSize: "1rem" }}>
                menu_book
              </span>
              <span>Comprehensive Statutory Knowledge Base</span>
            </div>
            <h1 className="rules-main-title">Legal Metrology &amp; E-Commerce Regulations</h1>
            <p className="rules-subtitle">
              Detailed statutory clauses, compliance checklists, typography standards, and regulatory penalties under The Legal Metrology Act, 2009 and Packaged Commodities (LMPC) Rules, 2011.
            </p>
          </div>
        </div>
      </div>

      {/* Live Search Section */}
      <div className="rules-search-wrapper">
        <div className={`rules-search-box ${isFocused ? "focused" : ""}`}>
          <span className="material-symbols-outlined search-icon">search</span>
          <input
            type="text"
            className="rules-search-input"
            placeholder="Search regulations (e.g., 'MRP', 'Net Quantity', 'Rule 6', 'Font Height', 'Customer Care', 'Importer', 'DPCO')..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
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

        {/* Category Pills Filter */}
        <div className="category-pills-row">
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

        <div className="search-meta-row">
          {searchTerm || selectedCategory !== "All" ? (
            <p className="search-result-count">
              Found <strong className="highlight-count">{filteredRules.length}</strong> matching regulation{filteredRules.length === 1 ? "" : "s"}
              {searchTerm && ` for "${searchTerm}"`}
              {selectedCategory !== "All" && ` in [${selectedCategory}]`}
            </p>
          ) : (
            <p className="search-result-count muted">
              Browsing all <strong className="highlight-count">{rulesData.length}</strong> codified legal provisions
            </p>
          )}

          <div className="expand-all-group">
            <button
              type="button"
              className="btn-text-action"
              onClick={() => toggleAll(true)}
            >
              Expand All Rules
            </button>
            <span className="text-sep">·</span>
            <button
              type="button"
              className="btn-text-action"
              onClick={() => toggleAll(false)}
            >
              Collapse All
            </button>
          </div>
        </div>
      </div>

      {/* E-Commerce Legal Metrology Overview Banner */}
      <div className="rules-ecommerce-card">
        <div className="rules-card-glow" />

        <div className="rules-card-header">
          <div className="rules-icon-badge">
            <span className="material-symbols-outlined">shopping_cart</span>
          </div>
          <div>
            <h2 className="rules-card-heading">E-Commerce Legal Metrology Framework</h2>
            <p className="muted" style={{ margin: 0 }}>
              Statutory obligations for digital marketplaces, sellers, direct-to-consumer (D2C) brands, and importers.
            </p>
          </div>
        </div>

        <div className="rules-sections-grid">
          {/* Act Overview */}
          <div className="rules-section-box">
            <h3 className="section-subheading">
              <span className="material-symbols-outlined icon-amber">gavel</span>
              The Legal Metrology Act, 2009 (1 of 2010)
            </h3>
            <p className="section-text">
              The <strong>Legal Metrology Act, 2009</strong> establishes and enforces standards of weights and measures, regulates trade and commerce in weights, measures, and packaged commodities sold or distributed by weight, measure, or number. It replaced the 1976 Act and 1985 Enforcement Act.
            </p>
            <p className="section-text">
              Its primary objective is to guarantee public certainty, accuracy, and security of weighments and measurements, ensuring robust consumer protection against short weights and deceptive trade practices across India.
            </p>
          </div>

          {/* LMPC Rules */}
          <div className="rules-section-box">
            <h3 className="section-subheading">
              <span className="material-symbols-outlined icon-amber">package_2</span>
              Packaged Commodities Rules, 2011 (LMPC)
            </h3>
            <p className="section-text">
              Under the Act, the <strong>Legal Metrology (Packaged Commodities) Rules, 2011</strong> regulate pre-packaged goods. Rule 6(10) explicitly mandates that e-commerce entities must display all statutory declarations on their digital networks for online transactions.
            </p>

            <div className="mandatory-declarations-grid">
              <div className="declarations-col">
                <h4 className="col-title">Mandatory E-Commerce Declarations:</h4>
                <ul className="rules-bullet-list">
                  <li><strong>Manufacturer / Packer / Importer:</strong> Full legal name and registered address with PIN Code.</li>
                  <li><strong>Generic Name:</strong> Common or generic identity of the commodity.</li>
                  <li><strong>Net Quantity:</strong> In standard metric units (kg, g, L, ml, m, or count).</li>
                  <li><strong>Maximum Retail Price (MRP):</strong> Inclusive of all taxes in ₹ format.</li>
                  <li><strong>Unit Sale Price (USP):</strong> Price per gram/kg or ml/litre for clear price transparency.</li>
                  <li><strong>Country of Origin:</strong> Mandatory for all domestic and imported goods.</li>
                  <li><strong>Customer Care Details:</strong> Contact name, phone, email, and postal address.</li>
                  <li><strong>Dimensions / Sizes:</strong> Relevant linear dimensions (apparel, footwear, etc.).</li>
                </ul>
              </div>

              <div className="declarations-col">
                <h4 className="col-title">Statutory Exemptions:</h4>
                <ul className="rules-bullet-list">
                  <li>Packages containing net quantity exceeding <strong>25 kg or 25 L</strong> (except cement &amp; fertilizer up to 50 kg).</li>
                  <li>Commodities exclusively packed for <strong>industrial or institutional consumers</strong>.</li>
                  <li>Fast food items packed by restaurants, bakeries, or hotels for immediate consumption.</li>
                  <li>Formulations governed under the <strong>Drugs (Price Control) Order (DPCO)</strong>.</li>
                  <li>Packages with net content of <strong>10g or 10ml or less</strong>.</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Penalties */}
          <div className="rules-section-box">
            <h3 className="section-subheading">
              <span className="material-symbols-outlined icon-danger">warning</span>
              Liabilities &amp; Penalties (Section 36 &amp; 49)
            </h3>
            <p className="section-text">
              Non-compliance with statutory declarations attracts strict penal action under Section 36 of the Act. E-commerce platforms can claim safe harbor under the IT Act <em>only</em> if they maintain diligent automated verification.
            </p>
            <div className="penalties-pill-grid">
              <div className="penalty-pill">
                <div className="penalty-offence">First Offence</div>
                <div className="penalty-fine">Fine extending up to ₹ 25,000</div>
              </div>
              <div className="penalty-pill">
                <div className="penalty-offence">Second Offence</div>
                <div className="penalty-fine">Fine extending up to ₹ 50,000</div>
              </div>
              <div className="penalty-pill">
                <div className="penalty-offence">Subsequent Offences</div>
                <div className="penalty-fine">Fine up to ₹ 1,00,000 / 1 Year Imprisonment / Both</div>
              </div>
            </div>
            <p className="section-text" style={{ marginTop: "0.75rem", fontSize: "0.88rem" }}>
              <strong>Corporate Liability:</strong> Directors and officers-in-charge at the time of the violation are held personally accountable. Companies must officially nominate a compliance officer under Section 49.
            </p>
          </div>

          {/* Safe harbor callout */}
          <div className="rules-notice-box">
            <span className="material-symbols-outlined notice-icon">info</span>
            <div>
              <strong className="notice-title">Important Marketplace Clarification:</strong>
              <p className="notice-desc">
                If an e-commerce platform acts purely as a marketplace intermediary, it must contractually obligate sellers to submit accurate declarations. If the platform holds inventory or alters product listings, it assumes direct manufacturer/seller liability for any missing declarations.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Rules List Title */}
      <div className="rules-list-section-header">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary">format_list_bulleted</span>
          <h2 className="text-xl font-bold">Codified Rules Directory</h2>
        </div>
        <span className="badge">
          Showing {filteredRules.length} of {rulesData.length} Rules
        </span>
      </div>

      {/* General Rules Expandable Cards */}
      <div className="rules-cards-stack">
        {filteredRules.length === 0 ? (
          <div className="panel empty-search-state">
            <span className="material-symbols-outlined empty-icon">search_off</span>
            <h3>No matching regulations found</h3>
            <p className="muted">
              Try searching with different terms like &ldquo;MRP&rdquo;, &ldquo;Address&rdquo;, &ldquo;Net Quantity&rdquo;, or &ldquo;Rule 6&rdquo;.
            </p>
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
          filteredRules.map((rule, index) => {
            const isExpanded = !!expandedRules[index];
            return (
              <div
                key={rule.section || index}
                className={`rule-glass-card ${isExpanded ? "expanded" : ""}`}
              >
                <div className="rule-card-main">
                  {/* Header */}
                  <div className="rule-card-header">
                    <div className="rule-title-group">
                      <span className="rule-section-pill">{rule.section}</span>
                      {rule.category && (
                        <span className="rule-category-badge">{rule.category}</span>
                      )}
                      <h3 className="rule-title">{rule.title}</h3>
                    </div>
                    <button
                      type="button"
                      className={`rule-expand-btn ${isExpanded ? "active" : ""}`}
                      onClick={() => toggleRule(index)}
                      aria-expanded={isExpanded}
                    >
                      {isExpanded ? "Hide Full Details" : "Read Full Details"}
                      <span className="material-symbols-outlined btn-arrow">
                        {isExpanded ? "expand_less" : "expand_more"}
                      </span>
                    </button>
                  </div>

                  {/* Summary description */}
                  <p className="rule-summary-desc">{rule.description}</p>

                  {/* Key Compliance Takeaways Box */}
                  {rule.keyPoints && rule.keyPoints.length > 0 && (
                    <div className="rule-key-takeaways">
                      <div className="key-takeaways-title">
                        <span className="material-symbols-outlined" style={{ fontSize: "1rem" }}>
                          checklist
                        </span>
                        <span>Key Compliance Requirements:</span>
                      </div>
                      <ul className="key-takeaways-list">
                        {rule.keyPoints.map((kp, kIdx) => (
                          <li key={kIdx}>{kp}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Expanded HTML Details */}
                  {isExpanded && (
                    <div className="rule-expanded-content">
                      <div className="rule-divider" />
                      <div
                        className="rule-html-body"
                        dangerouslySetInnerHTML={{ __html: rule.details }}
                      />
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
