import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import RegisterCoach from './pages/RegisterCoach';
import CoachDashboard from './pages/coach/Dashboard';
import ClientDashboard from './pages/client/Dashboard';
import ClientList from './pages/coach/ClientList';
import ApplicationList from './pages/common/ApplicationList';
import AppointmentList from './pages/common/AppointmentList';
import ResumeEditor from './pages/client/ResumeEditor';
import ResumeReview from './pages/coach/ResumeReview';
import ClientProfile from './pages/client/Profile';
import CoachProfile from './pages/coach/Profile';
import AvailabilityManagement from './pages/coach/AvailabilityManagement';
import AdminDashboard from './pages/AdminDashboard';

// ProtectedRoute component
const ProtectedRoute = ({ children, requiredRole }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user.user_type !== requiredRole) {
    return <Navigate to="/" replace />;
  }

  return children;
};

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/register/coach" element={<RegisterCoach />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            {user?.role === 'super_admin' ? (
              <Navigate to="/admin/dashboard" replace />
            ) : user?.user_type === 'coach' ? (
              <Navigate to="/coach/dashboard" replace />
            ) : (
              <Navigate to="/client/dashboard" replace />
            )}
          </ProtectedRoute>
        }
      />

      {/* Admin routes */}
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />

      {/* Coach routes */}
      <Route
        path="/coach/dashboard"
        element={
          <ProtectedRoute requiredRole="coach">
            <CoachDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/coach/profile"
        element={
          <ProtectedRoute requiredRole="coach">
            <CoachProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/coach/clients"
        element={
          <ProtectedRoute requiredRole="coach">
            <ClientList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/coach/resumes/pending"
        element={
          <ProtectedRoute requiredRole="coach">
            <ResumeReview />
          </ProtectedRoute>
        }
      />
      <Route
        path="/coach/availability"
        element={
          <ProtectedRoute requiredRole="coach">
            <AvailabilityManagement />
          </ProtectedRoute>
        }
      />

      {/* Client routes */}
      <Route
        path="/client/dashboard"
        element={
          <ProtectedRoute requiredRole="client">
            <ClientDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/client/profile"
        element={
          <ProtectedRoute requiredRole="client">
            <ClientProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/client/resume"
        element={
          <ProtectedRoute requiredRole="client">
            <ResumeEditor />
          </ProtectedRoute>
        }
      />

      {/* Common routes */}
      <Route
        path="/applications"
        element={
          <ProtectedRoute>
            <ApplicationList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/appointments"
        element={
          <ProtectedRoute>
            <AppointmentList />
          </ProtectedRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;
