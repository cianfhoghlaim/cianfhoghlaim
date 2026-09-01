import { defineConfig } from "vite";
import type { PluginOption } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import { nitro } from "nitro/vite";

export default defineConfig({
  // NOTE: `resolve.tsconfigPaths` is a rolldown-vite-only option and is not
  // valid on stock vite 7 (this app declares `vite: ^7.0.6`). It was also a
  // no-op here — this app's tsconfig declares no `paths`.
  //
  // The `as PluginOption[]` assertion bridges a dual-install type identity
  // mismatch: `vite` resolves to 7.x from this app's own node_modules while
  // the plugin packages resolve their `vite` peer from the workspace root
  // (6.x), so the structurally-identical `Plugin` types are nominally
  // distinct. Remove the assertion once the workspace hoists a single vite.
  plugins: [
    nitro({ rollupConfig: { external: [] } }),
    tanstackStart(),
    viteReact(),
  ] as PluginOption[],
  server: {
    port: 3004,
  },
});
