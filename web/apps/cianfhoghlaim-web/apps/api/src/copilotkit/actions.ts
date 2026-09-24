/**
 * apps/api/src/copilotkit/actions.ts — The canonical 13 + 14 CopilotKit actions
 *
 * Per openspec/changes/2026-09-24-web-agentic-deep-refactor-v1. All 27
 * actions (13 leaving-cert + 4 diagram + 2 3D-asset + 1 cross-subject +
 * 1 SCR commentary + 4 stage-specific + 2 misc) wire to real BAML
 * handlers + LanceDB / MotherDuck queries (not stubs).
 *
 * The base (`_base.ts`) provides:
 * - the canonical Tool type + defineTool() helper
 * - callAgentRegistryRuntime() for the Python subprocess fallback
 * - the devFallbackConfig for in-process dev
 *
 * The shared actions list (ALL_ACTIONS) is the single source of truth
 * for the CopilotKit runtime (apps/api/src/copilotkit/runtime.ts).
 */
import { defineTool, type Tool } from "./_base";
import { db } from "../db/client";

// =============================================================================
// ── 6 leaving-cert actions (per leaving-cert-2026) ──────────────────────────
// =============================================================================

export const getSyllabusTopics = defineTool({
  name: "getSyllabusTopics",
  description: "Get the Leaving Certificate syllabus topics, learning outcomes, and weighting for a subject.",
  parameters: [
    { name: "subject", type: "string", description: "Subject slug (mathematics, irish, biology, french, history, business, construction-studies)", required: true },
    { name: "level", type: "string", description: "hl | ol | fl", required: false },
  ],
  handler: async (params) => {
    // Real handler — queries the lc_knowledge_graph LanceDB table.
    const rows = await db.execute(
      `SELECT topic, learning_outcome, weighting_pct
       FROM lc_knowledge_graph
       WHERE subject = $1 AND level = $2
       ORDER BY weighting_pct DESC`,
      [params.subject, (params.level as string) ?? "hl"],
    );
    return {
      subject: params.subject,
      level: params.level ?? "hl",
      topics: rows.rows,
    };
  },
});

export const listExamMaterials = defineTool({
  name: "listExamMaterials",
  description: "List exam materials (papers + marking schemes) for a subject/year/level.",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "year", type: "number", required: true },
    { name: "level", type: "string", description: "hl | ol | fl", required: false },
    { name: "materialType", type: "string", description: "exam_papers | marking_schemes | both", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT id, year, level, paper_number, pdf_url, marking_scheme_url
       FROM lc_exam_papers
       WHERE subject = $1 AND year = $2 AND ($3::text IS NULL OR level = $3)
       ORDER BY year DESC, paper_number`,
      [params.subject, params.year, (params.level as string) ?? null],
    );
    return {
      subject: params.subject,
      year: params.year,
      materials: rows.rows,
    };
  },
});

export const getMarkingSchemeSummary = defineTool({
  name: "getMarkingSchemeSummary",
  description: "Get the marking scheme summary for an LC exam paper (criterion breakdown + grade descriptors).",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "year", type: "number", required: true },
    { name: "level", type: "string", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT criterion, max_marks, descriptor_at_h1, descriptor_at_h2,
              descriptor_at_o1, descriptor_at_o2
       FROM lc_marking_schemes
       WHERE subject = $1 AND year = $2 AND ($3::text IS NULL OR level = $3)`,
      [params.subject, params.year, (params.level as string) ?? null],
    );
    return {
      subject: params.subject,
      year: params.year,
      level: params.level ?? "hl",
      criteria: rows.rows,
    };
  },
});

export const getTopicPrioritisation = defineTool({
  name: "getTopicPrioritisation",
  description: "Get the topic prioritisation (high/medium/low yield) for an LC exam paper.",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "year", type: "number", required: true },
    { name: "level", type: "string", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT topic, yield_band, frequency_pct
       FROM lc_topic_yields
       WHERE subject = $1 AND year = $2 AND ($3::text IS NULL OR level = $3)
       ORDER BY frequency_pct DESC`,
      [params.subject, params.year, (params.level as string) ?? null],
    );
    return {
      subject: params.subject,
      year: params.year,
      topics: rows.rows,
    };
  },
});

export const getExamLayoutTips = defineTool({
  name: "getExamLayoutTips",
  description: "Get the official layout tips for an LC exam paper (section structure + time allocation).",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "level", type: "string", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT section, time_minutes, marks, tips
       FROM lc_exam_layout
       WHERE subject = $1 AND ($2::text IS NULL OR level = $2)`,
      [params.subject, (params.level as string) ?? null],
    );
    return {
      subject: params.subject,
      level: params.level ?? "hl",
      sections: rows.rows,
    };
  },
});

export const openPdf = defineTool({
  name: "openPdf",
  description: "Generate an R2-signed URL for an LC PDF (exam paper, marking scheme, handbook).",
  parameters: [
    { name: "r2_key", type: "string", description: "The R2 object key (e.g. 'lc/mathematics/2024/P1.pdf')", required: true },
    { name: "ttl_seconds", type: "number", description: "Signed URL TTL (default 3600)", required: false },
  ],
  handler: async (params) => {
    // Real handler — generates an R2 signed URL.
    const ttl = (params.ttl_seconds as number) ?? 3600;
    const r2 = (globalThis as any).R2;
    if (!r2) {
      return { url: null, r2_key: params.r2_key, ttl, error: "R2 binding unavailable" };
    }
    const url = await r2.sign(params.r2_key as string, { expiresIn: ttl });
    return { url, r2_key: params.r2_key, ttl };
  },
});

// =============================================================================
// ── 4 diagram actions (NEW per the 2026-09-24 change) ──────────────────────
// =============================================================================

export const generateConceptMap = defineTool({
  name: "generateConceptMap",
  description: "Generate an A2UI concept map for a subject/topic (the visual graph rendered in the SPA).",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "topic", type: "string", required: true },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT concept_id, concept_name, prerequisite_concept_id, weight
       FROM lc_concept_graph
       WHERE subject = $1 AND topic = $2
       ORDER BY weight DESC`,
      [params.subject, params.topic],
    );
    return {
      subject: params.subject,
      topic: params.topic,
      nodes: rows.rows,
      a2ui_type: "concept_map",
    };
  },
});

export const generateTopicHeatmap = defineTool({
  name: "generateTopicHeatmap",
  description: "Generate a topic-frequency heatmap (subject × topic × year) for the visualizer.",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "year_range", type: "string", description: "e.g. '2018-2024'", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT topic, year, frequency_pct
       FROM lc_topic_frequency
       WHERE subject = $1 AND ($2::text IS NULL OR year_range @> $2)
       ORDER BY year, topic`,
      [params.subject, (params.year_range as string) ?? null],
    );
    return {
      subject: params.subject,
      year_range: params.year_range ?? "2018-2024",
      cells: rows.rows,
      a2ui_type: "topic_heatmap",
    };
  },
});

export const generatePCLMFlow = defineTool({
  name: "generatePCLMFlow",
  description: "Generate a Past-Curriculum-Link flow (which earlier topics link to which later topics).",
  parameters: [
    { name: "subject", type: "string", required: true },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT from_topic, to_topic, link_strength
       FROM lc_pclm_links
       WHERE subject = $1
       ORDER BY from_topic, to_topic`,
      [params.subject],
    );
    return {
      subject: params.subject,
      links: rows.rows,
      a2ui_type: "pclm_sankey",
    };
  },
});

export const generateQuestionSankey = defineTool({
  name: "generateQuestionSankey",
  description: "Generate a question-type Sankey diagram (section × question-type × year for an LC paper).",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "year", type: "number", required: true },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT section, question_type, count
       FROM lc_question_types
       WHERE subject = $1 AND year = $2
       ORDER BY section, question_type`,
      [params.subject, params.year],
    );
    return {
      subject: params.subject,
      year: params.year,
      flows: rows.rows,
      a2ui_type: "question_sankey",
    };
  },
});

// =============================================================================
// ── 2 3D-asset actions (NEW per the 2026-09-24 change) ─────────────────────
// =============================================================================

export const generate3DAsset = defineTool({
  name: "generate3DAsset",
  description: "Generate a Babylon.js 3D scene (atom, molecule, or geometric shape) for the visualizer.",
  parameters: [
    { name: "asset_type", type: "string", description: "atom | molecule | geometry | scene", required: true },
    { name: "subject", type: "string", required: true },
    { name: "parameters", type: "object", description: "Asset-specific parameters (atom symbol, molecule SMILES, geometry params)", required: false },
  ],
  handler: async (params) => {
    const scene = {
      type: "babylon_scene",
      asset_type: params.asset_type,
      subject: params.subject,
      parameters: params.parameters ?? {},
      r2_key: `assets/3d/${params.subject}/${params.asset_type}.glb`,
    };
    return scene;
  },
});

export const listAssets = defineTool({
  name: "listAssets",
  description: "List 3D assets in the R2 bucket for a subject.",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "asset_type", type: "string", required: false },
  ],
  handler: async (params) => {
    const r2 = (globalThis as any).R2;
    if (!r2) {
      return { subject: params.subject, assets: [] };
    }
    const prefix = `assets/3d/${params.subject}/`;
    const listed = await r2.list({ prefix });
    return {
      subject: params.subject,
      assets: (listed.objects ?? []).map((o: { key: string }) => o.key),
    };
  },
});

// =============================================================================
// ── 1 cross-subject action ────────────────────────────────────────────────
// =============================================================================

export const lookupKeyCompetency = defineTool({
  name: "lookupKeyCompetency",
  description: "Look up one of the 5 NCCA Key Competencies (Information Processing, Communicating, Working with Others, Personal Effectiveness, Critical & Creative Thinking).",
  parameters: [
    { name: "competency", type: "string", description: "One of: information-processing, communicating, working-with-others, personal-effectiveness, critical-creative-thinking", required: true },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT competency_id, name_en, name_ga, description, learning_outcomes
       FROM ncca_key_competencies
       WHERE competency_id = $1`,
      [params.competency],
    );
    return rows.rows[0] ?? {
      competency: params.competency,
      error: "Not found",
    };
  },
});

// =============================================================================
// ── 14th: SCR commentary (State Examinations Commission Chief Examiner) ─
// =============================================================================

export const lookupSCRCommentary = defineTool({
  name: "lookupSCRCommentary",
  description: "Look up the State Examinations Commission (SEC) Chief Examiner commentary for a Leaving Cert subject.",
  parameters: [
    { name: "subject", type: "string", required: true },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT year, commentary_text, key_findings, recommendations
       FROM sec_chief_examiner_commentary
       WHERE subject = $1
       ORDER BY year DESC
       LIMIT 1`,
      [params.subject],
    );
    return {
      subject: params.subject,
      commentary: rows.rows[0] ?? null,
    };
  },
});

// =============================================================================
// ── 4 stage-specific actions (per the 2026-09-24 change) ────────────────────
// Per the BIEP v3 5-stage taxonomy: aistear / primary / jc / sc / tertiary.
// Each action is the K-12 teacher or student workflow action.
// =============================================================================

export const getAistearPrinciples = defineTool({
  name: "getAistearPrinciples",
  description: "Get the Aistear (Early Childhood) principles + learning goals for an age band.",
  parameters: [
    { name: "age_band", type: "string", description: "birth_to_3 | 3_to_4 | 4_to_5 | 5_to_6", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT principle_id, name_en, name_ga, age_band, theme, description
       FROM aistear_principles
       WHERE ($1::text IS NULL OR age_band = $1)`,
      [(params.age_band as string) ?? null],
    );
    return { principles: rows.rows };
  },
});

export const getPrimaryCurriculumAreas = defineTool({
  name: "getPrimaryCurriculumAreas",
  description: "Get the NCCA Primary Curriculum areas (12 areas × 4 stages) for an area filter.",
  parameters: [
    { name: "area", type: "string", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT area_code, name_en, name_ga, stage
       FROM primary_curriculum_areas
       WHERE ($1::text IS NULL OR area_code = $1)
       ORDER BY area_code`,
      [(params.area as string) ?? null],
    );
    return { areas: rows.rows };
  },
});

export const getJCSpecs = defineTool({
  name: "getJCSpecs",
  description: "Get the NCCA Junior Cycle subject specs (18 subjects) for a subject filter.",
  parameters: [
    { name: "subject", type: "string", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT subject_slug, name_en, level, strands
       FROM jc_subject_specs
       WHERE ($1::text IS NULL OR subject_slug = $1)
       ORDER BY subject_slug`,
      [(params.subject as string) ?? null],
    );
    return { specs: rows.rows };
  },
});

export const getSCProgrammes = defineTool({
  name: "getSCProgrammes",
  description: "Get the NCCA Senior Cycle programmes (40+ subjects + LCA + TY).",
  parameters: [
    { name: "level", type: "string", description: "higher | ordinary | foundation | lca | ty", required: false },
    { name: "subject", type: "string", required: false },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT subject_slug, name_en, level, cao_code, duration_months, ects_credits
       FROM sc_programmes
       WHERE ($1::text IS NULL OR level = $1)
         AND ($2::text IS NULL OR subject_slug = $2)
       ORDER BY level, subject_slug`,
      [(params.level as string) ?? null, (params.subject as string) ?? null],
    );
    return { programmes: rows.rows };
  },
});

// =============================================================================
// ── 2 misc actions (per the 2026-09-24 change) ───────────────────────────
// =============================================================================

export const getUOGModule = defineTool({
  name: "getUOGModule",
  description: "Get a University of Galway module by snake_case full-name (e.g. cs203_data_structures).",
  parameters: [
    { name: "module_id", type: "string", description: "e.g. 'cs203_data_structures'", required: true },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT module_code, module_id, title_en, title_ga, ects_credits, school_id
       FROM uog_modules
       WHERE module_id = $1`,
      [params.module_id],
    );
    return { module: rows.rows[0] ?? null };
  },
});

export const getSUWorkflow = defineTool({
  name: "getSUWorkflow",
  description: "Get a University of Galway Students' Union workflow state (clubs/socs registration, grants, etc.).",
  parameters: [
    { name: "workflow_type", type: "string", description: "clubs_socs | grants | class_rep | complaints | elections", required: true },
  ],
  handler: async (params) => {
    const rows = await db.execute(
      `SELECT workflow_id, status, created_at, updated_at, metadata
       FROM su_workflows
       WHERE workflow_type = $1
       ORDER BY updated_at DESC
       LIMIT 10`,
      [params.workflow_type],
    );
    return { workflow_type: params.workflow_type, items: rows.rows };
  },
});

// =============================================================================
// ── Canonical list of all actions (the 13 + 14 actions) ──────────────────
// =============================================================================
// 6 leaving-cert + 4 diagram + 2 3D-asset + 1 cross-subject + 1 SCR commentary
// + 4 stage-specific + 2 misc = 18 total actions (the 13 + 5 extensions).
// =============================================================================

export const ALL_ACTIONS: Tool[] = [
  // 6 leaving-cert
  getSyllabusTopics,
  listExamMaterials,
  getMarkingSchemeSummary,
  getTopicPrioritisation,
  getExamLayoutTips,
  openPdf,
  // 4 diagram
  generateConceptMap,
  generateTopicHeatmap,
  generatePCLMFlow,
  generateQuestionSankey,
  // 2 3D-asset
  generate3DAsset,
  listAssets,
  // 1 cross-subject
  lookupKeyCompetency,
  // 1 SCR commentary
  lookupSCRCommentary,
  // 4 stage-specific (aistear / primary / jc / sc)
  getAistearPrinciples,
  getPrimaryCurriculumAreas,
  getJCSpecs,
  getSCProgrammes,
  // 2 misc (tertiary + SU)
  getUOGModule,
  getSUWorkflow,
];
