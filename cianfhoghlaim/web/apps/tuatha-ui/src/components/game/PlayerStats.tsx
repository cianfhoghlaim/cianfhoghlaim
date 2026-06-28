import React, { useEffect, useState } from "react";
import { Heart, Zap, Flame, Shield } from "lucide-react";

interface PlayerStatsProps {
  health: number;
  maxHealth: number;
  xp: number;
  maxXp: number;
  level: number;
  streak: number;
  className?: string;
}

export const PlayerStats: React.FC<PlayerStatsProps> = ({
  health,
  maxHealth,
  xp,
  maxXp,
  level,
  streak,
  className = "",
}) => {
  const [animateXp, setAnimateXp] = useState(false);
  const [animateHealth, setAnimateHealth] = useState(false);

  useEffect(() => {
    setAnimateXp(true);
    const timer = setTimeout(() => setAnimateXp(false), 1000);
    return () => clearTimeout(timer);
  }, [xp]);

  useEffect(() => {
    setAnimateHealth(true);
    const timer = setTimeout(() => setAnimateHealth(false), 500);
    return () => clearTimeout(timer);
  }, [health]);

  const healthPercent = Math.min((health / maxHealth) * 100, 100);
  const xpPercent = Math.min((xp / maxXp) * 100, 100);

  return (
    <div className={`flex items-start gap-4 ${className}`}>
      <div className="relative group z-10">
        <div className="w-16 h-16 bg-slate-900 rounded-full border-4 border-slate-700 flex items-center justify-center shadow-xl shadow-black/50 relative overflow-hidden transition-transform group-hover:scale-105 duration-300">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-800 to-slate-950" />
          <div className="absolute inset-0 opacity-20 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIi8+CjxyZWN0IHdpZHRoPSIxIiBoZWlnaHQ9IjEiIGZpbGw9IiMwMDAiLz4KPC9zdmc+')] mix-blend-overlay" />

          <div className="relative flex flex-col items-center">
            <span className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold mb-[-2px]">
              Lvl
            </span>
            <span className="text-2xl font-bold text-white font-serif">
              {level}
            </span>
          </div>

          <div className="absolute inset-0 border-2 border-emerald-500/20 rounded-full scale-90" />
        </div>

        <div className="absolute -left-2 top-1/2 -translate-y-1/2 w-4 h-12 bg-emerald-900/0 border-l-2 border-emerald-600/50 rounded-l-full -z-10 group-hover:-translate-x-1 transition-all" />
        <div className="absolute -right-2 top-1/2 -translate-y-1/2 w-4 h-12 bg-emerald-900/0 border-r-2 border-emerald-600/50 rounded-r-full -z-10 group-hover:translate-x-1 transition-all" />
      </div>

      <div className="flex-1 flex flex-col gap-2 pt-1 min-w-[200px]">
        <div className="relative h-5 bg-slate-900/80 rounded-sm skew-x-[-10deg] border border-slate-700 overflow-hidden shadow-inner group">
          <div className="absolute inset-0 flex items-center justify-center z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <span className="text-[10px] font-bold text-white/90 drop-shadow-md">
              {health} / {maxHealth}
            </span>
          </div>

          <div className="absolute inset-0 bg-red-900/20" />

          <div
            className={`absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-800 via-emerald-600 to-emerald-500 transition-all duration-500 ease-out ${animateHealth ? "brightness-125" : ""}`}
            style={{ width: `${healthPercent}%` }}
          >
            <div className="absolute inset-0 bg-[linear-gradient(90deg,transparent_0%,rgba(255,255,255,0.2)_50%,transparent_100%)] w-full h-full skew-x-[10deg] animate-[shimmer_2s_infinite]" />
          </div>

          <div className="absolute left-1 top-1/2 -translate-y-1/2 z-20 skew-x-[10deg]">
            <Heart size={12} className="text-emerald-100 fill-emerald-600" />
          </div>
        </div>

        <div className="relative h-3 bg-slate-900/80 rounded-sm skew-x-[-10deg] border border-slate-700 overflow-hidden shadow-inner group mt-[-2px]">
          <div className="absolute inset-0 flex items-center justify-center z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <span className="text-[9px] font-bold text-white/90 drop-shadow-md">
              {xp} / {maxXp} XP
            </span>
          </div>

          <div
            className={`absolute inset-y-0 left-0 bg-gradient-to-r from-indigo-900 via-indigo-600 to-indigo-400 transition-all duration-700 ease-out ${animateXp ? "animate-pulse" : ""}`}
            style={{ width: `${xpPercent}%` }}
          />

          <div className="absolute left-1 top-1/2 -translate-y-1/2 z-20 skew-x-[10deg]">
            <Zap size={10} className="text-indigo-100 fill-indigo-400" />
          </div>
        </div>
      </div>

      <div
        className="flex flex-col items-center justify-center pt-1 group cursor-help"
        title="Daily Streak"
      >
        <div className="relative">
          <Flame
            className={`w-8 h-8 ${streak > 0 ? "text-amber-500 fill-amber-500 animate-[pulse_3s_ease-in-out_infinite]" : "text-slate-600"}`}
          />
          {streak > 5 && (
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full animate-ping" />
          )}
        </div>
        <div className="text-xs font-bold text-amber-500 group-hover:scale-110 transition-transform">
          {streak}
        </div>
      </div>
    </div>
  );
};
