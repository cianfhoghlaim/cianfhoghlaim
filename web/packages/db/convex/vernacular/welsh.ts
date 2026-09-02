/**
 * Per-vernacular Convex table for Welsh (Cymraeg).
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-v7-vernaculars-pipelines-v1
 * change (Phase 14 of the cianfhoghlaim-nua v6 era plan).
 *
 * Re-exports the canonical ``vernacular_documents`` table from
 * ``../schema`` with the WELSH vernacular literal pre-applied.
 *
 * Welsh uses the ExtractWelshSubjectSpec BAML function.
 * Jurisdiction: WL (Wales).
 */

export { vernacular_documents } from "../schema";
