/**
 * TanStack Start configuration for Tuath
 */

import { defineConfig } from "@tanstack/react-start/config";

export default defineConfig({
  server: {
    preset: "node-server",
    compatibilityDate: "2024-01-01",
  },
  tsr: {
    appDirectory: "./src",
    routesDirectory: "./src/routes",
    generatedRouteTree: "./src/routeTree.gen.ts",
  },
});
