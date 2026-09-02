/**
 * Hono route for Manx (Gaelg) vernacular CopilotKit actions.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Mounted at /api/copilotkit/vernacular/manx/* in
 * web/hono-api/src/index.ts. One of 3 vernaculars with actual
 * PDF corpora (per the Phase 14 spec).
 */

import { buildVernacularApp } from "./_vernacular_factory";

const manxApp = buildVernacularApp({
  vernacular: "manx",
  display_name: "Manx (Gaelg)",
  jurisdiction: "IM",
  baml_function: "ExtractManxSubjectSpec",
  language_code: "gv",
});

export default manxApp;
