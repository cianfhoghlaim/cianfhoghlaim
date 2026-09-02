import {
  HeadContent,
  Outlet,
  Scripts,
  createRootRouteWithContext,
} from "@tanstack/react-router";
import type { QueryClient } from "@tanstack/react-query";
import { Suspense } from "react";
import appCss from "../styles.css?url";

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Tuath - Celtic Educational MMO" },
      {
        name: "description",
        content: "Learn Celtic languages through mythology and adventure",
      },
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "icon", href: "/favicon.ico" },
    ],
  }),
  component: RootComponent,
  shellComponent: RootDocument,
});

function RootComponent() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen text-emerald-300">
          <div className="animate-pulse text-lg">Loading Tuath...</div>
        </div>
      }
    >
      <Outlet />
    </Suspense>
  );
}

function RootDocument({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <HeadContent />
      </head>
      <body className="min-h-screen bg-slate-900 antialiased">
        {children}
        <Scripts />
      </body>
    </html>
  );
}

/**
 * STUB for SUBJECTS — the 8 NCCA Leaving Certificate subjects registry.
 *
 * Per the 2026-08-26 build subagent report: realm/$subject.tsx imports
 * `SUBJECTS` from `__root` for the per-subject navigation; the symbol
 * never landed. Stubbed here.
 */
export const SUBJECTS: ReadonlyArray<{
  slug: string;
  name_en: string;
  name_ga: string;
  color: string;
}> = [
  { slug: "irish", name_en: "Irish", name_ga: "Gaeilge", color: "#0a7d4d" },
  { slug: "english", name_en: "English", name_ga: "Béarla", color: "#1e3a8a" },
  { slug: "mathematics", name_en: "Mathematics", name_ga: "Mata", color: "#b91c1c" },
  { slug: "biology", name_en: "Biology", name_ga: "Bitheolaíocht", color: "#15803d" },
  { slug: "chemistry", name_en: "Chemistry", name_ga: "Ceimic", color: "#a16207" },
  { slug: "physics", name_en: "Physics", name_ga: "Fisic", color: "#0c4a6e" },
  { slug: "history", name_en: "History", name_ga: "Stair", color: "#7c2d12" },
  { slug: "geography", name_en: "Geography", name_ga: "Tíreolaíocht", color: "#0f766e" },
];
