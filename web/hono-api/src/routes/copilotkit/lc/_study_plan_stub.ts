/**
 * Study plan stub dispatcher for LC subjects.
 *
 * Phase 16 + 17.4 (re-applied 2026-09-14, Plan 16-29 recovery):
 *  - Phase 16: `buildSubjectActionHandler(subject, stage, action, ...)` —
 *    a thin dispatcher that calls the canonical Python per-subject agent
 *    via `Bun.spawn`. Falls back to a stub response if Python is
 *    unavailable or the agent raises.
 *  - Phase 17.4: `buildSubjectSubApp(subject, displayName, stage, ...)`
 *    — a Hono `Hono` sub-app for one LC subject, exposing a health
 *    check, a generic prompt endpoint, and the canonical 7-tab BIEP
 *    layout (matching the lost `40_leaving_cert_subject_panel.py`
 *    marimo notebook).
 *
 * This file is the canonical home for both factories. They replace
 * the lost commit's `web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts`
 * (the original Phase 16+17 work) and are SAFE to apply — they do not
 * touch the 273 broken BAML files (those are deferred to Phase 21).
 *
 * Mounted from `web/hono-api/src/index.ts` via:
 *
 *     for (const subj of LC_SUBJECTS) {
 *       const app = buildSubjectSubApp(subj.slug, subj.displayName, "lc", 24, "en");
 *       hono.route(`/api/copilotkit/lc/${subj.slug}`, app);
 *     }
 */

import { Hono } from "hono";

// ---------------------------------------------------------------------------
// Phase 16: buildSubjectActionHandler
// ---------------------------------------------------------------------------

const PYTHON_AGENT_ENTRYPOINT = "agents/adk/subjects/lc/planner.py";

export interface ActionHandlerResult {
  /** Whether the response came from Python (true) or the stub fallback (false). */
  from_python: boolean;
  /** The canonical subject slug (e.g. "mathematics"). */
  subject: string;
  /** The canonical stage slug ("lc", "jc", "gcse", "a-level"). */
  stage: string;
  /** The action name (e.g. "get_study_plan"). */
  action: string;
  /** The duration in weeks (for `get_study_plan`); ignored otherwise. */
  duration_weeks: number;
  /** The language code ("en" or "ga"). */
  language: string;
  /** The original request params, for downstream debugging. */
  params: Record<string, unknown>;
  /** The agent's JSON response, or the stub response. */
  response: Record<string, unknown>;
}

export interface BuildSubjectActionHandlerOptions {
  /** Subprocess timeout in milliseconds. Default: 8000. */
  timeoutMs?: number;
  /** Skip the Python call entirely (force stub). Default: false. */
  forceStub?: boolean;
}

/**
 * Phase 16: build the canonical `action` handler for one (subject, stage) pair.
 *
 * Spawns `agents/adk/subjects/lc/planner.py` via `Bun.spawn` and passes
 * the (subject, stage, action, duration_weeks, language, params) tuple
 * as JSON on stdin. Falls back to a deterministic stub response if the
 * Python interpreter is unavailable, the spawn fails, or the process
 * exceeds the timeout.
 *
 * The Python planner is expected to expose `buildSubjectActionHandler`
 * (the canonical entrypoint per Phase 16). In environments where the
 * planner is not yet implemented, the stub response keeps the Hono
 * routes healthy.
 */
export function buildSubjectActionHandler(
  subject: string,
  stage: string,
  action: string,
  durationWeeks: number,
  language: string,
): (params: Record<string, unknown>) => Promise<ActionHandlerResult> {
  return async (params: Record<string, unknown>): Promise<ActionHandlerResult> => {
    const opts = (params.__handler_options__ as BuildSubjectActionHandlerOptions) || {};
    const timeoutMs = opts.timeoutMs ?? 8000;
    const forceStub = opts.forceStub ?? false;

    if (forceStub || typeof Bun === "undefined" || !Bun.spawn) {
      return stubResponse(subject, stage, action, durationWeeks, language, params);
    }

    const payload = JSON.stringify({
      subject,
      stage,
      action,
      duration_weeks: durationWeeks,
      language,
      params,
    });

    try {
      const proc = Bun.spawn(
        ["python3", PYTHON_AGENT_ENTRYPOINT, action, subject, stage, language, String(durationWeeks)],
        {
          stdin: new Blob([payload]),
          stdout: "pipe",
          stderr: "pipe",
          env: { ...process.env, PYTHONUNBUFFERED: "1" },
        },
      );

      const timer = setTimeout(() => {
        try {
          proc.kill();
        } catch {
          // already exited
        }
      }, timeoutMs);

      const stdout = await new Response(proc.stdout).text();
      const stderr = await new Response(proc.stderr).text();
      await proc.exited;
      clearTimeout(timer);

      if (proc.exitCode !== 0) {
        return {
          ...stubResponse(subject, stage, action, durationWeeks, language, params),
          from_python: false,
          response: {
            stub: true,
            reason: "python_nonzero_exit",
            exit_code: proc.exitCode,
            stderr_tail: stderr.slice(-500),
          },
        };
      }

      try {
        return {
          from_python: true,
          subject,
          stage,
          action,
          duration_weeks: durationWeeks,
          language,
          params,
          response: JSON.parse(stdout) as Record<string, unknown>,
        };
      } catch {
        return {
          from_python: true,
          subject,
          stage,
          action,
          duration_weeks: durationWeeks,
          language,
          params,
          response: { raw: stdout },
        };
      }
    } catch (err) {
      return {
        ...stubResponse(subject, stage, action, durationWeeks, language, params),
        from_python: false,
        response: {
          stub: true,
          reason: "spawn_failed",
          error: String(err),
        },
      };
    }
  };
}

function stubResponse(
  subject: string,
  stage: string,
  action: string,
  durationWeeks: number,
  language: string,
  params: Record<string, unknown>,
): ActionHandlerResult {
  return {
    from_python: false,
    subject,
    stage,
    action,
    duration_weeks: durationWeeks,
    language,
    params,
    response: {
      stub: true,
      reason: "python_unavailable",
      subject,
      stage,
      action,
      duration_weeks: durationWeeks,
      language,
      params,
    },
  };
}

// ---------------------------------------------------------------------------
// Phase 17.4: buildSubjectSubApp
// ---------------------------------------------------------------------------

export interface BuildSubjectSubAppOptions {
  /** Optional list of action names to expose on the sub-app. Default: all 13. */
  actions?: readonly string[];
  /** Optional seed for the BIEP tab ids. Default: 7 tabs. */
  biepTabs?: readonly BiepTabSpec[];
}

export interface BiepTabSpec {
  /** Stable tab id (e.g. "overview", "syllabus"). */
  id: string;
  /** Human-readable display name. */
  label: string;
  /** Marimo-equivalent notebook tab title (lost `40_leaving_cert_subject_panel.py`). */
  notebookTitle: string;
}

export const DEFAULT_BIEP_TABS: readonly BiepTabSpec[] = [
  { id: "overview", label: "Overview", notebookTitle: "0_overview" },
  { id: "syllabus", label: "Syllabus Topics", notebookTitle: "1_syllabus_topics" },
  { id: "exam_papers", label: "Exam Papers", notebookTitle: "2_exam_papers" },
  { id: "marking_schemes", label: "Marking Schemes", notebookTitle: "3_marking_schemes" },
  { id: "study_plan", label: "Study Plan", notebookTitle: "4_study_plan" },
  { id: "glossary", label: "Glossary", notebookTitle: "5_glossary" },
  { id: "equivalences", label: "Cross-Jurisdiction Equivalences", notebookTitle: "6_equivalences" },
];

export const DEFAULT_LC_ACTIONS: readonly string[] = [
  "get_syllabus_topics",
  "get_exam_papers",
  "get_marking_schemes",
  "get_topic_detail",
  "get_cross_jurisdictional_equivalences",
  "semantic_search",
  "extract_syllabus_from_pdf",
  "save_annotation",
  "track_progress",
  "get_study_plan",
  "compare_curricula",
  "get_glossary_term",
  "extract_learning_outcome",
];

/**
 * Phase 17.4: build a Hono sub-app for one LC subject.
 *
 * Layout (matches the lost `40_leaving_cert_subject_panel.py` marimo
 * notebook + the per-subject CopilotKit action surface):
 *
 *   GET  /health        → liveness probe
 *   POST /prompt        → generic prompt (delegates to `get_study_plan`)
 *   GET  /biep          → canonical 7-tab BIEP layout (metadata only)
 *   POST /actions/<name> → canonical 13 CopilotKit actions
 *
 * The factory is intentionally minimal — the per-action stub handlers
 * are delegated to `buildSubjectActionHandler` so a single Python
 * subprocess can answer every action.
 */
export function buildSubjectSubApp(
  subject: string,
  displayName: string,
  stage: string,
  durationWeeks: number,
  language: string,
  options: BuildSubjectSubAppOptions = {},
): Hono {
  const actions = options.actions ?? DEFAULT_LC_ACTIONS;
  const biepTabs = options.biepTabs ?? DEFAULT_BIEP_TABS;

  const subApp = new Hono();

  subApp.get("/health", (c) =>
    c.json({
      status: "ok",
      subject,
      stage,
      display_name: displayName,
      language,
      duration_weeks: durationWeeks,
      actions: actions.length,
      biep_tabs: biepTabs.length,
    }),
  );

  subApp.post("/prompt", async (c) => {
    const body = (await c.req.json().catch(() => ({}))) as Record<string, unknown>;
    const handler = buildSubjectActionHandler(subject, stage, "get_study_plan", durationWeeks, language);
    const result = await handler(body);
    return c.json(result);
  });

  subApp.get("/biep", (c) =>
    c.json({
      subject,
      display_name: displayName,
      stage,
      language,
      tabs: biepTabs.map((t) => ({
        id: t.id,
        label: t.label,
        notebook_title: t.notebookTitle,
      })),
    }),
  );

  for (const action of actions) {
    subApp.post(`/actions/${action}`, async (c) => {
      const body = (await c.req.json().catch(() => ({}))) as Record<string, unknown>;
      const handler = buildSubjectActionHandler(subject, stage, action, durationWeeks, language);
      const result = await handler(body);
      return c.json(result);
    });
  }

  return subApp;
}