// vite.config.ts — Cianfhoghlaim Leaving Cert web app
// DEPRECATED — superseded by app.config.ts (TanStack Start migration Phase 2).
// Kept here as a fallback for the dev-server boot path that does NOT
// load the TanStack Start plugin chain. The active config is
// `app.config.ts`; this file is intentionally a no-op so we don't
// confuse Vite with two competing configs.

import { defineConfig } from "vite";

export default defineConfig({
  // No plugins. The TanStack Start config lives at app.config.ts.
  plugins: [],
});
