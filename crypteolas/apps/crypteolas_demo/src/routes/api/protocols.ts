/**
 * Protocols API Route
 *
 * Returns DeFi protocol data from the backend
 */

import { createAPIFileRoute } from "@tanstack/start/api";

// Mock protocol data - would come from DuckDB/DeFiLlama in production
const PROTOCOLS = [
  {
    id: "ethena",
    name: "Ethena",
    tvl: 2800000000,
    apy: 27.4,
    category: "Synthetic USD",
    chain: "ethereum",
    status: "healthy" as const,
    riskScore: 6.5,
    lastUpdated: new Date().toISOString(),
  },
  {
    id: "aave-v3",
    name: "Aave v3",
    tvl: 12400000000,
    apy: 3.2,
    category: "Lending",
    chain: "multi",
    status: "healthy" as const,
    riskScore: 3.0,
    lastUpdated: new Date().toISOString(),
  },
  {
    id: "pendle",
    name: "Pendle",
    tvl: 4100000000,
    apy: 32.1,
    category: "Yield Trading",
    chain: "ethereum",
    status: "healthy" as const,
    riskScore: 5.5,
    lastUpdated: new Date().toISOString(),
  },
  {
    id: "lido",
    name: "Lido",
    tvl: 22300000000,
    apy: 3.8,
    category: "Liquid Staking",
    chain: "ethereum",
    status: "healthy" as const,
    riskScore: 2.5,
    lastUpdated: new Date().toISOString(),
  },
  {
    id: "curve",
    name: "Curve",
    tvl: 2100000000,
    apy: 8.5,
    category: "DEX",
    chain: "multi",
    status: "warning" as const,
    riskScore: 4.0,
    lastUpdated: new Date().toISOString(),
  },
  {
    id: "gmx",
    name: "GMX",
    tvl: 520000000,
    apy: 18.2,
    category: "Perpetuals",
    chain: "arbitrum",
    status: "warning" as const,
    riskScore: 7.0,
    lastUpdated: new Date().toISOString(),
  },
];

export const Route = createAPIFileRoute("/api/protocols")({
  GET: async ({ request }) => {
    const url = new URL(request.url);
    const category = url.searchParams.get("category");
    const chain = url.searchParams.get("chain");

    let filtered = PROTOCOLS;

    if (category) {
      filtered = filtered.filter(
        (p) => p.category.toLowerCase() === category.toLowerCase()
      );
    }

    if (chain) {
      filtered = filtered.filter(
        (p) => p.chain === chain || p.chain === "multi"
      );
    }

    return new Response(
      JSON.stringify({
        data: filtered,
        meta: {
          timestamp: new Date().toISOString(),
          source: "defillama",
          total: filtered.length,
        },
      }),
      {
        headers: { "Content-Type": "application/json" },
      }
    );
  },
});
