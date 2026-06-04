// app.config.ts - TanStack Start + Vinxi configuration
//
// Pattern from the official TanStack Start starter template:
//   https://github.com/TanStack/router/tree/main/examples/react/start-basic
//
// Vinxi 0.4.x uses an explicit `routers` array. We declare one TanStack
// Start router that handles all routes under `app/routes/`.
import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    tsconfigPaths(),
    tailwindcss(),
  ],
  server: {
    port: 80,
    host: true,
  },
  // The TanStack Start Vite plugin is loaded via the `vinxi` config in
  // vinxi.config.ts (sibling of this file). Vinxi composes the app
  // with TanStack Start's server-function + SSR runtime.
});
