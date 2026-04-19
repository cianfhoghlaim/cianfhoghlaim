import { createFileRoute } from "@tanstack/react-router";
import { MetricCard } from "../components/ui/MetricCard";
import { ProtocolCard } from "../components/ui/ProtocolCard";
import { PriceChart } from "../components/charts/PriceChart";
import { useState } from "react";

export const Route = createFileRoute("/analytics")({
  component: AnalyticsPage,
});

interface ProtocolData {
  name: string;
  tvl: string;
  tvlValue: number;
  apy: string;
  category: string;
  status: "healthy" | "warning" | "critical";
  description: string;
  risks: string[];
}

const protocols: ProtocolData[] = [
  {
    name: "Ethena",
    tvl: "$2.8B",
    tvlValue: 2800000000,
    apy: "27.4%",
    category: "Synthetic USD",
    status: "healthy",
    description:
      "Synthetic dollar protocol using delta-neutral hedging strategies",
    risks: ["Funding rate volatility", "CEX counterparty risk"],
  },
  {
    name: "Aave v3",
    tvl: "$12.4B",
    tvlValue: 12400000000,
    apy: "3.2%",
    category: "Lending",
    status: "healthy",
    description: "Decentralized lending and borrowing protocol",
    risks: ["Smart contract risk", "Liquidation cascades"],
  },
  {
    name: "Pendle",
    tvl: "$4.1B",
    tvlValue: 4100000000,
    apy: "32.1%",
    category: "Yield Trading",
    status: "healthy",
    description: "Yield tokenization and trading protocol",
    risks: ["Complexity risk", "Market maturity risk"],
  },
  {
    name: "Curve",
    tvl: "$2.1B",
    tvlValue: 2100000000,
    apy: "8.5%",
    category: "DEX",
    status: "warning",
    description: "Stablecoin-focused decentralized exchange",
    risks: ["Impermanent loss", "Governance attack surface"],
  },
  {
    name: "Lido",
    tvl: "$22.3B",
    tvlValue: 22300000000,
    apy: "3.8%",
    category: "Liquid Staking",
    status: "healthy",
    description: "Liquid staking solution for Ethereum",
    risks: ["Slashing risk", "Centralization concerns"],
  },
  {
    name: "GMX",
    tvl: "$520M",
    tvlValue: 520000000,
    apy: "18.2%",
    category: "Perpetuals",
    status: "warning",
    description: "Decentralized perpetual exchange",
    risks: ["Trader PnL exposure", "Oracle manipulation"],
  },
];

const marketMetrics = {
  totalTvl: "$44.2B",
  avgApy: "12.3%",
  activeProtocols: 156,
  riskScore: 6.2,
};

export default function AnalyticsPage() {
  const [selectedProtocol, setSelectedProtocol] = useState<ProtocolData | null>(
    null
  );
  const [sortBy, setSortBy] = useState<"tvl" | "apy">("tvl");
  const [filterCategory, setFilterCategory] = useState<string>("all");

  const categories = ["all", ...new Set(protocols.map((p) => p.category))];

  const filteredProtocols = protocols
    .filter((p) => filterCategory === "all" || p.category === filterCategory)
    .sort((a, b) => {
      if (sortBy === "tvl") return b.tvlValue - a.tvlValue;
      return parseFloat(b.apy) - parseFloat(a.apy);
    });

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold">DeFi Analytics</h1>
        <p className="text-muted-foreground">
          Protocol metrics, risk analysis, and market overview
        </p>
      </div>

      {/* Market Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <MetricCard
          title="Total TVL Tracked"
          value={marketMetrics.totalTvl}
          change={5.2}
          changeLabel="7d"
        />
        <MetricCard
          title="Average APY"
          value={marketMetrics.avgApy}
          change={-0.8}
          changeLabel="7d"
        />
        <MetricCard
          title="Active Protocols"
          value={marketMetrics.activeProtocols.toString()}
        />
        <MetricCard
          title="Risk Score"
          value={`${marketMetrics.riskScore}/10`}
          changeLabel="Moderate"
        />
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Category:</span>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="rounded-lg border bg-background px-3 py-1.5 text-sm"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat === "all" ? "All Categories" : cat}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as "tvl" | "apy")}
            className="rounded-lg border bg-background px-3 py-1.5 text-sm"
          >
            <option value="tvl">TVL</option>
            <option value="apy">APY</option>
          </select>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Protocol List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="font-semibold">Protocols</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {filteredProtocols.map((protocol) => (
              <ProtocolCard
                key={protocol.name}
                name={protocol.name}
                tvl={protocol.tvl}
                apy={protocol.apy}
                category={protocol.category}
                status={protocol.status}
                onClick={() => setSelectedProtocol(protocol)}
              />
            ))}
          </div>
        </div>

        {/* Protocol Details */}
        <div className="rounded-lg border bg-card">
          {selectedProtocol ? (
            <div className="p-4 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">
                  {selectedProtocol.name}
                </h2>
                <button
                  onClick={() => setSelectedProtocol(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  ✕
                </button>
              </div>
              <p className="text-sm text-muted-foreground">
                {selectedProtocol.description}
              </p>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">TVL</p>
                  <p className="text-lg font-semibold">{selectedProtocol.tvl}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">APY</p>
                  <p className="text-lg font-semibold text-green-500">
                    {selectedProtocol.apy}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Key Risks</p>
                <ul className="space-y-1">
                  {selectedProtocol.risks.map((risk, i) => (
                    <li
                      key={i}
                      className="flex items-center gap-2 text-sm text-muted-foreground"
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">TVL History</p>
                <PriceChart
                  symbol={selectedProtocol.name}
                  height={150}
                />
              </div>

              <div className="flex gap-2">
                <button className="flex-1 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
                  View in Graph
                </button>
                <button className="flex-1 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted">
                  Read Docs
                </button>
              </div>
            </div>
          ) : (
            <div className="flex h-full min-h-[400px] items-center justify-center p-8 text-center text-muted-foreground">
              <div>
                <p className="text-lg font-medium">Select a protocol</p>
                <p className="text-sm">
                  Click on any protocol card to view detailed analytics
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Risk Heatmap */}
      <div className="rounded-lg border bg-card p-4">
        <h2 className="mb-4 font-semibold">Risk Distribution</h2>
        <div className="grid grid-cols-3 gap-2">
          {[
            { label: "Smart Contract", level: "low" },
            { label: "Economic", level: "medium" },
            { label: "Governance", level: "low" },
            { label: "Counterparty", level: "high" },
            { label: "Oracle", level: "medium" },
            { label: "Liquidity", level: "low" },
          ].map((risk) => (
            <div
              key={risk.label}
              className={`rounded-lg p-3 text-center ${
                risk.level === "low"
                  ? "bg-green-500/10 text-green-500"
                  : risk.level === "medium"
                  ? "bg-amber-500/10 text-amber-500"
                  : "bg-red-500/10 text-red-500"
              }`}
            >
              <p className="text-sm font-medium">{risk.label}</p>
              <p className="text-xs capitalize">{risk.level}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
