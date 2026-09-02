/**
 * TanStack Start build config for the consolidated cianfhoghlaim-nua app.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
 * (Phase 3 completion). Replaces the 5 duplicate build configs
 * (one per legacy app).
 */

import { defineConfig } from "@tanstack/react-start/config";

export default defineConfig({
  tsr: {
    appDirectory: ".",
  },
  vite: {
    server: {
      port: 3087,
    },
  },
  server: {
    preset: "node-server",
  },
});
