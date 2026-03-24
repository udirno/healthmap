'use client';

import { useEffect, useRef, useState } from 'react';
import mapboxgl, { MapMouseEvent } from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Layers, ZoomIn, ZoomOut, RotateCcw, Flame, GitCompare } from 'lucide-react';

interface MapContainerProps {
  selectedDisease: string;
  selectedRegion: string;
  selectedRegionName?: string;
  dateRange: { start: string; end: string };
  onRegionSelect: (code: string, name?: string) => void;
  comparisonMode?: boolean;
  comparisonCountries?: Array<{ code: string; name: string }>;
  onToggleComparisonMode?: () => void;
}

export default function MapContainer({
  selectedDisease,
  selectedRegion,
  selectedRegionName,
  dateRange,
  onRegionSelect,
  comparisonMode = false,
  comparisonCountries = [],
  onToggleComparisonMode,
}: MapContainerProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [hoveredCountry, setHoveredCountry] = useState<string | null>(null);
  const [heatMapEnabled, setHeatMapEnabled] = useState(false);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || '';

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [0, 20],
      zoom: 2,
      projection: 'globe',
    });

    map.current.on('load', () => {
      if (!map.current) return;

      // Add world countries source
      map.current.addSource('world-countries', {
        type: 'vector',
        url: 'mapbox://mapbox.country-boundaries-v1'
      });

      // Country fill layer (only for selected countries)
      map.current.addLayer({
        id: 'country-fills',
        type: 'fill',
        source: 'world-countries',
        'source-layer': 'country_boundaries',
        paint: {
          'fill-color': 'rgba(239, 68, 68, 0.3)',  // Light red fill for selected
          'fill-opacity': [
            'case',
            ['==', ['get', 'iso_3166_1'], selectedRegion],
            1,  // Show fill for selected
            0   // No fill for others
          ]
        }
      });

      // Country line layer (for hover and selection outlines)
      map.current.addLayer({
        id: 'country-borders',
        type: 'line',
        source: 'world-countries',
        'source-layer': 'country_boundaries',
        paint: {
          'line-color': 'rgba(255, 255, 255, 0.3)',  // Default faint white
          'line-width': 1
        }
      });

      // Add hover effect
      map.current.on('mousemove', 'country-fills', (e: MapMouseEvent) => {
        if (map.current && e.features && e.features.length > 0) {
          map.current.getCanvas().style.cursor = 'pointer';
          // Use 3-letter ISO code to match backend format
          const countryCode = e.features[0].properties?.['iso_3166_1_alpha_3'];
          if (countryCode) {
            setHoveredCountry(countryCode);
          }
        }
      });

      // Remove hover effect
      map.current.on('mouseleave', 'country-fills', () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = '';
          setHoveredCountry(null);
        }
      });

      // Country click handler
      map.current.on('click', 'country-fills', (e: MapMouseEvent) => {
        if (e.features && e.features.length > 0) {
          // Use 3-letter ISO code to match backend format
          const countryCode = e.features[0].properties?.['iso_3166_1_alpha_3'];
          const countryName = e.features[0].properties?.['name_en'] || e.features[0].properties?.['name'];
          if (countryCode) {
            onRegionSelect(countryCode, countryName);
          }
        }
      });

      setMapLoaded(true);
    });

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []); // Remove dependencies to prevent re-render

  // Resize map when container size changes
  useEffect(() => {
    if (!map.current) return;

    const resizeObserver = new ResizeObserver(() => {
      map.current?.resize();
    });

    if (mapContainer.current) {
      resizeObserver.observe(mapContainer.current);
    }

    return () => {
      resizeObserver.disconnect();
    };
  }, [mapLoaded]);

  // Update map styling when selection, hover, or heat map changes
  useEffect(() => {
    if (map.current && mapLoaded) {
      if (heatMapEnabled) {
        // Heat map mode - show all countries with varying opacity
        map.current.setPaintProperty('country-fills', 'fill-color', [
          'case',
          ['==', ['get', 'iso_3166_1_alpha_3'], selectedRegion],
          'rgba(239, 68, 68, 1)',       // Selected country - bright red
          'rgba(239, 68, 68, 0.5)'      // Other countries - semi-transparent red
        ]);

        map.current.setPaintProperty('country-fills', 'fill-opacity', 1);
      } else {
        // Normal mode - only show selected country
        map.current.setPaintProperty('country-fills', 'fill-color', 'rgba(239, 68, 68, 0.3)');

        map.current.setPaintProperty('country-fills', 'fill-opacity', [
          'case',
          ['==', ['get', 'iso_3166_1_alpha_3'], selectedRegion],
          1,  // Show fill for selected
          0   // No fill for others
        ]);
      }

      // Update border layer - show different colors for selected, hovered, and default
      map.current.setPaintProperty('country-borders', 'line-color', [
        'case',
        ['==', ['get', 'iso_3166_1_alpha_3'], selectedRegion],
        'rgba(239, 68, 68, 1)',       // Bright red for selected
        ['==', ['get', 'iso_3166_1_alpha_3'], hoveredCountry || ''],
        'rgba(239, 68, 68, 0.7)',     // Red outline for hovered
        'rgba(255, 255, 255, 0.3)'    // Faint white for others
      ]);

      // Update border width
      map.current.setPaintProperty('country-borders', 'line-width', [
        'case',
        ['==', ['get', 'iso_3166_1_alpha_3'], selectedRegion],
        2.5,  // Thicker for selected
        ['==', ['get', 'iso_3166_1_alpha_3'], hoveredCountry || ''],
        2,    // Medium for hovered
        0.8   // Thin for others
      ]);
    }
  }, [selectedRegion, hoveredCountry, mapLoaded, heatMapEnabled]);

  const handleZoomIn = () => map.current?.zoomIn();
  const handleZoomOut = () => map.current?.zoomOut();
  const handleReset = () => {
    map.current?.flyTo({
      center: [0, 20],
      zoom: 2,
      pitch: 0,
      bearing: 0,
    });
  };

  return (
    <div className="h-full w-full bg-[#1e293b] rounded-xl border border-slate-700 overflow-hidden relative">
      {/* Currently Viewing Label */}
      <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur-sm px-4 py-2 rounded-lg shadow-lg z-10 border border-slate-700">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-0.5">Currently Viewing</p>
        <p className="text-sm font-bold text-slate-200">{selectedRegionName || selectedRegion}</p>
      </div>

      {/* Map Container */}
      <div ref={mapContainer} className="absolute inset-0 w-full h-full" />

      {/* Map Controls */}
      <div className="absolute bottom-4 right-4 flex flex-col gap-2 z-10">
        <div className="flex gap-2">
          <button
            onClick={handleReset}
            className="bg-slate-900/90 backdrop-blur-sm p-2.5 rounded-lg hover:bg-slate-800 transition-colors shadow-lg border border-slate-700"
            title="Reset View"
          >
            <RotateCcw className="w-4 h-4 text-slate-300" />
          </button>
          <button
            onClick={handleZoomIn}
            className="bg-slate-900/90 backdrop-blur-sm p-2.5 rounded-lg hover:bg-slate-800 transition-colors shadow-lg border border-slate-700"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4 text-slate-300" />
          </button>
          <button
            onClick={handleZoomOut}
            className="bg-slate-900/90 backdrop-blur-sm p-2.5 rounded-lg hover:bg-slate-800 transition-colors shadow-lg border border-slate-700"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4 text-slate-300" />
          </button>
        </div>
        <button
          onClick={() => setHeatMapEnabled(!heatMapEnabled)}
          className={`w-full backdrop-blur-sm p-2.5 rounded-lg transition-all shadow-lg border ${
            heatMapEnabled
              ? 'bg-red-600/90 border-red-500 hover:bg-red-700'
              : 'bg-slate-900/90 border-slate-700 hover:bg-slate-800'
          }`}
          title={heatMapEnabled ? 'Disable Heat Map' : 'Enable Heat Map'}
        >
          <div className="flex items-center justify-center gap-2">
            <Flame className={`w-4 h-4 ${heatMapEnabled ? 'text-white' : 'text-slate-300'}`} />
            <span className={`text-xs font-medium ${heatMapEnabled ? 'text-white' : 'text-slate-300'}`}>
              Heat Map
            </span>
          </div>
        </button>
        {onToggleComparisonMode && (
          <button
            onClick={onToggleComparisonMode}
            className={`w-full backdrop-blur-sm p-2.5 rounded-lg transition-all shadow-lg border ${
              comparisonMode
                ? 'bg-blue-600/90 border-blue-500 hover:bg-blue-700'
                : 'bg-slate-900/90 border-slate-700 hover:bg-slate-800'
            }`}
            title={comparisonMode ? 'Exit Comparison' : 'Compare Countries'}
          >
            <div className="flex items-center justify-center gap-2">
              <GitCompare className={`w-4 h-4 ${comparisonMode ? 'text-white' : 'text-slate-300'}`} />
              <span className={`text-xs font-medium ${comparisonMode ? 'text-white' : 'text-slate-300'}`}>
                Compare
              </span>
            </div>
          </button>
        )}
      </div>

      {!mapLoaded && (
        <div className="absolute inset-0 bg-[#1e293b] flex items-center justify-center">
          <div className="text-slate-400">Loading map...</div>
        </div>
      )}
    </div>
  );
}