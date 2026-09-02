/**
 * Per-vernacular Convex table for Manx (Gaelg).
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Re-exports the canonical ``vernacular_documents`` table from
 * ``../schema`` for Manx (gv).
 *
 * Manx uses the ExtractManxSubjectSpec BAML function.
 * Jurisdiction: IM (Isle of Man). One of 3 vernaculars with
 * actual PDF corpora (per the Phase 14 spec).
 */

export { vernacular_documents } from "../schema";
