/**
 * Game page - Babylon.js game embed (placeholder)
 *
 * The Babylon.js engine and SpacetimeDB integration will be wired here
 * once the @tuath/game-client package is available. For now this renders
 * a placeholder canvas with the player stats HUD so the route is functional.
 */

import { createFileRoute, Link } from '@tanstack/react-router';
import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from '../hooks/useAuth';
import { PlayerStats } from '../components/game/PlayerStats';

type ZoneId = 'gaeltacht' | 'albain' | 'breatainn_bheag' | 'kernew' | 'yny_ellan_vannin' | 'y_bruix';

const ZONE_NAMES: Record<ZoneId, string> = {
  gaeltacht: 'An Ghaeltacht',
  albain: 'Alba',
  breatainn_bheag: 'Breatainn Bheag',
  kernew: 'Cernyw',
  yny_ellan_vannin: 'Ellan Vannin',
  y_bruix: "Ar Vro-C'hall",
};

export const Route = createFileRoute('/game')({
  component: GamePage,
});

function GamePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadProgress, setLoadProgress] = useState(0);
  const [currentZone, setCurrentZone] = useState<ZoneId>('gaeltacht');
  const [isConnected, setIsConnected] = useState(false);
  const { address } = useAuth();

  // Simulate loading progress
  useEffect(() => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setLoadProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setIsLoading(false);
      }
    }, 200);
    return () => clearInterval(interval);
  }, []);

  const handleZoneChange = useCallback((zoneId: ZoneId) => {
    setIsLoading(true);
    setCurrentZone(zoneId);
    setTimeout(() => setIsLoading(false), 500);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      {/* Game Header */}
      <header className="bg-slate-800 border-b border-emerald-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-amber-300">Tuath</h1>
          <span className="text-emerald-400">|</span>
          <span className="text-emerald-200">{ZONE_NAMES[currentZone]}</span>
          <span className={`flex items-center gap-1 text-xs ${address ? 'text-green-400' : 'text-red-400'}`}>
            <span className={`w-2 h-2 rounded-full ${address ? 'bg-green-400' : 'bg-red-400'}`} />
            {address ? `Connected: ${address.slice(0, 6)}…${address.slice(-4)}` : 'Not connected'}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <PlayerStats
            health={80}
            maxHealth={100}
            xp={240}
            maxXp={500}
            level={3}
            streak={5}
          />
          <Link to="/" className="px-3 py-1 bg-emerald-700 hover:bg-emerald-600 text-white rounded">
            Menu
          </Link>
        </div>
      </header>

      {/* Game Canvas */}
      <main className="flex-1 relative">
        {isLoading && (
          <div className="absolute inset-0 bg-slate-900 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="text-amber-300 text-2xl mb-4">Loading {ZONE_NAMES[currentZone]}…</div>
              <div className="w-64 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-emerald-500 transition-all"
                  style={{ width: `${loadProgress}%` }}
                />
              </div>
              <div className="text-slate-400 mt-2">{loadProgress}%</div>
            </div>
          </div>
        )}
        <canvas
          ref={canvasRef}
          className="w-full h-full bg-gradient-to-b from-slate-800 to-emerald-900"
        />
      </main>

      {/* Zone selector */}
      <footer className="bg-slate-800 border-t border-emerald-700 p-3 flex justify-center gap-2">
        {(Object.keys(ZONE_NAMES) as ZoneId[]).map((zone) => (
          <button
            key={zone}
            onClick={() => handleZoneChange(zone)}
            className={`px-3 py-1 rounded text-sm ${
              currentZone === zone
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            {ZONE_NAMES[zone]}
          </button>
        ))}
      </footer>
    </div>
  );
}
