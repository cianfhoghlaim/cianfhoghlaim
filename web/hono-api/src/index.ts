import { Hono } from "hono";
import { cors } from "hono/cors";
import { auth } from "./auth";
import { requireAuth, requireOrg } from "./middleware";

import lineageBySubject from "./routes/lineage/[subject]";
import pdfWildcard from "./routes/pdf/[...r2-key]";

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
// BIEP v1 lineage endpoints (per openspec R30 + R31)
// ----------------------------------------------------------------------------
//
// Both routes are mounted at the top level (no `/api/v1` prefix) so the
// leaving-cert TanStack Start app's `loader()` can call them via the
// Vite dev server's `/api/*` reverse-proxy with zero config.

app.route("/", lineageBySubject);
app.route("/", pdfWildcard);

const port = parseInt(process.env.PORT ?? "4000", 10);
console.log(`[croilar-hono-api] Listening on port ${port}`);

export default {
  port,
  fetch: app.fetch,
};
