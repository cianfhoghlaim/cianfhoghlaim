// main.tsx — Cianfhoghlaim OS SPA entry point
// Uses @tanstack/react-router (file-based) without TanStack Start's
// virtual modules — for the initial dev deploy. TanStack Start migration
// deferred to Phase 2 (T1.7).

import * as React from "react";
import ReactDOM from "react-dom/client";
import { createRouter, createRoute, createRootRoute, RouterProvider, Outlet, Link } from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/react-router-devtools";

import "./app.css";

import * as IndexRoute from "./routes/index";
import * as SubjectsRoute from "./routes/en/subjects";
import * as DiagramsRoute from "./routes/en/diagrams";
import * as PracticeIndexRoute from "./routes/en/practice";
import * as MapRoute from "./routes/en/map";
import * as KeyCompetenciesRoute from "./routes/en/key-competencies";
import * as KeyCompetencySlugRoute from "./routes/en/key-competencies.$slug";
import * as EmblemsRoute from "./routes/en/key-competencies.emblems";
import * as AboutRoute from "./routes/en/about";
import * as EiraicRoute from "./routes/en/eiraic-treasures";
import * as EiraicTierRoute from "./routes/en/eiraic-treasures.$tier";
import * as BrownAjahRoute from "./routes/en/brown-ajah";
import * as BrownAjahMemberRoute from "./routes/en/brown-ajah.$member";
import * as SubjectGARoute from "./routes/ga/leaving-cert/$subject";
import * as AboutRouteGA from "./routes/ga/about";
import * as EiraicRouteGA from "./routes/ga/eiraic-treasures";
import * as EiraicTierRouteGA from "./routes/ga/eiraic-treasures.$tier";

const rootRoute = createRootRoute({
  component: () => (
    <div className="h-screen w-screen flex flex-col bg-slate-900 text-slate-100 font-sans">
      <header className="h-14 bg-slate-950 border-b border-slate-800 flex items-center px-4 justify-between shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-amber-700 flex items-center justify-center font-cinzel font-bold text-amber-100">BA</div>
          <div>
            <h1 className="font-cinzel text-lg font-bold tracking-wider text-emerald-500">CIANFHOGHLAIM OS</h1>
            <span className="text-xs text-slate-500 italic">Aes Sedai — servants of all</span>
          </div>
        </div>
        <nav className="flex items-center gap-4">
          <Link to="/" className="text-slate-300 hover:text-emerald-400 text-sm">Curriculum</Link>
          <Link to="/en/map" className="text-slate-300 hover:text-emerald-400 text-sm">Map</Link>
          <Link to="/en/key-competencies" className="text-slate-300 hover:text-emerald-400 text-sm">Key Comps</Link>
          <Link to="/en/eiraic-treasures" className="text-slate-300 hover:text-emerald-400 text-sm">13 Éraic</Link>
          <Link to="/en/about" className="text-slate-300 hover:text-emerald-400 text-sm">About</Link>
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

const subjectsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/subjects",
  component: SubjectsRoute.default || SubjectsRoute.Route?.component || (() => <div>Subjects</div>),
});

const diagramsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/diagrams",
  component: DiagramsRoute.default || DiagramsRoute.Route?.component || (() => <div>Diagrams</div>),
});

const practiceIndexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/practice",
  component: PracticeIndexRoute.default || PracticeIndexRoute.Route?.component || (() => <div>Practice</div>),
});

const mapRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/map",
  component: MapRoute.default || MapRoute.Route?.component || (() => <div>Map</div>),
});

const keyCompRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/key-competencies",
  component: KeyCompetenciesRoute.default || KeyCompetenciesRoute.Route?.component || (() => <div>Key Competencies</div>),
});

const emblemsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/key-competencies/emblems",
  component: EmblemsRoute.default || EmblemsRoute.Route?.component || (() => <div>5 Emblems</div>),
});

const keyCompetencySlugRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/key-competencies/$slug",
  component: KeyCompetencySlugRoute.default || KeyCompetencySlugRoute.Route?.component || (() => <div>KC</div>),
});

const subjectGARoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/ga/leaving-cert/$subject",
  component: SubjectGARoute.default || SubjectGARoute.Route?.component || (() => <div>Subject (GA)</div>),
});

const eiraicRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/eiraic-treasures",
  component: EiraicRoute.default || EiraicRoute.Route?.component || (() => <div>13 Éraic Treasures</div>),
});

const eiraicTierRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/eiraic-treasures/$tier",
  component: EiraicTierRoute.default || EiraicTierRoute.Route?.component || (() => <div>Éraic Tier</div>),
});

const brownAjahRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/brown-ajah",
  component: BrownAjahRoute.default || BrownAjahRoute.Route?.component || (() => <div>Brown Ajah</div>),
});

const brownAjahMemberRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/brown-ajah/$member",
  component: BrownAjahMemberRoute.default || BrownAjahMemberRoute.Route?.component || (() => <div>Brown Ajah Member</div>),
});

const aboutRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/en/about",
  component: AboutRoute.default || AboutRoute.Route?.component || (() => <div>About</div>),
});

const aboutGARoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/ga/about",
  component: AboutRouteGA.default || AboutRouteGA.Route?.component || (() => <div>About (GA)</div>),
});

const eiraicGARoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/ga/eiraic-treasures",
  component: EiraicRouteGA.default || EiraicRouteGA.Route?.component || (() => <div>13 Éraic (GA)</div>),
});

const eiraicTierGARoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/ga/eiraic-treasures/$tier",
  component: EiraicTierRouteGA.default || EiraicTierRouteGA.Route?.component || (() => <div>Éraic Tier (GA)</div>),
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  subjectsRoute,
  diagramsRoute,
  practiceIndexRoute,
  mapRoute,
  keyCompRoute,
  keyCompetencySlugRoute,
  emblemsRoute,
  eiraicRoute,
  eiraicTierRoute,
  brownAjahRoute,
  brownAjahMemberRoute,
  aboutRoute,
  aboutGARoute,
  eiraicGARoute,
  eiraicTierGARoute,
  subjectGARoute,
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