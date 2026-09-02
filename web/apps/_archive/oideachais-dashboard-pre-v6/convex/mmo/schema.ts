// Convex schema for the Cianfhoghlaim Educational MMO.
//
// Tables:
// - badges — SkillTreeBadge records (the hybrid x402 educational credential)
// - credentialAnchors — the daily Merkle batches published to Base L2
// - students — student pseudonyms (never PII)
// - questAttempts — per-quest attempt history
// - mastery — cross-subject mastery rollup (cached for fast UI reads)
// - questPacks — docs-informed generated quest packs (2026-08-08
//   docs-informed-quest-and-credential-generation-v1)
// - x402Payments — durable x402 payment state (2026-08-08
//   learn-to-earn-x402-credential-pipeline-v1, replacing
//   agents/api/routes/routes/payments.py's in-memory dicts)

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
    // Per docs-informed-quest-and-credential-generation-v1: grounds the
    // badge in the NCCA's own key-competency + evidence-type terminology
    // (see tuatha/badges/schema.py's KeyCompetency / EvidenceType enums).
    keyCompetencies: v.array(v.string()),
    evidenceType: v.string(), // 'FORMATIVE_ITEM' | 'CLASSROOM_BASED_ASSESSMENT'
    dateEarned: v.number(), // epoch ms
    agentIssuer: v.string(), // 'math_agent', 'gael_agent', etc.
    evidenceItemId: v.string(),
    evidenceResponse: v.string(),
    evidenceScorePct: v.number(),
    // Previously dropped on write (tuatha/badges/schema.py's EvidenceLink
    // has these fields but ledger.py's Convex mutation never sent them) —
    // added so a badge round-trips through Convex without losing the
    // feedback text or the source-PDF citation.
    evidenceFeedbackEn: v.optional(v.string()),
    evidenceFeedbackGa: v.optional(v.string()),
    evidenceSourcePdf: v.optional(v.string()),
    evidenceSourcePage: v.optional(v.number()),
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
    // Per learn-to-earn-x402-credential-pipeline-v1: the student's SIWE-
    // authenticated wallet address, when they've connected one. Optional
    // — badge issuance and off-chain credentials work fully without it;
    // only AchievementToken minting (tuatha/badges/ledger.py's step 6)
    // needs it, and skips gracefully when absent.
    walletAddress: v.optional(v.string()),
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

  // One row per docs-informed generated quest pack (one per subject,
  // Higher Level, English-medium — see
  // orchestration/defs/2_materials/lc_extraction/quest_pack_assets.py's
  // module docstring for the full scoping). `items` is the formative-
  // item array as `model_dump(mode="json")`'d from the subject's
  // `<Prefix>FormativeItem` BAML type — stored as `v.any()` rather than
  // a hand-written validator because the item shape's `topic`/
  // `item_type` enums differ per subject (MathTopicArea vs
  // ChemTopicArea, etc.); the source of truth for that shape is the
  // BAML class, not this schema.
  // Indexes:
  //   by_subject: the realm/$subject.tsx route's primary query
  //   by_pack_id: idempotent re-writes on asset re-materialisation
  questPacks: defineTable({
    packId: v.string(), // MathQuestPack.id etc. — UUID from the BAML function
    subject: v.string(),
    framework: v.string(), // 'ncca-lc' or 'ncca-jc'
    level: v.string(), // e.g. 'LC_HL'
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
    generatedAt: v.string(), // ISO datetime
    generatedBy: v.string(), // e.g. 'math_agent'
  })
    .index("by_subject", ["subject"])
    .index("by_pack_id", ["packId"]),

  // Durable x402 payment state — the primary store for
  // agents/api/routes/routes/payments.py's `_ConvexPaymentStore`
  // (replacing the in-memory `_payment_requests`/`_completed_payments`
  // dicts, which lost all state on every process restart).
  // Indexes:
  //   by_payment_id: the store's sole lookup key
  x402Payments: defineTable({
    paymentId: v.string(),
    resourceType: v.string(),
    priceUsd: v.number(),
    priceCrypto: v.string(),
    token: v.string(),
    status: v.string(), // 'pending' | 'verified' | 'failed' | 'expired'
    createdAt: v.string(), // ISO datetime
    expiresAt: v.string(), // ISO datetime
    transactionHash: v.optional(v.string()),
    verifiedAt: v.optional(v.string()),
    failureReason: v.optional(v.string()),
  }).index("by_payment_id", ["paymentId"]),
});