import { History } from "lucide-react";
import { motion } from "framer-motion";

export default function ProductList({ products, selectedId, onSelect }) {
  return (
    <div className="panel" style={{ marginTop: "1rem" }}>
      <h2>
        <History size={20} style={{ marginRight: "0.5rem" }} />
        Recent Scans
      </h2>
      {!products?.length ? (
        <p className="muted">No scans yet. Run a demo sample to get started.</p>
      ) : (
        <motion.ul 
          className="product-list"
          initial="hidden"
          animate="show"
          variants={{
            hidden: { opacity: 0 },
            show: {
              opacity: 1,
              transition: { staggerChildren: 0.05 }
            }
          }}
        >
          {products.map((p) => (
            <motion.li
              variants={{ hidden: { opacity: 0, x: -10 }, show: { opacity: 1, x: 0 } }}
              key={p.id}
              className={selectedId === p.id ? "active" : ""}
              onClick={() => onSelect(p.id)}
            >
              <div className="name">{p.name || p.id}</div>
              <div className="meta">
                <span className={`status-pill ${p.overall_status || ""}`}>
                  {p.overall_status || "—"}
                </span>{" "}
                score {p.compliance_score ?? "—"} · {p.input_type} ·{" "}
                {p.review_status}
              </div>
            </motion.li>
          ))}
        </motion.ul>
      )}
    </div>
  );
}
