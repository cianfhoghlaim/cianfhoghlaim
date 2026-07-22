"use client";

// <CiDiegeticPanel> — Hades diegetic UI (integrated into world)
// Per UI_INSPIRATION_GUIDE.md, the diegetic UI is integrated into the
// game world rather than overlaid. The Cianfhoghlaim OS renders the
// per-subject panel with a subject-tinted glow + no hard borders.

import * as React from "react";
import { cn } from "./utils";

export interface CiDiegeticPanelProps {
  subjectColor?: string;
  glow?: boolean;
  children: React.ReactNode;
  className?: string;
}

export function CiDiegeticPanel({
  subjectColor,
  glow = true,
  children,
  className,
}: CiDiegeticPanelProps) {
  const colorVar = subjectColor ? `var(--ci-subject-${subjectColor})` : "#475569";

  return (
    <div
      className={cn("relative rounded-2xl p-6 bg-slate-900/60 backdrop-blur-sm", className)}
      style={{
        boxShadow: glow
          ? `0 0 32px ${colorVar}40, inset 0 0 16px ${colorVar}20`
          : "none",
        border: `1px solid ${colorVar}40`,
      }}
    >
      {children}
    </div>
  );
}