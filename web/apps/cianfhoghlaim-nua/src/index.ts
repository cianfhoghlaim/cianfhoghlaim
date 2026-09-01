/**
 * cianfhoghlaim-nua — the consolidated web app.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
 * (Phase 3 of the cianfhoghlaim-nua v6 era plan).
 *
 * Consolidates the 5 previous web apps
 * (cianfhoghlaim + oideachais + oideachais-dashboard + tuatha +
 *  croilar-web) into ONE TanStack Start app with 6 route groups:
 *
 *   (student)     — the LC + JC + GCSE + A-Level subject surface
 *                    (was oideachais/(en|ga)/subjects/<subject>/)
 *   (educator)    — the NCCA / NCCE learning graphs + pedagogy
 *                    overlays + equivalencies
 *   (researcher)  — the BIEP v3 dashboards + marimo embeds +
 *                    RAG playground
 *   (author)      — the CV + identity + music + teaching + code
 *                    surface (was croilar-web)
 *   (mmo)         — the British Isles Formative Assessment MMO
 *                    (was tuatha/)
 *   (admin)       — the deployment control panel + model registry
 *                    + cost dashboards (was oideachais-dashboard/)
 *
 * The app consumes the canonical A2UI catalog from
 * `@cianfhoghlaim/a2ui` (Phase 2) + the canonical Hono API from
 * `web/hono-api/` + the canonical Convex schema from
 * `web/packages/db/convex/schema.ts` (Phase 1's 5 new tables).
 *
 * Re-gen after changes:
 *   cd cianfhoghlaim && mise run web:typecheck
 *
 * Reference:
 *   openspec/changes/2026-09-01-cianfhoghlaim-nua-web-consolidation-v1/
 */

export const CIANFHOGLAIM_NUA_VERSION = "2026-09-01.v1";

export const ROUTE_GROUP_PATHS = {
  student: "/(student)",
  educator: "/(educator)",
  researcher: "/(researcher)",
  author: "/(author)",
  mmo: "/(mmo)",
  admin: "/(admin)",
} as const;

export type RouteGroup = keyof typeof ROUTE_GROUP_PATHS;