// __root.tsx — Cianfhoghlaim OS root layout
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R10.
// Professional + minimal theming (per the 2026-07-09 WoT-theming cleanup).
//
// Mounts:
//   1. <CopilotKit runtimeUrl="/api/copilotkit"> — the CopilotKit v2 context
//   2. <CianfhoghlaimOSProvider> — the PostHog-style window manager
//   3. <Header> — the Cianfhoghlaim brand + Streak flame + Translation toggle
//   4. <Sidebar> — the bilingual nav (6 subnations / 8 subjects / 4 diagrams)
//   5. <Outlet> — the per-route content
//   6. <CopilotSidebar defaultOpen> — the v2 CopilotKit sidebar
//   7. <TanStackRouterDevtools /> — dev-only

import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRouteWithContext,
} from "@tanstack/react-router";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import type { QueryClient } from "@tanstack/react-query";
import type { ConvexReactClient } from "convex/react";
import { CianfhoghlaimOSProvider } from "../components/CianfhoghlaimOS";
import { Header } from "../components/Header";
import { Sidebar } from "../components/Sidebar";
import appCss from "../app.css?url";

interface MyRouterContext {
  queryClient: QueryClient;
  convex: ConvexReactClient | null;
}

export const Route = createRootRouteWithContext<MyRouterContext>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Cianfhoghlaim — Coláiste na Déisigh" },
      {
        name: "description",
        content:
          "Bilingual (EN/GA) agentic educational platform for the Irish Leaving Certificate. 8 NCCA LC subjects + accurate British Isles map + professional theming.",
      },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      {
        rel: "preconnect",
        href: "https://fonts.googleapis.com",
      },
      {
        rel: "preconnect",
        href: "https://fonts.gstatic.com",
        crossOrigin: "",
      },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Cinzel:wght@400..900&family=Inter:wght@400..700&family=JetBrains+Mono:wght@400..700&display=swap",
      },
    ],
  }),
  component: RootComponent,
});

function RootComponent() {
  return (
    <html lang="en" className="dark">
      <head>
        <HeadContent />
      </head>
      <body className="bg-slate-900 text-slate-100 font-sans h-screen w-screen overflow-hidden flex flex-col">
        <CopilotKit runtimeUrl="/api/copilotkit">
          <CianfhoghlaimOSProvider>
            <Header language="en" />
            <div className="flex-1 flex overflow-hidden">
              <Sidebar />
              <main className="flex-1 flex flex-col min-w-0 bg-slate-900 relative">
                <div className="flex-1 overflow-y-auto p-6">
                  <Outlet />
                </div>
              </main>
            </div>
            <CopilotSidebar defaultOpen={false} />
          </CianfhoghlaimOSProvider>
        </CopilotKit>
        <Scripts />
        {typeof window !== "undefined" && (
          <TanStackRouterDevtools position="bottom-right" />
        )}
      </body>
    </html>
  );
}