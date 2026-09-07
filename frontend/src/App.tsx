import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { LocationProvider } from "./context/LocationContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import LocationSelectionPage from "./pages/LocationSelectionPage";
import RecommendPage from "./pages/RecommendPage";
import FinancialCalculatorPage from "./pages/FinancialCalculatorPage";
import SchemesPage from "./pages/SchemesPage";
import MapPage from "./pages/MapPage";
import ReportPage from "./pages/ReportPage";

export default function App() {
  return (
    <AuthProvider>
      <LocationProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/location" element={<ProtectedRoute><LocationSelectionPage /></ProtectedRoute>} />
            <Route path="/recommend" element={<ProtectedRoute><RecommendPage /></ProtectedRoute>} />
            <Route path="/financial-calculator" element={<ProtectedRoute><FinancialCalculatorPage /></ProtectedRoute>} />
            <Route path="/schemes" element={<ProtectedRoute><SchemesPage /></ProtectedRoute>} />
            <Route path="/map" element={<ProtectedRoute><MapPage /></ProtectedRoute>} />
            <Route path="/reports/:id" element={<ProtectedRoute><ReportPage /></ProtectedRoute>} />

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </LocationProvider>
    </AuthProvider>
  );
}
