// TODO: implement the TanStack Query client with sensible defaults
// (retry, stale time, refetch on focus).

import { QueryClient } from "@tanstack/react-query";

export function getQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: 1,
        staleTime: 30_000,
        refetchOnWindowFocus: false,
      },
    },
  });
}
