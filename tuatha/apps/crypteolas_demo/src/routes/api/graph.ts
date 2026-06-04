/**
 * Knowledge Graph API Route
 *
 * Provides access to the crypto knowledge graph
 * In production, this queries Memgraph/Cognee
 */

import { createAPIFileRoute } from "@tanstack/start/api";

// Mock graph data - would come from Memgraph in production
const NODES = [
  // Protocols
  { id: "ethena", labels: ["Protocol"], properties: { name: "Ethena", tvl: 2.8e9, category: "Synthetic USD" } },
  { id: "aave", labels: ["Protocol"], properties: { name: "Aave v3", tvl: 12.4e9, category: "Lending" } },
  { id: "pendle", labels: ["Protocol"], properties: { name: "Pendle", tvl: 4.1e9, category: "Yield Trading" } },
  { id: "lido", labels: ["Protocol"], properties: { name: "Lido", tvl: 22.3e9, category: "Liquid Staking" } },
  { id: "curve", labels: ["Protocol"], properties: { name: "Curve", tvl: 2.1e9, category: "DEX" } },

  // Tokens
  { id: "usde", labels: ["Token"], properties: { symbol: "USDe", name: "Ethena USDe", type: "stablecoin" } },
  { id: "susde", labels: ["Token"], properties: { symbol: "sUSDe", name: "Staked USDe", type: "yield" } },
  { id: "steth", labels: ["Token"], properties: { symbol: "stETH", name: "Lido Staked Ether", type: "LST" } },
  { id: "weth", labels: ["Token"], properties: { symbol: "WETH", name: "Wrapped Ether", type: "wrapped" } },
  { id: "usdc", labels: ["Token"], properties: { symbol: "USDC", name: "USD Coin", type: "stablecoin" } },

  // Exchanges
  { id: "binance", labels: ["Exchange"], properties: { name: "Binance", type: "CEX" } },
  { id: "uniswap", labels: ["Exchange"], properties: { name: "Uniswap", type: "DEX" } },
  { id: "bybit", labels: ["Exchange"], properties: { name: "Bybit", type: "CEX" } },

  // Documents
  { id: "audit-zellic", labels: ["Document", "Audit"], properties: { title: "Zellic Audit Report", date: "2024-02" } },
  { id: "audit-spearbit", labels: ["Document", "Audit"], properties: { title: "Spearbit Audit Report", date: "2024-03" } },
  { id: "whitepaper-ethena", labels: ["Document"], properties: { title: "Ethena Whitepaper", type: "whitepaper" } },

  // Risks
  { id: "risk-funding", labels: ["Risk"], properties: { name: "Funding Rate Risk", severity: "medium" } },
  { id: "risk-custodial", labels: ["Risk"], properties: { name: "Custodial Risk", severity: "high" } },
  { id: "risk-smart-contract", labels: ["Risk"], properties: { name: "Smart Contract Risk", severity: "low" } },
];

const RELATIONSHIPS = [
  // Ethena ecosystem
  { id: "r1", type: "ISSUES", start: "ethena", end: "usde", properties: {} },
  { id: "r2", type: "ISSUES", start: "ethena", end: "susde", properties: {} },
  { id: "r3", type: "USES_COLLATERAL", start: "ethena", end: "steth", properties: {} },
  { id: "r4", type: "AUDITED_BY", start: "ethena", end: "audit-zellic", properties: {} },
  { id: "r5", type: "AUDITED_BY", start: "ethena", end: "audit-spearbit", properties: {} },
  { id: "r6", type: "DOCUMENTED_IN", start: "ethena", end: "whitepaper-ethena", properties: {} },
  { id: "r7", type: "HAS_RISK", start: "ethena", end: "risk-funding", properties: {} },
  { id: "r8", type: "HAS_RISK", start: "ethena", end: "risk-custodial", properties: {} },

  // Token trading
  { id: "r9", type: "TRADES_ON", start: "usde", end: "binance", properties: {} },
  { id: "r10", type: "TRADES_ON", start: "usde", end: "uniswap", properties: {} },
  { id: "r11", type: "TRADES_ON", start: "usde", end: "bybit", properties: {} },
  { id: "r12", type: "TRADES_ON", start: "susde", end: "uniswap", properties: {} },

  // Protocol integrations
  { id: "r13", type: "INTEGRATES", start: "susde", end: "aave", properties: {} },
  { id: "r14", type: "INTEGRATES", start: "susde", end: "pendle", properties: {} },
  { id: "r15", type: "ISSUED_BY", start: "steth", end: "lido", properties: {} },
  { id: "r16", type: "COLLATERAL_IN", start: "steth", end: "aave", properties: {} },
  { id: "r17", type: "LIQUIDITY_IN", start: "steth", end: "curve", properties: {} },

  // Lido ecosystem
  { id: "r18", type: "ISSUES", start: "lido", end: "steth", properties: {} },
  { id: "r19", type: "USES_COLLATERAL", start: "lido", end: "weth", properties: {} },
];

export const Route = createAPIFileRoute("/api/graph")({
  // Search the graph
  GET: async ({ request }) => {
    const url = new URL(request.url);
    const query = url.searchParams.get("q");
    const type = url.searchParams.get("type");

    let filteredNodes = NODES;

    if (query) {
      const q = query.toLowerCase();
      filteredNodes = filteredNodes.filter(
        (n) =>
          n.id.includes(q) ||
          Object.values(n.properties).some(
            (v) => typeof v === "string" && v.toLowerCase().includes(q)
          )
      );
    }

    if (type) {
      filteredNodes = filteredNodes.filter((n) =>
        n.labels.map((l) => l.toLowerCase()).includes(type.toLowerCase())
      );
    }

    // Get relationships for filtered nodes
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    const filteredRels = RELATIONSHIPS.filter(
      (r) => nodeIds.has(r.start) || nodeIds.has(r.end)
    );

    return new Response(
      JSON.stringify({
        data: {
          nodes: filteredNodes,
          relationships: filteredRels,
        },
        meta: {
          timestamp: new Date().toISOString(),
          source: "memgraph",
          nodeCount: filteredNodes.length,
          relCount: filteredRels.length,
        },
      }),
      {
        headers: { "Content-Type": "application/json" },
      }
    );
  },

  // Execute Cypher query
  POST: async ({ request }) => {
    const { query, params } = await request.json();

    // In production, this would execute against Memgraph
    // For now, return mock data based on query patterns
    let result = { nodes: NODES, relationships: RELATIONSHIPS };

    if (query?.toLowerCase().includes("token")) {
      result = {
        nodes: NODES.filter((n) => n.labels.includes("Token")),
        relationships: RELATIONSHIPS.filter(
          (r) => r.type === "ISSUES" || r.type === "TRADES_ON"
        ),
      };
    } else if (query?.toLowerCase().includes("risk")) {
      result = {
        nodes: NODES.filter((n) => n.labels.includes("Risk")),
        relationships: RELATIONSHIPS.filter((r) => r.type === "HAS_RISK"),
      };
    }

    return new Response(
      JSON.stringify({
        data: result,
        meta: {
          timestamp: new Date().toISOString(),
          source: "memgraph",
          query,
        },
      }),
      {
        headers: { "Content-Type": "application/json" },
      }
    );
  },
});
