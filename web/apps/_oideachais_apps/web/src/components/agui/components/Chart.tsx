/**
 * Chart Component (Placeholder)
 *
 * Displays chart data from agent responses.
 * This is a placeholder - in production, integrate with a chart library.
 * Rendered by agents via AG-UI GenerativeUI events.
 */

import { BarChart3 } from "lucide-react";
import { cn } from "../../../lib/utils";
import type { AgentComponentProps } from "../ComponentRegistry";

interface DataPoint {
  label: string;
  value: number;
  color?: string;
}

interface ChartProps extends AgentComponentProps {
  title?: string;
  type?: "bar" | "line" | "pie";
  data: DataPoint[];
  xLabel?: string;
  yLabel?: string;
}

export default function Chart({
  title,
  type = "bar",
  data,
  xLabel,
  yLabel,
}: ChartProps) {
  const maxValue = Math.max(...data.map((d) => d.value));

  return (
    <div className="rounded-lg border bg-card p-4 space-y-4">
      {/* Header */}
      {title && (
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-primary" />
          <h3 className="font-medium text-sm">{title}</h3>
          <span className="text-xs text-muted-foreground">({type})</span>
        </div>
      )}

      {/* Simple bar visualization */}
      <div className="space-y-2">
        {data.map((point, index) => (
          <div key={index} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">{point.label}</span>
              <span className="font-medium">{point.value}</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  point.color || "bg-primary"
                )}
                style={{ width: `${(point.value / maxValue) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Axis labels */}
      {(xLabel || yLabel) && (
        <div className="flex justify-between text-xs text-muted-foreground pt-2 border-t">
          {yLabel && <span>{yLabel}</span>}
          {xLabel && <span>{xLabel}</span>}
        </div>
      )}

      {/* Note about placeholder */}
      <p className="text-xs text-muted-foreground italic pt-2">
        Note: This is a simplified visualization. For production, integrate with
        a chart library like Recharts or Chart.js.
      </p>
    </div>
  );
}
