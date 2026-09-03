/**
 * @cianfhoghlaim/ui-kit — the single canonical web UI surface
 *
 * Post-Phase A (2026-08-13-web-monorepo-consolidation-and-agent-integration-v1):
 * MERGES the 4 former packages (analytics / i18n / ui / config) into one
 * consolidated surface. The 4 sub-package directories still exist (for
 * code organization + re-exports), but the canonical entry point is this
 * file at the ui-kit root.
 */

// Re-export all 5 sub-surfaces
export * from "./analytics/src/index";
export * from "./i18n/src/index";
export * from "./components/src/index";
export * from "./config/src/index";
export { useIsMobile } from "./hooks/use-mobile";
