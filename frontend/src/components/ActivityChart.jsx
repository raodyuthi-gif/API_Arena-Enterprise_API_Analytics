import { AreaChart, Area, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function ActivityChart({ data = [], window: activeWindow, onWindowChange }) {
  const chartData = data.map((point) => ({
    label: new Date(point.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    requests: point.request_count,
  }));

  return (
    <div style={styles.card}>
      <div style={styles.headerRow}>
        <div>
          <div style={styles.title}>Activity</div>
          <div style={styles.subtitle}>Request volume for the selected API</div>
        </div>
        <select
          value={activeWindow}
          onChange={(e) => onWindowChange?.(e.target.value)}
          style={styles.select}
        >
          <option value="1h">Last hour</option>
          <option value="24h">Last 24h</option>
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
        </select>
      </div>

      <div style={{ width: "100%", height: 220, marginTop: 12 }}>
        {chartData.length === 0 ? (
          <div style={styles.empty}>No traffic recorded for this window yet.</div>
        ) : (
          <ResponsiveContainer>
            <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="activityFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity={0.45} />
                  <stop offset="100%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="label"
                tick={{ fill: "var(--text-muted)", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                minTickGap={24}
              />
              <YAxis tick={{ fill: "var(--text-muted)", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  background: "var(--bg-panel-raised)",
                  border: "1px solid var(--border-strong)",
                  borderRadius: 10,
                  fontSize: 12,
                }}
                labelStyle={{ color: "var(--text-secondary)" }}
              />
              <Area
                type="monotone"
                dataKey="requests"
                stroke="#22c55e"
                strokeWidth={2.5}
                fill="url(#activityFill)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

const styles = {
  card: {
    background: "var(--bg-panel)",
    border: "1px solid var(--border-subtle)",
    borderRadius: "var(--radius-lg)",
    padding: 22,
  },
  headerRow: { display: "flex", alignItems: "flex-start", justifyContent: "space-between" },
  title: { fontFamily: "var(--font-display)", fontSize: 17, fontWeight: 600 },
  subtitle: { fontSize: 12, color: "var(--text-muted)", marginTop: 4 },
  select: {
    background: "var(--bg-panel-raised)",
    border: "1px solid var(--border-strong)",
    color: "var(--text-primary)",
    borderRadius: "var(--radius-sm)",
    padding: "6px 10px",
    fontSize: 12,
  },
  empty: {
    height: "100%",
    display: "grid",
    placeItems: "center",
    color: "var(--text-muted)",
    fontSize: 13,
  },
};