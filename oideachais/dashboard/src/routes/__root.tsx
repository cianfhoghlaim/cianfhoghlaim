import {
  createRootRoute,
  Outlet,
  ScrollRestoration,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { Header } from "~/components/layout/Header";
import "@copilotkit/react-ui/styles.css";
import "~/styles/globals.css";

const convex = new ConvexReactClient(
  import.meta.env.VITE_CONVEX_URL || "http://localhost:3210"
);

export const Route = createRootRoute({
  component: RootComponent,
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "OCR Comparison Dashboard" },
      {
        name: "description",
        content: "Compare OCR and vision models on PDF documents",
      },
    ],
  }),
});

function RootComponent() {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>OCR Comparison Dashboard</title>
      </head>
      <body>
        <ConvexProvider client={convex}>
          <CopilotKit runtimeUrl="/api/copilotkit">
            <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
              <Header />
              <main className="container mx-auto px-4 py-6">
                <Outlet />
              </main>
            </div>
            <CopilotSidebar
              labels={{
                title: "OCR Assistant",
                initial:
                  "I can help analyze OCR results, recommend the best model for your document, and explain differences between outputs.",
              }}
            />
          </CopilotKit>
        </ConvexProvider>
        <ScrollRestoration />
        <TanStackRouterDevtools position="bottom-right" />
      </body>
    </html>
  );
}
