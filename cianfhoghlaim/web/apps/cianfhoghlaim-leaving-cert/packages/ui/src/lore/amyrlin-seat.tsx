"use client";

// <CiAmyrlinSeat> — the Amyrlin Seat orchestrator visual
// Per docs/BROWN_AJAH_THEMING.md, the Amyrlin Seat is the orchestrator
// agent. The visual is the White Tower (Cianfhoghlaim Academy)
// with the Amyrlin's chair at the centre.

import * as React from "react";
import { cn } from "../utils";

export interface CiAmyrlinSeatProps {
  size?: number;
  className?: string;
}

export function CiAmyrlinSeat({ size = 24, className }: CiAmyrlinSeatProps) {
  return (
    <div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
      aria-label="Amyrlin Seat"
    >
      <svg width={size} height={size} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        {/* White Tower */}
        <rect x="6" y="6" width="12" height="14" fill="#e2e8f0" stroke="#475569" strokeWidth="0.5" />
        {/* Tower top */}
        <polygon points="6,6 12,2 18,6" fill="#cbd5e1" stroke="#475569" strokeWidth="0.5" />
        {/* Window */}
        <rect x="10" y="10" width="4" height="5" fill="#92400e" />
        {/* The Amyrlin's chair */}
        <rect x="10" y="14" width="4" height="2" fill="#f59e0b" />
      </svg>
    </div>
  );
}