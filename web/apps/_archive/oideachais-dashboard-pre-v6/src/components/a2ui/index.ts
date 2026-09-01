/**
 * A2UI module barrel — re-exports the canonical A2UI surface + renderer.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.5).
 */

export { A2UISurface, type A2UISurfaceProps } from "./A2UISurface";
export {
  BIEP_DASHBOARD_CATALOG,
  CIANFHOGHLAIM_THEME,
  type A2UIThemeComponents,
  A2UIProvider,
} from "./a2ui-renderer";
