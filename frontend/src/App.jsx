import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import ClaimSubmit from './pages/ClaimSubmit';
import AgentTrace from './pages/AgentTrace';
import ReviewerDashboard from './pages/ReviewerDashboard';
import Login from './pages/Login';
import ColdStartBanner from './components/ColdStartBanner';
import { AuthProvider, useAuth } from './context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

function AppContent() {
  return (
    <div className="min-h-screen flex flex-col">
      <ColdStartBanner />
      <main className="flex-1">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><ClaimSubmit /></ProtectedRoute>} />
          <Route path="/trace" element={<ProtectedRoute><AgentTrace /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><ReviewerDashboard /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
