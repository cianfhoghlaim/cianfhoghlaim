"use client";

// <CiDragonBanner> — the Welsh Dragon Banner (Y Ddraig Goch)
// Per docs/BROWN_AJAH_THEMING.md, the Dragon Banner (Cadwaladr ap
// Cadwallon + Owain Glyndwr; red dragon on white) is the Wales
// subnation flag in the Cianfhoghlaim OS.

import * as React from "react";
import { cn } from "../utils";

export interface CiDragonBannerProps {
  size?: number;
  className?: string;
}

export function CiDragonBanner({ size = 32, className }: CiDragonBannerProps) {
  return (
    <div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
      aria-label="Y Ddraig Goch — the Welsh Dragon Banner"
    >
      <svg width={size} height={size} viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
        {/* White background — per Cadwaladr ap Cadwallon */}
        <rect x="2" y="2" width="28" height="28" fill="#f8fafc" stroke="#b91c1c" strokeWidth="1" />

        {/* Red dragon — Y Ddraig Goch */}
        <path
          d="M 8 8 Q 6 12 8 16 Q 10 20 14 22 Q 16 24 20 22 Q 24 20 26 16 Q 28 12 24 8 Q 22 10 22 14 Q 20 16 18 16 Q 16 14 14 16 Q 12 18 12 22 Q 10 20 10 16 Q 12 12 8 8 Z"
          fill="#b91c1c"
        />

        {/* Golden outline (per Owain Glyndwr's golden dragon variant) */}
        <path
          d="M 8 8 Q 6 12 8 16 Q 10 20 14 22 Q 16 24 20 22 Q 24 20 26 16 Q 28 12 24 8"
          fill="none"
          stroke="#f59e0b"
          strokeWidth="0.5"
        />
      </svg>
    </div>
  );
}