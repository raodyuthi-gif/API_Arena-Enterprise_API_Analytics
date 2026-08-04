import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import client from "../api/client.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading"); // loading | authenticated | anonymous
  const [error, setError] = useState(null);

  const loadProfile = useCallback(async () => {
    try {
      const { data } = await client.get("/users/me");
      setUser(data);
      setStatus("authenticated");
    } catch {
      localStorage.removeItem("aa_access_token");
      localStorage.removeItem("aa_refresh_token");
      setUser(null);
      setStatus("anonymous");
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("aa_access_token");
    if (token) {
      loadProfile();
    } else {
      setStatus("anonymous");
    }
  }, [loadProfile]);

  // Client responds to a forced logout triggered by the API interceptor
  // (e.g. refresh token expired) so every tab/component stays in sync.
  useEffect(() => {
    const handler = () => {
      localStorage.removeItem("aa_access_token");
      localStorage.removeItem("aa_refresh_token");
      setUser(null);
      setStatus("anonymous");
    };
    window.addEventListener("aa:unauthorized", handler);
    return () => window.removeEventListener("aa:unauthorized", handler);
  }, []);

  const login = useCallback(
    async (email, password) => {
      setError(null);
      try {
        const { data } = await client.post("/auth/login", { email, password });
        localStorage.setItem("aa_access_token", data.access_token);
        localStorage.setItem("aa_refresh_token", data.refresh_token);
        await loadProfile();
        return true;
      } catch (err) {
        const detail = err.response?.data?.detail || "Unable to sign in. Check your credentials.";
        setError(detail);
        return false;
      }
    },
    [loadProfile]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("aa_access_token");
    localStorage.removeItem("aa_refresh_token");
    setUser(null);
    setStatus("anonymous");
  }, []);

  const value = useMemo(
    () => ({
      user,
      role: user?.role || null,
      status,
      isAuthenticated: status === "authenticated",
      error,
      login,
      logout,
    }),
    [user, status, error, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}