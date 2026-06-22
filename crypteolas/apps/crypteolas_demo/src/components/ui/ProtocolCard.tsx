import { cn } from "../../lib/utils";

interface ProtocolCardProps {
  name: string;
  tvl: string;
  apy: string;
  category: string;
  status: "healthy" | "warning" | "critical";
  onClick?: () => void;
}

export function ProtocolCard({
  name,
  tvl,
  apy,
  category,
  status,
  onClick,
}: ProtocolCardProps) {
  const statusColors = {
    healthy: "bg-green-500",
    warning: "bg-yellow-500",
    critical: "bg-red-500",
  };

  return (
    <div
      className={cn(
        "rounded-lg border bg-card p-4 transition-colors hover:bg-accent",
        onClick && "cursor-pointer"
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={cn("h-2 w-2 rounded-full", statusColors[status])} />
          <h3 className="font-semibold">{name}</h3>
        </div>
        <span className="rounded bg-muted px-2 py-0.5 text-xs">{category}</span>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4">
        <div>
          <span className="text-sm text-muted-foreground">TVL</span>
          <p className="text-lg font-medium">{tvl}</p>
        </div>
        <div>
          <span className="text-sm text-muted-foreground">APY</span>
          <p className="text-lg font-medium text-bullish">{apy}</p>
        </div>
      </div>
    </div>
  );
}
