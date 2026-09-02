import { defineConfig } from "@tanstack/start/config";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  vite: {
    plugins: [tsconfigPaths() as never, tailwindcss() as never],
  },
  server: {
    preset: "node-server",
  },
});
