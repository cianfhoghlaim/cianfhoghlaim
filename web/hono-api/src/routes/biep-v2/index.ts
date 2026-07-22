/**
 * BIEP v2 API barrel — re-exports the 3 BIEP v2 Hono routes
 * (`lc`, `jc`, `england`) so the TanStack Start web route at
 * `/biep-v2` can `import { lc, jc, england } from './biep-v2'`.
 *
 * Per the 2026-07-23-biep-v2-marimo-portal-v1 change.
 */
export { default as lc } from "./lc";
export { default as jc } from "./jc";
export { default as england } from "./england";
