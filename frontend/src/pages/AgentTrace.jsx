import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import StepTimeline from '../components/StepTimeline';
import DecisionBadge from '../components/DecisionBadge';
import { ArrowLeft } from 'lucide-react';

const AgentTrace = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Fix #9: Persist result in sessionStorage so page refresh doesn't lose data
  const result = React.useMemo(() => {
    if (location.state?.result) {
      sessionStorage.setItem('lastTraceResult', JSON.stringify(location.state.result));
      return location.state.result;
    }
    const saved = sessionStorage.getItem('lastTraceResult');
    return saved ? JSON.parse(saved) : null;
  }, [location.state]);

  if (!result) {
    return (
      <div className="max-w-3xl mx-auto py-12 px-4 text-center">
        <p>No trace data available.</p>
        <button onClick={() => navigate('/')} className="mt-4 text-blue-600 hover:underline">Go Back</button>
      </div>
    );
  }

  const { claim_id, reasoning_steps, final_decision, confidence_score } = result;

  return (
    <div className="max-w-3xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <button 
        onClick={() => navigate('/')}
        className="flex items-center text-sm font-medium text-gray-500 hover:text-gray-900 mb-8 transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-1" /> Back to Submit
      </button>

      <div className="mb-8">
        <h1 className="text-3xl font-extrabold text-gray-900">Agent Reasoning Trace</h1>
        <p className="mt-2 text-gray-500">Trace log for claim {claim_id}</p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 mb-8">
        <StepTimeline steps={reasoning_steps || []} />
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 flex flex-col items-center animate-fade-in-up" style={{ animationDelay: `${(reasoning_steps?.length || 0) * 300 + 300}ms`, animationFillMode: 'both' }}>
        <h3 className="text-lg font-bold text-gray-900 mb-4">Final Adjudication Decision</h3>
        <DecisionBadge decision={final_decision} className="text-lg px-6 py-3 mb-4" />
        
        {confidence_score !== null && (
          <p className="text-sm font-medium text-gray-500">
            AI Confidence Score: <span className="text-gray-900">{confidence_score}</span>
          </p>
        )}

        {final_decision === 'PENDING_HUMAN_REVIEW' && (
          <button 
            onClick={() => navigate('/dashboard')}
            className="mt-6 text-sm bg-yellow-100 hover:bg-yellow-200 text-yellow-800 font-bold py-2 px-4 rounded transition-colors"
          >
            Review in Dashboard
          </button>
        )}
      </div>
    </div>
  );
};

export default AgentTrace;
