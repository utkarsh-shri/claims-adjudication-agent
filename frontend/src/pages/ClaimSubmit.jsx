import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { processClaim } from '../api/claims';
import { Activity } from 'lucide-react';

const ClaimSubmit = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    claim_id: `CLM-${Math.floor(Math.random() * 1000000)}`,
    member_id: 'MBR-0000001',
    drug_ndc: 'NDC-ATORVA-40',
    drug_name: 'Atorvastatin 40mg',
    prescriber_npi: 'NPI-123456',
    quantity: 30,
    days_supply: 30,
    diagnosis_code: 'E78.5'
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await processClaim(formData);
      // Pass the result state to the next page
      navigate('/trace', { state: { result } });
    } catch (error) {
      alert("Error processing claim. Check console or make sure backend is running.");
      console.error(error);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-10">
        <Activity className="w-12 h-12 text-blue-600 mx-auto mb-4" />
        <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">AI Claims Adjudication</h1>
        <p className="mt-4 text-lg text-gray-500">Submit a pharmacy claim for automated agentic processing.</p>
      </div>

      <div className="bg-white shadow-xl rounded-2xl overflow-hidden border border-gray-100">
        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-semibold text-gray-700">Claim ID</label>
              <input type="text" name="claim_id" value={formData.claim_id} onChange={handleChange} required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700">Member ID</label>
              <input type="text" name="member_id" value={formData.member_id} onChange={handleChange} required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700">Drug NDC</label>
              <input type="text" name="drug_ndc" value={formData.drug_ndc} onChange={handleChange} required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700">Drug Name</label>
              <input type="text" name="drug_name" value={formData.drug_name} onChange={handleChange} required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700">Quantity</label>
              <input type="number" name="quantity" value={formData.quantity} onChange={handleChange} required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700">Days Supply</label>
              <input type="number" name="days_supply" value={formData.days_supply} onChange={handleChange} required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700">Diagnosis Code</label>
              <input type="text" name="diagnosis_code" value={formData.diagnosis_code} onChange={handleChange} required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700">Prescriber NPI</label>
              <input type="text" name="prescriber_npi" value={formData.prescriber_npi} onChange={handleChange} required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border" />
            </div>
          </div>
          
          <div className="pt-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all"
            >
              {loading ? 'Processing via Agent...' : 'Submit Claim'}
            </button>
          </div>
        </form>
      </div>
      
      <div className="mt-8 text-center">
        <button onClick={() => navigate('/dashboard')} className="text-sm text-blue-600 hover:text-blue-500 font-medium">
          → Go to Human Reviewer Dashboard
        </button>
      </div>
    </div>
  );
};

export default ClaimSubmit;
