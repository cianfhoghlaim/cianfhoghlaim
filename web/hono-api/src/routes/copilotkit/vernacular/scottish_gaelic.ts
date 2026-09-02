/**
 * Hono route for Scottish Gaelic (Gàidhlig) vernacular CopilotKit actions.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Mounted at /api/copilotkit/vernacular/scottish_gaelic/* in
 * web/hono-api/src/index.ts.
 */

import { buildVernacularApp } from "./_vernacular_factory";

const scottishGaelicApp = buildVernacularApp({
  vernacular: "scottish_gaelic",
  display_name: "Scottish Gaelic (Gàidhlig)",
  jurisdiction: "SC",
  baml_function: "ExtractScottishGaelicSubjectSpec",
  language_code: "gd",
});

export default scottishGaelicApp;
