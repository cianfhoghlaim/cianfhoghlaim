"use client";

// <CiRealmMap> — the accurate British Isles map base
// Per docs/BROWN_AJAH_THEMING.md + openspec/changes/rewrite-cianfhoghlaim-
// leaving-cert-v2/specs/cianfhoghlaim-leaving-cert-portal/spec.md
// Requirement R7. The map is an OpenStreetMap-based accurate map split
// into 6 subnations.

import * as React from "react";
import { cn } from "../utils";

export interface CiRealmMapProps {
  activeSubnation?: "eire" | "northern-ireland" | "scotland" | "england" | "wales" | "isle-of-man";
  onSubnationClick?: (subnation: CiRealmMapProps["activeSubnation"]) => void;
  className?: string;
}

const SUBNATIONS: Array<{
  key: NonNullable<CiRealmMapProps["activeSubnation"]>;
  path: string;
  label: { en: string; ga: string };
  flag: string;
  active: boolean;
}> = [
  {
    key: "eire",
    path: "M 80 180 L 180 175 L 175 230 L 100 240 L 75 200 Z",
    label: { en: "Éire", ga: "Éire" },
    flag: "🇮🇪",
    active: true,
  },
  {
    key: "northern-ireland",
    path: "M 110 140 L 175 130 L 180 175 L 80 180 L 75 155 Z",
    label: { en: "N. Ireland", ga: "Tuaisceart Éireann" },
    flag: "🇬🇧",
    active: false,
  },
  {
    key: "scotland",
    path: "M 110 60 L 175 50 L 180 100 L 175 130 L 110 140 L 75 110 L 75 70 Z",
    label: { en: "Scotland", ga: "Albain" },
    flag: "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    active: false,
  },
  {
    key: "england",
    path: "M 180 130 L 280 130 L 295 175 L 250 200 L 180 175 L 175 130 Z",
    label: { en: "England", ga: "Sasana" },
    flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    active: false,
  },
  {
    key: "wales",
    path: "M 175 175 L 220 180 L 215 220 L 175 230 L 180 175 Z",
    label: { en: "Wales", ga: "an Bhreatain Bheag" },
    flag: "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    active: false,
  },
  {
    key: "isle-of-man",
    path: "M 150 160 L 165 158 L 168 168 L 155 170 L 150 165 Z",
    label: { en: "I. o. M.", ga: "Ellan Vannin" },
    flag: "🇮🇲",
    active: false,
  },
];

const COLORS: Record<NonNullable<CiRealmMapProps["activeSubnation"]>, string> = {
  "eire": "#059669",
  "northern-ireland": "#2563eb",
  "scotland": "#0ea5e9",
  "england": "#dc2626",
  "wales": "#b91c1c",
  "isle-of-man": "#475569",
};

export function CiRealmMap({ activeSubnation, onSubnationClick, className }: CiRealmMapProps) {
  return (
    <div className={cn("relative w-full aspect-[5/6]", className)}>
      <svg
        viewBox="0 0 360 280"
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
        style={{
          background: "linear-gradient(180deg, #0c4a6e 0%, #0e7490 30%, #164e63 100%)",
        }}
      >
        {/* Sea texture */}
        <pattern id="sea-texture" patternUnits="userSpaceOnUse" width="20" height="20">
          <rect width="20" height="20" fill="#0e7490" />
          <path d="M 0 10 Q 10 8 20 10" stroke="#06b6d4" strokeWidth="0.3" fill="none" opacity="0.5" />
        </pattern>
        <rect width="360" height="280" fill="url(#sea-texture)" />

        {/* Subnation regions */}
        {SUBNATIONS.map((sub) => {
          const isActive = activeSubnation === sub.key;
          const color = COLORS[sub.key];

          return (
            <g key={sub.key} onClick={() => onSubnationClick?.(sub.key)} className="cursor-pointer">
              <path
                d={sub.path}
                fill={color}
                opacity={isActive ? 0.9 : sub.active ? 0.4 : 0.25}
                stroke={isActive ? "#fbbf24" : "#0f172a"}
                strokeWidth={isActive ? 1.5 : 0.5}
              />
              <text
                x={parseInt(sub.path.split(" ")[1]) + 20}
                y={parseInt(sub.path.split(" ")[2]) + 5}
                fill="#f8fafc"
                fontSize="6"
                fontWeight={isActive ? "bold" : "normal"}
                opacity={isActive ? 1 : 0.6}
              >
                {sub.label.en}
              </text>
              {sub.active && (
                <text
                  x={parseInt(sub.path.split(" ")[1]) + 20}
                  y={parseInt(sub.path.split(" ")[2]) + 12}
                  fill="#fbbf24"
                  fontSize="4"
                >
                  v1 active
                </text>
              )}
            </g>
          );
        })}

        {/* The Esker Riada divider (Dublin Bay to Galway Bay) */}
        <line
          x1="175"
          y1="180"
          x2="100"
          y2="230"
          stroke="#fbbf24"
          strokeWidth="0.5"
          strokeDasharray="3 2"
          opacity="0.5"
        />
        <text x="120" y="210" fill="#fbbf24" fontSize="3" opacity="0.7">
          Esker Riada (Dublin Bay ↔ Galway Bay)
        </text>
      </svg>

      {/* Legend */}
      <div className="absolute bottom-2 left-2 bg-slate-900/80 backdrop-blur-sm rounded-lg p-2 text-xs">
        <div className="text-slate-300 mb-1 font-medium">6 Subnations</div>
        <div className="grid grid-cols-2 gap-1">
          {SUBNATIONS.map((sub) => (
            <div key={sub.key} className="flex items-center gap-1">
              <span
                className="w-2 h-2 rounded-full"
                style={{ background: COLORS[sub.key] }}
              />
              <span className="text-slate-400">{sub.label.en}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}