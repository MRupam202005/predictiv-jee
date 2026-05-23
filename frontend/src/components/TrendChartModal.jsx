import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export default function TrendChartModal({ isOpen, onClose, queryParams, predictedCutoff }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && queryParams) {
      setLoading(true);
      fetch('http://127.0.0.1:8000/api/trends', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(queryParams)
      })
      .then(res => res.json())
      .then(result => {
        // We append the 2026 prediction to the historical data
        const combined = [
          ...result.trends,
          { year: 2026, closing_rank: predictedCutoff, isPrediction: true }
        ];
        setData(combined);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
    }
  }, [isOpen, queryParams, predictedCutoff]);

  if (!isOpen) return null;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const isPred = payload[0].payload.isPrediction;
      return (
        <div className="bg-slate-900 border border-white/10 p-3 rounded-xl shadow-xl">
          <p className="text-white font-bold mb-1">{label} {isPred ? '(Predicted)' : '(Actual)'}</p>
          <p className="text-blue-400 text-sm">
            Closing Rank: <span className="font-bold">{payload[0].value.toLocaleString()}</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="bg-slate-950 border border-white/10 rounded-2xl w-full max-w-2xl p-6 shadow-2xl relative"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors"
        >
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <h3 className="text-xl font-bold text-white mb-1">Historical Cutoff Trends</h3>
        <p className="text-sm text-slate-400 mb-6">
          {queryParams.institute} — <span className="text-slate-300">{queryParams.program}</span>
        </p>

        {loading ? (
          <div className="h-64 flex items-center justify-center">
             <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : data.length === 1 ? (
          <div className="h-64 flex items-center justify-center text-slate-500">
             No historical data found for this specific combination.
          </div>
        ) : (
          <div className="h-72 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data} margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis 
                  dataKey="year" 
                  stroke="#ffffff50" 
                  tick={{fill: '#ffffff50', fontSize: 12}}
                  tickMargin={10}
                />
                <YAxis 
                  stroke="#ffffff50" 
                  tick={{fill: '#ffffff50', fontSize: 12}}
                  tickFormatter={(val) => val.toLocaleString()}
                  domain={['auto', 'auto']}
                  reversed={true} 
                />
                <Tooltip content={<CustomTooltip />} />
                <Line 
                  type="monotone" 
                  dataKey="closing_rank" 
                  stroke="#3b82f6" 
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#1e3a8a', stroke: '#3b82f6', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#3b82f6' }}
                />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-center text-xs text-slate-500 mt-4">
              *Lower rank indicates higher competition. Rank 1 is at the top.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
