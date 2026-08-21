import React, { useEffect, useState } from "react";
import { Flame } from "lucide-react";

interface StreakCounterProps {
  days: number;
  isActive?: boolean;
  className?: string;
}

export function StreakCounter({
  days,
  isActive = false,
  className = "",
}: StreakCounterProps) {
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isActive) {
      setIsAnimating(true);
      const timer = setTimeout(() => setIsAnimating(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [isActive, days]);

  return (
    <div
      className={`
        relative group inline-flex items-center gap-1.5 px-3 py-1.5 
        rounded-xl border-2 cursor-help transition-all duration-300
        ${
          isActive
            ? "border-orange-500 bg-orange-50 text-orange-600"
            : "border-slate-200 bg-slate-50 text-slate-400 grayscale hover:grayscale-0"
        }
        ${className}
      `}
      title={
        isActive ? "Streak active!" : "Practice today to keep your streak!"
      }
    >
      <div className="relative">
        <Flame
          className={`
            w-5 h-5 fill-current transition-transform duration-500
            ${isActive ? "text-orange-500" : "text-slate-400"}
            ${isAnimating ? "animate-[bounce_0.5s_infinite]" : "group-hover:scale-110"}
          `}
        />

        {isActive && (
          <div className="absolute inset-0 blur-sm bg-orange-400 opacity-50 animate-pulse rounded-full" />
        )}
      </div>

      <span
        className={`font-bold text-lg ${isActive ? "text-orange-700" : "text-slate-500"}`}
      >
        {days}
      </span>

      {isAnimating && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-yellow-400 rounded-full animate-[ping_0.8s_ease-out]" />
          <div className="absolute top-0 right-0 w-1 h-1 bg-red-400 rounded-full animate-[ping_0.6s_ease-out_0.1s]" />
          <div className="absolute bottom-0 left-0 w-1 h-1 bg-orange-400 rounded-full animate-[ping_0.7s_ease-out_0.2s]" />
        </div>
      )}
    </div>
  );
}
