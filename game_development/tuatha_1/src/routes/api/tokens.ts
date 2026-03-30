/**
 * Tokens API Route
 *
 * Returns token price data from the backend
 */

import { createAPIFileRoute } from "@tanstack/start/api";

// Mock token data - would come from CoinGecko/DuckDB in production
const TOKENS = [
  {
    symbol: "BTC",
    name: "Bitcoin",
    price: 97000,
    marketCap: 1920000000000,
    volume24h: 45000000000,
    priceChange24h: 2.5,
    chain: "bitcoin",
  },
  {
    symbol: "ETH",
    name: "Ethereum",
    price: 3500,
    marketCap: 420000000000,
    volume24h: 18000000000,
    priceChange24h: 1.8,
    chain: "ethereum",
  },
  {
    symbol: "USDe",
    name: "Ethena USDe",
    price: 0.9998,
    marketCap: 2800000000,
    volume24h: 350000000,
    priceChange24h: -0.02,
    chain: "ethereum",
    contractAddress: "0x4c9EDD5852cd905f086C759E8383e09bff1E68B3",
  },
  {
    symbol: "sUSDe",
    name: "Staked USDe",
    price: 1.08,
    marketCap: 1500000000,
    volume24h: 85000000,
    priceChange24h: 0.1,
    chain: "ethereum",
    contractAddress: "0x9D39A5DE30e57443BfF2A8307A4256c8797A3497",
  },
  {
    symbol: "stETH",
    name: "Lido Staked Ether",
    price: 3480,
    marketCap: 32000000000,
    volume24h: 120000000,
    priceChange24h: 1.5,
    chain: "ethereum",
    contractAddress: "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
  },
  {
    symbol: "USDC",
    name: "USD Coin",
    price: 1.0,
    marketCap: 32500000000,
    volume24h: 5500000000,
    priceChange24h: 0,
    chain: "multi",
    contractAddress: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  },
  {
    symbol: "AAVE",
    name: "Aave",
    price: 185,
    marketCap: 2750000000,
    volume24h: 180000000,
    priceChange24h: 3.2,
    chain: "ethereum",
    contractAddress: "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
  },
  {
    symbol: "CRV",
    name: "Curve DAO Token",
    price: 0.48,
    marketCap: 580000000,
    volume24h: 85000000,
    priceChange24h: -1.5,
    chain: "ethereum",
    contractAddress: "0xD533a949740bb3306d119CC777fa900bA034cd52",
  },
];

export const Route = createAPIFileRoute("/api/tokens")({
  GET: async ({ request }) => {
    const url = new URL(request.url);
    const chain = url.searchParams.get("chain");
    const symbols = url.searchParams.get("symbols")?.split(",");

    let filtered = TOKENS;

    if (chain) {
      filtered = filtered.filter(
        (t) => t.chain === chain || t.chain === "multi"
      );
    }

    if (symbols && symbols.length > 0) {
      filtered = filtered.filter((t) =>
        symbols.map((s) => s.toUpperCase()).includes(t.symbol.toUpperCase())
      );
    }

    return new Response(
      JSON.stringify({
        data: filtered,
        meta: {
          timestamp: new Date().toISOString(),
          source: "coingecko",
          total: filtered.length,
        },
      }),
      {
        headers: { "Content-Type": "application/json" },
      }
    );
  },
});
