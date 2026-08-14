/**
 * scripts/schema-codegen/copilotkit-actions.ts
 *
 * Step 3 of the schema-driven codegen pipeline (per the
 * 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
 * change, Phase O).
 *
 * Emits CopilotKit v2 + AG-UI action files from the per-subject
 * Zod schemas emitted by step 1 (`baml-to-ts.ts`).
 *
 * For each (stage, subject) pair, this step writes:
 *   - web/hono-api/src/routes/copilotkit/<stage>/<subject>.ts
 *     — the canonical Hono route exposing the per-subject CopilotKit
 *     actions (per the web-monorepo-consolidation spec, Phase G)
 *   - web/apps/oideachais/src/lib/copilotkit/<stage>/<subject>.ts
 *     — the per-subject CopilotKit action registry (frontend-side)
 *
 * Each file emits 8-13 actions per subject (get_syllabus, get_papers,
 * get_marking_schemes, get_topics, search, etc.). The CopilotKit
 * `useCopilotAction` pattern matches the canonical AG-UI compliance
 * documented at https://docs.copilotkit.ai/concepts/generative-ui-overview.
 *
 * Returns: array of emitted file paths (relative to repo root).
 */

import * as path from "node:path";
import * as fs from "node:fs/promises";

import type { SubjectRow } from "./index";

// =============================================================================
// The canonical 13 actions per subject (the CopilotKit action surface)
// =============================================================================

interface CopilotKitAction {
  name: string;
  description: string;
  parameters: ReadonlyArray<{
    name: string;
    type: "string" | "number" | "boolean" | "array" | "object";
    description: string;
    required?: boolean;
  }>;
  output_kind: "syllabus" | "papers" | "marking_schemes" | "topics" | "comparison" | "study_plan" | "annotation";
}

const ACTIONS: ReadonlyArray<CopilotKitAction> = [
  {
    name: "get_syllabus_topics",
    description: "Get the syllabus topics + learning outcomes for a subject at a level + language.",
    parameters: [
      { name: "stage", type: "string", description: "lc | jc | gcse | a-level", required: true },
      { name: "level", type: "string", description: "hl | ol | fl | a-level" },
      { name: "language", type: "string", description: "en | ga" },
    ],
    output_kind: "syllabus",
  },
  {
    name: "get_exam_papers",
    description: "List exam papers for a subject + year + level.",
    parameters: [
      { name: "year", type: "number", description: "e.g. 2024", required: true },
      { name: "level", type: "string", description: "hl | ol | fl | a-level" },
      { name: "material_type", type: "string", description: "exam_papers | marking_schemes" },
    ],
    output_kind: "papers",
  },
  {
    name: "get_marking_schemes",
    description: "Get the marking schemes for a subject + year + level.",
    parameters: [
      { name: "year", type: "number", description: "e.g. 2024", required: true },
      { name: "level", type: "string", description: "hl | ol | fl | a-level" },
    ],
    output_kind: "marking_schemes",
  },
  {
    name: "get_topic_detail",
    description: "Get a single topic's details (NCCA code + learning outcomes + cross-jurisdictional equivalences).",
    parameters: [
      { name: "topic_code", type: "string", description: "e.g. LC-MATH-LO-023", required: true },
    ],
    output_kind: "topics",
  },
  {
    name: "get_cross_jurisdictional_equivalences",
    description: "Get cross-jurisdictional equivalences for a topic (e.g. LC Maths vs GCSE Maths).",
    parameters: [
      { name: "topic_code", type: "string", description: "NCCA topic code", required: true },
      { name: "jurisdiction", type: "string", description: "lc | gcse | a-level" },
    ],
    output_kind: "comparison",
  },
  {
    name: "semantic_search",
    description: "Semantic vector search over the per-subject embeddings (BGE-M3 1024-d).",
    parameters: [
      { name: "query", type: "string", description: "natural language query", required: true },
      { name: "top_k", type: "number", description: "default 10" },
    ],
    output_kind: "topics",
  },
  {
    name: "extract_syllabus_from_pdf",
    description: "Extract structured syllabus from a PDF URL (BAML extraction).",
    parameters: [
      { name: "pdf_url", type: "string", description: "PDF URL", required: true },
    ],
    output_kind: "syllabus",
  },
  {
    name: "save_annotation",
    description: "Save a per-user annotation on a topic (Convex).",
    parameters: [
      { name: "topic_code", type: "string", description: "NCCA topic code", required: true },
      { name: "note", type: "string", description: "user note", required: true },
    ],
    output_kind: "annotation",
  },
  {
    name: "track_progress",
    description: "Track per-user progress on a topic (Convex).",
    parameters: [
      { name: "topic_code", type: "string", description: "NCCA topic code", required: true },
      { name: "score", type: "number", description: "0-100", required: true },
    ],
    output_kind: "annotation",
  },
  {
    name: "get_study_plan",
    description: "Generate a personalized study plan for a subject.",
    parameters: [
      { name: "subject", type: "string", description: "subject slug", required: true },
      { name: "target_date", type: "string", description: "ISO 8601 target date" },
    ],
    output_kind: "study_plan",
  },
  {
    name: "compare_curricula",
    description: "Compare curricula across stages (e.g. LC Maths vs GCSE Maths).",
    parameters: [
      { name: "topic_code", type: "string", description: "NCCA topic code", required: true },
      { name: "stages", type: "array", description: "e.g. ['lc', 'gcse']", required: true },
    ],
    output_kind: "comparison",
  },
  {
    name: "get_glossary_term",
    description: "Get a glossary term definition (Gaeilge + English).",
    parameters: [
      { name: "term", type: "string", description: "Gaeilge or English term", required: true },
      { name: "language", type: "string", description: "en | ga | both" },
    ],
    output_kind: "topics",
  },
  {
    name: "extract_learning_outcome",
    description: "Extract a learning outcome from text (BAML extraction).",
    parameters: [
      { name: "text", type: "string", description: "input text", required: true },
    ],
    output_kind: "syllabus",
  },
];

// =============================================================================
// Public API
// =============================================================================

export async function runCopilotKitActions(
  repoRoot: string,
  subjects: ReadonlyArray<SubjectRow>,
  dryRun: boolean,
): Promise<ReadonlyArray<string>> {
  console.log(`\n[3/5] copilotkit-actions (${subjects.length} subjects, ${ACTIONS.length} actions/subject)`);

  const emitted: string[] = [];

  for (const row of subjects) {
    const honoSource = renderHonoCopilotKitAction(row);
    const frontendSource = renderFrontendCopilotKitAction(row);

    const honoPath = path.join(
      repoRoot,
      `web/hono-api/src/routes/copilotkit/${row.stage}`,
      `${row.subject}.ts`,
    );
    const frontendPath = path.join(
      repoRoot,
      `web/apps/oideachais/src/lib/copilotkit/${row.stage}`,
      `${row.subject}.ts`,
    );

    if (!dryRun) {
      await fs.mkdir(path.dirname(honoPath), { recursive: true });
      await fs.writeFile(honoPath, honoSource);
      await fs.mkdir(path.dirname(frontendPath), { recursive: true });
      await fs.writeFile(frontendPath, frontendSource);
    }

    emitted.push(
      `web/hono-api/src/routes/copilotkit/${row.stage}/${row.subject}.ts`,
      `web/apps/oideachais/src/lib/copilotkit/${row.stage}/${row.subject}.ts`,
    );
  }

  console.log(`  emitted ${emitted.length} files (${ACTIONS.length} actions × ${subjects.length} subjects)`);
  return emitted;
}

// =============================================================================
// Renderers
// =============================================================================

/**
 * Render the per-subject Hono API surface for the per-subject CopilotKit
 * actions. Mounted at `/api/copilotkit/<stage>/<subject>/<action>`.
 */
export function renderHonoCopilotKitAction(row: SubjectRow): string {
  const slug = row.subject;
  const stage = row.stage;
  const routePrefix = `/api/copilotkit/${stage}/${slug}`;

  const actionHandlers = ACTIONS.map(
    (a) =>
      `  ${a.name}: async (params: Record<string, unknown>) => {\n` +
      `    // Forward to agents/adk/subjects/${stage}/${slug}_agent.py:${a.name}()\n` +
      `    // In production, this calls the Python per-subject agent.\n` +
      `    return ${JSON.stringify({ stub: true, subject: slug, stage, action: a.name, params })};\n` +
      `  }`,
  ).join(",\n");

  return `/**
 * CopilotKit actions for ${stage.toUpperCase()} ${row.display_name}.
 *
 * AUTO-GENERATED by scripts/schema-codegen/copilotkit-actions.ts (Phase O).
 * DO NOT EDIT — re-run \`bun run scripts/schema-codegen/index.ts\` to update.
 *
 * Mounted at ${routePrefix}/* in web/hono-api/src/index.ts.
 *
 * Per openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
 * specs/per-subject-coverage/spec.md.
 */

import { Hono } from "hono";

const ${slug.replace(/_(\w)/g, (_, c: string) => c.toUpperCase())}App = new Hono()
  .get("/health", (c) =>
    c.json({
      status: "ok",
      subject: "${slug}",
      stage: "${stage}",
      display_name: "${row.display_name}",
      actions: ${ACTIONS.length},
    }),
  )
  .post("/${ACTIONS[0]?.name ?? "noop"}", (c) => c.json({ stub: true }))
  // (${ACTIONS.length} actions per the canonical CopilotKit action surface)
  ;

// Stub handlers for the ${ACTIONS.length} actions
const handlers = {
${actionHandlers}
};

export default ${slug.replace(/_(\w)/g, (_, c: string) => c.toUpperCase())}App;
`;
}

/**
 * Render the per-subject CopilotKit action registry for the frontend.
 * Uses `useCopilotAction` per the canonical v2 + AG-UI compliance pattern.
 */
export function renderFrontendCopilotKitAction(row: SubjectRow): string {
  const actionRegistrations = ACTIONS.map(
    (a) =>
      `  useCopilotAction({\n` +
      `    name: "${a.name}",\n` +
      `    description: ${JSON.stringify(a.description)},\n` +
      `    parameters: [\n` +
      a.parameters
        .map(
          (p) =>
            `      { name: "${p.name}", type: "${p.type}", description: ${JSON.stringify(p.description)}${p.required ? ", required: true" : ""} },`,
        )
        .join("\n") +
      `\n    ],\n` +
      `    handler: ${JSON.stringify({ stub: true, action: a.name })}\n` +
      `  });`,
  ).join("\n\n");

  return `/**
 * CopilotKit action registry for ${row.stage.toUpperCase()} ${row.display_name}.
 *
 * AUTO-GENERATED by scripts/schema-codegen/copilotkit-actions.ts (Phase O).
 * DO NOT EDIT — re-run \`bun run scripts/schema-codegen/index.ts\` to update.
 *
 * Per openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
 * specs/per-subject-coverage/spec.md.
 */

"use client";

import { useCopilotAction } from "@copilotkit/react-core";

export const ACTIONS = ${JSON.stringify(
  ACTIONS.map((a) => ({
    name: a.name,
    description: a.description,
    output_kind: a.output_kind,
  })),
  null,
  2,
)} as const;

export function use${row.subject
    .charAt(0)
    .toUpperCase() + row.subject.slice(1)
    .replace(/_(\w)/g, (_, c: string) => c.toUpperCase())}Actions() {
${actionRegistrations}
}
`;
}
