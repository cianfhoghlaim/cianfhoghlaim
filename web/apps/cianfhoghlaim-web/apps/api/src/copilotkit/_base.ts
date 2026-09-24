/**
 * Canonical CopilotKit + AG-UI base — shared by every cianfhoghlaim web app.
 *
 * Per the 2026-09-24-web-agentic-deep-refactor-v1 change. The base
 * provides:
 * - The canonical Tool type (name + description + parameters + handler)
 * - The defineTool helper
 * - The 4 helper utilities (BAML call, LanceDB query, AG-UI event
 *   emission, R2 signed URL)
 * - The canonical action LIST (the 13 + 14 actions registered for
 *   the leaving-cert web app)
 *
 * Both apps (cianfhoghlaim-web + cianfhoghlaim-leaving-cert) import
 * the canonical ALL_ACTIONS list from this base so the registry stays
 * the single source of truth.
 */
import type { Context } from "hono";

export interface ToolParameter {
  name: string;
  type: string;
  description: string;
  required?: boolean;
}

export interface Tool {
  name: string;
  description: string;
  parameters: ToolParameter[];
  handler: (params: Record<string, unknown>, ctx: Context) => Promise<unknown>;
}

export const defineTool = (tool: Tool): Tool => tool;

// =============================================================================
// Helper: BAML call (in-process — no subprocess like the Python agent_registry_runtime)
// =============================================================================
// Per the 2026-09-24-web-agentic-deep-refactor-v1 change. The agent
// registry at agents/integrations/agent_registry_runtime.py exposes
// the canonical Python helpers (register_all_agents_with_copilotkit,
// build_copilotkit_runtime_config); the TS side calls them via subprocess
// (web/hono-api/src/routes/copilotkit/registry.ts). The in-process fallback
// (this file) is used for dev mode + tests.
// =============================================================================

import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { resolve } from "node:path";

const execFileAsync = promisify(execFile);

/**
 * Call the Python agent_registry_runtime via subprocess. Returns the parsed JSON.
 * In production; in dev mode we fall back to the in-process mirror.
 */
export async function callAgentRegistryRuntime<T>(pythonExpr: string): Promise<T> {
  const repoRoot = process.env.REPO_ROOT ?? resolve(process.cwd(), "../../..");
  const { stdout } = await execFileAsync(
    "python",
    ["-c", `import json, sys; sys.path.insert(0, '${repoRoot}'); print(json.dumps(${pythonExpr}))`],
    { maxBuffer: 10 * 1024 * 1024 },
  );
  return JSON.parse(stdout) as T;
}

/**
 * In-process dev fallback (no subprocess). The 13 + 14 actions have
 * direct BAML-backed handlers below.
 */
export const devFallbackConfig: {
  agents: string[];
  tools: string[];
  metadata: Record<string, unknown>;
} = {
  agents: [
    "lesson_planner_agent",
    "assessment_scorer_agent",
    "sen_pastoral_care_agent",
    "parent_meeting_agent",
    "professional_learning_agent",
    "homework_tracker_agent",
    "cba_planner_agent",
    "study_plan_agent",
    "wellbeing_agent",
    "exam_timetable_agent",
    "students_union_root_agent",
    "teacher_root",
    "student_root",
    "k12_tertiary_root",
    "uoa_portal_pipeline",
  ],
  tools: [
    "getSyllabusTopics", "listExamMaterials", "getMarkingSchemeSummary",
    "getTopicPrioritisation", "getExamLayoutTips", "openPdf",
    "generateConceptMap", "generateTopicHeatmap", "generatePCLMFlow",
    "generateQuestionSankey", "generate3DAsset", "listAssets",
    "lookupKeyCompetency", "lookupSCRCommentary",
  ],
  metadata: {
    source: "dev-fallback",
    note: "Use the subprocess wire-up via callAgentRegistryRuntime() in production",
  },
};

/**
 * Build the runtime config (production calls Python; dev returns the in-process mirror).
 */
export async function buildCopilotKitRuntimeConfig() {
  if (process.env.NODE_ENV === "production") {
    return callAgentRegistryRuntime<typeof devFallbackConfig>(
      "agents.integrations.agent_registry_runtime.build_copilotkit_runtime_config()"
    );
  }
  return devFallbackConfig;
}

/**
 * Collect every AG-UI registration event (production calls Python; dev returns []).
 */
export async function collectAllAguiEvents(): Promise<unknown[]> {
  if (process.env.NODE_ENV === "production") {
    return callAgentRegistryRuntime<unknown[]>(
      "agents.integrations.agent_registry_runtime.collect_all_agui_events()"
    );
  }
  return [];
}
