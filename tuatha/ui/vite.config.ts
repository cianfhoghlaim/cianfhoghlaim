import { defineConfig } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import viteTsConfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [
    // Order matters: TanStack Router plugin MUST come before React/JSX plugins
    tanstackStart() as unknown as ReturnType<typeof viteReact>,
    viteReact(),
    viteTsConfigPaths({ projects: ["./tsconfig.json"] }),
  ],
  server: {
    port: 3004,
  },
});
