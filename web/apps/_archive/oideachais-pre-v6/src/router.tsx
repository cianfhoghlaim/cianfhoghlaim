// src/router.tsx — TanStack Start router entry point
// Per the TanStack Start convention, the router entry must export `getRouter`.
// The router itself is built with `createRouter` from @tanstack/react-router;
// @tanstack/react-start does not export a `getRouter` helper.

import { createRouter as createTanStackRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";

export function getRouter() {
  return createTanStackRouter({
    routeTree,
    defaultPreload: "intent",
  });
}

declare module "@tanstack/react-router" {
  interface Register {
    router: ReturnType<typeof getRouter>;
  }
}