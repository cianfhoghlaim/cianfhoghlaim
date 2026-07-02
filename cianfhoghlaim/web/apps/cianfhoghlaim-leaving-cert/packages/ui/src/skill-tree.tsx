"use client";

// <CiSkillTree> — Clair Obscur material library + BitCraft Empire Panel
// Per UI_INSPIRATION_GUIDE.md, the skill tree shows the Student → Subject →
// Mastery hierarchy (per the Brown Ajah theming).

import * as React from "react";
import { cn } from "./utils";

export interface SkillNode {
  id: string;
  label: string;
  tier: number; // 1-13 (the 13 éraic tiers)
  level?: "low" | "medium" | "high";
  unlocked?: boolean;
  children?: SkillNode[];
}

export interface CiSkillTreeProps {
  root: SkillNode;
  onSelect?: (nodeId: string) => void;
  subjectColor?: string;
  className?: string;
}

export function CiSkillTree({ root, onSelect, subjectColor, className }: CiSkillTreeProps) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3 p-4 rounded-2xl border-2 bg-slate-900",
        subjectColor ? `border-[var(--ci-subject-${subjectColor})]` : "border-amber-700",
        "shadow-2xl",
        className,
      )}
      style={{
        backgroundImage: "var(--ci-material-parchment), var(--ci-material-gold-leaf)",
        backgroundBlendMode: "overlay",
      }}
    >
      <SkillNodeView node={root} onSelect={onSelect} subjectColor={subjectColor} />
    </div>
  );
}

function SkillNodeView({
  node,
  onSelect,
  subjectColor,
}: {
  node: SkillNode;
  onSelect?: (id: string) => void;
  subjectColor?: string;
}) {
  return (
    <div className="flex flex-col gap-2">
      <button
        onClick={() => onSelect?.(node.id)}
        disabled={!node.unlocked}
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-lg text-left transition-colors",
          node.unlocked
            ? "bg-amber-900/40 text-amber-100 hover:bg-amber-800/60 border border-amber-700"
            : "bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed",
        )}
      >
        <span
          className={cn(
            "shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
            node.unlocked ? "bg-amber-700 text-amber-100" : "bg-slate-700 text-slate-500",
          )}
        >
          {node.tier}
        </span>
        <span className="text-sm font-medium">{node.label}</span>
      </button>
      {node.children && node.children.length > 0 && (
        <div className="ml-6 pl-3 border-l border-slate-700 flex flex-col gap-2">
          {node.children.map((child) => (
            <SkillNodeView
              key={child.id}
              node={child}
              onSelect={onSelect}
              subjectColor={subjectColor}
            />
          ))}
        </div>
      )}
    </div>
  );
}