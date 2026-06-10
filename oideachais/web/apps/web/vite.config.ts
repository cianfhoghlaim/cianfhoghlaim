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
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    tsconfigPaths(),
    tailwindcss(),
    // TanStack Router plugin: generates the file-based route tree from
    // src/routes/. The generated routeTree.gen.ts is imported by
    // app/router.tsx. autoCodeSplitting disabled for now — needs proper
    // TSR transformer setup that requires @vitejs/plugin-react SSR mode.
    TanStackRouterVite({
      addHmr: false,
    }),
    tanstackStart({
      tsr: {
        appDirectory: "src/app",
      },
    }),
    react(),
  ],
  resolve: {
    // Vite needs explicit dedupe for cross-workspace deps so that
    // packages hoisted into the root node_modules can be resolved
    // from sibling workspaces (e.g. croilar/packages/* imported by
    // apps/web) without each croilar package needing its own
    // node_modules. Without this, vite cannot resolve `clsx` or
    // `tailwind-merge` from inside @croilar/ui's source files.
    dedupe: [
      "react",
      "react-dom",
      "@tanstack/react-router",
      "@tanstack/react-query",
      "clsx",
      "tailwind-merge",
      "tailwindcss",
    ],
  },
  server: {
    port: 3001,
    host: true,
    proxy: {
      "/api": "http://localhost:8787",
      "/api-reference": "http://localhost:8787",
      "/rpc": "http://localhost:8787",
    },
  },
});
