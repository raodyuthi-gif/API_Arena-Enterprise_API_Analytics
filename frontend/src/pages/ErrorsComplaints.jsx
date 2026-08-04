import { useEffect, useState } from "react";
import client from "../api/client.js";
import AppShell from "../components/AppShell.jsx";
import ApiPicker from "../components/ApiPicker.jsx";
import ErrorsPanel from "../components/ErrorsPanel.jsx";
import StatCard from "../components/StatCard.jsx";

export default function ErrorsComplaints() {
  const [apis, setApis] = useState([]);
  const [selectedApiId, setSelectedApiId] = useState("");
  const [windowSize, setWindowSize] = useState("24h");
  const [errorData, setErrorData] = useState(null);

  useEffect(() => {
    client.get("/apis", { params: { page_size: 50 } }).then((res) => {
      setApis(res.data.items || []);
      if (res.data.items?.length) setSelectedApiId(res.data.items[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedApiId) return;
    client
      .get("/analytics/errors", { params: { api_id: selectedApiId, window: windowSize } })
      .then((res) => setErrorData(res.data))
      .catch(() => setErrorData(null));
  }, [selectedApiId, windowSize]);

  return (
    <AppShell title="Errors & Complaints" subtitle="Failure hotspots for the selected API and window">
      <div style={styles.controls}>
        <ApiPicker apis={apis} value={selectedApiId} onChange={setSelectedApiId} />
        <select value={windowSize} onChange={(e) => setWindowSize(e.target.value)} style={styles.select}>
          <option value="1h">Last hour</option>
          <option value="24h">Last 24h</option>
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
        </select>
      </div>

      <div style={styles.statRow}>
        <StatCard
          label="Total Errors"
          value={errorData?.total_errors ?? "—"}
          tone={errorData?.total_errors ? "bad" : "good"}
        />
        <StatCard
          label="Overall Error Rate"
          value={errorData ? `${errorData.overall_error_rate.toFixed(2)}%` : "—"}
          tone={errorData?.overall_error_rate > 5 ? "bad" : "good"}
        />
      </div>

      <ErrorsPanel items={errorData?.top_failing_endpoints || []} />
    </AppShell>
  );
}

const styles = {
  controls: { display: "flex", gap: 12, marginBottom: 20 },
  select: {
    background: "var(--bg-panel-raised)",
    border: "1px solid var(--border-strong)",
    color: "var(--text-primary)",
    borderRadius: "var(--radius-sm)",
    padding: "9px 12px",
    fontSize: 13,
  },
  statRow: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20, maxWidth: 520 },
};