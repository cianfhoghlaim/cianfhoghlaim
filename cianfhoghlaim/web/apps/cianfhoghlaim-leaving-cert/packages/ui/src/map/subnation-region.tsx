"use client";

// <CiSubnationRegion> — the 6 subnations SVG regions
// Used inside the CiRealmMap.

import * as React from "react";
import { cn } from "../utils";

export interface CiSubnationRegionProps {
  subnation: "eire" | "northern-ireland" | "scotland" | "england" | "wales" | "isle-of-man";
  active?: boolean;
  comingSoon?: boolean;
  onClick?: () => void;
  className?: string;
}

const REGIONS: Record<
  CiSubnationRegionProps["subnation"],
  { path: string; center: { x: number; y: number } }
> = {
  "eire": { path: "M 80 180 L 180 175 L 175 230 L 100 240 L 75 200 Z", center: { x: 120, y: 210 } },
  "northern-ireland": { path: "M 110 140 L 175 130 L 180 175 L 80 180 L 75 155 Z", center: { x: 125, y: 155 } },
  "scotland": { path: "M 110 60 L 175 50 L 180 100 L 175 130 L 110 140 L 75 110 L 75 70 Z", center: { x: 125, y: 95 } },
  "england": { path: "M 180 130 L 280 130 L 295 175 L 250 200 L 180 175 L 175 130 Z", center: { x: 235, y: 165 } },
  "wales": { path: "M 175 175 L 220 180 L 215 220 L 175 230 L 180 175 Z", center: { x: 197, y: 202 } },
  "isle-of-man": { path: "M 150 160 L 165 158 L 168 168 L 155 170 L 150 165 Z", center: { x: 159, y: 164 } },
};

const COLORS: Record<CiSubnationRegionProps["subnation"], string> = {
  "eire": "#059669",
  "northern-ireland": "#2563eb",
  "scotland": "#0ea5e9",
  "england": "#dc2626",
  "wales": "#b91c1c",
  "isle-of-man": "#475569",
};

export function CiSubnationRegion({
  subnation,
  active = false,
  comingSoon = false,
  onClick,
  className,
}: CiSubnationRegionProps) {
  const region = REGIONS[subnation];
  const color = COLORS[subnation];

  return (
    <path
      d={region.path}
      fill={color}
      opacity={active ? 0.9 : comingSoon ? 0.2 : 0.6}
      stroke={active ? "#fbbf24" : "#0f172a"}
      strokeWidth={active ? 1.5 : 0.5}
      onClick={onClick}
      className={cn(
        onClick && "cursor-pointer hover:opacity-80 transition-opacity",
        className,
      )}
    />
  );
}