/**
 * apps/web/vitest.config.ts — Vitest config for the leaving-cert web app.
 *
 * Per follow-up #5 of openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1:
 *   - happy-dom is the default environment (so @tanstack/react-router's
 *     `useRouter` / `useMatchRoute` hooks resolve with a real DOM)
 *   - `*.test.{ts,tsx}` globs cover both `src/` (the canonical app code)
 *     and `packages/` (the lineage components)
 *   - The vite-tsconfig-paths plugin is registered so `import "@/..."`
 *     resolves in tests just as it does at build time
 *   - Tests run in a thread pool (the parallel default) for speed
 */
import { defineConfig } from "vitest/config";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  plugins: [tsconfigPaths()],
  test: {
    environment: "happy-dom",
    globals: false,
    include: [
      "src/**/*.test.{ts,tsx}",
      "packages/**/*.test.{ts,tsx}",
    ],
    coverage: {
      enabled: false, // opt in via `bun run test:coverage` once the engine is wired in Phase 2
      reporter: ["text", "json-summary"],
    },
    // Keep test runs <30s for CI friendliness; most tests are pure.
    testTimeout: 5_000,
  },
});
