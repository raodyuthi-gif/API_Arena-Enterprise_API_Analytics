import Sidebar from "./Sidebar.jsx";
import Topbar from "./Topbar.jsx";

export default function AppShell({ title, subtitle, onSearch, children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-app)" }}>
      <Sidebar />
      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <Topbar title={title} subtitle={subtitle} onSearch={onSearch} />
        <main style={{ padding: 32, flex: 1, overflowY: "auto" }}>{children}</main>
      </div>
    </div>
  );
}