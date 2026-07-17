// app/router.tsx — TanStack Router instance for SSR
import { createRouter as createTanstackRouter } from "@tanstack/react-router";
import { routeTree } from "../routeTree.gen";
import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

// TanStack Query client (server-cache for the SSR pass)
const queryClient = new QueryClient();

export function getRouter() {
  return createTanstackRouter({
    routeTree,
    context: { queryClient, convex: null },
    defaultPreload: "intent",
    Wrap: ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    ),
  });
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof getRouter>;
  }
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof getRouter>;
  }
}
