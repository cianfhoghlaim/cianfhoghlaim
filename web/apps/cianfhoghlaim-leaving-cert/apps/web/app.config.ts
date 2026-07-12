// app.config.ts — Cianfhoghlaim Leaving Cert web app
// TanStack Start (Vite plugin) + Convex + CopilotKit v2

import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";

export default defineConfig({
  server: {
    port: 3082,
    host: true,
  },
  plugins: [
    tsconfigPaths(),
    tailwindcss(),
    tanstackStart({
      // The Convex deployment is configured via env vars
      runtimeUrl: process.env.COPILOTKIT_RUNTIME_URL || "/api/copilotkit",
    }),
  ],
});