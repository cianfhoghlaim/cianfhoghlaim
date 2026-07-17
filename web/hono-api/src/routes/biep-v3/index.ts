/**
 * Hono API barrel for BIEP v3 — re-exports the 5 jurisdiction endpoints.
 *
 * Per the 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1 change.
 */
export { default as ireland } from "./ireland";
export { default as england } from "./england";
export { default as sct_wls_ni } from "./sct_wls_ni";
export { default as crown } from "./crown";
export { default as registry } from "./registry";
