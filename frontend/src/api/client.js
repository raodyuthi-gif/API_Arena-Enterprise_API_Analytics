import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach the access token to every outgoing request.
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("aa_access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If a request comes back unauthorized, try one silent refresh before
// giving up and forcing the user back to the login screen.
let refreshPromise = null;

async function refreshAccessToken() {
  const refreshToken = localStorage.getItem("aa_refresh_token");
  if (!refreshToken) return null;

  if (!refreshPromise) {
    refreshPromise = axios
      .post(`${API_BASE_URL}/auth/refresh`, { refresh_token: refreshToken })
      .then((res) => {
        localStorage.setItem("aa_access_token", res.data.access_token);
        localStorage.setItem("aa_refresh_token", res.data.refresh_token);
        return res.data.access_token;
      })
      .catch(() => {
        localStorage.removeItem("aa_access_token");
        localStorage.removeItem("aa_refresh_token");
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const newToken = await refreshAccessToken();
      if (newToken) {
        original.headers.Authorization = `Bearer ${newToken}`;
        return client(original);
      }
      // No valid refresh token — send the user back to login.
      window.dispatchEvent(new CustomEvent("aa:unauthorized"));
    }
    return Promise.reject(error);
  }
);

export default client;