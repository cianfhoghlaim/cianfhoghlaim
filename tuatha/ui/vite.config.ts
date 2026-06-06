import { defineConfig } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import viteTsConfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [
    viteTsConfigPaths({ projects: ["./tsconfig.json"] }),
    viteReact(),
    // The TanStack Start plugin's types reference its own bundled Vite, which
    // causes a structural type mismatch with our root Vite. We cast to any
    // here because the runtime contract is correct; the type system just
    // can't reconcile the two Vite copies.
    tanstackStart() as unknown as ReturnType<typeof viteReact>,
  ],
  server: {
    port: 3004,
  },
});
