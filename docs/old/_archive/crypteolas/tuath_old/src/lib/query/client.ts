/**
 * TanStack Query Client Configuration
 *
 * Provides centralized query client setup with:
 * - Default stale/cache times optimized for crypto data
 * - Error handling and retry logic
 * - DevTools integration
 */

import { QueryClient } from "@tanstack/react-query";

/**
 * Default query options for crypto data
 */
export const defaultQueryOptions = {
  // Data freshness
  staleTime: 1000 * 60 * 1, // 1 minute - crypto prices change frequently
  gcTime: 1000 * 60 * 30, // 30 minutes cache

  // Retry configuration
  retry: 2,
  retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),

  // Refetch behavior
  refetchOnWindowFocus: true,
  refetchOnReconnect: true,
  refetchOnMount: true,
};

/**
 * Long-lived data options (protocols, audits)
 */
export const staticDataOptions = {
  staleTime: 1000 * 60 * 60, // 1 hour
  gcTime: 1000 * 60 * 60 * 24, // 24 hours
  refetchOnWindowFocus: false,
};

/**
 * Real-time data options (prices, TVL)
 */
export const realtimeDataOptions = {
  staleTime: 1000 * 30, // 30 seconds
  gcTime: 1000 * 60 * 5, // 5 minutes
  refetchInterval: 1000 * 60, // Poll every minute
};

/**
 * Create query client instance
 */
export function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        ...defaultQueryOptions,
      },
      mutations: {
        retry: 1,
        onError: (error) => {
          console.error("Mutation error:", error);
        },
      },
    },
  });
}

/**
 * Singleton query client for SSR
 */
let browserQueryClient: QueryClient | undefined;

export function getQueryClient() {
  if (typeof window === "undefined") {
    // Server: always create a new query client
    return createQueryClient();
  }

  // Browser: use singleton
  if (!browserQueryClient) {
    browserQueryClient = createQueryClient();
  }
  return browserQueryClient;
}
