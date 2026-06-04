import { createRootRoute, createRoute, Outlet, HeadContent, Scripts } from "@tanstack/react-router";
import { CopilotKit } from "@copilotkit/react-core";
import { Sidebar } from "./components/Sidebar";
import { Header } from "./components/Header";
import { AwenChat } from "./components/AwenChat";
import { IndexComponent } from "./routes/index";
import { DivesPage } from "./routes/dives";
import { ExamsPage } from "./routes/exams";
import { MarkingSchemesPage } from "./routes/marking-schemes";
import { SyllabusPage } from "./routes/syllabus";
import { LakehousePage } from "./routes/lakehouse";
import { RunsPage } from "./routes/runs";
import appCss from "./app.css?url";

const rootRoute = createRootRoute({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { title: "Awen Hub — Oideachais Education Engine" },
    ],
    links: [{ rel: "stylesheet", href: appCss }],
  }),
  component: () => (
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
  ),
});

const indexRoute = createRoute({ getParentRoute: () => rootRoute, path: "/", component: IndexComponent });
const divesRoute = createRoute({ getParentRoute: () => rootRoute, path: "/dives", component: DivesPage });
const examsRoute = createRoute({ getParentRoute: () => rootRoute, path: "/exams", component: ExamsPage });
const markingSchemesRoute = createRoute({ getParentRoute: () => rootRoute, path: "/marking-schemes", component: MarkingSchemesPage });
const syllabusRoute = createRoute({ getParentRoute: () => rootRoute, path: "/syllabus", component: SyllabusPage });
const lakehouseRoute = createRoute({ getParentRoute: () => rootRoute, path: "/lakehouse", component: LakehousePage });
const runsRoute = createRoute({ getParentRoute: () => rootRoute, path: "/runs", component: RunsPage });

export const routeTree = rootRoute.addChildren([
  indexRoute,
  divesRoute,
  examsRoute,
  markingSchemesRoute,
  syllabusRoute,
  lakehouseRoute,
  runsRoute,
]);
