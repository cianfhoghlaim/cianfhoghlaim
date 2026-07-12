"use client";

// <CiQuestionSankeyDiagram> — Question → Topic → Difficulty → Year Sankey
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R3 (diagram mode 4).

import * as React from "react";
import { cn } from "../../utils";

export interface SankeyNode {
  id: string;
  label: string;
  layer: "question" | "topic" | "difficulty" | "year";
}

export interface SankeyFlow {
  source: string;
  target: string;
  value: number;
}

export interface CiQuestionSankeyDiagramProps {
  nodes: SankeyNode[];
  flows: SankeyFlow[];
  subjectColor?: string;
  onNodeClick?: (nodeId: string) => void;
  className?: string;
}

export function CiQuestionSankeyDiagram({
  nodes,
  flows,
  subjectColor,
  onNodeClick,
  className,
}: CiQuestionSankeyDiagramProps) {
  // Group nodes by layer
  const layers = {
    question: nodes.filter((n) => n.layer === "question"),
    topic: nodes.filter((n) => n.layer === "topic"),
    difficulty: nodes.filter((n) => n.layer === "difficulty"),
    year: nodes.filter((n) => n.layer === "year"),
  };

  const layerKeys: Array<keyof typeof layers> = ["question", "topic", "difficulty", "year"];

  return (
    <div className={cn("overflow-x-auto p-4", className)}>
      <svg width="800" height="500" viewBox="0 0 800 500" className="w-full">
        {/* Sankey flows */}
        {flows.map((flow, idx) => {
          const sourceIdx = layerKeys.findIndex((l) => l === nodes.find((n) => n.id === flow.source)?.layer);
          const targetIdx = layerKeys.findIndex((l) => l === nodes.find((n) => n.id === flow.target)?.layer);
          if (sourceIdx === -1 || targetIdx === -1 || targetIdx !== sourceIdx + 1) return null;
          const x1 = (sourceIdx + 0.5) * (800 / layerKeys.length);
          const x2 = (targetIdx + 0.5) * (800 / layerKeys.length);

          // Find node positions
          const sourceNodes = layers[layerKeys[sourceIdx]];
          const targetNodes = layers[layerKeys[targetIdx]];
          const sourceI = sourceNodes.findIndex((n) => n.id === flow.source);
          const targetI = targetNodes.findIndex((n) => n.id === flow.target);
          const y1 = ((sourceI + 0.5) / sourceNodes.length) * 500;
          const y2 = ((targetI + 0.5) / targetNodes.length) * 500;

          const color = subjectColor ? `var(--ci-subject-${subjectColor})` : "#475569";
          return (
            <path
              key={idx}
              d={`M ${x1} ${y1} C ${(x1 + x2) / 2} ${y1}, ${(x1 + x2) / 2} ${y2}, ${x2} ${y2}`}
              fill="none"
              stroke={color}
              strokeWidth={Math.max(flow.value / 5, 1)}
              opacity={0.5}
            />
          );
        })}

        {/* Sankey nodes */}
        {layerKeys.map((layerKey, layerIdx) => {
          const layerNodes = layers[layerKey];
          const x = (layerIdx + 0.5) * (800 / layerKeys.length);
          const layerColor =
            layerKey === "question"
              ? "#2563eb"
              : layerKey === "topic"
              ? "#10b981"
              : layerKey === "difficulty"
              ? "#f59e0b"
              : "#f43f5e";

          return (
            <g key={layerKey}>
              {layerNodes.map((node, nodeIdx) => {
                const y = ((nodeIdx + 0.5) / layerNodes.length) * 500;
                return (
                  <g key={node.id} onClick={() => onNodeClick?.(node.id)} className="cursor-pointer">
                    <rect
                      x={x - 8}
                      y={y - 12}
                      width={16}
                      height={24}
                      fill={layerColor}
                      rx={2}
                    />
                    <text x={x + 12} y={y + 3} fill="#f8fafc" fontSize="9">
                      {node.label}
                    </text>
                  </g>
                );
              })}
            </g>
          );
        })}
      </svg>
    </div>
  );
}