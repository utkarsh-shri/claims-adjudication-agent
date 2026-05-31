import React from 'react';

const ColdStartBanner = () => {
  return (
    <div className="bg-blue-50 border-b border-blue-100 px-4 py-3 text-center">
      <p className="text-sm text-blue-700 font-medium">
        <span className="mr-2">ℹ️</span>
        Note: The backend is hosted on Render's free tier. It may take 50+ seconds to spin up on the first request.
      </p>
    </div>
  );
};

export default ColdStartBanner;
