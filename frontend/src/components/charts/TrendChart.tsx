'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Loader2 } from 'lucide-react';
import { apiClient, TimeSeriesData } from '@/lib/api-client';

interface TrendChartProps {
  disease: string;
  region: string;
  dateRange: { start: string; end: string };
}

export default function TrendChart({ disease, region, dateRange }: TrendChartProps) {
  const [data, setData] = useState<TimeSeriesData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch time series data when disease, region, or date range changes
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      // Small delay to let metrics render first
      await new Promise(resolve => setTimeout(resolve, 100));

      try {
        const timeSeries = await apiClient.getTimeSeries(
          disease,
          region,
          dateRange.start,
          dateRange.end
        );

        if (timeSeries && timeSeries.length > 0) {
          setData(timeSeries);
        } else {
          setError('No visualization data available');
        }
      } catch (err) {
        console.error('Error fetching time series data:', err);
        setError('Failed to load chart data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [disease, region, dateRange.start, dateRange.end]);

  if (loading) {
    return (
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl p-3 border border-slate-700/50 shadow-lg">
        <div className="absolute top-0 right-0 w-16 h-16 bg-blue-500/5 rounded-full blur-2xl -mr-8 -mt-8" />
        <div className="relative">
          <h3 className="text-xs font-medium text-slate-300 mb-3 text-center uppercase tracking-wider">Cases Over Time</h3>
          <div className="h-[140px] flex flex-col justify-end gap-1 px-2">
            {/* Animated skeleton bars */}
            {[...Array(8)].map((_, i) => (
              <div key={i} className="flex items-end gap-1">
                <div
                  className="flex-1 bg-blue-500/20 rounded-t animate-pulse"
                  style={{
                    height: `${Math.random() * 80 + 20}%`,
                    animationDelay: `${i * 0.1}s`
                  }}
                />
              </div>
            ))}
          </div>
          <div className="mt-3 flex items-center justify-center gap-2">
            <Loader2 className="w-3 h-3 text-slate-500 animate-spin" />
            <span className="text-xs text-slate-500">Loading chart...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error || data.length === 0) {
    return (
      <div className="bg-slate-800/60 rounded-2xl p-3 border border-slate-700/50">
        <h3 className="text-xs font-medium text-slate-300 mb-2 text-center uppercase tracking-wider">Trend</h3>
        <div className="h-24 flex items-center justify-center text-slate-500 text-xs">
          {error || 'No data available'}
        </div>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-slate-800/80 to-slate-900/80 rounded-2xl p-3 border border-slate-700/50 shadow-lg">
      <div className="absolute top-0 right-0 w-16 h-16 bg-blue-500/5 rounded-full blur-2xl -mr-8 -mt-8" />
      <div className="relative">
        <h3 className="text-xs font-medium text-slate-300 mb-3 text-center uppercase tracking-wider">Cases Over Time</h3>
        <ResponsiveContainer width="100%" height={140}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 9, fill: '#94a3b8' }}
              tickFormatter={(date) => {
                const d = new Date(date);
                return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              }}
            />
            <YAxis tick={{ fontSize: 9, fill: '#94a3b8' }} width={35} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '12px',
                fontSize: 10,
                padding: '6px 10px'
              }}
              labelStyle={{ color: '#e2e8f0', fontWeight: 600, fontSize: 10 }}
              itemStyle={{ color: '#cbd5e1', fontSize: 10 }}
            />
            <Line
              type="monotone"
              dataKey="new_cases"
              stroke="#3b82f6"
              strokeWidth={2.5}
              name="Cases"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="new_deaths"
              stroke="#f59e0b"
              strokeWidth={2.5}
              name="Deaths"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}