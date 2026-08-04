import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

/**
 * Wraps a page so it requires an authenticated session, and optionally
 * restricts it to a set of roles (e.g. ["admin"] or ["admin", "analyst"]).
 */
export default function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, status, role } = useAuth();
  const location = useLocation();

  if (status === "loading") {
    return (
      <div style={{ display: "grid", placeItems: "center", height: "100vh", color: "var(--text-muted)" }}>
        Loading your workspace…
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (roles && !roles.includes(role)) {
    return <Navigate to="/not-authorized" replace />;
  }

  return children;
}