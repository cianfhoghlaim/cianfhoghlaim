import { createRoute, createRootRoute, Outlet } from "@tanstack/react-router";
import { HeadContent, Scripts } from "@tanstack/react-router";
import { CopilotKit } from "@copilotkit/react-core";
import { AwenChat } from "./components/AwenChat";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { Index } from "./routes/index";
import { Dives } from "./routes/dives";
import { Exams } from "./routes/exams";
import { MarkingSchemes } from "./routes/marking-schemes";
import { Syllabus } from "./routes/syllabus";
import { Lakehouse } from "./routes/lakehouse";
import { Runs } from "./routes/runs";
import appCss from "./app.css?url";

/**
 * Root route. The TanStack Start `head` is computed at render time and
 * injected into the SSR HTML; in CSR it is collected and emitted by
 * `<HeadContent />`.
 */
export const rootRoute = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Awen Hub — Oideachais Education Engine" },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
  }),
  component: RootComponent,
});

function RootComponent() {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400..900&family=Inter:wght@400..700&family=JetBrains+Mono:wght@400..700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-slate-900 text-slate-100 font-sans h-screen w-screen overflow-hidden flex flex-col">
        <CopilotKit runtimeUrl="/api/copilotkit" agent="oideachais-exam-explorer">
          <Header />
          <div className="flex-1 flex overflow-hidden">
            <Sidebar />
            <main className="flex-1 flex flex-col min-w-0 bg-slate-900 relative">
              <div className="flex-1 overflow-y-auto p-6">
                <Outlet />
              </div>
            </main>
          </div>
          <AwenChat />
        </CopilotKit>
        <Scripts />
      </body>
    </html>
  );
}

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: Index,
});

const divesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/dives",
  component: Dives,
});

const examsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/exams",
  component: Exams,
  validateSearch: (search) => ({
    subject: (search.subject as string) || "mathematics",
    year: Number(search.year) || 2024,
    level: (search.level as string) || "leaving_certificate",
    materialType: (search.materialType as string) || "exam_papers",
  }),
});

const markingSchemesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/marking-schemes",
  component: MarkingSchemes,
  validateSearch: (search) => ({
    subject: (search.subject as string) || "english",
  }),
});

const syllabusRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/syllabus",
  component: Syllabus,
});

const lakehouseRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/lakehouse",
  component: Lakehouse,
});

const runsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/runs",
  component: Runs,
});

export const routeTree = rootRoute.addChildren([
  indexRoute,
  divesRoute,
  examsRoute,
  markingSchemesRoute,
  syllabusRoute,
  lakehouseRoute,
  runsRoute,
]);
