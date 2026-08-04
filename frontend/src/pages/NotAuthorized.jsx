import { Link } from "react-router-dom";
import { ShieldAlert } from "lucide-react";

export default function NotAuthorized() {
  return (
    <div style={styles.page}>
      <ShieldAlert size={40} color="var(--accent-amber)" />
      <h1 style={styles.title}>You don't have access to this page</h1>
      <p style={styles.text}>Your account role doesn't include this section. Ask an admin if you need it.</p>
      <Link to="/dashboard" style={styles.link}>
        Back to dashboard
      </Link>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    background: "var(--bg-app)",
    color: "var(--text-primary)",
    textAlign: "center",
    padding: 24,
  },
  title: { fontFamily: "var(--font-display)", fontSize: 22, margin: 0 },
  text: { color: "var(--text-muted)", fontSize: 14, maxWidth: 360 },
  link: {
    marginTop: 8,
    color: "#08150c",
    background: "var(--accent-gradient)",
    padding: "10px 18px",
    borderRadius: "var(--radius-sm)",
    fontWeight: 700,
    fontSize: 13,
  },
};