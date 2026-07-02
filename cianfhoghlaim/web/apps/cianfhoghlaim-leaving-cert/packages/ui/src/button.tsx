"use client";

// <CiButton> — Duolingo-style tactile 3D press feedback
// border-b-4 → border-b-2 on active (the 3D press effect)
// Per docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css

import * as React from "react";
import { cn } from "./utils";

export interface CiButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
  subjectColor?: string; // CSS variable name (e.g., "mathematics", "gaeilge")
  asChild?: boolean;
}

const variants = {
  primary:
    "bg-emerald-600 text-white border-b-4 border-emerald-800 hover:bg-emerald-500 active:border-b-2 active:translate-y-[2px]",
  secondary:
    "bg-slate-700 text-slate-100 border-b-4 border-slate-900 hover:bg-slate-600 active:border-b-2 active:translate-y-[2px]",
  outline:
    "bg-transparent text-slate-100 border-2 border-slate-700 hover:bg-slate-800",
  ghost:
    "bg-transparent text-slate-100 hover:bg-slate-800",
};

const sizes = {
  sm: "px-3 py-1.5 text-sm rounded-md",
  md: "px-4 py-2 text-base rounded-lg",
  lg: "px-6 py-3 text-lg rounded-xl",
};

export const CiButton = React.forwardRef<HTMLButtonElement, CiButtonProps>(
  ({ className, variant = "primary", size = "md", subjectColor, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center font-medium transition-all duration-100 select-none",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          variants[variant],
          sizes[size],
          subjectColor && `border-b-4`,
          className,
        )}
        style={subjectColor ? { borderBottomColor: `var(--ci-subject-${subjectColor})` } : undefined}
        {...props}
      >
        {children}
      </button>
    );
  },
);

CiButton.displayName = "CiButton";