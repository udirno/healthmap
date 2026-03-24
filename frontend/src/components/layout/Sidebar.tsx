'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Loader2, ChevronRight, Activity, Skull, Calendar, Percent } from 'lucide-react';
import { apiClient, PeriodMetrics, Region } from '@/lib/api-client';
import TrendChart from '@/components/charts/TrendChart';

interface SidebarProps {
  selectedDisease: string;
  onSelectDisease: (disease: string) => void;
  selectedRegion: string;
  onSelectRegion: (code: string, name: string) => void;
  dateRange: { start: string; end: string };
  onDateRangeChange: (range: { start: string; end: string }) => void;
  onMetricsUpdate?: (metrics: PeriodMetrics | null) => void;
}

const diseases = [
  { id: 'COVID-19', emoji: '🦠', color: '#3B82F6' },
  { id: 'Tuberculosis', emoji: '🫁', color: '#8B5CF6' },
  { id: 'Malaria', emoji: '🦟', color: '#10B981' },
];

export default function Sidebar({
  selectedDisease,
  onSelectDisease,
  selectedRegion,
  onSelectRegion,
  dateRange,
  onDateRangeChange,
  onMetricsUpdate,
}: SidebarProps) {
  const [metrics, setMetrics] = useState<PeriodMetrics | null>(null);
  const [regions, setRegions] = useState<Region[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [regionSearch, setRegionSearch] = useState('');
  const [showRegions, setShowRegions] = useState(false);
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    apiClient.getRegions().then(data => setRegions(data.filter(r => r.level === 'country'))).catch(() => {});
  }, []);

  // Auto-fetch metrics when region, disease, or date range changes
  useEffect(() => {
    if (!selectedDisease || !selectedRegion || !dateRange.start || !dateRange.end) return;

    setLoading(true);
    setError(null);
    apiClient.getPeriodMetrics(selectedDisease, selectedRegion, dateRange.start, dateRange.end)
      .then((data) => {
        setMetrics(data);
        onMetricsUpdate?.(data);
      })
      .catch(() => {
        setError('No data');
        setMetrics(null);
        onMetricsUpdate?.(null);
      })
      .finally(() => setLoading(false));
  }, [selectedRegion, selectedDisease, dateRange.start, dateRange.end]);

  const handleApplyFilters = () => {
    if (!selectedDisease || !selectedRegion || !dateRange.start || !dateRange.end) return;
    setApplying(true);
    setLoading(true);
    setError(null);
    apiClient.getPeriodMetrics(selectedDisease, selectedRegion, dateRange.start, dateRange.end)
      .then((data) => {
        setMetrics(data);
        onMetricsUpdate?.(data);
      })
      .catch(() => {
        setError('No data');
        setMetrics(null);
        onMetricsUpdate?.(null);
      })
      .finally(() => { setLoading(false); setApplying(false); });
  };

  const fmt = (n: number) => n >= 1e9 ? (n/1e9).toFixed(1)+'B' : n >= 1e6 ? (n/1e6).toFixed(1)+'M' : n >= 1e3 ? (n/1e3).toFixed(1)+'K' : n.toString();
  const regionName = regions.find(r => r.code === selectedRegion)?.name || selectedRegion;
  const filteredRegions = regions.filter(r => r.name.toLowerCase().includes(regionSearch.toLowerCase())).slice(0, 15);

  return (
    <div className="h-full flex flex-col bg-[#1e293b] rounded-xl overflow-hidden border border-slate-700">
      <div className="p-5 border-b border-slate-700">
        <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wide">Selection Filters</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Country Dropdown */}
        <div>
          <label className="text-xs font-semibold text-slate-400 mb-2 block uppercase">Country</label>
          <div className="relative">
            <input
              type="text"
              value={showRegions ? regionSearch : regionName}
              onChange={(e) => setRegionSearch(e.target.value)}
              onFocus={() => { setShowRegions(true); setRegionSearch(''); }}
              onBlur={() => setTimeout(() => setShowRegions(false), 200)}
              placeholder="Select country..."
              className="w-full bg-slate-800/50 text-slate-200 px-4 py-3 rounded-lg border border-slate-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm transition-all"
            />
            {showRegions && filteredRegions.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 rounded-lg shadow-xl border border-slate-700 max-h-48 overflow-y-auto z-50">
                {filteredRegions.map(r => (
                  <button
                    key={r.code}
                    onMouseDown={() => { onSelectRegion(r.code, r.name); setShowRegions(false); }}
                    className="w-full text-left px-4 py-2.5 text-slate-200 text-sm hover:bg-slate-700 transition-colors first:rounded-t-lg last:rounded-b-lg"
                  >
                    {r.name}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Disease Dropdown */}
        <div>
          <label className="text-xs font-semibold text-slate-400 mb-2 block uppercase">Disease</label>
          <select
            value={selectedDisease}
            onChange={(e) => onSelectDisease(e.target.value)}
            className="w-full bg-slate-800/50 text-slate-200 px-4 py-3 rounded-lg border border-slate-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm transition-all"
          >
            {diseases.map(d => (
              <option key={d.id} value={d.id}>{d.id}</option>
            ))}
          </select>
        </div>

        {/* Date Range */}
        <div>
          <label className="text-xs font-semibold text-slate-400 mb-2 block uppercase">Date Range</label>
          <div className="space-y-2">
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => onDateRangeChange({ ...dateRange, start: e.target.value })}
              className="w-full bg-slate-800/50 text-slate-200 px-4 py-3 rounded-lg border border-slate-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm transition-all"
            />
            <div className="text-center text-slate-500 text-xs font-medium">to</div>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => onDateRangeChange({ ...dateRange, end: e.target.value })}
              className="w-full bg-slate-800/50 text-slate-200 px-4 py-3 rounded-lg border border-slate-700 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none text-sm transition-all"
            />
          </div>
        </div>

        {/* Apply Button */}
        <button
          onClick={handleApplyFilters}
          disabled={applying}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 rounded-lg transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {applying ? 'Applying...' : 'Apply Filters'}
        </button>

        {/* Metrics & Trends */}
        <div>
          <h3 className="text-xs font-bold text-slate-400 mb-4 mt-6 uppercase tracking-wide">Metrics & Trends</h3>

          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-8 h-8 text-slate-500 animate-spin" />
            </div>
          ) : error ? (
            <div className="bg-slate-800/30 rounded-lg p-5 text-center border border-slate-700">
              <p className="text-slate-400 text-sm">{error}</p>
            </div>
          ) : metrics && (
            <div className="space-y-3">
              {/* Featured Card - Total Cases - Centered & Modern */}
              <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-5 shadow-xl shadow-blue-900/30">
                <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-3xl -mr-16 -mt-16" />
                <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full blur-2xl -ml-12 -mb-12" />

                <div className="relative">
                  <div className="flex items-center justify-center mb-4">
                    <div className="p-3 bg-white/15 rounded-2xl backdrop-blur-xl shadow-lg">
                      <Activity className="w-5 h-5 text-white" />
                    </div>
                  </div>

                  <div className="text-center mb-4">
                    <p className="text-xs font-medium text-blue-200 uppercase tracking-wider mb-2">Total Cases</p>
                    <p className="text-4xl font-black text-white mb-2">{fmt(metrics.total_new_cases)}</p>
                    <div className="inline-flex items-center justify-center p-2 bg-white/10 rounded-full backdrop-blur-sm">
                      {metrics.trend === 'increasing' ? (
                        <TrendingUp className="w-4 h-4 text-red-300" />
                      ) : metrics.trend === 'declining' ? (
                        <TrendingDown className="w-4 h-4 text-green-300" />
                      ) : (
                        <Minus className="w-4 h-4 text-white/60" />
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Stats Grid - Modern Cards */}
              <div className="grid grid-cols-2 gap-3">
                {/* Deaths Card */}
                <div className="relative overflow-hidden bg-gradient-to-br from-rose-600 to-pink-700 rounded-2xl p-4 shadow-lg shadow-rose-900/20 col-span-2">
                  <div className="absolute top-0 right-0 w-20 h-20 bg-white/5 rounded-full blur-2xl -mr-10 -mt-10" />
                  <div className="relative text-center">
                    <div className="inline-flex p-2.5 bg-white/15 rounded-xl mb-3 backdrop-blur-sm">
                      <Skull className="w-4 h-4 text-white" />
                    </div>
                    <p className="text-xs font-medium text-rose-100 uppercase tracking-wider mb-2">Deaths</p>
                    <p className="text-3xl font-black text-white">{fmt(metrics.total_new_deaths)}</p>
                  </div>
                </div>

                {/* Daily Average Card */}
                <div className="relative overflow-hidden bg-gradient-to-br from-violet-600 to-purple-700 rounded-2xl p-4 shadow-lg shadow-violet-900/20">
                  <div className="absolute top-0 right-0 w-16 h-16 bg-white/5 rounded-full blur-xl -mr-8 -mt-8" />
                  <div className="relative text-center">
                    <div className="inline-flex p-2 bg-white/15 rounded-xl mb-2.5 backdrop-blur-sm">
                      <Calendar className="w-3.5 h-3.5 text-white" />
                    </div>
                    <p className="text-[10px] font-medium text-violet-100 uppercase tracking-wider mb-1">Daily Avg</p>
                    <p className="text-xl font-black text-white mb-0.5">{fmt(Math.round(metrics.avg_daily_cases))}</p>
                    <p className="text-[10px] text-violet-200/80">Cases/day</p>
                  </div>
                </div>

                {/* Mortality Rate Card */}
                <div className="relative overflow-hidden bg-gradient-to-br from-teal-600 to-cyan-700 rounded-2xl p-4 shadow-lg shadow-teal-900/20">
                  <div className="absolute top-0 left-0 w-16 h-16 bg-white/5 rounded-full blur-xl -ml-8 -mt-8" />
                  <div className="relative text-center">
                    <div className="inline-flex p-2 bg-white/15 rounded-xl mb-2.5 backdrop-blur-sm">
                      <Percent className="w-3.5 h-3.5 text-white" />
                    </div>
                    <p className="text-[10px] font-medium text-teal-100 uppercase tracking-wider mb-1">Mortality</p>
                    <p className="text-xl font-black text-white mb-0.5">{metrics.mortality_rate.toFixed(1)}%</p>
                    <p className="text-[10px] text-teal-200/80">Case fatality</p>
                  </div>
                </div>
              </div>

              {/* Trend Chart */}
              <TrendChart
                disease={selectedDisease}
                region={selectedRegion}
                dateRange={dateRange}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}