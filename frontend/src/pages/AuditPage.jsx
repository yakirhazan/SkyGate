import { useState } from 'react';
import axios from 'axios';
import { motion } from 'framer-motion';

const AuditPage = () => {
  const [businessId, setBusinessId] = useState('');
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/audit', { business_id: businessId, url });
      setResult(response.data);
    } catch (error) {
      setResult({ error: 'Audit failed' });
    }
  };

  return (
    <motion.div
      initial={{ y: 20 }}
      animate={{ y: 0 }}
      className="bg-white p-6 rounded-lg shadow-lg max-w-2xl mx-auto"
    >
      <h2 className="text-2xl font-bold mb-4 text-primary">Website Audit</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Business ID</label>
          <input
            type="text"
            value={businessId}
            onChange={(e) => setBusinessId(e.target.value)}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-secondary focus:border-secondary"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Website URL</label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-secondary focus:border-secondary"
            required
          />
        </div>
        <button
          type="submit"
          className="bg-secondary text-white px-4 py-2 rounded-md hover:bg-blue-700 transition w-full"
        >
          Run Audit
        </button>
      </form>
      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded-md">
          {result.error ? (
            <p className="text-red-600">{result.error}</p>
          ) : (
            <div>
              <p className="text-green-600">{result.message}</p>
              {result.issues && (
                <ul className="mt-2 list-disc pl-5">
                  {result.issues.map((issue, index) => (
                    <li key={index} className="text-gray-700">{issue}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default AuditPage;
