import React from 'react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';
import { CheckCircle, XCircle, Clock } from 'lucide-react';

const DecisionBadge = ({ decision, className }) => {
  if (!decision) return null;

  const isApproved = decision === 'APPROVED';
  const isDenied = decision === 'DENIED';
  const isPending = decision === 'PENDING_HUMAN_REVIEW';

  const baseClass = "inline-flex items-center px-4 py-2 rounded-full font-bold text-sm uppercase tracking-wide shadow-sm";
  
  const colors = clsx(
    isApproved && "bg-green-100 text-green-700 border border-green-200",
    isDenied && "bg-red-100 text-red-700 border border-red-200",
    isPending && "bg-yellow-100 text-yellow-700 border border-yellow-200"
  );

  return (
    <div className={twMerge(baseClass, colors, className)}>
      {isApproved && <CheckCircle className="w-5 h-5 mr-2" />}
      {isDenied && <XCircle className="w-5 h-5 mr-2" />}
      {isPending && <Clock className="w-5 h-5 mr-2" />}
      {decision.replace(/_/g, ' ')}
    </div>
  );
};

export default DecisionBadge;
