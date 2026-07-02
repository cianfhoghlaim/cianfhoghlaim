"use client";

// <CiDetailCell> — Khan Academy detail cells (left icon + metadata)
// Per docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css and UI_INSPIRATION_GUIDE.md.

import * as React from "react";
import { cn } from "./utils";

export interface CiDetailCellProps {
  icon: React.ReactNode;
  title: string;
  metadata?: string;
  description?: string;
  subjectColor?: string;
  onClick?: () => void;
  className?: string;
}

export function CiDetailCell({
  icon,
  title,
  metadata,
  description,
  subjectColor,
  onClick,
  className,
}: CiDetailCellProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 p-3 rounded-lg border bg-slate-800 hover:bg-slate-700 transition-colors text-left w-full",
        subjectColor ? `border-[var(--ci-subject-${subjectColor})]` : "border-slate-700",
        onClick && "cursor-pointer",
        className,
      )}
    >
      <div className="shrink-0 w-10 h-10 rounded-md flex items-center justify-center bg-slate-900">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-medium text-slate-100 truncate">{title}</div>
        {metadata && <div className="text-xs text-slate-400 truncate">{metadata}</div>}
        {description && <div className="text-xs text-slate-500 mt-0.5">{description}</div>}
      </div>
    </button>
  );
}