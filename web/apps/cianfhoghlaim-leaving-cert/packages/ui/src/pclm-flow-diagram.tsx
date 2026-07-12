"use client";

// <CiPCLMFlowDiagram> — PCLM (Partial Credit, Logical Marking) flow
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R3 (diagram mode 3).
// Uses React Flow + dagre layout (placeholder SVG-based for now).

import * as React from "react";
import { cn } from "../../utils";

export interface PCLMNode {
  id: string;
  label: string;
  type: "question" | "criterion" | "mistake";
  children?: PCLMNode[];
}

export interface CiPCLMFlowDiagramProps {
  data: PCLMNode;
  subjectColor?: string;
  onNodeClick?: (nodeId: string) => void;
  className?: string;
}

export function CiPCLMFlowDiagram({
  data,
  subjectColor,
  onNodeClick,
  className,
}: CiPCLMFlowDiagramProps) {
  return (
    <div className={cn("p-4", className)}>
      <PCLMNodeView
        node={data}
        subjectColor={subjectColor}
        onNodeClick={onNodeClick}
      />
    </div>
  );
}

function PCLMNodeView({
  node,
  subjectColor,
  onNodeClick,
}: {
  node: PCLMNode;
  subjectColor?: string;
  onNodeClick?: (id: string) => void;
}) {
  const color =
    node.type === "question"
      ? subjectColor ? `var(--ci-subject-${subjectColor})` : "#475569"
      : node.type === "criterion"
      ? "#10b981"
      : "#f43f5e";

  return (
    <div className="flex flex-col gap-2 mb-3">
      <button
        onClick={() => onNodeClick?.(node.id)}
        className={cn(
          "px-3 py-2 rounded-lg text-sm text-left border-l-4 transition-all hover:translate-x-1",
          "bg-slate-800 hover:bg-slate-700",
        )}
        style={{ borderLeftColor: color }}
      >
        <span className="text-xs uppercase text-slate-500 mr-2">{node.type}</span>
        {node.label}
      </button>
      {node.children && node.children.length > 0 && (
        <div className="ml-6 pl-3 border-l border-slate-700">
          {node.children.map((child) => (
            <PCLMNodeView
              key={child.id}
              node={child}
              subjectColor={subjectColor}
              onNodeClick={onNodeClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}