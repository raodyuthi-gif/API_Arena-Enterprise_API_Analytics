import { useEffect, useState } from "react";
import { LineChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import client from "../api/client.js";
import AppShell from "../components/AppShell.jsx";
import ApiPicker from "../components/ApiPicker.jsx";

export default function ForecastLab() {
  const [apis, setApis] = useState([]);
  const [selectedApiId, setSelectedApiId] = useState("");
  const [modelType, setModelType] = useState("prophet");
  const [lookbackDays, setLookbackDays] = useState(30);
  const [training, setTraining] = useState(false);
  const [trainResult, setTrainResult] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    client.get("/apis", { params: { page_size: 50 } }).then((res) => {
      setApis(res.data.items || []);
      if (res.data.items?.length) setSelectedApiId(res.data.items[0].id);
    });
  }, []);

  async function handleTrain() {
    if (!selectedApiId) return;
    setTraining(true);
    setErrorMsg("");
    try {
      const { data } = await client.post(
        `/forecast/train`,
        { model_type: modelType, lookback_days: Number(lookbackDays) },
        { params: { api_id: selectedApiId } }
      );
      setTrainResult(data);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || "Training failed.");
    } finally {
      setTraining(false);
    }
  }

  async function loadForecast() {
    if (!selectedApiId) return;
    try {
      const { data } = await client.get(`/forecast/${selectedApiId}`);
      setForecast(data);
    } catch {
      setForecast(null);
    }
  }

  const chartData = (forecast?.data || []).map((p) => ({
    label: new Date(p.timestamp).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit" }),
    predicted: p.predicted_requests,
  }));

  return (
    <AppShell title="Forecast Lab" subtitle="Train and inspect traffic forecasting models · Analyst / Admin">
      <div style={styles.panel}>
        <div style={styles.row}>
          <ApiPicker apis={apis} value={selectedApiId} onChange={setSelectedApiId} />
          <select value={modelType} onChange={(e) => setModelType(e.target.value)} style={styles.select}>
            <option value="prophet">Prophet</option>
            <option value="ridge">Ridge Regression</option>
          </select>
          <input
            type="number"
            min={7}
            max={90}
            value={lookbackDays}
            onChange={(e) => setLookbackDays(e.target.value)}
            style={styles.input}
          />
          <span style={styles.unit}>days lookback</span>
          <button onClick={handleTrain} disabled={training} style={styles.primaryBtn}>
            {training ? "Training…" : "Train model"}
          </button>
          <button onClick={loadForecast} style={styles.secondaryBtn}>
            Load forecast
          </button>
        </div>

        {errorMsg && <div style={styles.error}>{errorMsg}</div>}

        {trainResult && (
          <div style={styles.resultRow}>
            <span>Status: {trainResult.status}</span>
            <span>Samples: {trainResult.training_samples}</span>
            <span>MAE: {trainResult.mae?.toFixed(2) ?? "—"}</span>
            <span>MAPE: {trainResult.mape?.toFixed(2) ?? "—"}%</span>
          </div>
        )}
      </div>

      <div style={styles.chartCard}>
        <div style={styles.chartTitle}>Predicted request volume</div>
        <div style={{ width: "100%", height: 280, marginTop: 10 }}>
          {chartData.length === 0 ? (
            <div style={styles.empty}>Train a model, then load the forecast to see predictions here.</div>
          ) : (
            <ResponsiveContainer>
              <LineChart data={chartData} margin={{ left: -18, right: 8, top: 8 }}>
                <XAxis dataKey="label" tick={{ fill: "var(--text-muted)", fontSize: 11 }} minTickGap={30} />
                <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ background: "var(--bg-panel-raised)", border: "1px solid var(--border-strong)", borderRadius: 10 }}
                />
                <Line type="monotone" dataKey="predicted" stroke="#22c55e" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </AppShell>
  );
}

const styles = {
  panel: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-lg)",
    padding: 20,
    marginBottom: 20,
  },
  row: { display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" },
  select: {
    background: "var(--bg-panel-raised)",
    border: "1px solid var(--border-strong)",
    color: "var(--text-primary)",
    borderRadius: "var(--radius-sm)",
    padding: "9px 12px",
    fontSize: 13,
  },
  input: {
    width: 70,
    background: "var(--bg-panel-raised)",
    border: "1px solid var(--border-strong)",
    color: "var(--text-primary)",
    borderRadius: "var(--radius-sm)",
    padding: "9px 10px",
    fontSize: 13,
  },
  unit: { fontSize: 12, color: "var(--text-muted)" },
  primaryBtn: {
    background: "var(--accent-gradient)",
    border: "none",
    color: "#08150c",
    fontWeight: 700,
    borderRadius: "var(--radius-sm)",
    padding: "9px 16px",
    fontSize: 13,
    cursor: "pointer",
  },
  secondaryBtn: {
    background: "transparent",
    border: "1px solid var(--border-strong)",
    color: "var(--text-primary)",
    borderRadius: "var(--radius-sm)",
    padding: "9px 16px",
    fontSize: 13,
    cursor: "pointer",
  },
  error: { marginTop: 14, color: "#ff9d9f", fontSize: 13 },
  resultRow: { display: "flex", gap: 20, marginTop: 16, fontSize: 12.5, color: "var(--text-secondary)" },
  chartCard: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-lg)",
    padding: 20,
  },
  chartTitle: { fontFamily: "var(--font-display)", fontSize: 16, fontWeight: 600 },
  empty: { height: "100%", display: "grid", placeItems: "center", color: "var(--text-muted)", fontSize: 13 },
};