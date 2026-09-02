/**
 * Root layout for the consolidated cianfhoghlaim-nua TanStack Start app.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
 * (Phase 3 completion) and the 2026-09-01-cianfhoghlaim-nua-a2ui-catalog-v1
 * change (Phase 2 — A2UI v0.9 catalog).
 *
 * Mounts:
 *   - CianfhoghlaimOS (the canonical app shell)
 *   - CopilotKitProvider (the A2UI catalog mount via createCatalog())
 *   - Convex client (the reactive schema)
 */

import * as React from "react";
import { Outlet, createRootRouteWithContext } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";
import { Meta, Scripts } from "@tanstack/react-start";

import { CianfhoghlaimOS } from "../src/components/CianfhoghlaimOS";
import { CopilotKitProvider } from "../src/copilot/CopilotKitProvider";

export const Route = createRootRouteWithContext<{}>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { title: "cianfhoghlaim-nua · v6 era" },
      { name: "description", content: "The British Isles education platform — chat with your syllabus, get study plans, hear them spoken in your dialect." },
    ],
  }),
  component: RootComponent,
});

function RootComponent() {
  return (
    <RootDocument>
      <CopilotKitProvider>
        <CianfhoghlaimOS>
          <Outlet />
        </CianfhoghlaimOS>
      </CopilotKitProvider>
    </RootDocument>
  );
}

function RootDocument({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <Meta />
      </head>
      <body className="bg-slate-50 text-slate-900 antialiased">
        {children}
        <Scripts />
        {process.env.NODE_ENV === "development" ? <TanStackRouterDevtools /> : null}
      </body>
    </html>
  );
}
