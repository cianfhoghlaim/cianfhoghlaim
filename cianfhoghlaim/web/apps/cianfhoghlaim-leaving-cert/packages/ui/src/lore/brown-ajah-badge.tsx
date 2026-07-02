"use client";

// <CiBrownAjahBadge> — the russet brown knotwork badge
// Per docs/BROWN_AJAH_THEMING.md, the Brown Ajah badge is a
// knotwork pattern in russet brown (the colour of fertile earth).
// It appears in the Cianfhoghlaim OS window chrome.

import * as React from "react";
import { cn } from "../utils";

export interface CiBrownAjahBadgeProps {
  size?: number;
  className?: string;
}

export function CiBrownAjahBadge({ size = 32, className }: CiBrownAjahBadgeProps) {
  return (
    <div
      className={cn("relative inline-flex items-center justify-center rounded-full", className)}
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 32 32"
        xmlns="http://www.w3.org/2000/svg"
        aria-label="Brown Ajah badge"
      >
        {/* Outer ring — russet brown */}
        <circle cx="16" cy="16" r="15" fill="#92400e" stroke="#f59e0b" strokeWidth="1" />

        {/* Inner knotwork pattern — the Trí Dé Dána (3 crafts) */}
        <g stroke="#f59e0b" strokeWidth="1.2" fill="none">
          <path d="M 8 16 Q 12 8 16 16 Q 20 24 24 16" />
          <path d="M 8 16 Q 12 24 16 16 Q 20 8 24 16" />
        </g>

        {/* Central cauldron — the Dagda's cauldron of plenty */}
        <ellipse cx="16" cy="20" rx="5" ry="2" fill="#f59e0b" opacity="0.8" />

        {/* Flame above */}
        <path
          d="M 14 12 Q 16 7 18 12 Q 17 10 16 11 Q 15 10 14 12 Z"
          fill="#fb923c"
        />
      </svg>
    </div>
  );
}