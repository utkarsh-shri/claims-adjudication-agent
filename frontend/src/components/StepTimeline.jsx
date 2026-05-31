import React from 'react';
import { CheckCircle, XCircle, Clock } from 'lucide-react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

const StepTimeline = ({ steps }) => {
  return (
    <div className="flex flex-col space-y-4 my-8 relative">
      {/* Vertical line connecting steps */}
      <div className="absolute left-[23px] top-4 bottom-4 w-0.5 bg-gray-200 dark:bg-gray-700 z-0"></div>
      
      {steps.map((stepText, index) => {
        // Extract the icon string from text, e.g., "ELIGIBILITY ✅: ..."
        const isSuccess = stepText.includes('✅');
        const isFailure = stepText.includes('❌');
        const isPending = stepText.includes('⏳') || (!isSuccess && !isFailure);

        const iconClass = twMerge(
          "relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-4 border-white dark:border-gray-900",
          isSuccess ? "bg-green-100 text-green-600" : "",
          isFailure ? "bg-red-100 text-red-600" : "",
          isPending ? "bg-yellow-100 text-yellow-600" : ""
        );

        // Remove the emoji from the display text for cleaner look, optional. Let's keep it if we just want raw string or we can strip it.
        const cleanText = stepText.replace(/[✅❌⏳]/g, '').trim();

        return (
          <div 
            key={index} 
            className="flex items-start opacity-0 translate-y-4 animate-fade-in-up"
            style={{ animationDelay: `${index * 300}ms`, animationFillMode: 'forwards' }}
          >
            <div className={iconClass}>
              {isSuccess && <CheckCircle className="w-6 h-6" />}
              {isFailure && <XCircle className="w-6 h-6" />}
              {isPending && <Clock className="w-6 h-6" />}
            </div>
            <div className="ml-4 mt-2 p-4 bg-white dark:bg-gray-800 rounded-xl shadow-sm flex-1 border border-gray-100 dark:border-gray-700 hover:shadow-md transition-shadow">
              <p className="text-gray-700 dark:text-gray-300 font-medium leading-relaxed">
                {cleanText}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StepTimeline;
