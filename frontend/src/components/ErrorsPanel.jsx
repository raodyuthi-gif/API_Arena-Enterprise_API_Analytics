import { OctagonAlert, TriangleAlert } from "lucide-react";

export default function ErrorsPanel({ items = [] }) {
  return (
    <div style={styles.card}>
      <div style={styles.title}>Errors &amp; Complaints</div>

      <div style={styles.list}>
        {items.length === 0 && <div style={styles.empty}>No failing endpoints in this window.</div>}

        {items.map((item, i) => {
          const critical = item.error_rate_percent >= 5;
          return (
            <div key={i} style={styles.item}>
              <div style={{ ...styles.iconWrap, background: critical ? "rgba(240,87,90,0.14)" : "rgba(242,181,68,0.14)" }}>
                {critical ? (
                  <OctagonAlert size={16} color="var(--accent-red)" />
                ) : (
                  <TriangleAlert size={16} color="var(--accent-amber)" />
                )}
              </div>
              <div style={{ minWidth: 0 }}>
                <div style={styles.itemTitle}>
                  {item.method} {item.endpoint_path}
                </div>
                <div style={styles.itemNote}>
                  {item.error_count} errors · {item.error_rate_percent.toFixed(1)}% rate · HTTP{" "}
                  {item.top_status_code}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-lg)",
    padding: 22,
    height: "100%",
  },
  title: { fontFamily: "var(--font-display)", fontSize: 17, fontWeight: 600, marginBottom: 16 },
  list: { display: "flex", flexDirection: "column", gap: 14 },
  empty: { fontSize: 13, color: "var(--text-muted)" },
  item: { display: "flex", gap: 12, alignItems: "flex-start" },
  iconWrap: {
    width: 32,
    height: 32,
    borderRadius: "var(--radius-sm)",
    display: "grid",
    placeItems: "center",
    flexShrink: 0,
  },
  itemTitle: {
    fontSize: 13,
    fontWeight: 600,
    color: "var(--text-primary)",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
  },
  itemNote: { fontSize: 11.5, color: "var(--text-muted)", marginTop: 3 },
};