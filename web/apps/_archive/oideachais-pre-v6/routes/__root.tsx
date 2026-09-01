/**
 * routes/__root.tsx — the TanStack Router root route for `oideachais`.
 *
 * The router entry point is `src/router.tsx`, which consumes the generated
 * `src/routeTree.gen.ts`. Regenerate the route tree with:
 *
 *   bun run scripts/gen-route-tree.ts web/apps/oideachais routes src/routeTree.gen.ts
 */

import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRoute,
} from "@tanstack/react-router";
import type { ReactNode } from "react";

import appCss from "../src/app.css?url";
import a2uiThemeCss from "../src/a2ui-theme.css?url";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "cianfhoghlaim — self-hosted NCCA education resources" },
      {
        name: "description",
        content:
          "Self-hostable consolidation of education system resources for the NCCA Leaving Certificate, Junior Cycle, GCSE and A-level curricula.",
      },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "stylesheet", href: a2uiThemeCss },
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
      <body className="min-h-screen bg-slate-900 text-slate-100 font-sans antialiased">
        {children}
        <Scripts />
      </body>
    </html>
  );
}
