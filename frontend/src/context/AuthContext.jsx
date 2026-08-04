import { createContext, useContext, useEffect, useState, useCallback } from "react";
import client from "../api/client.js";

const AuthContext = createContext(null);

const ACCESS_TOKEN_KEY = "aa_access_token";
const REFRESH_TOKEN_KEY = "aa_refresh_token";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [status, setStatus] = useState("loading"); // "loading" | "authenticated" | "anonymous"
  const [error, setError] = useState(null);

  const loadCurrentUser = useCallback(async () => {
    try {
      const { data } = await client.get("/users/me");
      setUser(data);
      setStatus("authenticated");
    } catch {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      setUser(null);
      setStatus("anonymous");
    }
  }, []);

  // On first load, restore the session if a token is already stored
  // (e.g. the user refreshed the page).
  useEffect(() => {
    const token = localStorage.getItem(ACCESS_TOKEN_KEY);
    if (token) {
      loadCurrentUser();
    } else {
      setStatus("anonymous");
    }
  }, [loadCurrentUser]);

  // The API client dispatches this when a refresh attempt fails, so any
  // page can react without each of them wiring up their own 401 handling.
  useEffect(() => {
    function handleUnauthorized() {
      setUser(null);
      setStatus("anonymous");
    }
    window.addEventListener("aa:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("aa:unauthorized", handleUnauthorized);
  }, []);

  async function login(email, password) {
    setError(null);
    try {
      const { data } = await client.post("/auth/login", { email, password });
      localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
      await loadCurrentUser();
      return true;
    } catch (err) {
      setError(
        err.response?.status === 401
          ? "Incorrect email or password."
          : "Couldn't sign in — please try again."
      );
      return false;
    }
  }

  function logout() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setUser(null);
    setStatus("anonymous");
  }

  const value = {
    user,
    role: user?.role,
    status,
    isAuthenticated: status === "authenticated" && !!user,
    error,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
