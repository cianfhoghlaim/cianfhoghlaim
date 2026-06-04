import { createRouter } from "@tanstack/react-router";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { routeTree } from "./routeTree";
import appCss from "./app.css?url";

export const queryClient = new QueryClient();

export const router = createRouter({
  routeTree,
  scrollRestoration: true,
  defaultPreload: "intent",
  Wrap: ({ children }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  ),
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
