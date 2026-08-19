// app/routes/__root.tsx — TanStack Start file-based root route (Cianfhoghlaim Oideachais)
//
// Replaces the code-based routeTree.tsx (which was a Vite SPA workaround).
// Bilingual EN/GA pages live under src/routes/(en)/ and src/routes/(ga)/.
import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRouteWithContext,
} from "@tanstack/react-router";
import { CopilotKit } from "@copilotkit/react-core/v2";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";
import type { QueryClient } from "@tanstack/react-query";
import type { ConvexReactClient } from "convex/react";
import { Sidebar } from "../components/Sidebar";
import { Header } from "../components/Header";
import { OideachasChat } from "../components/OideachasChat";
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
      { title: "Cianfhoghlaim Oideachais" },
      {
        name: "description",
        content:
          "Bilingual (EN/GA) agentic platform for the Irish education system — Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary.",
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
          <Header />
          <div className="flex-1 flex overflow-hidden">
            <Sidebar />
            <main className="flex-1 flex flex-col min-w-0 bg-slate-900 relative">
              <div className="flex-1 overflow-y-auto p-6">
                <Outlet />
              </div>
            </main>
          </div>
          {typeof window !== "undefined" && <OideachasChat />}
        </CopilotKit>
        <Scripts />
        {typeof window !== "undefined" && (
          <TanStackRouterDevtools position="bottom-right" />
        )}
      </body>
    </html>
  );
}
