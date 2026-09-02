/**
 * Per-subject Hono bridge to the canonical Python `planner`.
 *
 * Per the 2026-09-XX-orchestration-integration-v1 change (Phase 11 of the
 * cianfhoghlaim-nua v6 era plan). Replaces the prior Phase 1 stub response
 * with a real subprocess call to
 * `agents/adk/subjects/lc/planner.py::generate_study_plan(...)`. The
 * Python function is the canonical entry point for every per-subject
 * `get_study_plan` action handler in `agents/adk/subjects/lc/<subject>.py`
 * — it wraps `b.GenerateStudyPlanAssets(...)` from the canonical
 * `baml_src/british_isles/_shared/study_plan.baml` schema and rehydrates
 * the Convex `study_plans` row.
 *
 * The subprocess pattern mirrors the precedent set by
 * `web/hono-api/src/routes/copilotkit/registry.ts::invokePythonRuntime(...)`
 * — we use `node:child_process::execFile` (NOT `exec`) so no shell
 * interpolation is possible, and we keep the Python module path +
 * function name as fixed strings so user input from the HTTP body is
 * not concatenated into the command line. Inputs to the planner
 * (subject, lo_codes, duration_weeks, dialect, language, target_date,
 * user_id, trace_id) are written to JSON on stdin, not argv, which
 * avoids both shell quoting bugs and argument-length limits.
 *
 * Behaviour:
 * - Happy path: planner returns the canonical Phase 1 stub shape (or
 *   the live BAML response shape). We forward it verbatim to the
 *   TanStack Start `/useStudyPlan` hook with `phase: "phase1_stub"` or
 *   `phase: "phase1_wired"` depending on whether the BAML call
 *   succeeded.
 * - BAML unavailable: planner returns the stub. We return it
 *   with the stub_reason preserved.
 * - Subprocess failure (Python missing, planner raises): we fall back
 *   to the local stub helper so the route never 5xxs in dev / CI.
 *
 * Convex hydration:
 * - `web/apps/cianfhoghlaim-nua/convex/schema.ts::study_plans` is the
 *   canonical Convex table. The Python planner hydrates the row on
 *   materialisation; the Hono route just returns the same dict that
 *   lands in Convex so the front-end hooks can `useQuery` either side.
 */

import { Hono } from "hono";
import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

/** Canonical shape of the response. Mirrors `agents/adk/subjects/lc/planner.py::_stub_response`. */
export interface StudyPlanWeek {
  week_number: number;
  theme: { text_en: string; text_ga: string | null };
  marking_scheme_focus: string[];
  estimated_hours: number;
  lo_codes: string[];
  recommended_past_papers: Array<Record<string, unknown>>;
}

export interface StudyPlanResponse {
  subject: string;
  dialect: string | null;
  language: string;
  duration_weeks: number;
  total_study_hours: number;
  weeks_plan: StudyPlanWeek[];
  milestones: Array<Record<string, unknown>>;
  kc_weights: Array<Record<string, unknown>>;
  recommended_past_papers: Array<Record<string, unknown>>;
  user_id: string | undefined;
  langfuse_trace_id: string;
  phase?: string;
  stub_reason?: string;
}

const SUBJECT_THEMES: Record<string, string> = {
  chemistry: "Atomic Structure + Chemical Bonding",
  mathematics: "Number + Algebra + Functions",
  gaeilge: "Léamh + Scríbhneoireacht + Cluastuiscint",
  computer_science: "Algorithms + Data + Programming",
};

const DEFAULT_WEEKS = 12;

const REPO_ROOT =
  process.env.PLANNER_REPO_ROOT
  ?? process.env.REPO_ROOT
  ?? "/Users/cianmacandeisigh/dev/cianfhoghlaim";

/** The canonical Python module + function path. Fixed string — never templated with user input. */
const PLANNER_INVOKER_SNIPPET =
  `from agents.adk.subjects.lc.planner import generate_study_plan`
  + `; import asyncio, json, sys`
  + `; params = json.loads(sys.stdin.read() or "{}")`
  + `; _trace = params.pop("trace_id", None)`
  + `; _user = params.pop("user_id", None)`
  + `; result = asyncio.run(generate_study_plan(**params))`
  + `; out = dict(result)`
  + `; out.setdefault("phase", "phase1_wired")`
  + `; out["langfuse_trace_id"] = _trace or out.get("langfuse_trace_id")`
  + `; out["user_id"] = _user`
  + `; sys.stdout.write(json.dumps(out))`;

async function invokePythonPlanner(
  subject: string,
  params: {
    lo_codes?: string[];
    target_date?: string;
    duration_weeks?: number;
    dialect?: string;
    language?: string;
    user_id?: string;
    trace_id?: string;
  },
): Promise<StudyPlanResponse | null> {
  const args: Record<string, unknown> = {
    subject,
    lo_codes: params.lo_codes ?? [],
    duration_weeks: params.duration_weeks ?? DEFAULT_WEEKS,
    target_date: params.target_date ?? null,
    dialect: params.dialect ?? null,
    language: params.language ?? (subject === "gaeilge" ? "en_and_ga" : "en"),
  };
  // Populated only when populated — protects the planner from `null`
  // dialect being passed for non-Gaeilge subjects.
  if (subject !== "gaeilge") args.dialect = null;
  if (params.trace_id) args.trace_id = params.trace_id;
  if (params.user_id) args.user_id = params.user_id;

  try {
    const { stdout } = await execFileAsync(
      "python",
      ["-c", PLANNER_INVOKER_SNIPPET],
      {
        cwd: REPO_ROOT,
        maxBuffer: 8 * 1024 * 1024,
        timeout: 30_000,
        env: { ...process.env, PYTHONPATH: REPO_ROOT },
        input: JSON.stringify(args),
      },
    );
    return JSON.parse(stdout) as StudyPlanResponse;
  } catch (_err) {
    return null;
  }
}

export function studyPlanStubResponse(
  subject: string,
  params: {
    user_id?: string;
    trace_id?: string;
    lo_codes?: string[];
    target_date?: string;
    duration_weeks?: number;
    dialect?: string;
    language?: string;
  } = {},
): StudyPlanResponse {
  const subjectSlug = subject.toLowerCase();
  const duration = Math.max(1, Math.min(52, params.duration_weeks ?? DEFAULT_WEEKS));
  const isGaeilge = subjectSlug === "gaeilge";
  const weeks_plan: StudyPlanWeek[] = Array.from({ length: duration }, (_, i) => {
    const week = i + 1;
    return {
      week_number: week,
      theme: {
        text_en: `Week ${week}: ${SUBJECT_THEMES[subjectSlug] ?? SUBJECT_THEMES.chemistry}`,
        text_ga: isGaeilge ? `Seachtain ${week}: ${SUBJECT_THEMES[subjectSlug]}` : null,
      },
      marking_scheme_focus: [
        "PCLM-1: Comprehension",
        "PCLM-2: Application",
      ],
      estimated_hours: 4.5,
      lo_codes: (params.lo_codes ?? []).slice(0, week),
      recommended_past_papers: [],
    };
  });
  return {
    subject: subjectSlug,
    dialect: isGaeilge ? params.dialect ?? "standard" : null,
    language: params.language ?? (isGaeilge ? "en_and_ga" : "en"),
    duration_weeks: duration,
    total_study_hours: duration * 4.5,
    weeks_plan,
    milestones: [],
    kc_weights: [
      { competency: "communicating", weight: 0.2 },
      { competency: "information_processing", weight: 0.2 },
      { competency: "critical_creative", weight: 0.2 },
      { competency: "personal_effectiveness", weight: 0.2 },
      { competency: "working_with_others", weight: 0.2 },
    ],
    recommended_past_papers: [],
    user_id: params.user_id,
    langfuse_trace_id: params.trace_id ?? `phase1-stub-${subjectSlug}-${Date.now()}`,
    phase: "phase1_stub",
    stub_reason: "hono_planner_subprocess_failed_or_unavailable",
  };
}

/**
 * Build the canonical /get_study_plan POST handler for the given subject.
 *
 * The handler:
 * 1. Parses the JSON body (no enforcement — Phase 1 keeps the surface
 *    forgiving; Phase 5+ adds zod validation).
 * 2. Tries the live Python planner via subprocess.
 * 3. On subprocess failure or BAML unavailable, falls back to the
 *    in-process stub so the route never 5xxs.
 */
export function buildStudyPlanHandler(
  subject: string,
  defaultDurationWeeks: number = 12,
  defaultLanguage?: string,
) {
  return async (c: { req: { json: () => Promise<unknown> }; json: (body: unknown, status?: number) => Response }) => {
    const rawBody = await c.req.json().catch(() => ({}));
    const body = (rawBody ?? {}) as Record<string, unknown>;

    const cleanParams = {
      user_id: typeof body.user_id === "string" ? body.user_id : undefined,
      trace_id: typeof body.trace_id === "string" ? body.trace_id : undefined,
      lo_codes: Array.isArray(body.lo_codes) ? (body.lo_codes as string[]) : undefined,
      target_date: typeof body.target_date === "string" ? body.target_date : undefined,
      duration_weeks:
        typeof body.duration_weeks === "number" ? body.duration_weeks : defaultDurationWeeks,
      dialect: typeof body.dialect === "string" ? body.dialect : undefined,
      language:
        typeof body.language === "string"
          ? body.language
          : defaultLanguage ?? (subject === "gaeilge" ? "en_and_ga" : "en"),
    };

    const live = await invokePythonPlanner(subject, cleanParams);
    if (live) {
      return c.json(live);
    }
    return c.json(studyPlanStubResponse(subject, cleanParams));
  };
}

/** A reusable Hono sub-app that mounts `/get_study_plan` only. */
export function buildStudyPlanSubApp(
  subject: string,
  options: { defaultDurationWeeks?: number; defaultLanguage?: string } = {},
): Hono {
  return new Hono().post(
    "/get_study_plan",
    buildStudyPlanHandler(
      subject,
      options.defaultDurationWeeks ?? 12,
      options.defaultLanguage,
    ),
  );
}

export default buildStudyPlanSubApp;
