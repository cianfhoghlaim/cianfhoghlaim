// vite.config.ts — Cianfhoghlaim Leaving Cert web app
// Minimal Vite + React SPA (TanStack Start migration deferred to Phase 2)
// Per the openspec change, the app uses TanStack Router (file-based)
// via the standard vite plugin. TanStack Start's virtual modules are
// disabled for the initial dev deploy.

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";

export default defineConfig({
  appType: "spa",
  server: {
    port: 3082,
    host: true,
  },
  plugins: [
    tsconfigPaths(),
    tailwindcss(),
    react(),
    TanStackRouterVite({
      routesDirectory: "./src/routes",
      generatedRouteTree: "./src/routeTree.gen.ts",
      routeFileIgnorePrefix: "-",
      quoteStyle: "single",
      semicolons: false,
    }),
    {
      // SPA history fallback — serve index.html for any non-asset route
      name: "spa-fallback",
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          const url = req.url || "";
          // Skip Vite internals + asset paths
          if (
            url.startsWith("/@") ||
            url.startsWith("/src/") ||
            url.startsWith("/node_modules/") ||
            url.startsWith("/.vite/") ||
            url.startsWith("/assets/") ||
            url.includes(".") ||
            url === "/index.html"
          ) {
            return next();
          }
          // Fallback to index.html for SPA routes
          req.url = "/index.html";
          return next();
        });
      },
    },
  ],
});