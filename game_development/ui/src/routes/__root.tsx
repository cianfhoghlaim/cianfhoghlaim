import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRoute,
} from "@tanstack/react-router";
import { Suspense } from "react";
import appCss from "../styles.css?url";

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Tuath - Celtic Educational MMO" },
      { name: "description", content: "Learn Celtic languages through mythology and adventure" },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "icon", href: "/favicon.ico" },
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
      <body className="min-h-screen bg-slate-900 antialiased">
        <Suspense
          fallback={
            <div className="flex items-center justify-center min-h-screen text-emerald-300">
              <div className="animate-pulse text-lg">Loading Tuath...</div>
            </div>
          }
        >
          <Outlet />
        </Suspense>
        <Scripts />
      </body>
    </html>
  );
}
