"use client";

// <CiTopicHeatmapDiagram> — topic-frequency heatmap
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R3 (diagram mode 2).
// Uses D3-style 2.5D matrix rendering (CSS grid + opacity).

import * as React from "react";
import { cn } from "../../utils";

export interface HeatmapCell {
  topic: string;
  paper: string;
  year: number;
  value: number; // 0-100 (frequency intensity)
}

export interface CiTopicHeatmapDiagramProps {
  data: HeatmapCell[];
  subjectColor?: string;
  onCellClick?: (cell: HeatmapCell) => void;
  className?: string;
}

export function CiTopicHeatmapDiagram({
  data,
  subjectColor,
  onCellClick,
  className,
}: CiTopicHeatmapDiagramProps) {
  const topics = Array.from(new Set(data.map((d) => d.topic)));
  const papers = Array.from(new Set(data.map((d) => d.paper)));
  const years = Array.from(new Set(data.map((d) => d.year))).sort();

  const cellMap = new Map<string, HeatmapCell>();
  data.forEach((d) => cellMap.set(`${d.topic}|${d.paper}|${d.year}`, d));

  return (
    <div className={cn("overflow-x-auto", className)}>
      <table className="text-xs">
        <thead>
          <tr>
            <th className="text-left text-slate-400 p-1">Topic</th>
            {years.map((year) => (
              <th key={year} colSpan={papers.length} className="text-center text-slate-400 p-1 border-l border-slate-700">
                {year}
              </th>
            ))}
          </tr>
          <tr>
            <th />
            {years.flatMap((year) =>
              papers.map((paper) => (
                <th key={`${year}-${paper}`} className="text-center text-slate-500 p-1">
                  {paper}
                </th>
              )),
            )}
          </tr>
        </thead>
        <tbody>
          {topics.map((topic) => (
            <tr key={topic}>
              <td className="text-slate-300 p-1 font-medium whitespace-nowrap">{topic}</td>
              {years.flatMap((year) =>
                papers.map((paper) => {
                  const cell = cellMap.get(`${topic}|${paper}|${year}`);
                  const value = cell?.value ?? 0;
                  const color = subjectColor ? `var(--ci-subject-${subjectColor})` : "#475569";
                  return (
                    <td
                      key={`${topic}-${paper}-${year}`}
                      onClick={() => cell && onCellClick?.(cell)}
                      className={cn("p-1 cursor-pointer hover:ring-1 hover:ring-amber-400")}
                      style={{
                        background: `${color}${Math.round(value * 2.55).toString(16).padStart(2, "0")}`,
                      }}
                      title={`${topic} · ${paper} · ${year}: ${value}`}
                    >
                      <div className="w-8 h-8" />
                    </td>
                  );
                }),
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}