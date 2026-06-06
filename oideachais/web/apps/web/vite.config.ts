// vite.config.ts — TanStack Start + Vite
//
// Replaces the Vite SPA config with a TanStack Start config that supports:
// - File-based routes (replaces code-based routeTree.tsx)
// - Server functions via createServerFn (replaces the SPA's Vite proxy for Hono)
// - SSR streaming with React Suspense
// - Bilingual route groups under (en) and (ga) — see src/app/routes/
//
// Pattern from https://github.com/TanStack/router/tree/main/examples/react/start-basic
import { defineConfig } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    tsconfigPaths(),
    tailwindcss(),
    // The TanStack Start Vite plugin provides createStartHandler, SSR, server
    // functions, and file-based routing. It composes with @tanstack/router-plugin
    // (loaded via app/router.tsx's tsr plugin config).
    tanstackStart(),
    react(),
  ],
  server: {
    port: 3001,
    host: true,
    // Proxy /api, /rpc, /api-reference, /api/copilotkit to the Hono app server.
    proxy: {
      "/api": "http://localhost:8787",
      "/api-reference": "http://localhost:8787",
      "/rpc": "http://localhost:8787",
    },
  },
});
