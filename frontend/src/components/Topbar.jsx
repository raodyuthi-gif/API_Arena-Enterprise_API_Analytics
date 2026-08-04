import { Search, Bell } from "lucide-react";

export default function Topbar({ title, subtitle, onSearch }) {
  return (
    <header style={styles.header}>
      <div>
        <h1 style={styles.title}>{title}</h1>
        {subtitle && <p style={styles.subtitle}>{subtitle}</p>}
      </div>

      <div style={styles.right}>
        <div style={styles.searchBox}>
          <Search size={16} color="var(--text-muted)" />
          <input
            placeholder="Type to search"
            style={styles.searchInput}
            onChange={(e) => onSearch?.(e.target.value)}
          />
        </div>
        <button style={styles.iconBtn} aria-label="Notifications">
          <Bell size={18} />
        </button>
      </div>
    </header>
  );
}

const styles = {
  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "26px 32px",
    borderBottom: "1px solid var(--border-subtle)",
  },
  title: { fontFamily: "var(--font-display)", fontSize: 24, margin: 0, color: "var(--text-primary)" },
  subtitle: { margin: "4px 0 0", fontSize: 13, color: "var(--text-muted)" },
  right: { display: "flex", alignItems: "center", gap: 12 },
  searchBox: {
    display: "flex",
    alignItems: "center",
    gap: 8,
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-sm)",
    padding: "9px 14px",
    width: 260,
  },
  searchInput: {
    border: "none",
    background: "transparent",
    outline: "none",
    color: "var(--text-primary)",
    fontSize: 13,
    width: "100%",
  },
  iconBtn: {
    width: 38,
    height: 38,
    borderRadius: "50%",
    border: "1px solid var(--border-subtle)",
    background: "var(--bg-panel)",
    color: "var(--text-secondary)",
    display: "grid",
    placeItems: "center",
    cursor: "pointer",
  },
};