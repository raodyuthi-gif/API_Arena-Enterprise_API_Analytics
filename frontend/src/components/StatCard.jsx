export default function StatCard({ label, value, hint, tone = "default" }) {
  return (
    <div style={styles.card}>
      <div style={styles.label}>{label}</div>
      <div style={{ ...styles.value, color: TONE_COLORS[tone] || TONE_COLORS.default }}>{value}</div>
      {hint && <div style={styles.hint}>{hint}</div>}
    </div>
  );
}

const TONE_COLORS = {
  default: "var(--text-primary)",
  good: "var(--accent-green)",
  warn: "var(--accent-amber)",
  bad: "var(--accent-red)",
};

const styles = {
  card: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-lg)",
    padding: "22px 22px",
    minWidth: 0,
  },
  label: { fontSize: 13, color: "var(--text-secondary)", marginBottom: 10 },
  value: { fontFamily: "var(--font-display)", fontSize: 32, fontWeight: 700, lineHeight: 1 },
  hint: { fontSize: 12, color: "var(--text-muted)", marginTop: 10 },
};