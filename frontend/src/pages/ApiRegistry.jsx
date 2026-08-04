import { useEffect, useState } from "react";
import client from "../api/client.js";
import AppShell from "../components/AppShell.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function ApiRegistry() {
  const { role } = useAuth();
  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  useEffect(() => {
    client
      .get("/apis", { params: { page_size: 100 } })
      .then((res) => setApis(res.data.items || []))
      .finally(() => setLoading(false));
  }, []);

  const filtered = apis.filter((a) => a.name.toLowerCase().includes(query.toLowerCase()));

  return (
    <AppShell title="API Registry" subtitle="Every endpoint currently under monitoring" onSearch={setQuery}>
      {loading ? (
        <div style={{ color: "var(--text-muted)" }}>Loading APIs…</div>
      ) : (
        <div style={styles.grid}>
          {filtered.map((api) => (
            <div key={api.id} style={styles.card}>
              <div style={styles.cardHeader}>
                <span style={styles.method}>{api.method}</span>
                <span style={styles.name}>{api.name}</span>
              </div>
              <div style={styles.url}>
                {api.base_url}
                {api.path}
              </div>
              {role !== "viewer" && (
                <div style={styles.metaRow}>
                  <span>ID: {api.id.slice(0, 8)}…</span>
                </div>
              )}
            </div>
          ))}
          {filtered.length === 0 && (
            <div style={{ color: "var(--text-muted)" }}>No APIs match your search.</div>
          )}
        </div>
      )}
    </AppShell>
  );
}

const styles = {
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 16 },
  card: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-lg)",
    padding: 20,
  },
  cardHeader: { display: "flex", alignItems: "center", gap: 10, marginBottom: 8 },
  method: {
    fontSize: 11,
    fontWeight: 700,
    color: "var(--accent-green)",
    background: "var(--accent-green-soft)",
    padding: "3px 8px",
    borderRadius: 6,
  },
  name: { fontWeight: 600, fontSize: 14, color: "var(--text-primary)" },
  url: { fontSize: 12.5, color: "var(--text-secondary)", wordBreak: "break-all" },
  metaRow: { marginTop: 10, fontSize: 11, color: "var(--text-muted)" },
};