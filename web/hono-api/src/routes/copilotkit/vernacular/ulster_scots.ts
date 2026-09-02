/**
 * Hono route for Ulster Scots vernacular CopilotKit actions.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Mounted at /api/copilotkit/vernacular/ulster_scots/* in
 * web/hono-api/src/index.ts. Ulster Scots uses the
 * ExtractUlsterScotsSubjectSpec BAML function and is the 8th
 * vernacular in the BAML enum (jurisdiction NI — Northern Ireland).
 */

import { buildVernacularApp } from "./_vernacular_factory";

const ulsterScotsApp = buildVernacularApp({
  vernacular: "ulster_scots",
  display_name: "Ulster Scots",
  jurisdiction: "NI",
  baml_function: "ExtractUlsterScotsSubjectSpec",
  language_code: "sco",
});

export default ulsterScotsApp;
