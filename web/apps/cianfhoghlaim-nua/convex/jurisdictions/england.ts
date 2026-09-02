/**
 * England jurisdiction subject-spec table.
 *
 * Per the 2026-09-XX-orchestration-integration-v1 change
 * (Phase 11 §3 of the cianfhoghlaim-nua v6 era plan). The 5
 * jurisdiction subject_spec tables are added to the canonical Convex
 * schema in `web/apps/cianfhoghlaim-nua/convex/schema.ts`. The
 * extracted `<Jur>SubjectSpec` rows come from the per-jurisdiction
 * BAML extractors:
 *
 * - england_subject_specs        → b.ExtractEnglandSubjectSpec
 * - wales_subject_specs          → b.ExtractWalesSubjectSpec
 * - scotland_subject_specs       → b.ExtractScotlandSubjectSpec
 * - northern_ireland_subject_specs → b.ExtractNorthernIrelandSubjectSpec
 * - isle_of_man_subject_specs    → b.ExtractIsleOfManSubjectSpec
 *
 * These tables back Phase 11 §2 (the 5 orchestrators at
 * `orchestration/defs/2_materials/{england,wales,scotland,
 * northern_ireland,isle_of_man}_education/<jur>_assets.py`) which now
 * materialise the extracted `ENSubjectSpec` / `WLSubjectSpec` etc. to
 * these tables instead of letting them sit in the prior
 * `getattr(b, fn_name, None)` null-fallback path.
 *
 * The create mutation (`england_subject_specs:create`) is the entry
 * point called from Python via `convex.ConvexClient.mutation(...)` in
 * `orchestration/defs/2_materials/_base/jurisdiction_baml_extractor.py`.
 */

import { defineTable } from "convex/server";
import { v } from "convex/values";

export const england_subject_specs = defineTable({
  jurisdiction: v.literal("england"),
  subject_slug: v.string(),
  source_pdf: v.string(),
  source_url: v.string(),
  stage: v.string(),
  display_name: v.string(),
  display_name_ga: v.string(),
  display_name_local: v.string(),
  award_descriptor: v.string(),
  descriptor_vocabulary: v.array(v.string()),
  key_competencies: v.array(v.string()),
  language: v.string(),
  year: v.number(),
  page: v.number(),
  payload_json: v.string(),
  created_at: v.number(),
})
  .index("by_jurisdiction", ["jurisdiction"])
  .index("by_subject", ["jurisdiction", "subject_slug"])
  .index("by_stage", ["jurisdiction", "stage"]);

// Mutation: invoked by the Python orchestrator via the convex
// ConvexClient.mutation(...) call. The Python helper sends the camelCase
// payload exactly as defined here.
import { mutation } from "../_generated/server";

export const create = mutation({
  args: {
    jurisdiction: v.literal("england"),
    subjectSlug: v.string(),
    sourcePdf: v.string(),
    sourceUrl: v.string(),
    stage: v.string(),
    displayName: v.string(),
    displayNameGa: v.string(),
    displayNameLocal: v.string(),
    awardDescriptor: v.string(),
    descriptorVocabulary: v.array(v.string()),
    keyCompetencies: v.array(v.string()),
    language: v.string(),
    year: v.number(),
    page: v.number(),
    payloadJson: v.string(),
    createdAt: v.number(),
  },
  handler: async (
    ctx,
    args,
  ) => {
    const id = await ctx.db.insert("england_subject_specs", {
      jurisdiction: args.jurisdiction,
      subject_slug: args.subjectSlug,
      source_pdf: args.sourcePdf,
      source_url: args.sourceUrl,
      stage: args.stage,
      display_name: args.displayName,
      display_name_ga: args.displayNameGa,
      display_name_local: args.displayNameLocal,
      award_descriptor: args.awardDescriptor,
      descriptor_vocabulary: args.descriptorVocabulary,
      key_competencies: args.keyCompetencies,
      language: args.language,
      year: args.year,
      page: args.page,
      payload_json: args.payloadJson,
      created_at: args.createdAt,
    });
    return { id };
  },
});
