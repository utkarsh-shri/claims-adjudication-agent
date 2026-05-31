import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ClaimSubmit from './pages/ClaimSubmit';
import AgentTrace from './pages/AgentTrace';
import ReviewerDashboard from './pages/ReviewerDashboard';
import ColdStartBanner from './components/ColdStartBanner';

function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <ColdStartBanner />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<ClaimSubmit />} />
          <Route path="/trace" element={<AgentTrace />} />
          <Route path="/dashboard" element={<ReviewerDashboard />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
