import React from "react";

export default function StatsBar({ stats }) {
  const items = [
    {
      label: "Products scanned",
      value: stats?.products_scanned ?? 0,
      badgeClass: "stat-neutral",
    },
    {
      label: "Potential issues",
      value: stats?.potential_issues ?? 0,
      badgeClass: "stat-warn",
    },
    {
      label: "Needs review",
      value: stats?.needs_review ?? 0,
      badgeClass: "stat-info",
    },
    {
      label: "Confirmed",
      value: stats?.confirmed ?? 0,
      badgeClass: "stat-ok",
    },
    {
      label: "Avg. score",
      value: stats?.average_score != null ? `${stats.average_score}%` : "—",
      badgeClass: "stat-accent",
    },
  ];

  return (
    <div className="stats-vertical-card">
      <div className="stats-vertical-header">
        <span className="material-symbols-outlined stats-hdr-icon">analytics</span>
        <div className="stats-hdr-text">
          <h3 className="stats-card-title">Audit Overview</h3>
          <span className="stats-card-subtitle">Live inspection metrics</span>
        </div>
      </div>
      <div className="stats-vertical-list">
        {items.map((item) => (
          <div className={`stat-item-vertical ${item.badgeClass}`} key={item.label}>
            <span className="stat-item-label">{item.label}</span>
            <span className="stat-item-val">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
