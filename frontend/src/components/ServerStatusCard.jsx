import { ServerCog } from "lucide-react";

const STATUS_COPY = {
  healthy: { label: "All Systems Online", dot: "#eafff2" },
  degraded: { label: "Degraded Performance", dot: "#fff4d6" },
  critical: { label: "Critical Incident", dot: "#ffe3e3" },
};

export default function ServerStatusCard({ status = "healthy", apiCount = 0, lastIncident }) {
  const copy = STATUS_COPY[status] || STATUS_COPY.healthy;

  return (
    <div style={styles.card}>
      <div style={styles.headerRow}>
        <span style={styles.title}>{copy.label}</span>
        <span style={{ ...styles.dot, background: copy.dot }} />
      </div>

      <div style={styles.body}>
        <div style={styles.iconWrap}>
          <ServerCog size={30} color="#eafff2" strokeWidth={1.6} />
        </div>
        <div>
          <div style={styles.row}>
            <span style={styles.rowLabel}>Monitored APIs</span>
            <span style={styles.rowValue}>{apiCount}</span>
          </div>
          <div style={styles.row}>
            <span style={styles.rowLabel}>Last incident</span>
            <span style={styles.rowValue}>{lastIncident || "No incidents recorded"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: "var(--accent-gradient)",
    borderRadius: "var(--radius-lg)",
    padding: "22px 22px",
    color: "#eafff2",
    minHeight: 190,
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
  },
  headerRow: { display: "flex", alignItems: "center", justifyContent: "space-between" },
  title: { fontWeight: 700, fontSize: 15 },
  dot: { width: 9, height: 9, borderRadius: "50%" },
  body: { display: "flex", alignItems: "center", gap: 18, marginTop: 14 },
  iconWrap: {
    width: 56,
    height: 56,
    borderRadius: "var(--radius-md)",
    background: "rgba(255,255,255,0.14)",
    display: "grid",
    placeItems: "center",
    flexShrink: 0,
  },
  row: { display: "flex", flexDirection: "column", marginBottom: 8 },
  rowLabel: { fontSize: 11.5, opacity: 0.85 },
  rowValue: { fontSize: 14, fontWeight: 600 },
};