import { createFileRoute } from "@tanstack/react-router";
import { PriceChart } from "../components/charts/PriceChart";
import { ProtocolCard } from "../components/ui/ProtocolCard";
import { MetricCard } from "../components/ui/MetricCard";

export const Route = createFileRoute("/")({
  component: Dashboard,
});

function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of DeFi metrics and market conditions
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          title="ETH Price"
          value="$3,456.78"
          change={5.2}
          changeLabel="24h"
        />
        <MetricCard
          title="sUSDe APY"
          value="18.5%"
          change={-1.2}
          changeLabel="7d"
        />
        <MetricCard
          title="Ethena TVL"
          value="$2.8B"
          change={3.4}
          changeLabel="30d"
        />
        <MetricCard
          title="USDe Peg"
          value="$0.9998"
          change={0.02}
          changeLabel="24h"
        />
      </div>

      {/* Price Chart */}
      <div className="rounded-lg border bg-card p-4">
        <h2 className="mb-4 text-lg font-semibold">ETH Price</h2>
        <div className="h-[400px]">
          <PriceChart symbol="ETH" timeframe="1d" />
        </div>
      </div>

      {/* Protocol Cards */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">Tracked Protocols</h2>
        <div className="grid grid-cols-3 gap-4">
          <ProtocolCard
            name="Ethena"
            tvl="$2.8B"
            apy="18.5%"
            category="Stablecoin"
            status="healthy"
          />
          <ProtocolCard
            name="Aave v3"
            tvl="$12.5B"
            apy="4.2%"
            category="Lending"
            status="healthy"
          />
          <ProtocolCard
            name="Pendle"
            tvl="$1.2B"
            apy="Variable"
            category="Yield"
            status="healthy"
          />
        </div>
      </div>

      {/* Recent Events */}
      <div>
        <h2 className="mb-4 text-lg font-semibold">Recent Events</h2>
        <div className="space-y-2">
          <EventItem
            timestamp="2h ago"
            title="ETH funding rate spike"
            description="Binance ETH-PERP funding at 0.05% (annualized ~18%)"
            type="info"
          />
          <EventItem
            timestamp="1d ago"
            title="Ethena yield distribution"
            description="Weekly sUSDe rewards distributed, 18.5% APY maintained"
            type="success"
          />
          <EventItem
            timestamp="3d ago"
            title="Aave v3 governance"
            description="AIP-342 passed: Updated stablecoin e-mode parameters"
            type="info"
          />
        </div>
      </div>
    </div>
  );
}

function EventItem({
  timestamp,
  title,
  description,
  type,
}: {
  timestamp: string;
  title: string;
  description: string;
  type: "info" | "success" | "warning" | "error";
}) {
  const colors = {
    info: "border-l-blue-500",
    success: "border-l-green-500",
    warning: "border-l-yellow-500",
    error: "border-l-red-500",
  };

  return (
    <div className={`rounded border border-l-4 ${colors[type]} bg-card p-3`}>
      <div className="flex items-center justify-between">
        <span className="font-medium">{title}</span>
        <span className="text-xs text-muted-foreground">{timestamp}</span>
      </div>
      <p className="text-sm text-muted-foreground">{description}</p>
    </div>
  );
}
