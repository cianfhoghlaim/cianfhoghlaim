"use client";

// <CiConceptMapDiagram> — concept-map of the syllabus LO + 5 NCCA Key Competencies
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R3 (diagram mode 1).

import * as React from "react";
import { cn } from "../../utils";

export interface ConceptNode {
  id: string;
  label: string;
  type: "root" | "subject" | "topic" | "lo";
  children?: ConceptNode[];
}

export interface CiConceptMapDiagramProps {
  data: ConceptNode;
  subjectColor?: string;
  onNodeClick?: (nodeId: string) => void;
  className?: string;
}

export function CiConceptMapDiagram({
  data,
  subjectColor,
  onNodeClick,
  className,
}: CiConceptMapDiagramProps) {
  return (
    <div className={cn("flex flex-col items-center", className)}>
      <ConceptNodeView
        node={data}
        subjectColor={subjectColor}
        onNodeClick={onNodeClick}
        depth={0}
      />
    </div>
  );
}

function ConceptNodeView({
  node,
  subjectColor,
  onNodeClick,
  depth,
}: {
  node: ConceptNode;
  subjectColor?: string;
  onNodeClick?: (id: string) => void;
  depth: number;
}) {
  const nodeColor =
    node.type === "root"
      ? "#f59e0b"
      : subjectColor
      ? `var(--ci-subject-${subjectColor})`
      : "#475569";

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={() => onNodeClick?.(node.id)}
        className={cn(
          "px-4 py-2 rounded-lg text-sm font-medium border-2 transition-all",
          "hover:scale-105 hover:shadow-lg",
          depth === 0 ? "text-base font-bold px-6 py-3" : "",
        )}
        style={{
          borderColor: nodeColor,
          background: `${nodeColor}20`,
        }}
      >
        {node.label}
      </button>
      {node.children && node.children.length > 0 && (
        <div className="flex flex-wrap justify-center gap-4 mt-2">
          {node.children.map((child) => (
            <ConceptNodeView
              key={child.id}
              node={child}
              subjectColor={subjectColor}
              onNodeClick={onNodeClick}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}