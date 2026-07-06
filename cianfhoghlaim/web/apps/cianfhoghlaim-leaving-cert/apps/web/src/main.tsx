// main.tsx — cianfhoghlaim SPA entry point
// Self-hostable consolidation of education system resources
// Reduce barriers to education

import * as React from "react";
import ReactDOM from "react-dom/client";
import { createRouter, createRoute, createRootRoute, RouterProvider, Outlet, Link } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

import "./app.css";

import * as IndexRoute from "./routes/index";
import * as FoundationsRoute from "./routes/en/foundations";
import * as SubjectRoute from "./routes/en/leaving-cert/$subject";
import * as SectionRoute from "./routes/en/leaving-cert/$subject.$section";
import * as PracticeRoute from "./routes/en/leaving-cert/$subject.practice.$topic";
import * as AgentsRoute from "./routes/en/agents";
import * as AgentRoute from "./routes/en/agents/$agent";
import * as SelfHostRoute from "./routes/en/self-host";
import * as SearchRoute from "./routes/en/search";

const rootRoute = createRootRoute({
  component: () => (
    <div className="h-screen w-screen flex flex-col bg-slate-900 text-slate-100 font-sans">
      <header className="h-14 bg-slate-950 border-b border-slate-800 flex items-center px-4 justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Link to="/" className="w-8 h-8 rounded-md bg-emerald-600 flex items-center justify-center font-bold text-white text-sm">
            C
          </Link>
          <div>
            <Link to="/" className="font-cinzel text-lg font-bold tracking-wider text-emerald-400">
              cianfhoghlaim
            </Link>
            <span className="block text-xs text-slate-500">
              self-hosted NCCA LC education
            </span>
          </div>
        </div>
        <nav className="flex items-center gap-4 text-sm">
          <Link to="/en/foundations" className="text-slate-300 hover:text-emerald-400">
            Foundations
          </Link>
          <Link to="/en/subjects/mathematics" className="text-slate-300 hover:text-emerald-400">
            Subjects
          </Link>
          <Link to="/en/agents" className="text-slate-300 hover:text-emerald-400">
            9 ADK Agents
          </Link>
          <Link to="/en/self-host" className="text-slate-300 hover:text-emerald-400">
            Self-host
          </Link>
          <Link to="/en/search" className="text-slate-300 hover:text-emerald-400">
            Search
          </Link>
        </nav>
      </header>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
      {import.meta.env.DEV && <TanStackRouterDevtools position="bottom-right" />}
    </div>
  ),
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: IndexRoute.default || IndexRoute.Route?.component || (() => <div>Index</div>),
});

const foundationsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/foundations",
  component: FoundationsRoute.default || FoundationsRoute.Route?.component || (() => <div>Foundations</div>),
});

const subjectRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/leaving-cert/$subject",
  component: SubjectRoute.default || SubjectRoute.Route?.component || (() => <div>Subject</div>),
});

const sectionRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/leaving-cert/$subject/$section",
  component: SectionRoute.default || SectionRoute.Route?.component || (() => <div>Section</div>),
});

const practiceRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/leaving-cert/$subject/practice/$topic",
  component: PracticeRoute.default || PracticeRoute.Route?.component || (() => <div>Practice</div>),
});

const agentsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/agents",
  component: AgentsRoute.default || AgentsRoute.Route?.component || (() => <div>Agents</div>),
});

const agentRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/agents/$agent",
  component: AgentRoute.default || AgentRoute.Route?.component || (() => <div>Agent</div>),
});

const selfHostRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/self-host",
  component: SelfHostRoute.default || SelfHostRoute.Route?.component || (() => <div>Self-host</div>),
});

const searchRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/search",
  component: SearchRoute.default || SearchRoute.Route?.component || (() => <div>Search</div>),
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  foundationsRoute,
  subjectRoute,
  sectionRoute,
  practiceRoute,
  agentsRoute,
  agentRoute,
  selfHostRoute,
  searchRoute,
]);

const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

const root = document.getElementById("root")!;
ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);