import { motion } from "framer-motion";

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

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemAnim = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div className="stats-grid" variants={container} initial="hidden" animate="show">
      {items.map((item) => (
        <motion.div className="stat-card" key={item.label} variants={itemAnim}>
          <div className="label">{item.label}</div>
          <div className="value">{item.value}</div>
        </motion.div>
      ))}
    </motion.div>
  );
}
