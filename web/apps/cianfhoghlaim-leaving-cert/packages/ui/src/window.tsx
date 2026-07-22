"use client";

// <CiWindow> — PostHog Navigation 3000 multi-panel resizable window
// Per UI_INSPIRATION_GUIDE.md and docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css.

import * as React from "react";
import { cn } from "./utils";

export interface CiWindowProps {
  title: string;
  active?: boolean;
  onClose?: () => void;
  onMinimize?: () => void;
  onMaximize?: () => void;
  onFocus?: () => void;
  children: React.ReactNode;
  className?: string;
}

export function CiWindow({
  title,
  active = false,
  onClose,
  onMinimize,
  onMaximize,
  onFocus,
  children,
  className,
}: CiWindowProps) {
  return (
    <div
      onMouseDown={onFocus}
      className={cn(
        "rounded-xl overflow-hidden shadow-2xl border-2 flex flex-col",
        active ? "border-emerald-600" : "border-slate-700",
        className,
      )}
    >
      <div className="bg-slate-950 px-3 py-2 flex items-center justify-between border-b border-slate-800">
        <span className="font-cinzel text-emerald-400 text-sm">{title}</span>
        <div className="flex items-center gap-2">
          {onMinimize && (
            <button
              onClick={onMinimize}
              className="text-slate-400 hover:text-amber-400 text-xs"
              aria-label="Minimize"
            >
              _
            </button>
          )}
          {onMaximize && (
            <button
              onClick={onMaximize}
              className="text-slate-400 hover:text-blue-400 text-xs"
              aria-label="Maximize"
            >
              ▢
            </button>
          )}
          {onClose && (
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-red-400 text-xs"
              aria-label="Close"
            >
              ✕
            </button>
          )}
        </div>
      </div>
      <div className="flex-1 overflow-auto bg-slate-900">{children}</div>
    </div>
  );
}