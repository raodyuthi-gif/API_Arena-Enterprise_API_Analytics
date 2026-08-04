import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ApiRegistry from "./pages/ApiRegistry.jsx";
import ErrorsComplaints from "./pages/ErrorsComplaints.jsx";
import ForecastLab from "./pages/ForecastLab.jsx";
import AdminConsole from "./pages/AdminConsole.jsx";
import NotAuthorized from "./pages/NotAuthorized.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/not-authorized" element={<NotAuthorized />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute roles={["admin", "analyst", "viewer"]}>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/apis"
        element={
          <ProtectedRoute roles={["admin", "analyst", "viewer"]}>
            <ApiRegistry />
          </ProtectedRoute>
        }
      />
      <Route
        path="/errors"
        element={
          <ProtectedRoute roles={["admin", "analyst", "viewer"]}>
            <ErrorsComplaints />
          </ProtectedRoute>
        }
      />
      <Route
        path="/forecast"
        element={
          <ProtectedRoute roles={["admin", "analyst"]}>
            <ForecastLab />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute roles={["admin"]}>
            <AdminConsole />
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}