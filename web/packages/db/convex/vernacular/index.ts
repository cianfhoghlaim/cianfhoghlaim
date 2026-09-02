/**
 * web.packages.db.convex.vernacular — per-vernacular Convex tables.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * All 7 sibling files re-export the single canonical
 * ``vernacular_documents`` table from ``../schema`` (with the
 * appropriate literal). One row per BAML-extracted
 * ``VernacularSubjectSpec`` across the 7 British Isles vernacular
 * languages (beyond the canonical EN + GA pair).
 */
export { vernacular_documents as welsh } from "./welsh";
export { vernacular_documents as scottish_gaelic } from "./scottish_gaelic";
export { vernacular_documents as breton } from "./breton";
export { vernacular_documents as cornish } from "./cornish";
export { vernacular_documents as manx } from "./manx";
export { vernacular_documents as jersey_french } from "./jersey_french";
export { vernacular_documents as guernsey_french } from "./guernsey_french";
export { vernacular_documents as ulster_scots } from "./ulster_scots";
export { vernacular_documents } from "../schema";
