import React from "react";
import { cn } from "@/lib/utils";
import { TVLSparkline } from "./TVLSparkline";

interface MetricCardProps {
  label: string;
  value: string;
  change: number;
  changeLabel?: string;
  sparklineData?: number[];
  color?: "emerald" | "rose" | "indigo" | "slate";
  className?: string;
}

export function MetricCard({
  label,
  value,
  change,
  changeLabel = "24h",
  sparklineData,
  color,
  className,
}: MetricCardProps) {
  const trend = change >= 0 ? "up" : "down";

  const baseColor = color || (trend === "up" ? "emerald" : "rose");

  const colorMap = {
    emerald: {
      text: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
      chart: "#10b981",
    },
    rose: {
      text: "text-rose-400",
      bg: "bg-rose-500/10",
      border: "border-rose-500/20",
      chart: "#f43f5e",
    },
    indigo: {
      text: "text-indigo-400",
      bg: "bg-indigo-500/10",
      border: "border-indigo-500/20",
      chart: "#6366f1",
    },
    slate: {
      text: "text-slate-400",
      bg: "bg-slate-500/10",
      border: "border-slate-500/20",
      chart: "#94a3b8",
    },
  };

  const styles = colorMap[baseColor];

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-xl border p-5 transition-all duration-300",
        "bg-slate-800/50 border-slate-700",
        "hover:-translate-y-1 hover:shadow-lg hover:border-slate-600",
        "group",
        className,
      )}
    >
      <div className="relative z-10 flex flex-col h-full justify-between">
        <div>
          <div className="text-sm font-medium text-slate-400 mb-1">{label}</div>
          <div className="text-2xl font-bold tracking-tight text-white mb-2">
            {value}
          </div>
        </div>

        <div className="flex items-end justify-between">
          <div
            className={cn(
              "text-sm font-medium flex items-center gap-1",
              styles.text,
            )}
          >
            <span>
              {change > 0 ? "+" : ""}
              {change}%
            </span>
            <span className="text-slate-500 text-xs font-normal">
              ({changeLabel})
            </span>
          </div>

          {sparklineData && (
            <div className="opacity-70 transition-opacity group-hover:opacity-100">
              <TVLSparkline
                data={sparklineData}
                width={80}
                height={30}
                color={styles.chart}
                trend={trend}
              />
            </div>
          )}
        </div>
      </div>

      <div
        className={cn(
          "absolute -right-6 -bottom-6 w-24 h-24 rounded-full blur-2xl opacity-0 transition-opacity group-hover:opacity-20 pointer-events-none",
          styles.bg.replace("/10", ""),
        )}
      />
    </div>
  );
}
