import React, { useState, useEffect } from 'react';
import { apiService, type PollCandlestickData } from '../services/api';
import { PollCandlestickChart } from './PollCandlestickChart';

export const HerdPerformance: React.FC = () => {
  const [pollData, setPollData] = useState<PollCandlestickData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHerdPerformance() {
      try {
        setLoading(true);
        const response = await apiService.getHerdPerformance();

        if (response.success) {
          // Filter out tied polls (where vote counts are equal)
          const untiedPolls = response.data.filter(
            pollData => pollData.poll.optionAVotes !== pollData.poll.optionBVotes
          );
          setPollData(untiedPolls);
        } else {
          setError('Failed to load herd performance data');
        }
      } catch (err) {
        console.error('Error fetching herd performance:', err);
        setError('Failed to load herd performance data');
      } finally {
        setLoading(false);
      }
    }

    fetchHerdPerformance();
  }, []);

  if (loading) {
    return (
      <div className="bg-dark-500 rounded-lg p-6 shadow-lg">
        <h2 className="text-lg font-bold text-gray-50 mb-6 text-center">Herd Performance</h2>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">Loading performance data...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-dark-500 rounded-lg p-6 shadow-lg">
        <h2 className="text-lg font-bold text-gray-50 mb-6 text-center">Herd Performance</h2>
        <div className="flex items-center justify-center h-64">
          <div className="text-red-400">{error}</div>
        </div>
      </div>
    );
  }

  if (pollData.length === 0) {
    return (
      <div className="bg-dark-500 rounded-lg p-6 shadow-lg">
        <h2 className="text-lg font-bold text-gray-50 mb-6 text-center">Herd Performance</h2>
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-400">No performance data available yet.</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-dark-500 rounded-lg p-6 shadow-lg">
      <h2 className="text-lg font-bold text-gray-50 mb-6 text-center">Herd Performance</h2>

      {/* Grid Layout: 2 columns on large screens, 1 on mobile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {pollData.map((data) => (
          <PollCandlestickChart key={data.poll.id} pollData={data} />
        ))}
      </div>
    </div>
  );
};
