'use client';

import { useState } from 'react';
import NavBar from '@/components/layout/NavBar';
import Sidebar from '@/components/layout/Sidebar';
import MapContainer from '@/components/map/MapContainer';
import AIInsightPanel from '@/components/layout/AIInsightPanel';
import { PeriodMetrics } from '@/lib/api-client';

export default function Home() {
  const [selectedDisease, setSelectedDisease] = useState('COVID-19');
  const [selectedRegion, setSelectedRegion] = useState('USA');
  const [selectedRegionName, setSelectedRegionName] = useState('United States');
  const [dateRange, setDateRange] = useState({
    start: '2022-01-01',
    end: '2022-12-31'
  });
  const [metrics, setMetrics] = useState<PeriodMetrics | null>(null);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [comparisonCountries, setComparisonCountries] = useState<Array<{ code: string; name: string }>>([]);

  const handleRegionSelect = (code: string, name?: string) => {
    if (comparisonMode) {
      // In comparison mode, add/remove from comparison list
      const exists = comparisonCountries.find(c => c.code === code);
      if (exists) {
        // Remove if already in list
        setComparisonCountries(comparisonCountries.filter(c => c.code !== code));
      } else if (comparisonCountries.length < 4) {
        // Add if less than 4 countries
        setComparisonCountries([...comparisonCountries, { code, name: name || code }]);
      }
    } else {
      // Normal mode - single selection
      setSelectedRegion(code);
      if (name) setSelectedRegionName(name);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-[#0f172a]">
      <NavBar />

      <div className="flex-1 flex gap-4 p-4 overflow-hidden">
        {/* Left: Filters Sidebar */}
        <div className="w-[340px] flex-shrink-0">
          <Sidebar
            selectedDisease={selectedDisease}
            onSelectDisease={setSelectedDisease}
            selectedRegion={selectedRegion}
            onSelectRegion={(code, name) => {
              setSelectedRegion(code);
              setSelectedRegionName(name);
            }}
            dateRange={dateRange}
            onDateRangeChange={setDateRange}
            onMetricsUpdate={setMetrics}
          />
        </div>

        {/* Center: Map - Full Height */}
        <main className="flex-1 flex flex-col overflow-hidden gap-3">
          <MapContainer
            selectedDisease={selectedDisease}
            selectedRegion={selectedRegion}
            selectedRegionName={selectedRegionName}
            dateRange={dateRange}
            onRegionSelect={handleRegionSelect}
            comparisonMode={comparisonMode}
            comparisonCountries={comparisonCountries}
            onToggleComparisonMode={() => {
              setComparisonMode(!comparisonMode);
              if (!comparisonMode) {
                // Entering comparison mode - add current selection
                setComparisonCountries([{ code: selectedRegion, name: selectedRegionName }]);
              } else {
                // Exiting comparison mode - clear list
                setComparisonCountries([]);
              }
            }}
          />

          {/* Comparison Panel */}
          {comparisonMode && comparisonCountries.length > 0 && (
            <div className="bg-[#1e293b] rounded-xl border border-slate-700 p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-slate-200">
                  Comparing {comparisonCountries.length} {comparisonCountries.length === 1 ? 'Country' : 'Countries'}
                </h3>
                <button
                  onClick={() => setComparisonCountries([])}
                  className="text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                  Clear All
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {comparisonCountries.map((country) => (
                  <div
                    key={country.code}
                    className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-600/20 border border-blue-500/30 rounded-lg"
                  >
                    <span className="text-sm text-blue-200">{country.name}</span>
                    <button
                      onClick={() => setComparisonCountries(comparisonCountries.filter(c => c.code !== country.code))}
                      className="text-blue-300 hover:text-white transition-colors"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>

        {/* Right: AI Insights (Always visible) */}
        <div className="w-[380px] flex-shrink-0">
          <AIInsightPanel
            selectedDisease={selectedDisease}
            selectedRegion={selectedRegion}
            dateRange={dateRange}
            onClose={() => {}} // No close button needed
          />
        </div>
      </div>
    </div>
  );
}