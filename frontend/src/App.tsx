import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import { useOnboardingStatus } from "./hooks/useOnboardingStatus";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import OnboardingPage from "./pages/OnboardingPage";
import DashboardPage from "./pages/DashboardPage";
import FeedbackPage from "./pages/FeedbackPage";
import CustomersPage from "./pages/CustomersPage";
import CustomerProfilePage from "./pages/CustomerProfilePage";
import SpecsPage from "./pages/SpecsPage";
import SpecDetailPage from "./pages/SpecDetailPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import SettingsPage from "./pages/SettingsPage";
import AppLayout from "./components/layout/AppLayout";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-gray-100">Loading...</div>
      </div>
    );
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function OnboardingGuard({ children }: { children: React.ReactNode }) {
  const { status, loading } = useOnboardingStatus();
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-gray-100">Loading...</div>
      </div>
    );
  }
  if (status && !status.completed) {
    return <Navigate to="/onboarding" replace />;
  }
  return <>{children}</>;
}

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route
        path="/onboarding"
        element={
          <PrivateRoute>
            <OnboardingPage />
          </PrivateRoute>
        }
      />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <OnboardingGuard>
              <AppLayout>
                <DashboardPage />
              </AppLayout>
            </OnboardingGuard>
          </PrivateRoute>
        }
      />
      <Route
        path="/feedback"
        element={
          <PrivateRoute>
            <OnboardingGuard>
              <AppLayout>
                <FeedbackPage />
              </AppLayout>
            </OnboardingGuard>
          </PrivateRoute>
        }
      />
      <Route
        path="/customers/:id"
        element={
          <PrivateRoute>
            <OnboardingGuard>
              <AppLayout>
                <CustomerProfilePage />
              </AppLayout>
            </OnboardingGuard>
          </PrivateRoute>
        }
      />
      <Route
        path="/customers"
        element={
          <PrivateRoute>
            <OnboardingGuard>
              <AppLayout>
                <CustomersPage />
              </AppLayout>
            </OnboardingGuard>
          </PrivateRoute>
        }
      />
      <Route
        path="/specs"
        element={
          <PrivateRoute>
            <OnboardingGuard>
              <AppLayout>
                <SpecsPage />
              </AppLayout>
            </OnboardingGuard>
          </PrivateRoute>
        }
      />
      <Route
        path="/specs/:id"
        element={
          <PrivateRoute>
            <OnboardingGuard>
              <AppLayout>
                <SpecDetailPage />
              </AppLayout>
            </OnboardingGuard>
          </PrivateRoute>
        }
      />
      <Route
        path="/analytics"
        element={
          <PrivateRoute>
            <OnboardingGuard>
              <AppLayout>
                <AnalyticsPage />
              </AppLayout>
            </OnboardingGuard>
          </PrivateRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <PrivateRoute>
            <OnboardingGuard>
              <AppLayout>
                <SettingsPage />
              </AppLayout>
            </OnboardingGuard>
          </PrivateRoute>
        }
      />
      <Route
        path="/"
        element={
          <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
        }
      />
    </Routes>
  );
}

export default App;
