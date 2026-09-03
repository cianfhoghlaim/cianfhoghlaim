import { Hono } from "hono";
import { cors } from "hono/cors";
import { auth } from "./auth";
import { requireAuth, requireOrg } from "./middleware";

import lineageBySubject from "./routes/lineage/[subject]";
import pdfWildcard from "./routes/pdf/[...r2-key]";
import imageGeneration from "./routes/copilotkit/image-generation";
import copilotkitRegistry from "./routes/copilotkit/registry";

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

const port = parseInt(process.env.PORT ?? "4000", 10);
console.log(`[croilar-hono-api] Listening on port ${port}`);

export default {
  port,
  fetch: app.fetch,
};
