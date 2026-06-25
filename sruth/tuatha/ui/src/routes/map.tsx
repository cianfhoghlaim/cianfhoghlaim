/**
 * Celtic language map - MapLibre visualization
 */

import { createFileRoute } from '@tanstack/react-router';
import { useEffect, useRef, useState } from 'react';

export const Route = createFileRoute('/map')({
  component: MapPage,
});

interface CelticRegion {
  id: string;
  name: string;
  nativeName: string;
  language: string;
  languageName: string;
  country: string;
  coordinates: { lat: number; lon: number };
  speakers: number;
  speakerPercentage: number;
  gameZone: string;
}

const CELTIC_REGIONS: CelticRegion[] = [
  {
    id: 'connemara',
    name: 'Connemara',
    nativeName: 'Conamara',
    language: 'ga',
    languageName: 'Irish',
    country: 'ireland',
    coordinates: { lat: 53.4, lon: -9.8 },
    speakers: 20000,
    speakerPercentage: 61,
    gameZone: 'conamara_realm',
  },
  {
    id: 'donegal',
    name: 'Donegal Gaeltacht',
    nativeName: 'Gaeltacht Dhún na nGall',
    language: 'ga',
    languageName: 'Irish',
    country: 'ireland',
    coordinates: { lat: 55.0, lon: -8.3 },
    speakers: 24000,
    speakerPercentage: 68,
    gameZone: 'ulster_highlands',
  },
  {
    id: 'kerry',
    name: 'Kerry Gaeltacht',
    nativeName: 'Gaeltacht Chiarraí',
    language: 'ga',
    languageName: 'Irish',
    country: 'ireland',
    coordinates: { lat: 52.1, lon: -10.3 },
    speakers: 10000,
    speakerPercentage: 50,
    gameZone: 'munster_coast',
  },
  {
    id: 'western_isles',
    name: 'Western Isles',
    nativeName: 'Na h-Eileanan Siar',
    language: 'gd',
    languageName: 'Scottish Gaelic',
    country: 'scotland',
    coordinates: { lat: 58.2, lon: -6.8 },
    speakers: 15000,
    speakerPercentage: 52,
    gameZone: 'hebridean_realm',
  },
  {
    id: 'skye',
    name: 'Isle of Skye',
    nativeName: 'An t-Eilean Sgitheanach',
    language: 'gd',
    languageName: 'Scottish Gaelic',
    country: 'scotland',
    coordinates: { lat: 57.3, lon: -6.2 },
    speakers: 2500,
    speakerPercentage: 25,
    gameZone: 'skye_highlands',
  },
  {
    id: 'gwynedd',
    name: 'Gwynedd',
    nativeName: 'Gwynedd',
    language: 'cy',
    languageName: 'Welsh',
    country: 'wales',
    coordinates: { lat: 52.9, lon: -4.1 },
    speakers: 77000,
    speakerPercentage: 65,
    gameZone: 'gwynedd_kingdom',
  },
  {
    id: 'ynys_mon',
    name: 'Anglesey',
    nativeName: 'Ynys Môn',
    language: 'cy',
    languageName: 'Welsh',
    country: 'wales',
    coordinates: { lat: 53.3, lon: -4.3 },
    speakers: 38000,
    speakerPercentage: 57,
    gameZone: 'druid_isle',
  },
];

function MapPage() {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [selectedRegion, setSelectedRegion] = useState<CelticRegion | null>(null);
  const [filter, setFilter] = useState<string>('all');

  const filteredRegions = CELTIC_REGIONS.filter((region) => {
    if (filter === 'all') return true;
    return region.language === filter;
  });

  return (
    <div className="min-h-screen bg-slate-900 flex">
      {/* Sidebar */}
      <aside className="w-80 bg-slate-800 border-r border-emerald-700 flex flex-col">
        <header className="p-4 border-b border-emerald-700">
          <h1 className="text-2xl font-bold text-amber-300">Celtic Language Map</h1>
          <p className="text-emerald-300 text-sm">Explore Celtic-speaking regions</p>
        </header>

        {/* Filters */}
        <div className="p-4 border-b border-slate-700">
          <label className="text-sm text-slate-400 block mb-2">Filter by language</label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white"
          >
            <option value="all">All Languages</option>
            <option value="ga">Irish (Gaeilge)</option>
            <option value="gd">Scottish Gaelic (Gàidhlig)</option>
            <option value="cy">Welsh (Cymraeg)</option>
          </select>
        </div>

        {/* Region List */}
        <div className="flex-1 overflow-y-auto">
          {filteredRegions.map((region) => (
            <RegionCard
              key={region.id}
              region={region}
              isSelected={selectedRegion?.id === region.id}
              onClick={() => setSelectedRegion(region)}
            />
          ))}
        </div>

        {/* Legend */}
        <div className="p-4 border-t border-slate-700">
          <h4 className="text-sm font-bold text-slate-400 mb-2">Language Legend</h4>
          <div className="flex flex-col gap-1 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-slate-300">Irish (Gaeilge)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-slate-300">Scottish Gaelic (Gàidhlig)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-slate-300">Welsh (Cymraeg)</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Map Container */}
      <main className="flex-1 relative">
        <div ref={mapContainerRef} className="w-full h-full bg-slate-700">
          {/* MapLibre would render here */}
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-slate-400 mb-2">Map visualization</p>
              <p className="text-slate-500 text-sm">MapLibre GL would render here</p>
            </div>
          </div>
        </div>

        {/* Selected Region Detail */}
        {selectedRegion && (
          <div className="absolute bottom-4 left-4 right-4 max-w-md bg-slate-800/95 rounded-lg border border-emerald-700 p-4">
            <div className="flex justify-between items-start mb-2">
              <div>
                <h3 className="text-xl font-bold text-white">{selectedRegion.name}</h3>
                <p className="text-amber-300">{selectedRegion.nativeName}</p>
              </div>
              <button
                onClick={() => setSelectedRegion(null)}
                className="text-slate-400 hover:text-white"
              >
                ×
              </button>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-slate-400">Language:</span>
                <span className="text-white ml-1">{selectedRegion.languageName}</span>
              </div>
              <div>
                <span className="text-slate-400">Speakers:</span>
                <span className="text-white ml-1">{selectedRegion.speakers.toLocaleString()}</span>
              </div>
              <div>
                <span className="text-slate-400">% Speakers:</span>
                <span className="text-emerald-300 ml-1">{selectedRegion.speakerPercentage}%</span>
              </div>
              <div>
                <span className="text-slate-400">Game Zone:</span>
                <span className="text-purple-300 ml-1">{selectedRegion.gameZone}</span>
              </div>
            </div>
            <button className="mt-3 w-full px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-medium">
              Visit in Game
            </button>
          </div>
        )}
      </main>
    </div>
  );
}

interface RegionCardProps {
  region: CelticRegion;
  isSelected: boolean;
  onClick: () => void;
}

function RegionCard({ region, isSelected, onClick }: RegionCardProps) {
  const languageColors: Record<string, string> = {
    ga: 'bg-emerald-500',
    gd: 'bg-blue-500',
    cy: 'bg-red-500',
  };

  return (
    <button
      onClick={onClick}
      className={`w-full p-3 text-left border-b border-slate-700 hover:bg-slate-700/50 transition-colors ${
        isSelected ? 'bg-emerald-900/30' : ''
      }`}
    >
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full ${languageColors[region.language]}`} />
        <span className="font-medium text-white">{region.name}</span>
      </div>
      <p className="text-sm text-amber-300 ml-4">{region.nativeName}</p>
      <p className="text-xs text-slate-400 ml-4">
        {region.speakers.toLocaleString()} speakers ({region.speakerPercentage}%)
      </p>
    </button>
  );
}
