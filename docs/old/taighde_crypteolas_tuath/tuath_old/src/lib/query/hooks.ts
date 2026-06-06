/**
 * TanStack Query Hooks for Crypto Data
 *
 * Provides type-safe hooks for fetching:
 * - Token prices
 * - Protocol metrics
 * - Usage/payment data
 * - Knowledge graph queries
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { realtimeDataOptions, staticDataOptions } from "./client";

// ============================================================================
// QUERY KEYS
// ============================================================================

export const queryKeys = {
  // Prices
  prices: ["prices"] as const,
  price: (symbol: string) => ["prices", symbol] as const,
  priceHistory: (symbol: string, days: number) => ["prices", symbol, "history", days] as const,

  // Protocols
  protocols: ["protocols"] as const,
  protocol: (slug: string) => ["protocols", slug] as const,

  // Usage
  usage: ["usage"] as const,
  usageSummary: (walletAddress?: string) => ["usage", "summary", walletAddress] as const,
  usageFeature: (featureId: string, walletAddress?: string) => ["usage", featureId, walletAddress] as const,

  // Payments
  payments: (walletAddress: string) => ["payments", walletAddress] as const,

  // Knowledge Graph
  knowledge: ["knowledge"] as const,
  knowledgeSearch: (query: string, type?: string) => ["knowledge", "search", query, type] as const,
  knowledgeEntity: (id: string) => ["knowledge", "entity", id] as const,

  // Market Overview
  marketOverview: ["market", "overview"] as const,
  trending: ["market", "trending"] as const,
};

// ============================================================================
// PRICE HOOKS
// ============================================================================

export interface TokenPrice {
  symbol: string;
  price: number;
  change24h: number;
  volume24h: number;
  marketCap?: number;
  high24h?: number;
  low24h?: number;
}

export function useTokenPrice(symbol: string) {
  return useQuery({
    queryKey: queryKeys.price(symbol),
    queryFn: async (): Promise<TokenPrice> => {
      const response = await fetch(`/api/tokens?symbol=${symbol}`);
      if (!response.ok) throw new Error("Failed to fetch price");
      return response.json();
    },
    ...realtimeDataOptions,
    enabled: !!symbol,
  });
}

export function useTokenPrices(symbols: string[]) {
  return useQuery({
    queryKey: [...queryKeys.prices, symbols.join(",")],
    queryFn: async (): Promise<Record<string, TokenPrice>> => {
      const response = await fetch(`/api/tokens?symbols=${symbols.join(",")}`);
      if (!response.ok) throw new Error("Failed to fetch prices");
      return response.json();
    },
    ...realtimeDataOptions,
    enabled: symbols.length > 0,
  });
}

// ============================================================================
// PROTOCOL HOOKS
// ============================================================================

export interface Protocol {
  slug: string;
  name: string;
  tvl: number;
  tvlChange24h?: number;
  apy?: number;
  chains: string[];
  category: string;
  riskScore?: number;
  auditStatus: "audited" | "partial" | "none";
}

export function useProtocol(slug: string) {
  return useQuery({
    queryKey: queryKeys.protocol(slug),
    queryFn: async (): Promise<Protocol> => {
      const response = await fetch(`/api/protocols?slug=${slug}`);
      if (!response.ok) throw new Error("Failed to fetch protocol");
      return response.json();
    },
    ...staticDataOptions,
    enabled: !!slug,
  });
}

export function useProtocols(category?: string) {
  return useQuery({
    queryKey: category ? [...queryKeys.protocols, category] : queryKeys.protocols,
    queryFn: async (): Promise<Protocol[]> => {
      const url = category ? `/api/protocols?category=${category}` : "/api/protocols";
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch protocols");
      return response.json();
    },
    ...staticDataOptions,
  });
}

// ============================================================================
// USAGE HOOKS
// ============================================================================

export interface UsageSummary {
  featureId: string;
  used: number;
  freeLimit: number;
  remaining: number;
  priceUsd?: number;
}

export function useUsageSummary(walletAddress?: string) {
  return useQuery({
    queryKey: queryKeys.usageSummary(walletAddress),
    queryFn: async (): Promise<UsageSummary[]> => {
      const url = walletAddress
        ? `/api/usage?wallet=${walletAddress}`
        : "/api/usage";
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch usage");
      return response.json();
    },
    enabled: !!walletAddress,
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useFeatureUsage(featureId: string, walletAddress?: string) {
  return useQuery({
    queryKey: queryKeys.usageFeature(featureId, walletAddress),
    queryFn: async (): Promise<UsageSummary> => {
      const url = walletAddress
        ? `/api/usage/${featureId}?wallet=${walletAddress}`
        : `/api/usage/${featureId}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error("Failed to fetch feature usage");
      return response.json();
    },
    enabled: !!walletAddress,
    staleTime: 1000 * 10, // 10 seconds for active feature checks
  });
}

// ============================================================================
// PAYMENT HOOKS
// ============================================================================

export interface Payment {
  id: string;
  featureId: string;
  amount: string;
  txHash?: string;
  status: "pending" | "verified" | "settled" | "failed";
  createdAt: string;
}

export function usePayments(walletAddress: string) {
  return useQuery({
    queryKey: queryKeys.payments(walletAddress),
    queryFn: async (): Promise<Payment[]> => {
      const response = await fetch(`/api/payments?wallet=${walletAddress}`);
      if (!response.ok) throw new Error("Failed to fetch payments");
      return response.json();
    },
    enabled: !!walletAddress,
  });
}

// ============================================================================
// KNOWLEDGE GRAPH HOOKS
// ============================================================================

export interface KnowledgeSearchResult {
  id: string;
  type: "token" | "protocol" | "document" | "risk";
  name: string;
  description?: string;
  relevance: number;
  metadata?: Record<string, unknown>;
}

export function useKnowledgeSearch(query: string, type?: string) {
  return useQuery({
    queryKey: queryKeys.knowledgeSearch(query, type),
    queryFn: async (): Promise<KnowledgeSearchResult[]> => {
      const params = new URLSearchParams({ query });
      if (type) params.set("type", type);
      const response = await fetch(`/api/graph?${params}`);
      if (!response.ok) throw new Error("Failed to search knowledge graph");
      return response.json();
    },
    enabled: query.length >= 2,
    ...staticDataOptions,
  });
}

// ============================================================================
// MARKET OVERVIEW HOOKS
// ============================================================================

export interface MarketOverview {
  totalMarketCap: number;
  totalVolume24h: number;
  btcDominance: number;
  ethDominance: number;
  fearGreedIndex: number;
  trendingCoins: string[];
}

export function useMarketOverview() {
  return useQuery({
    queryKey: queryKeys.marketOverview,
    queryFn: async (): Promise<MarketOverview> => {
      const response = await fetch("/api/market/overview");
      if (!response.ok) throw new Error("Failed to fetch market overview");
      return response.json();
    },
    ...realtimeDataOptions,
  });
}

// ============================================================================
// YIELD STRATEGY HOOKS
// ============================================================================

export interface YieldStrategy {
  protocol: string;
  asset: string;
  apy: number;
  risk: "low" | "medium" | "high";
  tvl?: number;
  description?: string;
}

export function useYieldStrategies(riskLevel: "low" | "medium" | "high") {
  return useQuery({
    queryKey: ["yields", riskLevel],
    queryFn: async (): Promise<YieldStrategy[]> => {
      const response = await fetch(`/api/analytics/yield?risk=${riskLevel}`);
      if (!response.ok) throw new Error("Failed to fetch yield strategies");
      const data = await response.json();
      return data.strategies || [];
    },
    ...staticDataOptions,
  });
}

// ============================================================================
// MUTATIONS
// ============================================================================

/**
 * Invalidate price data (after payment or update)
 */
export function useInvalidatePrices() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.prices });
    },
  });
}

/**
 * Invalidate usage data (after payment)
 */
export function useInvalidateUsage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (walletAddress?: string) => {
      await queryClient.invalidateQueries({
        queryKey: walletAddress
          ? queryKeys.usageSummary(walletAddress)
          : queryKeys.usage,
      });
    },
  });
}
