/**
 * Per-jurisdiction subject-spec tables — Phase 11 additions.
 *
 * Per the 2026-09-XX-orchestration-integration-v1 change (Phase 11 of
 * the cianfhoghlaim-nua v6 era plan). The 5 new tables
 * ({england,wales,scotland,northern_ireland,isle_of_man}_subject_specs)
 * back the per-jurisdiction BAML extractors defined in
 * `baml_src/british_isles/{en,wl,sc,ni,im}/education/<jur>_extraction.baml`.
 *
 * Each jurisdiction orchestrator at
 * `orchestration/defs/2_materials/{jurisdiction}_education/<jur>_assets.py`
 * reads the canonical PDF, invokes the canonical BAML function, and
 * writes the result to its matching `*_subject_specs` table.
 */

export { england_subject_specs } from "./england";
export { wales_subject_specs } from "./wales";
export { scotland_subject_specs } from "./scotland";
export { northern_ireland_subject_specs } from "./northern_ireland";
export { isle_of_man_subject_specs } from "./isle_of_man";
