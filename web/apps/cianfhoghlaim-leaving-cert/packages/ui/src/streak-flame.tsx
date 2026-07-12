"use client";

// <CiStreakFlame> — Duolingo streak flame (the Cauldron of the Dagda)
// Per docs/BROWN_AJAH_THEMING.md, the streak indicator is themed as
// the Cauldron of the Dagda — the ever-full cauldron that never empties.
// On Beltane (1 May) the indicator resets to 100%.

import * as React from "react";
import { cn } from "./utils";

export interface CiStreakFlameProps {
  days: number;
  size?: number;
  className?: string;
}

export function CiStreakFlame({ days, size = 20, className }: CiStreakFlameProps) {
  // The flame intensity grows with days (cap at 30)
  const intensity = Math.min(days / 30, 1);
  const flameColor = intensity > 0.7 ? "#f59e0b" : intensity > 0.4 ? "#fb923c" : "#92400e";

  return (
    <div className={cn("inline-flex items-center gap-1.5 bg-orange-900/30 px-2 py-1 rounded-full border border-orange-700", className)}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* The Dagda's cauldron + the Duolingo flame */}
        <ellipse cx="12" cy="18" rx="8" ry="3" fill="#92400e" stroke="#f59e0b" strokeWidth="1" />
        <path
          d="M8 14 Q 12 4 16 14 Q 14 10 12 12 Q 10 10 8 14 Z"
          fill={flameColor}
          opacity={0.9}
        />
      </svg>
      <span className="text-xs font-medium text-orange-200">{days}</span>
    </div>
  );
}