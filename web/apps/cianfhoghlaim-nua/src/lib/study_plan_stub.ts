/**
 * Study plan stub — the Phase 1 stub response shape that the 4
 * per-subject Hono endpoints return when the canonical BAML
 * function fails.
 *
 * Lifted + generalized from
 * web/hono-api/src/routes/copilotkit/lc/_study_plan_stub.ts
 * (per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change,
 * Phase 3 §D.2).
 *
 * The stub response is the canonical Phase 1 Phase 1 stub shape
 * — matches what the Python `planner.generate_study_plan(...)`
 * function returns when the baml_client is unavailable.
 */

export interface StudyPlanStubWeek {
  week_number: number;
  theme: { text_en: string; text_ga: string | null };
  marking_scheme_focus: string[];
  estimated_hours: number;
  lo_codes: string[];
  recommended_past_papers: Array<Record<string, unknown>>;
}

export interface StudyPlanStubResponse {
  subject: string;
  dialect: string | null;
  language: string;
  duration_weeks: number;
  total_study_hours: number;
  weeks_plan: StudyPlanStubWeek[];
  milestones: Array<Record<string, unknown>>;
  kc_weights: Array<Record<string, unknown>>;
  recommended_past_papers: Array<Record<string, unknown>>;
  user_id: string | undefined;
  langfuse_trace_id: string;
  phase: "phase1_stub";
  stub_reason: string;
}

const SUBJECT_THEMES: Record<string, string> = {
  chemistry: "Atomic Structure + Chemical Bonding",
  mathematics: "Number + Algebra + Functions",
  gaeilge: "Léamh + Scríbhneoireacht + Cluastuiscint",
  computer_science: "Algorithms + Data + Programming",
};

const DEFAULT_WEEKS = 12;

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
): StudyPlanStubResponse {
  const subjectSlug = subject.toLowerCase();
  const duration = Math.max(1, Math.min(52, params.duration_weeks ?? DEFAULT_WEEKS));
  const isGaeilge = subjectSlug === "gaeilge";
  const weeks_plan: StudyPlanStubWeek[] = Array.from(
    { length: duration },
    (_, i) => {
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
    },
  );
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
    stub_reason: "hono_planner_service_not_yet_deployed",
  };
}

export default studyPlanStubResponse;
