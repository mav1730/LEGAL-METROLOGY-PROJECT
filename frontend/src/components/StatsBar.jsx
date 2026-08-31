import React from "react";

export default function StatsBar({ stats }) {
  const items = [
    { label: "Products scanned", value: stats?.products_scanned ?? 0 },
    { label: "Potential issues", value: stats?.potential_issues ?? 0 },
    { label: "Needs review", value: stats?.needs_review ?? 0 },
    { label: "Confirmed", value: stats?.confirmed ?? 0 },
    {
      label: "Avg. score",
      value: stats?.average_score != null ? `${stats.average_score}%` : "—",
    },
  ];

  return (
    <div className="stats-bar">
      {items.map((item) => (
        <div className="stat-item" key={item.label}>
          <span className="stat-item-label">{item.label}</span>
          <span className="stat-item-val">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
