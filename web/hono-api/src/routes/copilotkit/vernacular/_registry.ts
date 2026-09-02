/**
 * web.hono-api.src.routes.copilotkit.vernacular — Phase 14 vernacular routes.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * The 8 vernacular Hono apps for the British Isles vernacular
 * languages (7 + 1 Ulster Scots). Each app exposes 4 endpoints:
 *  - GET  /health
 *  - POST /extract_subject_spec
 *  - POST /search_vernacular_corpus
 *  - POST /get_display_name
 *
 * The canonical factory lives in ``_vernacular_factory.ts``.
 */

export {
  VERNACULAR_ROUTE_SPECS,
  buildVernacularApp,
} from "./_vernacular_factory";

export { default as welsh } from "./welsh";
export { default as scottish_gaelic } from "./scottish_gaelic";
export { default as breton } from "./breton";
export { default as cornish } from "./cornish";
export { default as manx } from "./manx";
export { default as jersey_french } from "./jersey_french";
export { default as guernsey_french } from "./guernsey_french";
export { default as ulster_scots } from "./ulster_scots";
