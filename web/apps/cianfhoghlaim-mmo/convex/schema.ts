// Convex schema for the Cianfhoghlaim Educational MMO.
//
// Tables:
// - badges — SkillTreeBadge records (the hybrid x402 educational credential)
// - credentialAnchors — the daily Merkle batches published to Base L2
// - students — student pseudonyms (never PII)
// - questAttempts — per-quest attempt history
// - mastery — cross-subject mastery rollup (cached for fast UI reads)

import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // One row per issued SkillTreeBadge.
  // Indexes:
  //   by_student:   lookup all badges for a student (badge wallet)
  //   by_anchor:    find all badges anchored in a particular daily batch
  //   by_subject:   filter by subject (e.g. "mathematics")
  //   by_lo:        filter by NCCA LO code
  //   by_unanchored: badges not yet anchored on-chain (used by daily_credential_anchor)
  badges: defineTable({
    studentId: v.string(),
    framework: v.string(), // 'ncca-lc' or 'ncca-jc'
    level: v.string(), // 'hl', 'ol', 'fl', 'jc'
    subject: v.string(), // 'mathematics', 'gaeilge', etc.
    competencyCode: v.string(), // e.g. 'LC-MATHS-LO-2.4'
    competencyTextEn: v.string(),
    competencyTextGa: v.optional(v.string()),
    dateEarned: v.number(), // epoch ms
    agentIssuer: v.string(), // 'math_agent', 'gael_agent', etc.
    evidenceItemId: v.string(),
    evidenceResponse: v.string(),
    evidenceScorePct: v.number(),
    evidenceHash: v.string(), // SHA-256, used as Merkle leaf
    signature: v.string(), // ETH signature from agent wallet
    onChainAnchor: v.optional(v.string()), // Base L2 tx_hash
    anchorDate: v.optional(v.string()), // YYYY-MM-DD
  })
    .index("by_student", ["studentId"])
    .index("by_anchor", ["anchorDate"])
    .index("by_subject", ["subject"])
    .index("by_lo", ["competencyCode"])
    .index("by_unanchored", ["dateEarned"]),

  // One row per daily Merkle batch.
  // Indexes:
  //   by_date: lookup by YYYY-MM-DD
  credentialAnchors: defineTable({
    batchId: v.string(),
    batchDate: v.string(), // YYYY-MM-DD
    merkleRoot: v.string(),
    leafCount: v.number(),
    badgeIds: v.array(v.string()),
    txHash: v.optional(v.string()),
    publishedAt: v.optional(v.number()), // epoch ms
    publishedBy: v.string(), // 'daily_credential_anchor' asset
  }).index("by_date", ["batchDate"]),

  // Student pseudonyms. Never PII — only a hash of (pseudonym + salt).
  // The salt is stored in Infisical; the hash is the canonical student_id.
  students: defineTable({
    pseudonymHash: v.string(), // SHA-256 of (pseudonym + salt)
    displayName: v.optional(v.string()), // Optional display name (teacher view)
    school: v.optional(v.string()),
    classSlug: v.optional(v.string()),
    createdAt: v.number(),
  })
    .index("by_pseudonym", ["pseudonymHash"])
    .index("by_class", ["classSlug"]),

  // Per-quest attempt history.
  // Indexes:
  //   by_student: lookup all attempts for a student
  //   by_item:    lookup all attempts for a formative item
  questAttempts: defineTable({
    studentId: v.string(),
    itemId: v.string(),
    loCode: v.string(),
    subject: v.string(),
    level: v.string(),
    response: v.string(),
    responseFormat: v.string(),
    timeTakenSeconds: v.number(),
    hintsUsed: v.number(),
    marksAwarded: v.number(),
    totalMarks: v.number(),
    partialCreditPct: v.number(),
    isCorrect: v.boolean(),
    badgeEarned: v.boolean(),
    agentIssuer: v.string(),
    createdAt: v.number(),
  })
    .index("by_student", ["studentId"])
    .index("by_item", ["itemId"]),

  // Cross-subject mastery rollup, cached for fast UI reads.
  // Keyed by (studentId, subject) — one row per (student, subject).
  // Updated by a Dagster asset or a Convex cron.
  mastery: defineTable({
    studentId: v.string(),
    subject: v.string(),
    level: v.string(),
    badgesCount: v.number(),
    lastEarnedAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_student", ["studentId"])
    .index("by_subject", ["subject"]),
});