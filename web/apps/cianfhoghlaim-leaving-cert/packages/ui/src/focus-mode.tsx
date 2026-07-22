"use client";

// <CiFocusMode> — Khan Academy Focus Mode (stripped nav during study)
// Per UI_INSPIRATION_GUIDE.md, the Focus Mode strips the navigation
// during video playback. The Cianfhoghlaim OS strips the sidebar +
// the header tagline + the breadcrumb during active practice sessions.

import * as React from "react";
import { cn } from "./utils";

export interface CiFocusModeProps {
  active: boolean;
  onToggle: () => void;
  children: React.ReactNode;
  className?: string;
}

export function CiFocusMode({ active, onToggle, children, className }: CiFocusModeProps) {
  return (
    <div className={cn("relative", className)}>
      {children}
      <button
        onClick={onToggle}
        className={cn(
          "fixed top-20 right-4 z-40 px-3 py-1.5 rounded-full text-xs font-medium border transition-all",
          active
            ? "bg-emerald-700 text-white border-emerald-500"
            : "bg-slate-800 text-slate-300 border-slate-700 hover:border-slate-500",
        )}
        aria-label={active ? "Exit Focus Mode" : "Enter Focus Mode"}
      >
        {active ? "Exit Focus" : "Focus Mode"}
      </button>
    </div>
  );
}