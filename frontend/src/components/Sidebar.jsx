import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  LayoutGrid,
  BookOpen,
  MapPin,
  FlaskConical,
  ShieldCheck,
  ChevronLeft,
  ChevronRight,
  LogOut,
} from "lucide-react";
import { useAuth } from "../context/AuthContext.jsx";

// Every entry is visible to any of the roles listed here.
const NAV_ITEMS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutGrid, roles: ["admin", "analyst", "viewer"] },
  { to: "/apis", label: "API Registry", icon: BookOpen, roles: ["admin", "analyst", "viewer"] },
  { to: "/errors", label: "Errors & Complaints", icon: MapPin, roles: ["admin", "analyst", "viewer"] },
  { to: "/forecast", label: "Forecast Lab", icon: FlaskConical, roles: ["admin", "analyst"] },
  { to: "/admin", label: "Admin Console", icon: ShieldCheck, roles: ["admin"] },
];

export default function Sidebar() {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  const items = NAV_ITEMS.filter((item) => item.roles.includes(role));
  const initials = (user?.full_name || user?.username || "?")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <aside style={{ ...styles.sidebar, width: collapsed ? 84 : 248 }}>
      <div style={styles.brandRow}>
        <div style={styles.logoMark}>AA</div>
        {!collapsed && <span style={styles.brandName}>API ARENA</span>}
      </div>

      <nav style={styles.nav}>
        {items.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            style={({ isActive }) => ({
              ...styles.navItem,
              ...(isActive ? styles.navItemActive : {}),
              justifyContent: collapsed ? "center" : "flex-start",
            })}
          >
            <Icon size={18} strokeWidth={2} />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      <div style={styles.bottomArea}>
        <button
          onClick={() => setCollapsed((c) => !c)}
          style={styles.collapseBtn}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>

        <div style={{ ...styles.profileRow, justifyContent: collapsed ? "center" : "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, minWidth: 0 }}>
            <div style={styles.avatar}>{initials}</div>
            {!collapsed && (
              <div style={{ minWidth: 0 }}>
                <div style={styles.profileName}>{user?.full_name || user?.username}</div>
                <div style={styles.profileRole}>{role}</div>
              </div>
            )}
          </div>
          {!collapsed && (
            <button onClick={handleLogout} style={styles.logoutBtn} aria-label="Log out">
              <LogOut size={16} />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
}

const styles = {
  sidebar: {
    background: "var(--bg-sidebar)",
    borderRight: "1px solid var(--border-subtle)",
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    position: "sticky",
    top: 0,
    padding: "22px 16px",
    transition: "width 160ms ease",
    flexShrink: 0,
  },
  brandRow: { display: "flex", alignItems: "center", gap: 10, padding: "0 6px", marginBottom: 28 },
  logoMark: {
    width: 32,
    height: 32,
    borderRadius: "50%",
    display: "grid",
    placeItems: "center",
    background: "var(--accent-gradient)",
    color: "#08150c",
    fontFamily: "var(--font-display)",
    fontWeight: 700,
    fontSize: 12,
    flexShrink: 0,
  },
  brandName: {
    fontFamily: "var(--font-display)",
    fontWeight: 600,
    letterSpacing: "0.06em",
    fontSize: 14,
    whiteSpace: "nowrap",
  },
  nav: { display: "flex", flexDirection: "column", gap: 4, flex: 1 },
  navItem: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "10px 12px",
    borderRadius: "var(--radius-sm)",
    color: "var(--text-secondary)",
    fontSize: 13.5,
    fontWeight: 500,
    whiteSpace: "nowrap",
    overflow: "hidden",
  },
  navItemActive: {
    background: "var(--accent-green)",
    color: "#06170d",
    fontWeight: 700,
  },
  bottomArea: { display: "flex", flexDirection: "column", gap: 14 },
  collapseBtn: {
    alignSelf: "flex-start",
    width: 30,
    height: 30,
    borderRadius: "50%",
    border: "1px solid var(--border-strong)",
    background: "var(--bg-panel)",
    color: "var(--text-secondary)",
    display: "grid",
    placeItems: "center",
    cursor: "pointer",
  },
  profileRow: {
    display: "flex",
    alignItems: "center",
    borderTop: "1px solid var(--border-subtle)",
    paddingTop: 14,
  },
  avatar: {
    width: 34,
    height: 34,
    borderRadius: "50%",
    background: "var(--bg-panel-raised)",
    border: "1px solid var(--border-strong)",
    display: "grid",
    placeItems: "center",
    fontSize: 12,
    fontWeight: 700,
    color: "var(--text-primary)",
    flexShrink: 0,
  },
  profileName: {
    fontSize: 13,
    fontWeight: 600,
    color: "var(--text-primary)",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
    maxWidth: 130,
  },
  profileRole: { fontSize: 11, color: "var(--text-muted)", textTransform: "capitalize" },
  logoutBtn: {
    width: 30,
    height: 30,
    borderRadius: "50%",
    border: "1px solid var(--border-strong)",
    background: "transparent",
    color: "var(--text-secondary)",
    display: "grid",
    placeItems: "center",
    cursor: "pointer",
    flexShrink: 0,
  },
};