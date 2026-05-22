import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import {
  AnalyticsPanel,
  MetricCard,
  ProtocolTable,
  ChunkyButton,
} from "../components/dashboard";
import { Search, Filter, Download, Share2 } from "lucide-react";
import type { Protocol } from "../components/dashboard/ProtocolTable";

export const Route = createFileRoute("/analytics")({
  component: AnalyticsPage,
});

const PROTOCOLS: Protocol[] = [
  {
    id: "1",
    name: "Lido",
    tvl: "$34.2B",
    change24h: 2.4,
    chains: ["Ethereum", "Solana"],
    category: "Liquid Staking",
    status: "active",
  },
  {
    id: "2",
    name: "Aave V3",
    tvl: "$12.8B",
    change24h: -1.2,
    chains: ["Ethereum", "Arbitrum", "Optimism", "Polygon"],
    category: "Lending",
    status: "active",
  },
  {
    id: "3",
    name: "Uniswap V3",
    tvl: "$8.4B",
    change24h: 0.8,
    chains: ["Ethereum", "Arbitrum", "Optimism", "Polygon"],
    category: "DEX",
    status: "active",
  },
  {
    id: "4",
    name: "EigenLayer",
    tvl: "$15.1B",
    change24h: 5.2,
    chains: ["Ethereum"],
    category: "Restaking",
    status: "active",
  },
  {
    id: "5",
    name: "Maker",
    tvl: "$6.9B",
    change24h: -0.5,
    chains: ["Ethereum"],
    category: "CDP",
    status: "warning",
  },
  {
    id: "6",
    name: "Rocket Pool",
    tvl: "$3.8B",
    change24h: 1.1,
    chains: ["Ethereum"],
    category: "Liquid Staking",
    status: "active",
  },
  {
    id: "7",
    name: "GMX",
    tvl: "$640M",
    change24h: -3.4,
    chains: ["Arbitrum", "Avalanche"],
    category: "Derivatives",
    status: "risk",
  },
  {
    id: "8",
    name: "Curve",
    tvl: "$2.1B",
    change24h: 0.2,
    chains: ["Ethereum", "Arbitrum"],
    category: "DEX",
    status: "warning",
  },
];

const METRICS = [
  {
    label: "Total Value Locked",
    value: "$89.2B",
    change: 2.4,
    changeLabel: "24h",
    sparklineData: [82, 84, 83, 85, 86, 88, 89, 92, 89.2],
    color: "emerald" as const,
  },
  {
    label: "Active Wallets",
    value: "2.1M",
    change: -1.2,
    changeLabel: "24h",
    sparklineData: [2.2, 2.3, 2.1, 2.15, 2.1, 2.05, 2.1],
    color: "rose" as const,
  },
  {
    label: "Protocol Revenue",
    value: "$12.4M",
    change: 5.8,
    changeLabel: "7d",
    sparklineData: [10, 11, 10.5, 12, 11.8, 12.2, 12.4],
    color: "indigo" as const,
  },
  {
    label: "Gas (Gwei)",
    value: "45",
    change: -12.3,
    changeLabel: "1h",
    sparklineData: [60, 55, 48, 52, 45, 42, 45],
    color: "slate" as const,
  },
];

function AnalyticsPage() {
  const [timeframe, setTimeframe] = useState<"24h" | "7d" | "30d" | "1y">("7d");

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="sticky top-0 z-40 w-full border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="text-xl font-bold text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              Crypteolas
            </Link>
            <span className="text-slate-700">/</span>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <h1 className="text-sm font-semibold text-slate-200">
                Live Analytics
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <nav className="hidden md:flex gap-6 mr-4">
              <Link
                to="/protocols"
                className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
              >
                Protocols
              </Link>
              <Link
                to="/github"
                className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
              >
                GitHub Intel
              </Link>
            </nav>
            <ChunkyButton
              variant="secondary"
              size="sm"
              icon={<Share2 className="h-4 w-4" />}
            >
              Share
            </ChunkyButton>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold tracking-tight">
              Market Overview
            </h2>
            <span className="text-sm text-slate-500 mt-1">
              Last updated: Just now
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800">
              {(["24h", "7d", "30d", "1y"] as const).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${
                    timeframe === tf
                      ? "bg-indigo-500 text-white shadow-sm"
                      : "text-slate-400 hover:text-white hover:bg-slate-800"
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>

            <ChunkyButton
              variant="secondary"
              size="sm"
              icon={<Download className="h-4 w-4" />}
            >
              Export
            </ChunkyButton>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {METRICS.map((metric) => (
            <MetricCard key={metric.label} {...metric} />
          ))}
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <AnalyticsPanel
              title="Total Value Locked"
              className="h-[400px]"
              headerActions={
                <div className="flex gap-2">
                  <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-xs border border-indigo-500/30">
                    DeFi
                  </span>
                  <span className="px-2 py-0.5 rounded bg-slate-700 text-slate-300 text-xs">
                    All Chains
                  </span>
                </div>
              }
            >
              <div className="h-full w-full flex flex-col">
                <div className="flex-1 flex items-end justify-between gap-2 px-2 pb-2">
                  {[
                    65, 70, 68, 75, 82, 78, 85, 89, 84, 88, 92, 89, 94, 98, 95,
                    92, 96, 99, 102, 98, 105, 108, 104, 110,
                  ].map((value, i) => (
                    <div
                      key={i}
                      className="flex-1 group relative flex flex-col items-center justify-end h-full"
                    >
                      <div
                        className="w-full bg-gradient-to-t from-indigo-600/20 to-indigo-500/50 rounded-t border-t border-indigo-400/30 transition-all duration-300 group-hover:from-indigo-500/40 group-hover:to-indigo-400/60"
                        style={{ height: `${value * 0.8}%` }}
                      >
                        <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-xs px-2 py-1 rounded border border-slate-700 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                          ${(value * 0.85).toFixed(1)}B
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex justify-between px-2 pt-2 border-t border-slate-800 text-xs text-slate-500 font-mono">
                  <span>00:00</span>
                  <span>04:00</span>
                  <span>08:00</span>
                  <span>12:00</span>
                  <span>16:00</span>
                  <span>20:00</span>
                </div>
              </div>
            </AnalyticsPanel>

            <AnalyticsPanel title="Top Protocols by TVL">
              <div className="flex items-center gap-2 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Search protocols..."
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                </div>
                <ChunkyButton
                  variant="secondary"
                  size="sm"
                  icon={<Filter className="h-4 w-4" />}
                >
                  Filter
                </ChunkyButton>
              </div>
              <ProtocolTable data={PROTOCOLS} />
            </AnalyticsPanel>
          </div>

          <div className="space-y-6">
            <AnalyticsPanel title="Market Sentiment" className="min-h-[250px]">
              <div className="space-y-6 p-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-400">
                    Fear & Greed Index
                  </span>
                  <span className="text-xl font-bold text-emerald-400">74</span>
                </div>

                <div className="relative h-4 bg-slate-800 rounded-full overflow-hidden">
                  <div className="absolute inset-y-0 left-0 w-[74%] bg-gradient-to-r from-rose-500 via-yellow-500 to-emerald-500" />
                  <div
                    className="absolute top-0 bottom-0 w-1 bg-white shadow-[0_0_10px_rgba(255,255,255,0.5)]"
                    style={{ left: "74%" }}
                  />
                </div>
                <div className="flex justify-between text-xs text-slate-500 font-medium">
                  <span>Fear</span>
                  <span>Neutral</span>
                  <span>Greed</span>
                </div>

                <div className="pt-4 border-t border-slate-800">
                  <h4 className="text-sm font-semibold text-slate-200 mb-3">
                    Dominance
                  </h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">Bitcoin</span>
                      <span className="text-white font-mono">52.4%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-orange-500 h-full rounded-full"
                        style={{ width: "52.4%" }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-sm">
                      <span className="text-slate-400">Ethereum</span>
                      <span className="text-white font-mono">18.1%</span>
                    </div>
                    <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-indigo-500 h-full rounded-full"
                        style={{ width: "18.1%" }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </AnalyticsPanel>

            <div className="bg-gradient-to-br from-indigo-600 to-violet-700 rounded-xl p-6 text-white relative overflow-hidden group">
              <div className="relative z-10">
                <h3 className="text-lg font-bold mb-2">AI Copilot</h3>
                <p className="text-indigo-100 text-sm mb-4">
                  Ask questions about on-chain data and get instant insights.
                </p>
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Ask about TVL trends..."
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-indigo-200 focus:outline-none focus:bg-white/20 transition-all backdrop-blur-sm"
                  />
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 px-1.5 py-0.5 rounded bg-white/20 text-[10px] font-mono text-indigo-100 border border-white/10">
                    ⌘K
                  </div>
                </div>
              </div>

              <div className="absolute -top-12 -right-12 w-32 h-32 bg-white/10 rounded-full blur-2xl group-hover:bg-white/20 transition-colors duration-500" />
              <div className="absolute -bottom-12 -left-12 w-32 h-32 bg-indigo-900/40 rounded-full blur-2xl" />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
