import { useEffect, useState } from "react";
import client from "../api/client.js";
import AppShell from "../components/AppShell.jsx";
import StatCard from "../components/StatCard.jsx";
import ServerStatusCard from "../components/ServerStatusCard.jsx";
import ActivityChart from "../components/ActivityChart.jsx";
import ErrorsPanel from "../components/ErrorsPanel.jsx";
import ApiPicker from "../components/ApiPicker.jsx";
import { useAuth } from "../context/AuthContext.jsx";

export default function Dashboard() {
  const { user, role } = useAuth();
  const [overview, setOverview] = useState(null);
  const [apis, setApis] = useState([]);
  const [selectedApiId, setSelectedApiId] = useState("");
  const [trafficWindow, setTrafficWindow] = useState("24h");
  const [traffic, setTraffic] = useState([]);
  const [errors, setErrors] = useState([]);
  const [adminStats, setAdminStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // Overview + API list load once.
  useEffect(() => {
    (async () => {
      try {
        const [overviewRes, apisRes] = await Promise.all([
          client.get("/dashboard/overview"),
          client.get("/apis", { params: { page_size: 50 } }),
        ]);
        setOverview(overviewRes.data);
        setApis(apisRes.data.items || []);
        if (apisRes.data.items?.length) setSelectedApiId(apisRes.data.items[0].id);
      } catch (err) {
        console.error("Failed to load dashboard overview", err);
      } finally {
        setLoading(false);
      }
    })();

    if (role === "admin") {
      client
        .get("/admin/stats")
        .then((res) => setAdminStats(res.data))
        .catch(() => {});
    }
  }, [role]);

  // Traffic + errors reload whenever the selected API or window changes.
  useEffect(() => {
    if (!selectedApiId) return;
    client
      .get("/analytics/traffic", { params: { api_id: selectedApiId, window: trafficWindow } })
      .then((res) => setTraffic(res.data.data || []))
      .catch(() => setTraffic([]));

    client
      .get("/analytics/errors", { params: { api_id: selectedApiId, window: trafficWindow } })
      .then((res) => setErrors(res.data.top_failing_endpoints || []))
      .catch(() => setErrors([]));
  }, [selectedApiId, trafficWindow]);

  const overallStatus = overview?.critical_apis > 0 ? "critical" : overview?.degraded_apis > 0 ? "degraded" : "healthy";

  return (
    <AppShell
      title="Dashboard"
      subtitle={`Welcome back, ${user?.full_name?.split(" ")[0] || user?.username} · ${role}`}
    >
      {loading ? (
        <div style={{ color: "var(--text-muted)" }}>Loading dashboard…</div>
      ) : (
        <>
          <div style={styles.topGrid}>
            <ServerStatusCard
              status={overallStatus}
              apiCount={overview?.total_apis ?? 0}
              lastIncident={overview?.recent_alerts?.[0]?.message}
            />
            <StatCard label="API Calls (24h)" value={overview?.total_requests_24h?.toLocaleString() ?? "—"} hint="Across all registered APIs" />
            <StatCard
              label="Avg Latency (24h)"
              value={overview ? `${Math.round(overview.avg_latency_ms_24h)} ms` : "—"}
              hint={overview ? `P99: ${Math.round(overview.p99_latency_ms_24h)} ms` : ""}
            />
            {role === "admin" && adminStats ? (
              <StatCard label="Platform Users" value={adminStats.total_users} hint="Registered accounts" />
            ) : (
              <StatCard
                label="Error Rate (24h)"
                value={overview ? `${overview.error_rate_24h.toFixed(2)}%` : "—"}
                tone={overview?.error_rate_24h > 5 ? "bad" : "good"}
              />
            )}
          </div>

          <div style={styles.apiRow}>
            <span style={styles.apiRowLabel}>Focused API</span>
            <ApiPicker apis={apis} value={selectedApiId} onChange={setSelectedApiId} />
          </div>

          <div style={styles.bottomGrid}>
            <ActivityChart data={traffic} window={trafficWindow} onWindowChange={setTrafficWindow} />
            <ErrorsPanel items={errors} />
          </div>
        </>
      )}
    </AppShell>
  );
}

const styles = {
  topGrid: {
    display: "grid",
    gridTemplateColumns: "1.3fr 1fr 1fr 1fr",
    gap: 18,
    marginBottom: 22,
  },
  apiRow: { display: "flex", alignItems: "center", gap: 12, marginBottom: 18 },
  apiRowLabel: { fontSize: 12, color: "var(--text-muted)" },
  bottomGrid: { display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: 18, alignItems: "stretch" },
};