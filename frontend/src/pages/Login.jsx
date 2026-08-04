import { useState } from "react";
import { useNavigate, useLocation, Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

const ROLE_HINTS = [
  { role: "Admin", note: "Full platform control — users, APIs, system stats" },
  { role: "Analyst", note: "Train forecasts, manage the API registry" },
  { role: "Viewer", note: "Read-only dashboards and health status" },
];

export default function Login() {
  const { login, error, isAuthenticated, status } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (status !== "loading" && isAuthenticated) {
    return <Navigate to={location.state?.from?.pathname || "/dashboard"} replace />;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    const ok = await login(email, password);
    setSubmitting(false);
    if (ok) navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
  }

  return (
    <div style={styles.page}>
      <div style={styles.leftPanel}>
        <div style={styles.brandRow}>
          <div style={styles.logoMark}>AA</div>
          <span style={styles.brandName}>API ARENA</span>
        </div>

        <h1 style={styles.headline}>
          One dashboard for every
          <br />
          API you run in production.
        </h1>
        <p style={styles.subhead}>
          Latency, errors, forecasts and health checks — scoped to what your role is
          allowed to see and do.
        </p>

        <div style={styles.roleList}>
          {ROLE_HINTS.map((r) => (
            <div key={r.role} style={styles.roleRow}>
              <span style={styles.roleDot} />
              <div>
                <div style={styles.roleTitle}>{r.role}</div>
                <div style={styles.roleNote}>{r.note}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={styles.rightPanel}>
        <form style={styles.card} onSubmit={handleSubmit}>
          <div style={styles.cardHeader}>
            <h2 style={styles.cardTitle}>Sign in</h2>
            <p style={styles.cardSubtitle}>Use the account issued by your workspace admin.</p>
          </div>

          <label style={styles.label} htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            required
            autoComplete="username"
            placeholder="you@company.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={styles.input}
          />

          <label style={styles.label} htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            autoComplete="current-password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
          />

          {error && <div style={styles.errorBox}>{error}</div>}

          <button type="submit" disabled={submitting} style={styles.submitBtn}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>

          <p style={styles.footNote}>
            Your role (Admin, Analyst or Viewer) is assigned server-side — the dashboard
            adapts automatically once you're in.
          </p>
        </form>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "grid",
    gridTemplateColumns: "1.1fr 1fr",
    background: "var(--bg-app)",
    fontFamily: "var(--font-body)",
  },
  leftPanel: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    padding: "64px 72px",
    background:
      "radial-gradient(120% 120% at 0% 0%, rgba(34,197,94,0.12) 0%, rgba(18,22,29,0) 55%), var(--bg-sidebar)",
    borderRight: "1px solid var(--border-subtle)",
  },
  brandRow: { display: "flex", alignItems: "center", gap: 12, marginBottom: 56 },
  logoMark: {
    width: 40,
    height: 40,
    borderRadius: "50%",
    display: "grid",
    placeItems: "center",
    background: "var(--accent-gradient)",
    color: "#08150c",
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    fontSize: 14,
  },
  brandName: {
    fontFamily: "var(--font-display)",
    fontWeight: 600,
    letterSpacing: "0.08em",
    fontSize: 16,
    color: "var(--text-primary)",
  },
  headline: {
    fontFamily: "var(--font-display)",
    fontSize: 40,
    lineHeight: 1.15,
    fontWeight: 600,
    color: "var(--text-primary)",
    margin: "0 0 20px",
    maxWidth: 520,
  },
  subhead: {
    color: "var(--text-secondary)",
    fontSize: 15,
    lineHeight: 1.6,
    maxWidth: 440,
    margin: "0 0 48px",
  },
  roleList: { display: "flex", flexDirection: "column", gap: 20 },
  roleRow: { display: "flex", alignItems: "flex-start", gap: 12 },
  roleDot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    background: "var(--accent-green)",
    marginTop: 6,
    flexShrink: 0,
  },
  roleTitle: { color: "var(--text-primary)", fontWeight: 600, fontSize: 14 },
  roleNote: { color: "var(--text-muted)", fontSize: 13, marginTop: 2 },
  rightPanel: { display: "flex", alignItems: "center", justifyContent: "center", padding: 32 },
  card: {
    width: "100%",
    maxWidth: 380,
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-lg)",
    padding: 36,
    boxShadow: "var(--shadow-panel)",
  },
  cardHeader: { marginBottom: 28 },
  cardTitle: { fontFamily: "var(--font-display)", fontSize: 24, margin: 0, color: "var(--text-primary)" },
  cardSubtitle: { color: "var(--text-muted)", fontSize: 13, marginTop: 8 },
  label: { display: "block", fontSize: 12, color: "var(--text-secondary)", marginBottom: 6, marginTop: 18 },
  input: {
    width: "100%",
    padding: "11px 14px",
    borderRadius: "var(--radius-sm)",
    border: "1px solid var(--border-strong)",
    background: "var(--bg-panel-raised)",
    color: "var(--text-primary)",
    fontSize: 14,
  },
  errorBox: {
    marginTop: 18,
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    background: "rgba(240, 87, 90, 0.12)",
    border: "1px solid rgba(240, 87, 90, 0.35)",
    color: "#ff9d9f",
    fontSize: 13,
  },
  submitBtn: {
    width: "100%",
    marginTop: 26,
    padding: "12px 0",
    borderRadius: "var(--radius-sm)",
    border: "none",
    background: "var(--accent-gradient)",
    color: "#08150c",
    fontWeight: 700,
    fontSize: 14,
    cursor: "pointer",
  },
  footNote: { marginTop: 18, fontSize: 12, color: "var(--text-muted)", lineHeight: 1.5 },
};