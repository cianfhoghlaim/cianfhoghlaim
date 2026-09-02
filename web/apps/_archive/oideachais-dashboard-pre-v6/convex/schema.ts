import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

/**
 * Umbrella Convex schema for the Cianfhoghlaim platform.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change (Wave 6.7) + the **2026-08-24-wave-5-web-consolidation-v1** openspec
 * change (Wave 5 K.5). Consolidates 4 historical Convex deployments into
 * one:
 *   - `oideachais-dashboard/convex/`  (the OCR comparison + model registry)
 *   - `cianfhoghlaim-web/convex/`     (the subject-session tracking)
 *   - `croilar-portal/convex/`        (the portfolio Convex deployment)
 *   - `cianfhoghlaim-mmo/convex/`     (the Celtic MMO Convex deployment)
 *   - `cianfhoghlaim/convex/`         (the homepage chat + personal archive)
 *
 * All tables live at `web/apps/oideachais-dashboard/convex/`. The other
 * source directories were removed by the Wave 5 follow-ups (K.1-K.5);
 * the `--allow-non-umbrella-convex` flag in `lint:web-stack` was
 * dropped per the K.5 unification.
 */

export default defineSchema({
  // ─── OCR comparison + model registry (the original oideachais-dashboard) ────
  tasks: defineTable({
    filename: v.string(),
    fileSize: v.number(),
    fileStorageId: v.optional(v.id("_storage")),
    outputFormat: v.union(
      v.literal("markdown"),
      v.literal("json"),
      v.literal("text"),
    ),
    status: v.union(
      v.literal("pending"),
      v.literal("running"),
      v.literal("completed"),
      v.literal("failed"),
      v.literal("cancelled"),
    ),
    selectedModels: v.array(v.string()),
    totalDurationMs: v.optional(v.number()),
    createdAt: v.number(),
    completedAt: v.optional(v.number()),
    createdBy: v.optional(v.string()),
    metadata: v.optional(
      v.object({
        pageCount: v.optional(v.number()),
        hasImages: v.optional(v.boolean()),
        language: v.optional(v.string()),
      }),
    ),
  })
    .index("by_status", ["status"])
    .index("by_created", ["createdAt"]),

  comparisons: defineTable({
    taskId: v.id("tasks"),
    modelName: v.string(),
    modelProvider: v.string(),
    status: v.union(
      v.literal("pending"),
      v.literal("running"),
      v.literal("success"),
      v.literal("failed"),
      v.literal("timeout"),
    ),
    startedAt: v.optional(v.number()),
    completedAt: v.optional(v.number()),
    durationMs: v.optional(v.number()),
    outputStorageId: v.optional(v.id("_storage")),
    outputSizeBytes: v.optional(v.number()),
    errorMessage: v.optional(v.string()),
    metrics: v.optional(
      v.object({
        tokenCount: v.optional(v.number()),
        characterCount: v.optional(v.number()),
        wordCount: v.optional(v.number()),
        confidence: v.optional(v.number()),
      }),
    ),
  })
    .index("by_task", ["taskId"])
    .index("by_model", ["modelName"])
    .index("by_status", ["status"]),

  models: defineTable({
    name: v.string(),
    displayName: v.string(),
    provider: v.string(),
    endpoint: v.string(),
    isAvailable: v.boolean(),
    capabilities: v.array(v.string()),
    vramRequirement: v.optional(v.string()),
    avgLatencyMs: v.optional(v.number()),
    successRate: v.optional(v.number()),
    lastChecked: v.optional(v.number()),
    metadata: v.optional(
      v.object({
        contextLength: v.optional(v.number()),
        supportsIrish: v.optional(v.boolean()),
        specialization: v.optional(v.string()),
      }),
    ),
  })
    .index("by_name", ["name"])
    .index("by_provider", ["provider"])
    .index("by_availability", ["isAvailable"]),

  results: defineTable({
    comparisonId: v.id("comparisons"),
    content: v.string(),
    fullContentStorageId: v.optional(v.id("_storage")),
    isTruncated: v.boolean(),
    previewLength: v.number(),
  }).index("by_comparison", ["comparisonId"]),

  // ─── Cianfhoghlaim homepage + per-subject chat (consolidated) ───────────────
  chat_messages: defineTable({
    thread_id: v.string(),
    subject: v.string(),
    stage: v.string(),
    role: v.string(),
    content: v.string(),
    ragas_score: v.optional(v.number()),
    agent: v.optional(v.string()),
    created_at: v.number(),
  })
    .index("by_thread", ["thread_id", "created_at"])
    .index("by_subject", ["subject", "stage", "created_at"])
    .index("by_stage_subject", ["stage", "subject"]),

  subject_sessions: defineTable({
    stage: v.string(),
    subject: v.string(),
    user_id: v.string(),
    agno_session_id: v.string(),
    message_count: v.number(),
    last_active_at: v.number(),
    language: v.union(v.literal("en"), v.literal("ga")),
  })
    .index("by_user_stage", ["user_id", "stage"])
    .index("by_agno_session", ["agno_session_id"]),

  practice_attempts: defineTable({
    stage: v.string(),
    subject: v.string(),
    user_id: v.string(),
    question_id: v.string(),
    essay: v.string(),
    score: v.number(),
    rubric_fingerprint: v.string(),
    trace_id: v.optional(v.string()),
    submitted_at: v.number(),
  })
    .index("by_user_subject", ["user_id", "subject"])
    .index("by_trace", ["trace_id"]),

  annotations: defineTable({
    stage: v.string(),
    document_url: v.string(),
    range_start: v.number(),
    range_end: v.number(),
    note: v.string(),
    author_id: v.string(),
    visibility: v.union(v.literal("private"), v.literal("public")),
    created_at: v.number(),
  })
    .index("by_document", ["document_url"])
    .index("by_author", ["author_id"]),

  classmate_shares: defineTable({
    stage: v.string(),
    session_id: v.id("subject_sessions"),
    owner_id: v.string(),
    share_token: v.string(),
    visibility: v.union(v.literal("public"), v.literal("link-only")),
    created_at: v.number(),
  })
    .index("by_token", ["share_token"])
    .index("by_owner", ["owner_id"]),

  extraction_budget: defineTable({
    session_id: v.string(),
    papers_extracted: v.number(),
    tokens_consumed: v.number(),
    reset_at: v.number(),
    last_extraction_at: v.optional(v.number()),
  }).index("by_session", ["session_id"]),

  // ─── Croilar portfolio Convex deployment (consolidated) ────────────────────
  portfolio_projects: defineTable({
    slug: v.string(),
    title: v.string(),
    description: v.string(),
    url: v.optional(v.string()),
    tags: v.array(v.string()),
    published_at: v.number(),
    author_id: v.string(),
  })
    .index("by_slug", ["slug"])
    .index("by_author", ["author_id"]),

  portfolio_education: defineTable({
    institution: v.string(),
    programme: v.string(),
    start_year: v.number(),
    end_year: v.optional(v.number()),
    grade: v.optional(v.string()),
    description: v.optional(v.string()),
    user_id: v.string(),
  })
    .index("by_user", ["user_id"])
    .index("by_year", ["start_year"]),

  // ─── Tuatha Celtic MMO Convex deployment (consolidated) ─────────────────────
  mmo_sessions: defineTable({
    session_id: v.string(),
    player_id: v.string(),
    language: v.string(),
    language_level: v.string(),
    current_quest: v.optional(v.string()),
    current_zone: v.optional(v.string()),
    xp: v.number(),
    started_at: v.number(),
    updated_at: v.number(),
  })
    .index("by_session", ["session_id"])
    .index("by_player", ["player_id"]),

  mmo_npcs: defineTable({
    npc_id: v.string(),
    zone: v.string(),
    name: v.string(),
    role: v.string(),
    xp_reward: v.number(),
    language: v.string(),
  })
    .index("by_zone", ["zone"])
    .index("by_language", ["language"]),

  // ─── Cianfhoghlaim-mmo badges + x402 credential pipeline (Wave 5 lift) ──
  // Per 2026-08-25-tuatha-british-isles-mmo-consolidation-v1 K.4: lifted
  // from web/apps/tuatha/_merged/cianfhoghlaim-mmo/app/convex/.
  badges: defineTable({
    studentId: v.string(),
    framework: v.string(),
    level: v.string(),
    subject: v.string(),
    competencyCode: v.string(),
    competencyTextEn: v.string(),
    competencyTextGa: v.optional(v.string()),
    keyCompetencies: v.array(v.string()),
    evidenceType: v.string(),
    dateEarned: v.number(),
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
    onChainAnchor: v.optional(v.string()),
    anchorDate: v.optional(v.string()),
  })
    .index("by_student", ["studentId"])
    .index("by_anchor", ["anchorDate"])
    .index("by_subject", ["subject"])
    .index("by_lo", ["competencyCode"])
    .index("by_unanchored", ["dateEarned"]),

  credentialAnchors: defineTable({
    batchId: v.string(),
    batchDate: v.string(),
    merkleRoot: v.string(),
    leafCount: v.number(),
    badgeIds: v.array(v.string()),
    txHash: v.optional(v.string()),
    publishedAt: v.optional(v.number()),
    publishedBy: v.string(),
  }).index("by_date", ["batchDate"]),

  questPacks: defineTable({
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
  })
    .index("by_subject", ["subject"])
    .index("by_pack_id", ["packId"]),

  x402Payments: defineTable({
    paymentId: v.string(),
    resourceType: v.string(),
    priceUsd: v.number(),
    priceCrypto: v.string(),
    token: v.string(),
    status: v.string(),
    createdAt: v.string(),
    expiresAt: v.string(),
    transactionHash: v.optional(v.string()),
    verifiedAt: v.optional(v.string()),
    failureReason: v.optional(v.string()),
  }).index("by_payment_id", ["paymentId"]),

  // ─── Cianfhoghlaim-web subject-session tracking (Wave 5 lift) ────────
  // Per 2026-08-24-wave-5-web-consolidation-v1 K.2: lifted from
  // web/apps/cianfhoghlaim/_merged/cianfhoghlaim-web/app/convex/.
  //
  // NOTE: `subject_sessions`, `practice_attempts`, `classmate_shares`,
  // `extraction_budget` and `chat_messages` were already defined above by the
  // earlier consolidation pass, so the lift's re-declarations were removed —
  // duplicate keys in this object literal are a hard TS error (TS1117) and
  // silently discard the earlier definition at runtime. The lift's extra
  // `extraction_budget` fields (`reset_at`, `last_extraction_at`) were merged
  // into the canonical definition above. Only `web_annotations` was unique to
  // the lift and is retained here.
  web_annotations: defineTable({
    stage: v.string(),
    document_url: v.string(),
    range_start: v.number(),
    range_end: v.number(),
    note: v.string(),
    author_id: v.string(),
    visibility: v.union(v.literal("private"), v.literal("public")),
    created_at: v.number(),
  })
    .index("by_document", ["document_url"])
    .index("by_author", ["author_id"]),

  // ─── Cianfhoghlaim homepage chat + progress (Wave 5 lift) ───────────
  // Per 2026-08-24-wave-5-web-consolidation-v1 K.2: lifted from
  // web/apps/cianfhoghlaim/convex/ (was previously tolerated via
  // --allow-non-umbrella-convex flag — now consolidated).
  //
  // NOTE: the lift's `chat_messages` re-declaration was removed (TS1117); its
  // two index definitions were supersets of the canonical ones and have been
  // merged into the `chat_messages` definition above.
  homepage_annotations: defineTable({
    user_id: v.string(),
    subject: v.string(),
    stage: v.string(),
    topic_code: v.string(),
    note: v.string(),
    ncca_code: v.optional(v.string()),
    lo_code: v.optional(v.string()),
    created_at: v.number(),
    updated_at: v.number(),
  })
    .index("by_user", ["user_id", "created_at"])
    .index("by_subject_topic", ["subject", "topic_code", "created_at"]),

  progress: defineTable({
    user_id: v.string(),
    subject: v.string(),
    stage: v.string(),
    topic_code: v.string(),
    score: v.number(),
    completed: v.boolean(),
    notes: v.optional(v.string()),
    last_attempted: v.number(),
    created_at: v.number(),
  })
    .index("by_user", ["user_id", "last_attempted"])
    .index("by_subject", ["subject", "score"]),

  pipeline_health: defineTable({
    pipeline: v.string(),
    stage: v.string(),
    status: v.string(),
    subjects_processed: v.number(),
    subjects_total: v.number(),
    pdfs_processed: v.number(),
    pdfs_total: v.number(),
    ragas_score: v.optional(v.number()),
    last_update: v.number(),
  })
    .index("by_pipeline", ["pipeline", "last_update"])
    .index("by_stage", ["stage", "last_update"]),

  knowledge_graph: defineTable({
    cluster: v.string(),
    name: v.string(),
    description: v.string(),
    entity_count: v.number(),
    relationship_count: v.number(),
    centroid_embedding: v.optional(v.string()),
    updated_at: v.number(),
  })
    .index("by_cluster", ["cluster", "updated_at"]),

  activity_events: defineTable({
    kind: v.string(),
    subject: v.string(),
    agent: v.string(),
    message: v.string(),
    ragas_score: v.optional(v.number()),
    created_at: v.number(),
  })
    .index("by_kind", ["kind", "created_at"])
    .index("by_subject", ["subject", "created_at"])
    .index("by_agent", ["agent", "created_at"]),

  // ─── UoG personal-archive chat-over-my-archive (Wave 5 lift) ───────
  // Per 2026-08-23-uog-personal-archive-tertiary-modules-v1 + the Wave 6.7
  // consolidation. The personalArchive.ts functions live at
  // web/apps/oideachais-dashboard/convex/personalArchive.ts (moved from
  // web/apps/cianfhoghlaim/convex/); the schema tables are declared
  // alongside in this umbrella schema.
  archive_documents: defineTable({
    user_id: v.string(),
    title: v.string(),
    source_url: v.optional(v.string()),
    content_text: v.string(),
    embedding: v.optional(v.array(v.float64())),
    metadata: v.optional(v.any()),
    created_at: v.number(),
  })
    .index("by_user", ["user_id", "created_at"]),

  archive_chat_threads: defineTable({
    user_id: v.string(),
    title: v.string(),
    document_ids: v.array(v.id("archive_documents")),
    last_active_at: v.number(),
    created_at: v.number(),
  })
    .index("by_user", ["user_id", "last_active_at"]),

  archive_chat_messages: defineTable({
    thread_id: v.id("archive_chat_threads"),
    role: v.string(),
    content: v.string(),
    cited_doc_ids: v.array(v.id("archive_documents")),
    ragas_score: v.optional(v.number()),
    created_at: v.number(),
  })
    .index("by_thread", ["thread_id", "created_at"]),

  // ─── conic-leaving-cert skill/diagram/badge tables ───────────────────
  // Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
  // cianfhoghlaim-leaving-cert-portal/spec.md Requirement R6.
  //
  // `convex/legacy_lc_convex/src/functions.ts` consumes these 3 tables, but
  // they were only ever declared in the non-canonical
  // `convex/legacy_lc_convex/src/index.ts` schema. The generated data model is
  // derived from THIS file, so the tables were invisible to the type checker
  // and every `ctx.db` call against them failed. Lifted here to match the 5
  // sibling tables the Wave 5 consolidation already promoted.
  skill_assets: defineTable({
    subject: v.string(),
    mode: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    level: v.union(v.literal("hl"), v.literal("ol"), v.literal("fl"), v.literal("jc")),
    storage_id: v.string(),
    storage_format: v.union(
      v.literal("svg"),
      v.literal("png"),
      v.literal("glb"),
      v.literal("usdz"),
    ),
    eiraic_tier: v.optional(v.number()),
    meta: v.object({
      width: v.optional(v.number()),
      height: v.optional(v.number()),
      byte_size: v.optional(v.number()),
      sha256: v.optional(v.string()),
    }),
    created_at: v.number(),
  }).index("by_subject_mode", ["subject", "mode", "language"]),

  diagram_cache: defineTable({
    mode: v.string(),
    subject: v.string(),
    language: v.union(v.literal("en"), v.literal("ga")),
    level: v.optional(
      v.union(v.literal("hl"), v.literal("ol"), v.literal("fl"), v.literal("jc")),
    ),
    payload: v.any(),
    rendered_at: v.number(),
    stale_at: v.number(),
  }).index("by_mode_subject", ["mode", "subject", "language"]),

  badge_ledger: defineTable({
    student_id: v.string(),
    framework: v.string(),
    level: v.string(),
    subject: v.string(),
    competency_code: v.string(),
    competency_text_en: v.string(),
    competency_text_ga: v.optional(v.string()),
    eiraic_tier: v.number(),
    agent_issuer: v.string(),
    evidence_hash: v.string(),
    signature: v.string(),
    on_chain_anchor: v.optional(v.string()),
    anchor_date: v.optional(v.string()),
    date_earned: v.number(),
    eiraic_treasures_unlocked: v.optional(v.array(v.string())),
  }).index("by_student", ["student_id"]),

  // ─── UoG personal-archive tables (per 2026-08-23-uog-personal-archive-tertiary-modules-v1) ───
  // Consumed by convex/personalArchive.ts (chatOverMyArchive + getModuleDossier).
  // The actual data lives in LanceDB (the 4 personal_archive_* tables + student_transcripts);
  // these Convex tables mirror the per-module metadata for fast queries.
  personal_archive_artefacts: defineTable({
    module_code: v.string(),
    artefact_id: v.string(),
    artefact_type: v.string(),
    title: v.string(),
    url: v.optional(v.string()),
    page_count: v.optional(v.number()),
    language: v.optional(v.string()),
    metadata: v.optional(v.any()),
    created_at: v.number(),
  })
    .index("by_module_code", ["module_code"])
    .index("by_artefact_id", ["artefact_id"]),

  personal_archive_questions: defineTable({
    module_code: v.string(),
    question_id: v.string(),
    question_text: v.string(),
    marks: v.optional(v.number()),
    blooms_level: v.optional(v.string()),
    source_artefact_id: v.optional(v.string()),
    created_at: v.number(),
  })
    .index("by_module_code", ["module_code"])
    .index("by_question_id", ["question_id"]),

  personal_archive_topics: defineTable({
    module_code: v.string(),
    topic_id: v.string(),
    topic_title: v.string(),
    learning_outcome_code: v.optional(v.string()),
    weight: v.optional(v.number()),
    created_at: v.number(),
  })
    .index("by_module_code", ["module_code"])
    .index("by_topic_id", ["topic_id"]),

  personal_archive_reading_lists: defineTable({
    module_code: v.string(),
    reading_list_id: v.string(),
    title: v.string(),
    items: v.optional(v.array(v.any())),
    created_at: v.number(),
  })
    .index("by_module_code", ["module_code"])
    .index("by_reading_list_id", ["reading_list_id"]),

  personal_archive_code_cells: defineTable({
    module_code: v.string(),
    cell_id: v.string(),
    language: v.string(),
    code: v.string(),
    source_artefact_id: v.optional(v.string()),
    created_at: v.number(),
  })
    .index("by_module_code", ["module_code"])
    .index("by_cell_id", ["cell_id"]),

  personal_archive_lecture_notes: defineTable({
    module_code: v.string(),
    note_id: v.string(),
    title: v.string(),
    transcript: v.optional(v.string()),
    duration_seconds: v.optional(v.number()),
    recorded_at: v.optional(v.number()),
    created_at: v.number(),
  })
    .index("by_module_code", ["module_code"])
    .index("by_note_id", ["note_id"]),

  student_transcripts: defineTable({
    student_id: v.string(),
    module_code: v.string(),
    transcript_id: v.string(),
    grade: v.optional(v.string()),
    gpa: v.optional(v.number()),
    recorded_at: v.number(),
    created_at: v.number(),
  })
    .index("by_module_code", ["module_code"])
    .index("by_student", ["student_id"]),
});
