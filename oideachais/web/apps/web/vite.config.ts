import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [
    tailwindcss(),
    react(),
    tsconfigPaths(),
  ],
  server: {
    port: 3001,
    host: true,
    proxy: {
      "/api": "http://localhost:8787",
      "/rpc": "http://localhost:8787",
    },
  },
});
