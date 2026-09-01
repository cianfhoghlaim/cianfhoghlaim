import { defineConfig } from "vite";
import tsConfigPaths from "vite-tsconfig-paths";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";

export default defineConfig({
  plugins: [
    TanStackRouterVite({
      autoCodeSplitting: true,
    }),
    tsConfigPaths(),
  ],
  server: {
    port: 3000,
    host: true,
  },
  build: {
    target: "esnext",
  },
});
