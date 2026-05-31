import React, { useEffect, useState } from 'react';
import { getPendingClaims } from '../api/claims';
import ClaimCard from '../components/ClaimCard';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Inbox } from 'lucide-react';

const ReviewerDashboard = () => {
  const navigate = useNavigate();
  const [pendingClaims, setPendingClaims] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPending = async () => {
    setLoading(true);
    try {
      const data = await getPendingClaims();
      setPendingClaims(data.pending_reviews || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  return (
    <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-end mb-8 border-b border-gray-200 pb-5">
        <div>
          <button 
            onClick={() => navigate('/')}
            className="flex items-center text-sm font-medium text-gray-500 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-1" /> Back to Submit
          </button>
          <h1 className="text-3xl font-extrabold text-gray-900">Reviewer Dashboard</h1>
          <p className="mt-2 text-gray-500">Manage claims flagged for human-in-the-loop review</p>
        </div>
        <button 
          onClick={fetchPending}
          className="text-sm bg-white hover:bg-gray-50 border border-gray-300 text-gray-700 font-semibold py-2 px-4 rounded shadow-sm transition-colors"
        >
          Refresh Queue
        </button>
      </div>

      {loading ? (
        <div className="text-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500 font-medium">Loading queue...</p>
        </div>
      ) : pendingClaims.length === 0 ? (
        <div className="text-center py-20 bg-gray-50 rounded-2xl border border-dashed border-gray-300">
          <Inbox className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900">All caught up!</h3>
          <p className="text-gray-500">There are no claims pending human review.</p>
        </div>
      ) : (
        <div>
          {pendingClaims.map(claim => (
            <ClaimCard key={claim.id} claim={claim} onReviewComplete={fetchPending} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ReviewerDashboard;
