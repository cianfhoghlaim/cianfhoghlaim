"use client";

// <CiLandmark> — the 5 NCCA Key Competencies land-marks on the map
// Per docs/BROWN_AJAH_THEMING.md, the 5 NCCA Key Competencies are the
// 5 land-marks on the map (one per subnation for the 5 mainland ones,
// with Isle of Man as the 6th).

import * as React from "react";
import { cn } from "../utils";

export type KeyCompetencySlug =
  | "communicating"
  | "information-processing"
  | "critical-creative-thinking"
  | "personal-effectiveness"
  | "working-with-others";

export interface CiLandmarkProps {
  competency: KeyCompetencySlug;
  city: { name: string; coords: { x: number; y: number } };
  subnation: string;
  onClick?: () => void;
  className?: string;
}

const COLORS: Record<KeyCompetencySlug, string> = {
  communicating: "#059669", // Brigid
  "information-processing": "#2563eb", // Ogma
  "critical-creative-thinking": "#ca8a04", // Lugh
  "personal-effectiveness": "#92400e", // Dian Cecht
  "working-with-others": "#b91c1c", // Trí Dé Dána
};

const TUATHA_DE: Record<KeyCompetencySlug, string> = {
  communicating: "Brigid",
  "information-processing": "Ogma",
  "critical-creative-thinking": "Lugh",
  "personal-effectiveness": "Dian Cecht",
  "working-with-others": "Trí Dé Dána",
};

export function CiLandmark({ competency, city, subnation, onClick, className }: CiLandmarkProps) {
  const color = COLORS[competency];

  return (
    <g onClick={onClick} className={cn(onClick && "cursor-pointer")}>
      {/* The 5-gate-tower marker (per docs/BROWN_AJAH_THEMING.md) */}
      <circle
        cx={city.coords.x}
        cy={city.coords.y}
        r="4"
        fill={color}
        stroke="#f59e0b"
        strokeWidth="1"
        opacity="0.95"
      />
      <circle
        cx={city.coords.x}
        cy={city.coords.y}
        r="6"
        fill="none"
        stroke={color}
        strokeWidth="0.5"
        opacity="0.5"
      />
      <text
        x={city.coords.x + 7}
        y={city.coords.y + 2}
        fill="#f8fafc"
        fontSize="4"
        fontWeight="bold"
      >
        {city.name}
      </text>
      <text x={city.coords.x + 7} y={city.coords.y + 7} fill={color} fontSize="3">
        {competency.replace("-", " ")} · {TUATHA_DE[competency]}
      </text>
    </g>
  );
}