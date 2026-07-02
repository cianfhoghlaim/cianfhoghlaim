// apps/api/src/copilotkit/actions.ts — The 13 CopilotKit actions
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T5.11.
// The 13 actions are:
//   - 6 leaving-cert actions (per leaving-cert-2026)
//   - 4 diagram actions (NEW)
//   - 2 3D-asset actions (NEW)
//   - 1 cross-subject action (lookupKeyCompetency)
//
// Plus the lookupSCRCommentary action.

import { Hono } from "hono";

export const actions = new Hono();

const defineTool = (tool: {
  name: string;
  description: string;
  parameters: Array<{ name: string; type: string; description: string; required?: boolean }>;
  handler: (params: Record<string, unknown>) => Promise<unknown>;
}) => {
  return tool;
};

// ── 6 leaving-cert actions ────────────────────────────────────────────

export const getSyllabusTopics = defineTool({
  name: "getSyllabusTopics",
  description: "Get the Leaving Certificate syllabus topics, learning outcomes, and weighting for a subject.",
  parameters: [
    { name: "subject", type: "string", description: "Subject slug (mathematics, irish, biology, french, history, business, construction-studies)", required: true },
    { name: "level", type: "string", description: "hl | ol | fl", required: false },
  ],
  handler: async (params) => {
    // TODO: call cianfhoghlaim/api leavingCert.getSyllabus
    return {
      subject: params.subject,
      level: params.level ?? "hl",
      topics: [],
    };
  },
});

export const listExamMaterials = defineTool({
  name: "listExamMaterials",
  description: "List exam materials for subject/year/level",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "year", type: "number", required: true },
    { name: "level", type: "string", required: false },
    { name: "materialType", type: "string", description: "exam_papers | marking_schemes", required: false },
  ],
  handler: async (_params) => [],
});

export const getMarkingSchemeSummary = defineTool({
  name: "getMarkingSchemeSummary",
  description: "Canonical rubric + recent years for a subject",
  parameters: [
    { name: "subject", type: "string", required: true },
  ],
  handler: async (_params) => ({}),
});

export const getTopicPrioritisation = defineTool({
  name: "getTopicPrioritisation",
  description: "Get the topic prioritisation ranked by marks per hour of study",
  parameters: [
    { name: "subject", type: "string", required: true },
  ],
  handler: async (_params) => ({}),
});

export const getExamLayoutTips = defineTool({
  name: "getExamLayoutTips",
  description: "Get exam layout tips for a Leaving Cert subject (paper structure, time per question, common traps, marker expectations)",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "level", type: "string", required: false },
  ],
  handler: async (_params) => ({ subject: _params.subject, tips: [] }),
});

export const openPdf = defineTool({
  name: "openPdf",
  description: "Get a signed R2 URL for the original exam paper, marking scheme, or syllabus PDF",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "type", type: "string", description: "syllabus | exam-paper | marking-scheme", required: true },
    { name: "year", type: "number", required: true },
    { name: "paper", type: "string", description: "paper-1 | paper-2 | paper-1-f", required: false },
  ],
  handler: async (_params) => ({ url: "https://r2.cianfhoghlaim.ie/placeholder.pdf" }),
});

// ── 4 diagram actions ────────────────────────────────────────────────

export const generateConceptMap = defineTool({
  name: "generateConceptMap",
  description: "Generate a concept-map diagram for a Leaving Cert subject (5 NCCA Key Competencies as root nodes + per-subject LOs as children)",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "language", type: "string", description: "en | ga", required: false },
  ],
  handler: async (params) => {
    // TODO: call cianfhoghlaim/api diagrams.renderConceptMap
    return {
      mode: "concept-map",
      subject: params.subject,
      language: params.language ?? "en",
      payload: null,
    };
  },
});

export const generateTopicHeatmap = defineTool({
  name: "generateTopicHeatmap",
  description: "Generate a topic-frequency heatmap diagram for a Leaving Cert subject",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "yearFrom", type: "number", required: false },
    { name: "yearTo", type: "number", required: false },
  ],
  handler: async (_params) => ({ mode: "topic-heatmap", subject: _params.subject, payload: null }),
});

export const generatePCLMFlow = defineTool({
  name: "generatePCLMFlow",
  description: "Generate a PCLM (Partial Credit, Logical Marking) flow diagram for a Leaving Cert subject's marking scheme",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "paper", type: "string", required: true },
    { name: "year", type: "number", required: true },
  ],
  handler: async (_params) => ({ mode: "pclm-flow", subject: _params.subject, payload: null }),
});

export const generateQuestionSankey = defineTool({
  name: "generateQuestionSankey",
  description: "Generate a Question → Topic → Difficulty → Year Sankey diagram",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "yearFrom", type: "number", required: false },
    { name: "yearTo", type: "number", required: false },
  ],
  handler: async (_params) => ({ mode: "question-sankey", subject: _params.subject, payload: null }),
});

// ── 2 3D-asset actions ───────────────────────────────────────────────

export const generate3DAsset = defineTool({
  name: "generate3DAsset",
  description: "Generate a 3D mesh asset (via TRELLIS.2 + SAM-3D-Objects) for a Leaving Cert subject",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "prompt", type: "string", required: true },
    { name: "eiraicTier", type: "number", description: "1-13", required: false },
  ],
  handler: async (params) => {
    // TODO: call cianfhoghlaim/api assets.generate3D
    return {
      status: "queued",
      subject: params.subject,
      prompt: params.prompt,
      estimated_minutes: 8,
    };
  },
});

export const listAssets = defineTool({
  name: "listAssets",
  description: "List the 3D + 2D assets for a Leaving Cert subject",
  parameters: [
    { name: "subject", type: "string", required: true },
    { name: "format", type: "string", description: "all | 3d-mesh | 2d-sprite", required: false },
  ],
  handler: async (_params) => ({ assets: [] }),
});

// ── 1 cross-subject action ────────────────────────────────────────────

export const lookupKeyCompetency = defineTool({
  name: "lookupKeyCompetency",
  description: "Look up one of the 5 NCCA Key Competencies (Information Processing, Communicating, Working with Others, Personal Effectiveness, Critical & Creative Thinking)",
  parameters: [
    { name: "competency", type: "string", description: "One of: information-processing, communicating, working-with-others, personal-effectiveness, critical-creative-thinking", required: true },
  ],
  handler: async (params) => {
    return {
      competency: params.competency,
      // The full details are in cianfhoghlaim/tuatha/agents/cross_subject_agent.py
    };
  },
});

// ── 1 SCR commentary action ────────────────────────────────────────────

export const lookupSCRCommentary = defineTool({
  name: "lookupSCRCommentary",
  description: "Look up the State Examinations Commission (SEC) Chief Examiner commentary for a Leaving Cert subject",
  parameters: [
    { name: "subject", type: "string", required: true },
  ],
  handler: async (_params) => ({ commentary: null }),
});

// ── 13 actions total (6 leaving-cert + 4 diagram + 2 3D-asset + 1 cross-subject) ──
// Plus the 14th (lookupSCRCommentary) for the Practice page "Exam Layout Tips" section.

export const ALL_ACTIONS = [
  getSyllabusTopics,
  listExamMaterials,
  getMarkingSchemeSummary,
  getTopicPrioritisation,
  getExamLayoutTips,
  openPdf,
  generateConceptMap,
  generateTopicHeatmap,
  generatePCLMFlow,
  generateQuestionSankey,
  generate3DAsset,
  listAssets,
  lookupKeyCompetency,
  lookupSCRCommentary,
];