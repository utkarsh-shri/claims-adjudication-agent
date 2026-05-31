import React from 'react';
import DecisionBadge from './DecisionBadge';
import StepTimeline from './StepTimeline';
import { approveClaim, rejectClaim } from '../api/claims';

const ClaimCard = ({ claim, onReviewComplete }) => {
  const [expanded, setExpanded] = React.useState(false);
  const [loading, setLoading] = React.useState(false);
  
  const claimData = claim.claims || {};
  const steps = claimData.reasoning_steps || [];

  const handleApprove = async () => {
    setLoading(true);
    try {
      await approveClaim(claimData.claim_id, 'HUMAN_REVIEWER_1');
      onReviewComplete();
    } catch (e) {
      alert("Error approving claim: " + e.message);
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      await rejectClaim(claimData.claim_id, 'HUMAN_REVIEWER_1', 'Manual reviewer override');
      onReviewComplete();
    } catch (e) {
      alert("Error rejecting claim: " + e.message);
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden mb-4 transition-all duration-300">
      <div 
        className="p-6 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-750 flex items-center justify-between"
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <h3 className="font-bold text-lg text-gray-900 dark:text-white">Claim: {claimData.claim_id}</h3>
          <p className="text-sm text-gray-500 mt-1">
            Member: {claimData.member_id} • Drug: {claimData.drug_name} ({claimData.drug_ndc})
          </p>
        </div>
        <DecisionBadge decision="PENDING_HUMAN_REVIEW" />
      </div>

      {expanded && (
        <div className="p-6 border-t border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50">
          <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-4">Agent Reasoning Trace</h4>
          
          <div className="bg-white dark:bg-gray-900 p-4 rounded-lg shadow-inner mb-6">
            <StepTimeline steps={steps} />
          </div>

          <div className="flex gap-4">
            <button 
              onClick={handleApprove}
              disabled={loading}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 px-4 rounded-lg shadow-sm transition-colors disabled:opacity-50"
            >
              Approve Override
            </button>
            <button 
              onClick={handleReject}
              disabled={loading}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white font-semibold py-3 px-4 rounded-lg shadow-sm transition-colors disabled:opacity-50"
            >
              Reject Claim
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClaimCard;
