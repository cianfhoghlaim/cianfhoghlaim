"use client";

// <CiMapZone> — WoW hex-based claim with decay indicator
// Per UI_INSPIRATION_GUIDE.md, the map zone uses hex-based claims with
// decay indicators. The Cianfhoghlaim OS uses this for the 6 subnations
// of the British Isles.

import * as React from "react";
import { cn } from "./utils";

export interface CiMapZoneProps {
  subnation: "eire" | "northern-ireland" | "scotland" | "england" | "wales" | "isle-of-man";
  active?: boolean;
  comingSoon?: boolean;
  decayPercent?: number;
  onClick?: () => void;
  className?: string;
}

const SUBNATION_COLORS: Record<CiMapZoneProps["subnation"], string> = {
  "eire": "var(--ci-subnation-eire)",
  "northern-ireland": "var(--ci-subnation-northern-ireland)",
  "scotland": "var(--ci-subnation-scotland)",
  "england": "var(--ci-subnation-england)",
  "wales": "var(--ci-subnation-wales)",
  "isle-of-man": "var(--ci-subnation-isle-of-man)",
};

const SUBNATION_LABELS: Record<CiMapZoneProps["subnation"], { en: string; ga: string }> = {
  "eire": { en: "Éire", ga: "Éire" },
  "northern-ireland": { en: "Northern Ireland", ga: "Tuaisceart Éireann" },
  "scotland": { en: "Scotland", ga: "Albain" },
  "england": { en: "England", ga: "Sasana" },
  "wales": { en: "Wales", ga: "an Bhreatain Bheag" },
  "isle-of-man": { en: "Isle of Man", ga: "Ellan Vannin" },
};

export function CiMapZone({
  subnation,
  active = false,
  comingSoon = false,
  decayPercent = 0,
  onClick,
  className,
}: CiMapZoneProps) {
  const color = SUBNATION_COLORS[subnation];
  const labels = SUBNATION_LABELS[subnation];

  return (
    <button
      onClick={onClick}
      disabled={comingSoon}
      className={cn(
        "relative w-full aspect-[5/6] flex flex-col items-center justify-center gap-1 transition-all",
        "rounded-xl border-2 p-3 overflow-hidden",
        active ? "border-amber-400 shadow-2xl" : "border-slate-700",
        comingSoon ? "opacity-40 cursor-not-allowed" : "hover:scale-105 cursor-pointer",
        className,
      )}
      style={{
        background: `linear-gradient(135deg, ${color}30 0%, ${color}10 100%)`,
      }}
    >
      {/* Hex-based claim indicator (per UI_INSPIRATION_GUIDE.md) */}
      <svg
        className="absolute inset-0 w-full h-full opacity-30"
        viewBox="0 0 100 120"
        preserveAspectRatio="none"
      >
        <polygon
          points="50,5 95,30 95,90 50,115 5,90 5,30"
          fill="none"
          stroke={color}
          strokeWidth="1"
        />
      </svg>

      {/* Decay indicator */}
      {decayPercent > 0 && (
        <div
          className="absolute inset-0 bg-slate-900/60"
          style={{ clipPath: `inset(${decayPercent}% 0 0 0)` }}
        />
      )}

      <div className="relative z-10 flex flex-col items-center gap-1">
        <div
          className="text-3xl font-bold"
          style={{ color: active ? "#fbbf24" : color }}
        >
          {labels.en}
        </div>
        <div className="text-xs text-slate-400 font-mono">{labels.ga}</div>
        {comingSoon && (
          <div className="text-xs text-slate-500 mt-1">Coming soon</div>
        )}
        {active && !comingSoon && (
          <div className="text-xs text-emerald-400 mt-1">v1 active</div>
        )}
      </div>
    </button>
  );
}