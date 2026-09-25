// src/router.tsx — TanStack Start router entry point
// Per the TanStack Start convention, the router entry must export `getRouter`.

import { getRouter as getTanStackRouter } from "@tanstack/react-start";
import { routeTree } from "./routeTree.gen";

export function getRouter() {
  return getTanStackRouter({
    routeTree,
    defaultPreload: "intent",
  });
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof getRouter>;
  }
}