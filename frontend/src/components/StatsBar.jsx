export default function StatsBar({ stats }) {
  const items = [
    { label: "Products scanned", value: stats?.products_scanned ?? 0 },
    { label: "Potential issues", value: stats?.potential_issues ?? 0 },
    { label: "Needs review", value: stats?.needs_review ?? 0 },
    { label: "Confirmed", value: stats?.confirmed ?? 0 },
    {
      label: "Avg. score",
      value: stats?.average_score != null ? stats.average_score : "—",
    },
  ];

  return (
    <div className="stats-grid">
      {items.map((item) => (
        <div className="stat-card" key={item.label}>
          <div className="label">{item.label}</div>
          <div className="value">{item.value}</div>
        </div>
      ))}
    </div>
  );
}
