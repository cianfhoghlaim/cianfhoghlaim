"use client";

// <CiTuathanWagon> — the Irish Travellers' covered wagon (mobile client)
// Per docs/BROWN_AJAH_THEMING.md, the Tuatha'an wagon is the
// Cianfhoghlaim mobile client. The student-as-Tuatha'an travels
// the 6 subnations in this wagon.

import * as React from "react";
import { cn } from "../utils";

export interface CiTuathanWagonProps {
  size?: number;
  className?: string;
}

export function CiTuathanWagon({ size = 20, className }: CiTuathanWagonProps) {
  return (
    <div
      className={cn("relative inline-flex items-center justify-center", className)}
      style={{ width: size, height: size }}
      aria-label="Tuatha'an wagon (mobile client)"
    >
      <svg width={size} height={size} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        {/* Wagon body */}
        <rect x="3" y="8" width="18" height="8" fill="#92400e" stroke="#475569" strokeWidth="0.5" rx="1" />
        {/* Curved cover */}
        <path d="M 3 8 Q 12 2 21 8" fill="#a16207" stroke="#475569" strokeWidth="0.5" />
        {/* Wheels */}
        <circle cx="7" cy="18" r="2.5" fill="#1e293b" stroke="#92400e" strokeWidth="0.5" />
        <circle cx="17" cy="18" r="2.5" fill="#1e293b" stroke="#92400e" strokeWidth="0.5" />
        <circle cx="7" cy="18" r="1" fill="#92400e" />
        <circle cx="17" cy="18" r="1" fill="#92400e" />
      </svg>
    </div>
  );
}