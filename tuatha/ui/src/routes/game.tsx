/**
 * Game page - Babylon.js game embed
 *
 * Integrates the @tuath/game-client with the TanStack Start UI.
 * Provides real-time multiplayer via SpacetimeDB.
 */

import { createFileRoute } from '@tanstack/react-router';
import { useEffect, useRef, useState, useCallback } from 'react';
import {
  initTuathGame,
  type TuathGame,
  type ZoneId,
} from '../../game/client/src';
import { useAuth } from '../hooks/useAuth';

export const Route = createFileRoute('/game')({
  component: GamePage,
});

function GamePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const gameRef = useRef<TuathGame | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadProgress, setLoadProgress] = useState(0);
  const [currentZone, setCurrentZone] = useState<ZoneId>('gaeltacht');
  const [isConnected, setIsConnected] = useState(false);
  const [isWebGPU, setIsWebGPU] = useState(false);

  // Get auth session for SpacetimeDB
  const { sessionId, playerId } = useAuth();

  // Initialize game engine
  useEffect(() => {
    if (!canvasRef.current) return;

    let mounted = true;

    const initGame = async () => {
      try {
        const game = await initTuathGame({
          canvas: canvasRef.current!,
          sessionToken: sessionId ?? undefined,
          initialZone: 'gaeltacht',
          onConnected: () => {
            if (mounted) setIsConnected(true);
          },
          onDisconnected: () => {
            if (mounted) setIsConnected(false);
          },
          onZoneChange: (zoneId) => {
            if (mounted) setCurrentZone(zoneId);
          },
          onLoadProgress: (progress) => {
            if (mounted) setLoadProgress(progress);
          },
        });

        if (!mounted) {
          game.dispose();
          return;
        }

        gameRef.current = game;
        setIsWebGPU(game.isWebGPU);

        // Start the game
        await game.start();
        setIsLoading(false);
      } catch (error) {
        console.error('[Game] Failed to initialize:', error);
        setIsLoading(false);
      }
    };

    initGame();

    return () => {
      mounted = false;
      gameRef.current?.dispose();
      gameRef.current = null;
    };
  }, [sessionId]);

  // Handle zone change
  const handleZoneChange = useCallback(async (zoneId: ZoneId) => {
    if (!gameRef.current) return;
    setIsLoading(true);
    await gameRef.current.loadZone(zoneId);
    setIsLoading(false);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      {/* Game Header */}
      <header className="bg-slate-800 border-b border-emerald-700 px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-amber-300">Tuath</h1>
          <span className="text-emerald-400">|</span>
          <span className="text-emerald-200">{ZONE_NAMES[currentZone] || currentZone}</span>
          {/* Connection status */}
          <span className={`flex items-center gap-1 text-xs ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`} />
            {isConnected ? 'Connected' : 'Offline'}
          </span>
          {/* Renderer indicator */}
          <span className="text-xs text-slate-400">
            {isWebGPU ? 'WebGPU' : 'WebGL2'}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <PlayerStats />
          <button className="px-3 py-1 bg-emerald-700 hover:bg-emerald-600 text-white rounded">
            Menu
          </button>
        </div>
      </header>

      {/* Game Canvas */}
      <main className="flex-1 relative">
        {isLoading && (
          <div className="absolute inset-0 bg-slate-900 flex items-center justify-center z-10">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4" />
              <p className="text-emerald-300 text-lg">Loading the Celtic world...</p>
              <p className="text-emerald-400 text-sm mt-2">Ag lódáil...</p>
              {/* Progress bar */}
              <div className="w-64 h-2 bg-slate-700 rounded-full mt-4 mx-auto overflow-hidden">
                <div
                  className="h-full bg-emerald-500 transition-all duration-300"
                  style={{ width: `${loadProgress}%` }}
                />
              </div>
              <p className="text-slate-400 text-xs mt-2">{Math.round(loadProgress)}%</p>
            </div>
          </div>
        )}

        <canvas
          ref={canvasRef}
          className="w-full h-full"
          style={{ display: isLoading ? 'none' : 'block' }}
        />

        {/* Game UI Overlay */}
        {!isLoading && (
          <>
            {/* Quest Tracker */}
            <div className="absolute top-4 right-4 w-72 bg-slate-800/90 rounded-lg p-4 border border-emerald-700">
              <h3 className="font-bold text-amber-300 mb-2">Current Quest</h3>
              <div className="text-sm">
                <p className="text-white font-medium">First Words</p>
                <p className="text-emerald-300 text-xs mb-2">Na Chéad Focail</p>
                <p className="text-slate-300">Talk to the village elder near the standing stones</p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="flex-1 h-2 bg-slate-700 rounded-full">
                    <div className="h-full w-1/4 bg-emerald-500 rounded-full" />
                  </div>
                  <span className="text-xs text-slate-400">1/4</span>
                </div>
              </div>
            </div>

            {/* Chat/Tutor Panel */}
            <div className="absolute bottom-4 left-4 right-4 max-w-2xl mx-auto">
              <div className="bg-slate-800/90 rounded-lg border border-emerald-700 p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-amber-300 font-bold">Celtic Tutor</span>
                  <span className="text-xs text-emerald-400">Online</span>
                </div>
                <input
                  type="text"
                  placeholder="Ask the tutor for help... (e.g., 'How do I say hello?')"
                  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            {/* Minimap */}
            <div className="absolute top-4 left-4 w-40 h-40 bg-slate-800/90 rounded-lg border border-emerald-700 overflow-hidden">
              <div className="w-full h-full bg-emerald-900/50 flex items-center justify-center">
                <span className="text-emerald-400 text-xs">Minimap</span>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

function PlayerStats() {
  return (
    <div className="flex items-center gap-4 text-sm">
      <div className="flex items-center gap-1">
        <span className="text-amber-300">Level</span>
        <span className="text-white font-bold">1</span>
      </div>
      <div className="flex items-center gap-1">
        <span className="text-emerald-300">XP</span>
        <span className="text-white">0/1000</span>
      </div>
      <div className="flex items-center gap-1">
        <span className="text-purple-300">Zone</span>
        <span className="text-white">Tutorial</span>
      </div>
    </div>
  );
}

// Zone display names (matching Godot client)
const ZONE_NAMES: Record<ZoneId, string> = {
  gaeltacht: 'An Ghaeltacht',
  alba: 'Alba',
  cymru: 'Cymru',
};

// Zone descriptions for UI
const ZONE_INFO: Record<ZoneId, { english: string; celtic: string }> = {
  gaeltacht: { english: 'Irish Gaeltacht', celtic: 'An Ghaeltacht' },
  alba: { english: 'Scottish Highlands', celtic: 'Alba' },
  cymru: { english: 'Wales', celtic: 'Cymru' },
};
