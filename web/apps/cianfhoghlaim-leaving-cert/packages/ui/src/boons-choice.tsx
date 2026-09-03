"use client";

// <CiBoonsChoice> — Hades 3-way vertical choice with god colours
// Per UI_INSPIRATION_GUIDE.md (the Hades boon-selection interface).
// Each "boon" is a formative item choice with 3 vertical options in
// the subject colour.

import * as React from "react";
import { cn } from "./utils";

export interface BoonChoice {
  id: string;
  label: string;
  description?: string;
  color?: string;
  difficulty?: "low" | "medium" | "high";
}

export interface CiBoonsChoiceProps {
  prompt: string;
  choices: [BoonChoice, BoonChoice, BoonChoice];
  onChoose?: (choiceId: string) => void;
  subjectColor?: string;
  className?: string;
}

export function CiBoonsChoice({
  prompt,
  choices,
  onChoose,
  subjectColor,
  className,
}: CiBoonsChoiceProps) {
  return (
    <div className={cn("flex flex-col gap-4", className)}>
      <div className="text-base text-slate-200 font-medium text-center italic">
        {prompt}
      </div>
      <div className="grid grid-cols-3 gap-3">
        {choices.map((choice) => (
          <button
            key={choice.id}
            onClick={() => onChoose?.(choice.id)}
            className={cn(
              "flex flex-col items-center gap-2 p-4 rounded-xl border-2 bg-slate-900 transition-all",
              "hover:scale-105 hover:border-amber-400 hover:shadow-2xl",
              subjectColor ? `border-[var(--ci-subject-${subjectColor})]` : "border-slate-700",
              choice.color && `border-[${choice.color}]`,
            )}
          >
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold text-white"
              style={{
                background: `radial-gradient(circle, ${
                  choice.color ?? (subjectColor ? `var(--ci-subject-${subjectColor})` : "#475569")
                } 0%, ${subjectColor ? `var(--ci-subject-${subjectColor})` : "#1e293b"} 100%)`,
                boxShadow: `0 0 16px ${choice.color ?? "#475569"}80`,
              }}
            >
              {choice.label.charAt(0)}
            </div>
            <div className="text-sm font-bold text-slate-100 text-center">
              {choice.label}
            </div>
            {choice.description && (
              <div className="text-xs text-slate-400 text-center">
                {choice.description}
              </div>
            )}
            {choice.difficulty && (
              <div className="text-xs text-amber-400 uppercase tracking-wider">
                {choice.difficulty}
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}