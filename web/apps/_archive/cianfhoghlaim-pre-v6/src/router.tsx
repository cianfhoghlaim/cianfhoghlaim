/**
 * src/router.tsx — the TanStack Start router entry point.
 *
 * Declaring `Register` here is what gives every `createFileRoute(...)` call in
 * `routes/` its literal route-id type. Without it the route ids degrade to
 * `undefined` and each route file reports TS2345.
 */

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
