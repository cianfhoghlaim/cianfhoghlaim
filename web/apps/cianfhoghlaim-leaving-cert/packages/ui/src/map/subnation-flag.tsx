"use client";

// <CiSubnationFlag> — the 6 subnation flags
// Per docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css.

import * as React from "react";
import { cn } from "../utils";

export type SubnationSlug =
  | "eire"
  | "northern-ireland"
  | "scotland"
  | "england"
  | "wales"
  | "isle-of-man";

export interface CiSubnationFlagProps {
  subnation: SubnationSlug;
  size?: number;
  className?: string;
}

export function CiSubnationFlag({ subnation, size = 24, className }: CiSubnationFlagProps) {
  switch (subnation) {
    case "eire":
      return <EireFlag size={size} className={className} />;
    case "northern-ireland":
      return <NorthernIrelandFlag size={size} className={className} />;
    case "scotland":
      return <ScotlandFlag size={size} className={className} />;
    case "england":
      return <EnglandFlag size={size} className={className} />;
    case "wales":
      return <WalesFlag size={size} className={className} />;
    case "isle-of-man":
      return <IsleOfManFlag size={size} className={className} />;
  }
}

function EireFlag({ size, className }: { size: number; className?: string }) {
  return (
    <svg width={size} height={size * 2 / 3} viewBox="0 0 60 40" className={cn("rounded", className)}>
      <rect width="60" height="40" fill="#059669" />
      <rect width="40" height="40" fill="#f8fafc" />
      <rect width="20" height="40" fill="#ea580c" />
    </svg>
  );
}

function NorthernIrelandFlag({ size, className }: { size: number; className?: string }) {
  return (
    <svg width={size} height={size * 2 / 3} viewBox="0 0 60 40" className={cn("rounded", className)}>
      <rect width="60" height="40" fill="#1e293b" />
      <rect width="30" height="40" fill="#2563eb" />
      <rect x="13" y="10" width="6" height="20" fill="#f8fafc" />
      <rect x="11" y="12" width="10" height="2" fill="#f8fafc" />
      <rect x="11" y="26" width="10" height="2" fill="#f8fafc" />
      <rect x="11" y="20" width="10" height="2" fill="#f8fafc" />
      <line x1="16" y1="10" x2="16" y2="30" stroke="#f43f5e" strokeWidth="1" />
      <line x1="13" y1="20" x2="19" y2="20" stroke="#f43f5e" strokeWidth="1" />
    </svg>
  );
}

function ScotlandFlag({ size, className }: { size: number; className?: string }) {
  return (
    <svg width={size} height={size * 2 / 3} viewBox="0 0 60 40" className={cn("rounded", className)}>
      <rect width="60" height="40" fill="#1e3a8a" />
      <line x1="0" y1="0" x2="60" y2="40" stroke="#f8fafc" strokeWidth="6" />
      <line x1="60" y1="0" x2="0" y2="40" stroke="#f8fafc" strokeWidth="6" />
    </svg>
  );
}

function EnglandFlag({ size, className }: { size: number; className?: string }) {
  return (
    <svg width={size} height={size * 2 / 3} viewBox="0 0 60 40" className={cn("rounded", className)}>
      <rect width="60" height="40" fill="#f8fafc" />
      <line x1="0" y1="20" x2="60" y2="20" stroke="#dc2626" strokeWidth="8" />
      <line x1="30" y1="0" x2="30" y2="40" stroke="#dc2626" strokeWidth="8" />
    </svg>
  );
}

function WalesFlag({ size, className }: { size: number; className?: string }) {
  return (
    <svg width={size} height={size * 2 / 3} viewBox="0 0 60 40" className={cn("rounded", className)}>
      <rect width="30" height="40" fill="#f8fafc" />
      <rect x="30" width="30" height="40" fill="#16a34a" />
      {/* Y Ddraig Goch (simplified) */}
      <path
        d="M 20 10 Q 18 14 20 18 Q 22 22 25 24 Q 27 26 30 24 Q 32 22 32 18 Q 30 16 28 18 Q 26 16 25 18 Q 24 22 22 20 Q 21 18 22 14 Q 24 12 20 10 Z"
        fill="#b91c1c"
      />
    </svg>
  );
}

function IsleOfManFlag({ size, className }: { size: number; className?: string }) {
  return (
    <svg width={size} height={size * 2 / 3} viewBox="0 0 60 40" className={cn("rounded", className)}>
      <rect width="60" height="40" fill="#dc2626" />
      <g stroke="#f8fafc" strokeWidth="1" fill="none">
        <path d="M 8 10 L 20 26 L 8 30 M 16 16 L 16 36" />
        <path d="M 52 10 L 40 26 L 52 30 M 44 16 L 44 36" />
      </g>
    </svg>
  );
}