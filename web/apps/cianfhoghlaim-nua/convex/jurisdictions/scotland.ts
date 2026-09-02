/**
 * Scotland jurisdiction subject-spec table.
 *
 * Per the 2026-09-XX-orchestration-integration-v1 change (Phase 11 §3).
 * The SCSubjectSpec row from `b.ExtractScotlandSubjectSpec` is
 * materialised here by the canonical Python orchestrator at
 * `orchestration/defs/2_materials/scotland_education/scotland_assets.py`.
 */

import { defineTable } from "convex/server";
import { v } from "convex/values";
import { mutation } from "../_generated/server";

export const scotland_subject_specs = defineTable({
  jurisdiction: v.literal("scotland"),
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

export const create = mutation({
  args: {
    jurisdiction: v.literal("scotland"),
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
  handler: async (ctx, args) => {
    const id = await ctx.db.insert("scotland_subject_specs", {
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
