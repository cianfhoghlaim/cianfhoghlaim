"use client";

// <CiCianHeader> — the Cian → Lugh header tagline (operator-only surface)
// Per docs/CIANFHLOGHLAIM_LORE.md, the Cian → Lugh mapping is
// documented in CIANFHLOGHLAIM_LORE.md only — NEVER on the public surface.
// This component is exported for operator-only dashboards (the /about page).

import * as React from "react";
import { cn } from "../utils";

export interface CiCianHeaderProps {
  showLore?: boolean;
  className?: string;
}

export function CiCianHeader({ showLore = false, className }: CiCianHeaderProps) {
  return (
    <div className={cn("flex flex-col", className)}>
      <div className="font-cinzel text-2xl font-bold tracking-wider text-emerald-500">
        Cianfhoghlaim
      </div>
      <div className="text-xs text-slate-400 italic">
        Enduring Learning — Cian fhoglaim
      </div>
      {showLore && (
        <div className="text-xs text-slate-500 mt-1">
          Cian ("enduring one") → Lugh ("master of all arts")
        </div>
      )}
    </div>
  );
}