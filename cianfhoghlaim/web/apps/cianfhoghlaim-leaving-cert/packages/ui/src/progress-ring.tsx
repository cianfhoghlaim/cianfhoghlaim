"use client";

// <CiProgressRing> — Khan Academy 4-tier mastery ring
// Attempted (0%) → Familiar (33%) → Proficient (66%) → Mastered (100%)
// Optionally surfaces the 13 éraic tiers as a pedagogical anchor.

import * as React from "react";
import { cn } from "./utils";

export type MasteryTier = "attempted" | "familiar" | "proficient" | "mastered";

export interface CiProgressRingProps {
  value: number; // 0-100
  tier?: MasteryTier;
  eiraicTier?: number; // 1-13 (the 13 éraic treasures)
  size?: number;
  subjectColor?: string;
  label?: string;
  className?: string;
}

const tierColors: Record<MasteryTier, string> = {
  attempted: "fill-slate-500",
  familiar: "fill-amber-500",
  proficient: "fill-blue-500",
  mastered: "fill-emerald-500",
};

const tierLabels: Record<MasteryTier, string> = {
  attempted: "Attempted",
  familiar: "Familiar",
  proficient: "Proficient",
  mastered: "Mastered",
};

export function CiProgressRing({
  value,
  tier = "attempted",
  eiraicTier,
  size = 80,
  subjectColor,
  label,
  className,
}: CiProgressRingProps) {
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (value / 100) * circumference;

  return (
    <div className={cn("inline-flex flex-col items-center gap-1", className)}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
          className="text-slate-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          className={cn(tierColors[tier], subjectColor && `text-[var(--ci-subject-${subjectColor})]`)}
        />
        <text
          x={size / 2}
          y={size / 2}
          textAnchor="middle"
          dominantBaseline="middle"
          className="fill-slate-100 text-lg font-bold"
        >
          {value}%
        </text>
      </svg>
      {(label || eiraicTier) && (
        <div className="text-center text-xs text-slate-400">
          {eiraicTier && <div>Éraic {eiraicTier}/13</div>}
          {label && <div>{label}</div>}
          <div className="font-medium">{tierLabels[tier]}</div>
        </div>
      )}
    </div>
  );
}