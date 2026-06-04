import { cn } from "../../lib/utils";

interface MetricCardProps {
  title: string;
  value: string;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
}

export function MetricCard({
  title,
  value,
  change,
  changeLabel,
  icon,
}: MetricCardProps) {
  const isPositive = change !== undefined && change >= 0;

  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted-foreground">{title}</span>
        {icon && <span className="text-muted-foreground">{icon}</span>}
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-bold">{value}</span>
        {change !== undefined && (
          <span
            className={cn(
              "text-sm",
              isPositive ? "text-bullish" : "text-bearish"
            )}
          >
            {isPositive ? "+" : ""}
            {change.toFixed(2)}%
            {changeLabel && (
              <span className="text-muted-foreground"> {changeLabel}</span>
            )}
          </span>
        )}
      </div>
    </div>
  );
}
