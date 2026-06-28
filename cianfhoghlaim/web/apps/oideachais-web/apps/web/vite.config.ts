// vite.config.ts — TanStack Start + Vite
//
// Replaces the Vite SPA config with a TanStack Start config that supports:
// - File-based routes (replaces code-based routeTree.tsx)
// - Server functions via createServerFn (replaces the SPA's Vite proxy for Hono)
// - SSR streaming with React Suspense
// - Bilingual route groups under (en) and (ga) — see src/app/routes/
//
// Pattern from https://github.com/TanStack/router/tree/main/examples/react/start-basic
import { defineConfig, type Plugin } from "vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import { TanStackRouterVite } from "@tanstack/router-plugin/vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";

// Workaround for a TanStack router-plugin 1.168 dev-mode bug: the
// @tanstack/start-plugin-core hard-codes `addHmr: true` on its client-side
// code-splitter instance (see node_modules/@tanstack/start-plugin-core/
// dist/esm/vite/start-router-plugin/plugin.js), which emits a duplicated
// `const hot = import.meta.hot` declaration in the same generated route
// module. Babel rejects it with `Duplicate declaration "hot"` and the Vite
// overlay floods the dev UI with stack traces, even though the route itself
// still loads and renders.
//
// We strip the *first* of the two declarations (the
// react-refresh-ignored-route-exports block) in a post-transform plugin so
// the second `accept(...)` HMR handler is the only `const hot` left in
// scope. React Fast Refresh still works because each route module is
// wrapped in its own Fast Refresh boundary by @vitejs/plugin-react, and
// the surviving HMR handler below covers the route options swap.
const stripTsrIgnoredRouteExports: Plugin = {
  name: "strip-tsr-ignored-route-exports",
  enforce: "post",
  apply: () => true,
  transform(code, id) {
    if (!/\.(m|c)?(j|t)sx?$/.test(id)) return null;
    if (
      !code.includes(
        "window.__TSR_REACT_REFRESH__ ??= (() => {",
      )
    ) {
      return null;
    }
    const before = code;
    const next = code.replace(
      /\nconst hot = import\.meta\.hot\nif \(hot && typeof window !== 'undefined'\) \{\n  hot\.data \?\?= \{\}\n  const tsrReactRefresh = window\.__TSR_REACT_REFRESH__ \?\?= \(\(\) => \{[\s\S]*?tsrReactRefresh\.ignoredExportsById\.set\([^)]*,\s*\['Route'\]\);\n\}\n/,
      "\n",
    );
    if (next === before) return null;
    return { code: next, map: null };
  },
};

export default defineConfig({
  plugins: [
    tsconfigPaths(),
    tailwindcss(),
    // TanStack Router plugin: generates the file-based route tree from
    // src/routes/. The generated routeTree.gen.ts is imported by
    // app/router.tsx. We pass `addHmr: false` here, but the
    // tanstackStart() plugin below has its own splitter instance that
    // hard-codes `addHmr: true` for the client environment; the
    // stripTsrIgnoredRouteExports plugin above compensates.
    TanStackRouterVite({
      addHmr: false,
    }),
    tanstackStart({
      tsr: {
        appDirectory: "src/app",
      },
    }),
    react(),
    stripTsrIgnoredRouteExports,
  ],
  resolve: {
    // Vite needs explicit dedupe for cross-workspace deps so that
    // packages hoisted into the root node_modules can be resolved
    // from sibling workspaces (e.g. croilar/packages/* imported by
    // apps/web) without each croilar package needing its own
    // node_modules. Without this, vite cannot resolve `clsx` or
    // `tailwind-merge` from inside @croilar/ui's source files.
    dedupe: [
      "react",
      "react-dom",
      "@tanstack/react-router",
      "@tanstack/react-query",
      "clsx",
      "tailwind-merge",
      "tailwindcss",
    ],
  },
  server: {
    port: 3001,
    host: true,
    // Disable the Vite HMR error overlay in dev. The TanStack
    // router-plugin's code-splitter emits `Duplicate declaration
    // "hot"` for parametric routes (examiner-reports, dashboards,
    // past-papers, marking-schemes, practice) and the overlay
    // floods the dev UI with stack traces that obscure the actual
    // page content. The stripTsrIgnoredRouteExports plugin above
    // handles the most common case; turning the overlay off is a
    // belt-and-braces measure for the routes where the
    // replacement regex misses. Errors are still logged to the
    // browser console and the dev server stdout.
    hmr: { overlay: false },
    proxy: {
      "/api": "http://localhost:8787",
      "/api-reference": "http://localhost:8787",
      "/rpc": "http://localhost:8787",
    },
  },
});
