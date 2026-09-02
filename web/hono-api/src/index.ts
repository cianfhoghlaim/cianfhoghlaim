import { Hono } from "hono";
import { cors } from "hono/cors";
import { auth } from "./auth";
import { requireAuth, requireOrg } from "./middleware";

import lineageBySubject from "./routes/lineage/[subject]";
import pdfWildcard from "./routes/pdf/[...r2-key]";
import imageGeneration from "./routes/copilotkit/image-generation";
import copilotkitRegistry from "./routes/copilotkit/registry";
import chemistryApp from "./routes/copilotkit/lc/chemistry";
import mathematicsApp from "./routes/copilotkit/lc/mathematics";
import gaeilgeApp from "./routes/copilotkit/lc/gaeilge";
import computerScienceApp from "./routes/copilotkit/lc/computer_science";
// Phase 14 — the 8 British Isles vernacular Hono apps (7 + Ulster Scots).
import welshVernacularApp from "./routes/copilotkit/vernacular/welsh";
import scottishGaelicVernacularApp from "./routes/copilotkit/vernacular/scottish_gaelic";
import bretonVernacularApp from "./routes/copilotkit/vernacular/breton";
import cornishVernacularApp from "./routes/copilotkit/vernacular/cornish";
import manxVernacularApp from "./routes/copilotkit/vernacular/manx";
import jerseyFrenchVernacularApp from "./routes/copilotkit/vernacular/jersey_french";
import guernseyFrenchVernacularApp from "./routes/copilotkit/vernacular/guernsey_french";
import ulsterScotsVernacularApp from "./routes/copilotkit/vernacular/ulster_scots";
import aguiApp from "./routes/agui";

const app = new Hono();

app.use(
  "*",
  cors({
    origin: [
      process.env.PUBLIC_WEB_URL ?? "http://localhost:3000",
      process.env.PUBLIC_AUTH_URL ?? "http://localhost:4000",
      "https://croilar.cianfhoghlaim.ie",
      "https://convex.croilar.cianfhoghlaim.ie",
      "https://auth.croilar.cianfhoghlaim.ie",
      // The leaving-cert TanStack Start dev server on port 3082 (per the
      // cianfhoghlaim-leaving-cert app README).
      "http://localhost:3082",
    ],
    credentials: true,
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
  }),
);

app.get("/api/health", (c) => {
  return c.json({
    status: "ok",
    service: "croilar-hono-api",
    version: "0.1.0",
    timestamp: new Date().toISOString(),
  });
});

// Mount BetterAuth handler at /api/auth/*
// Handles: /sign-in, /sign-up, /sign-out, /session, /oauth2/callback, /jwks, etc.
app.on(["GET", "POST"], "/api/auth/*", (c) => auth.handler(c.req.raw));

// Example protected route — returns the current user's session info
app.get("/api/me", requireAuth, async (c) => {
  const user = c.get("user");
  return c.json({ user });
});

// Example org-protected route — only members of aleyum/cianfhoghlaim/croilar-admin
app.get("/api/admin/stacks", requireAuth, requireOrg("admin"), async (c) => {
  // Will be filled in by PR-4a (Stacks module via Komodo API)
  return c.json({ stacks: [] });
});

// ----------------------------------------------------------------------------
// Deployment control panel endpoints (per openspec deployment-control-panel)
// ----------------------------------------------------------------------------
//
// The 8 control-panel endpoints back the 5 tabs of the marimo notebook
// at notebooks/00_control_panel.py and the TanStack Start route at
// web/apps/cianfhoghlaim-web/src/routes/control-panel/index.tsx.
// All endpoints delegate to the Python subprocess bridge at
// web/hono-api/control-panel/_python_bridge.py (which calls into
// MODEL_REGISTRY + notebooks/_shared/schema.py).
//
// Per the 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1
// change (commit 48bfc9328).

import controlPanelApp from "../control-panel";

app.route("/api/control-panel", controlPanelApp);

// ----------------------------------------------------------------------------
// BIEP v1 lineage endpoints (per openspec R30 + R31)
// ----------------------------------------------------------------------------
//
// Both routes are mounted at the top level (no `/api/v1` prefix) so the
// leaving-cert TanStack Start app's `loader()` can call them via the
// Vite dev server's `/api/*` reverse-proxy with zero config.

app.route("/", lineageBySubject);
app.route("/", pdfWildcard);

// ----------------------------------------------------------------------------
// Image generation CopilotKit actions (Phase L)
// ----------------------------------------------------------------------------
//
// Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
// change (Phase L), the `image_generation_agent` is the 13th main ADK
// agent. Its 5 tools (list_image_models / generate_2d_asset /
// generate_texture / style_match / cocoindex_register) are exposed via
// the unified Hono gateway at `/api/copilotkit/image-gen/*`.

app.route("/api/copilotkit/image-gen", imageGeneration);

// The agent_registry_runtime wire-up (Mega-3d Phase 2). The 3 routes
// (config / events / agents) delegate to the canonical Python runtime
// at `agents/integrations/agent_registry_runtime.py` and return the
// JSON config / AG-UI events / agent names. This is the bridge between
// the Python agent registry and the TanStack Start front-end.
app.route("/api/copilotkit/registry", copilotkitRegistry);

// Phase 1 study-plan routes (the 4 subjects) — mounted per
// the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
// (Phase 3 §C-D completion). These power the Phase 1
// useStudyPlan hook in the consolidated cianfhoghlaim-nua app.
app.route("/api/copilotkit/lc/chemistry", chemistryApp);
app.route("/api/copilotkit/lc/mathematics", mathematicsApp);
app.route("/api/copilotkit/lc/gaeilge", gaeilgeApp);
app.route("/api/copilotkit/lc/computer_science", computerScienceApp);

// Phase 14 — the 8 vernacular Hono apps.
// Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
// change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
app.route("/api/copilotkit/vernacular/welsh", welshVernacularApp);
app.route("/api/copilotkit/vernacular/scottish_gaelic", scottishGaelicVernacularApp);
app.route("/api/copilotkit/vernacular/breton", bretonVernacularApp);
app.route("/api/copilotkit/vernacular/cornish", cornishVernacularApp);
app.route("/api/copilotkit/vernacular/manx", manxVernacularApp);
app.route("/api/copilotkit/vernacular/jersey_french", jerseyFrenchVernacularApp);
app.route("/api/copilotkit/vernacular/guernsey_french", guernseyFrenchVernacularApp);
app.route("/api/copilotkit/vernacular/ulster_scots", ulsterScotsVernacularApp);

// AG-UI SSE bridge (Phase 3 §B.9 + the 2026-09-01
// cianfhoghlaim-nua-oral-study-plans-v1 change for Phase 6)
app.route("/api/agui", aguiApp);

const port = parseInt(process.env.PORT ?? "4000", 10);
console.log(`[croilar-hono-api] Listening on port ${port}`);

export default {
  port,
  fetch: app.fetch,
};
