// app.config.ts — Cianfhoghlaim Leaving Cert web app
// TanStack Start (Vite plugin) + Convex + CopilotKit v2
//
// Per follow-up #3 of openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// (R31 + R33 — WASM-compatible deployment):
//   - The PDF.js WASM build (`pdfjs-dist/build/pdf.worker.mjs`) is shipped
//     self-hosted. `<PdfViewer>` imports it via
//     `import PdfWorker from 'pdfjs-dist/build/pdf.worker.mjs?url'` —
//     Vite handles the build-time copy + asset hashing; the worker lands
//     in `dist/assets/` along with the rest of the bundle.
//   - The `assetsInclude` glob below is the cleanest cross-bundler way
//     to teach Vite that this specific WASM worker is a static asset
//     (it doesn't need a JS module wrapper).

import { defineConfig } from "vite";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";

export default defineConfig({
  server: {
    port: 3082,
    host: true,
  },
  // Per R33 — explicitly allow the PDF.js WASM worker to be served
  // through Vite as a static asset. The runtime URL is computed by
  // `packages/lineage/PdfViewer.tsx` via the Vite `?url` import pattern.
  assetsInclude: ["**/pdfjs-dist/build/pdf.worker.mjs", "**/pdf.worker.mjs"],
  plugins: [
    tsconfigPaths(),
    tailwindcss(),
    tanstackStart({
      // The Convex deployment is configured via env vars
      runtimeUrl: process.env.COPILOTKIT_RUNTIME_URL || "/api/copilotkit",
    }),
  ],
  // Per R33 — default asset filenames are fine; the `<PdfViewer>` resolves
  // the hashed URL via Vite's `?url` import at build time.
  build: {
    target: "esnext",
    assetsInlineLimit: 0,
  },
});
