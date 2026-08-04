export default function ApiPicker({ apis, value, onChange }) {
  return (
    <select value={value || ""} onChange={(e) => onChange(e.target.value)} style={styles.select}>
      {apis.length === 0 && <option value="">No APIs registered yet</option>}
      {apis.map((api) => (
        <option key={api.id} value={api.id}>
          {api.name}
        </option>
      ))}
    </select>
  );
}

const styles = {
  select: {
    background: "var(--bg-panel-raised)",
    border: "1px solid var(--border-strong)",
    color: "var(--text-primary)",
    borderRadius: "var(--radius-sm)",
    padding: "9px 12px",
    fontSize: 13,
    minWidth: 200,
  },
};