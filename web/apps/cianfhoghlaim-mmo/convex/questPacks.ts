// Convex functions for the questPacks table.
//
// Written by orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py
// (`_write_quest_pack_to_convex`), read by the MMO client's
// `realm/$subject.tsx` route. Per
// 2026-08-08-docs-informed-quest-and-credential-generation-v1.

import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

// Create or replace a quest pack for a subject. Idempotent on `packId`:
// re-materialising the Dagster asset (e.g. after a syllabus PDF update)
// overwrites the existing row for that pack rather than accumulating
// duplicates, since only one Higher Level pack per subject is generated
// today (see quest_pack_assets.py's module docstring "Scope").
export const create = mutation({
  args: {
    packId: v.string(),
    subject: v.string(),
    framework: v.string(),
    level: v.string(),
    titleEn: v.string(),
    titleGa: v.optional(v.string()),
    descriptionEn: v.string(),
    descriptionGa: v.optional(v.string()),
    totalItems: v.number(),
    totalMarks: v.number(),
    estTimeMinutes: v.number(),
    losCovered: v.array(v.string()),
    items: v.any(),
    prerequisites: v.array(v.string()),
    crossSubjectLinks: v.array(v.string()),
    generatedAt: v.string(),
    generatedBy: v.string(),
  },
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("questPacks")
      .withIndex("by_subject", (q) => q.eq("subject", args.subject))
      .collect();
    for (const row of existing) {
      await ctx.db.delete(row._id);
    }
    return await ctx.db.insert("questPacks", args);
  },
});

// The realm/$subject.tsx route's primary query: the current quest pack
// for a subject (there is at most one today, per `create`'s replace
// semantics above).
export const getBySubject = query({
  args: { subject: v.string() },
  handler: async (ctx, { subject }) => {
    return await ctx.db
      .query("questPacks")
      .withIndex("by_subject", (q) => q.eq("subject", subject))
      .first();
  },
});

// List every generated quest pack (realm map overview / landing page).
export const listAll = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("questPacks").collect();
  },
});
