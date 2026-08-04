import { useEffect, useState } from "react";
import client from "../api/client.js";
import AppShell from "../components/AppShell.jsx";
import StatCard from "../components/StatCard.jsx";

const ROLES = ["admin", "analyst", "viewer"];

const emptyForm = { email: "", username: "", full_name: "", password: "", role: "viewer" };

export default function AdminConsole() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [creating, setCreating] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  async function loadUsers() {
    const { data } = await client.get("/users", { params: { page_size: 100 } });
    setUsers(data.items || []);
  }

  useEffect(() => {
    client.get("/admin/stats").then((res) => setStats(res.data));
    loadUsers();
  }, []);

  async function handleCreate(e) {
    e.preventDefault();
    setCreating(true);
    setErrorMsg("");
    try {
      await client.post("/users", form);
      setForm(emptyForm);
      await loadUsers();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || "Could not create user.");
    } finally {
      setCreating(false);
    }
  }

  async function handleRoleChange(userId, role) {
    await client.patch(`/users/${userId}`, { role });
    loadUsers();
  }

  async function handleToggleActive(user) {
    await client.patch(`/users/${user.id}`, { is_active: !user.is_active });
    loadUsers();
  }

  return (
    <AppShell title="Admin Console" subtitle="Platform-wide stats and account management">
      <div style={styles.statRow}>
        <StatCard label="Total Users" value={stats?.total_users ?? "—"} />
        <StatCard label="Registered APIs" value={stats?.total_apis ?? "—"} />
        <StatCard label="Request Logs" value={stats?.total_request_logs?.toLocaleString() ?? "—"} />
      </div>

      <div style={styles.grid}>
        <div style={styles.card}>
          <div style={styles.cardTitle}>Create account</div>
          <form onSubmit={handleCreate} style={styles.form}>
            <input
              placeholder="Full name"
              required
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              style={styles.input}
            />
            <input
              placeholder="Username"
              required
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              style={styles.input}
            />
            <input
              placeholder="Email"
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              style={styles.input}
            />
            <input
              placeholder="Temporary password"
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              style={styles.input}
            />
            <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} style={styles.input}>
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
            {errorMsg && <div style={styles.error}>{errorMsg}</div>}
            <button type="submit" disabled={creating} style={styles.primaryBtn}>
              {creating ? "Creating…" : "Create account"}
            </button>
          </form>
        </div>

        <div style={styles.card}>
          <div style={styles.cardTitle}>Accounts</div>
          <div style={styles.tableWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.th}>Name</th>
                  <th style={styles.th}>Role</th>
                  <th style={styles.th}>Status</th>
                  <th style={styles.th}></th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td style={styles.td}>
                      <div style={{ fontWeight: 600 }}>{u.full_name}</div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{u.email}</div>
                    </td>
                    <td style={styles.td}>
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        style={styles.smallSelect}
                      >
                        {ROLES.map((r) => (
                          <option key={r} value={r}>
                            {r}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td style={styles.td}>
                      <span style={{ color: u.is_active ? "var(--accent-green)" : "var(--text-muted)" }}>
                        {u.is_active ? "Active" : "Deactivated"}
                      </span>
                    </td>
                    <td style={styles.td}>
                      <button onClick={() => handleToggleActive(u)} style={styles.linkBtn}>
                        {u.is_active ? "Deactivate" : "Reactivate"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

const styles = {
  statRow: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 22, maxWidth: 760 },
  grid: { display: "grid", gridTemplateColumns: "340px 1fr", gap: 18, alignItems: "start" },
  card: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-lg)",
    padding: 20,
  },
  cardTitle: { fontFamily: "var(--font-display)", fontSize: 16, fontWeight: 600, marginBottom: 14 },
  form: { display: "flex", flexDirection: "column", gap: 10 },
  input: {
    background: "var(--bg-panel-raised)",
    border: "1px solid var(--border-strong)",
    color: "var(--text-primary)",
    borderRadius: "var(--radius-sm)",
    padding: "10px 12px",
    fontSize: 13,
  },
  error: { color: "#ff9d9f", fontSize: 12.5 },
  primaryBtn: {
    background: "var(--accent-gradient)",
    border: "none",
    color: "#08150c",
    fontWeight: 700,
    borderRadius: "var(--radius-sm)",
    padding: "10px 0",
    fontSize: 13,
    cursor: "pointer",
    marginTop: 4,
  },
  tableWrap: { overflowX: "auto" },
  table: { width: "100%", borderCollapse: "collapse" },
  th: {
    textAlign: "left",
    fontSize: 11,
    color: "var(--text-muted)",
    borderBottom: "1px solid var(--border-subtle)",
    padding: "8px 10px",
  },
  td: { padding: "10px", borderBottom: "1px solid var(--border-subtle)", fontSize: 13, color: "var(--text-primary)" },
  smallSelect: {
    background: "var(--bg-panel-raised)",
    border: "1px solid var(--border-strong)",
    color: "var(--text-primary)",
    borderRadius: 6,
    padding: "5px 8px",
    fontSize: 12,
  },
  linkBtn: {
    background: "transparent",
    border: "none",
    color: "var(--accent-blue)",
    fontSize: 12,
    cursor: "pointer",
  },
};