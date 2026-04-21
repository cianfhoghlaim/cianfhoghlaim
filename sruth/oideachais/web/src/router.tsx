import { QueryClient } from "@tanstack/react-query";
import { createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

// Create a query client for React Query
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      gcTime: 1000 * 60 * 5, // 5 minutes
    },
  },
});

// Create and export the router
export function createAppRouter() {
  return createRouter({
    routeTree,
    context: {
      queryClient,
    },
    defaultPreloadStaleTime: 0,
    scrollRestoration: true,
  });
}

// Register the router for type safety
declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof createAppRouter>;
  }
}
