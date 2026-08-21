import React from "react";
import { Check, Circle, Star, Trophy } from "lucide-react";

export type MasteryLevel = "attempted" | "familiar" | "proficient" | "mastered";

interface MasteryPillProps {
  level: MasteryLevel;
  className?: string;
}

const levelConfig = {
  attempted: {
    color: "bg-slate-100 text-slate-600 border-slate-200",
    icon: Circle,
    label: "Attempted",
    dot: "bg-slate-400",
  },
  familiar: {
    color: "bg-amber-50 text-amber-700 border-amber-200",
    icon: Star,
    label: "Familiar",
    dot: "bg-amber-500",
  },
  proficient: {
    color: "bg-emerald-50 text-emerald-700 border-emerald-200",
    icon: Check,
    label: "Proficient",
    dot: "bg-emerald-500",
  },
  mastered: {
    color: "bg-indigo-50 text-indigo-700 border-indigo-200",
    icon: Trophy,
    label: "Mastered",
    dot: "bg-indigo-600",
  },
};

export function MasteryPill({ level, className = "" }: MasteryPillProps) {
  const config = levelConfig[level];
  const Icon = config.icon;

  return (
    <div
      className={`
        inline-flex items-center gap-1.5 px-3 py-1 
        rounded-full border text-xs font-semibold tracking-wide uppercase
        shadow-sm backdrop-blur-sm
        ${config.color}
        ${className}
      `}
    >
      <div
        className={`w-1.5 h-1.5 rounded-full ${config.dot} shadow-[0_0_4px_currentColor]`}
      />
      <span>{config.label}</span>
      {level === "mastered" && <Icon className="w-3 h-3 ml-0.5" />}
    </div>
  );
}
