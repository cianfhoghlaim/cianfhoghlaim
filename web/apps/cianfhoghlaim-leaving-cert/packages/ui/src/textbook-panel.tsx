"use client";

// <CiTextbookPanel> — Clair Obscur material library frame
// Per UI_INSPIRATION_GUIDE.md, the Clair Obscur panels use the
// material library (parchment + slate + ink-wash + gold-leaf + knotwork).
// The Cianfhoghlaim OS uses these for the per-subject textbook frames.

import * as React from "react";
import { cn } from "./utils";

export type CiTextbookMaterial = "parchment" | "slate" | "ink-wash" | "gold-leaf" | "knotwork";

export interface CiTextbookPanelProps {
  title: string;
  material?: CiTextbookMaterial;
  subjectColor?: string;
  children: React.ReactNode;
  className?: string;
}

export function CiTextbookPanel({
  title,
  material = "parchment",
  subjectColor,
  children,
  className,
}: CiTextbookPanelProps) {
  return (
    <div
      className={cn(
        "relative rounded-2xl p-6 overflow-hidden",
        subjectColor ? `border-2 border-[var(--ci-subject-${subjectColor})]` : "border-2 border-amber-700",
        className,
      )}
      style={{
        backgroundImage: `var(--ci-material-${material})`,
        backgroundBlendMode: "multiply",
      }}
    >
      {/* Material overlay (knotwork pattern) */}
      {material === "knotwork" && (
        <div
          className="absolute inset-0 opacity-30 pointer-events-none"
          style={{ backgroundImage: "var(--ci-material-knotwork)" }}
        />
      )}

      {/* Gold leaf accent */}
      {material === "gold-leaf" && (
        <div
          className="absolute top-0 left-0 right-0 h-1"
          style={{ background: "linear-gradient(90deg, transparent, #f59e0b, transparent)" }}
        />
      )}

      <div className="relative z-10">
        <h2 className="font-cinzel text-2xl font-bold text-slate-100 mb-4 text-center">
          {title}
        </h2>
        {children}
      </div>
    </div>
  );
}