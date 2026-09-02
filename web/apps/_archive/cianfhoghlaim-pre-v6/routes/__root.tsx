/**
 * routes/__root.tsx — the TanStack Router root route for `cianfhoghlaim`.
 *
 * This app previously had no root route, no router entry and no generated
 * route tree, which left every `createFileRoute(...)` call untyped (the route
 * id parameter degrades to `undefined`, producing a TS2345 on each route file).
 *
 * Regenerate the route tree with:
 *
 *   bun run scripts/gen-route-tree.ts web/apps/cianfhoghlaim routes src/routeTree.gen.ts
 */

import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRoute,
} from "@tanstack/react-router";
import type { ReactNode } from "react";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Cianfhoghlaim — British Isles education pipeline" },
      {
        name: "description",
        content:
          "The central Cianfhoghlaim platform: per-subject agents, pipeline health and the British Isles Education Pipeline registry.",
      },
    ],
  }),
  component: RootComponent,
  shellComponent: RootDocument,
});

function RootComponent() {
  return <Outlet />;
}

function RootDocument({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}
