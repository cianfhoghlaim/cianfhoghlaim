// apps/web/src/lib/portal-marimo.ts
//
// Constants for the central portal entry. Single source of truth for
// where the marimo notebooks live in production.
//
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/
// R15 (Marimo notebook deployed to `*.workers.dev` URL).

/**
 * Base URL for the 6 per-subject marimo notebooks.
 *
 * In production:
 *   https://portal-marimo.cianfhoghlaim.ie/<subject>
 *
 * At dev time (when the container is not yet deployed), this defaults
 * to localhost:8080 which the marimo dev server serves via
 * `marimo run --headless --port 8080`.
 */
export const PORTAL_MARIMO_BASE: string =
  process.env.PORTAL_MARIMO_BASE ||
  (typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "http://localhost:8080"
    : "https://portal-marimo.cianfhoghlaim.ie");
