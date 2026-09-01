// Convex functions for the badges table.

import { v } from "convex/values";
import { mutation, query } from "../_generated/server";

// Create a new badge row.
export const create = mutation({
  args: {
    studentId: v.string(),
    framework: v.string(),
    level: v.string(),
    subject: v.string(),
    competencyCode: v.string(),
    competencyTextEn: v.string(),
    competencyTextGa: v.optional(v.string()),
    keyCompetencies: v.array(v.string()),
    evidenceType: v.string(),
    agentIssuer: v.string(),
    evidenceItemId: v.string(),
    evidenceResponse: v.string(),
    evidenceScorePct: v.number(),
    evidenceFeedbackEn: v.optional(v.string()),
    evidenceFeedbackGa: v.optional(v.string()),
    evidenceSourcePdf: v.optional(v.string()),
    evidenceSourcePage: v.optional(v.number()),
    evidenceHash: v.string(),
    signature: v.string(),
  },
  handler: async (ctx, args) => {
    const id = await ctx.db.insert("badges", {
      ...args,
      dateEarned: Date.now(),
      onChainAnchor: undefined,
      anchorDate: undefined,
    });
    return id;
  },
});

// Set the on-chain anchor on a badge after the daily Merkle batch
// is published to Base L2.
export const setOnChainAnchor = mutation({
  args: {
    id: v.id("badges"),
    onChainAnchor: v.string(),
    anchorDate: v.string(),
  },
  handler: async (ctx, { id, onChainAnchor, anchorDate }) => {
    await ctx.db.patch(id, { onChainAnchor, anchorDate });
  },
});

// List all badges for a student, ordered by dateEarned desc.
export const listByStudent = query({
  args: { studentId: v.string() },
  handler: async (ctx, { studentId }) => {
    return await ctx.db
      .query("badges")
      .withIndex("by_student", (q) => q.eq("studentId", studentId))
      .order("desc")
      .collect();
  },
});

// List all badges since the given epoch ms timestamp.
// Used by the daily_credential_anchor asset.
export const listSince = query({
  args: { sinceMs: v.number() },
  handler: async (ctx, { sinceMs }) => {
    return await ctx.db
      .query("badges")
      .withIndex("by_unanchored", (q) => q.gte("dateEarned", sinceMs))
      .collect();
  },
});

// List all badges anchored on a particular date (YYYY-MM-DD).
export const listByAnchorDate = query({
  args: { anchorDate: v.string() },
  handler: async (ctx, { anchorDate }) => {
    return await ctx.db
      .query("badges")
      .withIndex("by_anchor", (q) => q.eq("anchorDate", anchorDate))
      .collect();
  },
});

// List badges by subject (e.g. all "mathematics" badges).
export const listBySubject = query({
  args: {
    studentId: v.string(),
    subject: v.string(),
  },
  handler: async (ctx, { studentId, subject }) => {
    return await ctx.db
      .query("badges")
      .withIndex("by_student", (q) => q.eq("studentId", studentId))
      .filter((q) => q.eq(q.field("subject"), subject))
      .collect();
  },
});

// List badges by NCCA LO code (e.g. all "LC-MATHS-LO-2.4" badges).
export const listByLO = query({
  args: {
    studentId: v.string(),
    competencyCode: v.string(),
  },
  handler: async (ctx, { studentId, competencyCode }) => {
    return await ctx.db
      .query("badges")
      .withIndex("by_student", (q) => q.eq("studentId", studentId))
      .filter((q) => q.eq(q.field("competencyCode"), competencyCode))
      .collect();
  },
});