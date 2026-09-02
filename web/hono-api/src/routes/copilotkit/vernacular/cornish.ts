/**
 * Hono route for Cornish (Kernewek) vernacular CopilotKit actions.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Mounted at /api/copilotkit/vernacular/cornish/* in
 * web/hono-api/src/index.ts. Sister-repo lift target.
 */

import { buildVernacularApp } from "./_vernacular_factory";

const cornishApp = buildVernacularApp({
  vernacular: "cornish",
  display_name: "Cornish (Kernewek)",
  jurisdiction: "KW",
  baml_function: "ExtractCornishSubjectSpec",
  language_code: "kw",
});

export default cornishApp;
