"use client";

// <CiSemanticPill> — Khan Academy semantic pills (status indicators)
// 8 status kinds × 8 subject colours per docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css.

import * as React from "react";
import { cn } from "./utils";

export type PillKind =
  | "attempted"
  | "familiar"
  | "proficient"
  | "mastered"
  | "locked"
  | "available"
  | "eiraic"
  | "streak";

export interface CiSemanticPillProps {
  kind: PillKind;
  label: string;
  subjectColor?: string;
  icon?: React.ReactNode;
  onClick?: () => void;
  className?: string;
}

const kindStyles: Record<PillKind, string> = {
  attempted: "bg-slate-700 text-slate-200 border-slate-600",
  familiar: "bg-amber-900/40 text-amber-200 border-amber-700",
  proficient: "bg-blue-900/40 text-blue-200 border-blue-700",
  mastered: "bg-emerald-900/40 text-emerald-200 border-emerald-700",
  locked: "bg-slate-800 text-slate-500 border-slate-700",
  available: "bg-slate-700 text-slate-100 border-slate-600",
  eiraic: "bg-amber-900/60 text-amber-100 border-amber-500",
  streak: "bg-orange-900/40 text-orange-200 border-orange-700",
};

export function CiSemanticPill({
  kind,
  label,
  subjectColor,
  icon,
  onClick,
  className,
}: CiSemanticPillProps) {
  return (
    <button
      onClick={onClick}
      disabled={!onClick}
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-colors",
        kindStyles[kind],
        subjectColor && `border-[var(--ci-subject-${subjectColor})]`,
        onClick && "cursor-pointer hover:opacity-80",
        className,
      )}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      <span>{label}</span>
    </button>
  );
}