import React from "react";
import { cn } from "@/lib/utils";

interface TVLSparklineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  className?: string;
  trend?: "up" | "down" | "neutral";
}

export function TVLSparkline({
  data,
  width = 120,
  height = 40,
  color = "#10b981",
  className,
  trend,
}: TVLSparklineProps) {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data
    .map((val, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((val - min) / range) * height;
      return `${x},${y}`;
    })
    .join(" ");

  const finalColor =
    trend === "down" ? "#f43f5e" : trend === "up" ? "#10b981" : color;

  const gradientId = `gradient-${color.replace("#", "")}-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className={cn("overflow-visible", className)}
    >
      <defs>
        <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={finalColor} stopOpacity="0.2" />
          <stop offset="100%" stopColor={finalColor} stopOpacity="0" />
        </linearGradient>
      </defs>

      <path
        d={`M 0 ${height} L ${points} L ${width} ${height} Z`}
        fill={`url(#${gradientId})`}
        stroke="none"
      />

      <polyline
        points={points}
        fill="none"
        stroke={finalColor}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      <circle
        cx={(data.length - 1) * (width / (data.length - 1))}
        cy={height - ((data[data.length - 1] - min) / range) * height}
        r="2"
        fill={finalColor}
      />
    </svg>
  );
}
