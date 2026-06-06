/**
 * TanStack Query Exports
 */

export { createQueryClient, getQueryClient, defaultQueryOptions, staticDataOptions, realtimeDataOptions } from "./client";

export {
  queryKeys,
  // Price hooks
  useTokenPrice,
  useTokenPrices,
  // Protocol hooks
  useProtocol,
  useProtocols,
  // Usage hooks
  useUsageSummary,
  useFeatureUsage,
  // Payment hooks
  usePayments,
  // Knowledge hooks
  useKnowledgeSearch,
  // Market hooks
  useMarketOverview,
  useYieldStrategies,
  // Mutations
  useInvalidatePrices,
  useInvalidateUsage,
  // Types
  type TokenPrice,
  type Protocol,
  type UsageSummary,
  type Payment,
  type KnowledgeSearchResult,
  type MarketOverview,
  type YieldStrategy,
} from "./hooks";
