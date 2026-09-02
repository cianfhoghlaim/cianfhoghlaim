/**
 * StudyPlanCard — the canonical Phase 1 A2UI surface for the
 * chat-with-syllabus → study-plan flow.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
 * (Phase 1, §3.4 of tasks.md). One of the 11 A2UI catalog components
 * (the other 10 ship in Phase 2).
 *
 * Phase 1 ships a basic placeholder render with:
 *  - subject + duration summary
 *  - per-week theme list (bilingual EN/GA where applicable)
 *  - LO codes echo
 *  - KC weights bar
 *  - langfuse_trace_id display
 *
 * Phase 2 fills in the full A2UI catalog (WeekTimeline,
 * MilestoneBadge, ExamPaperCard, MarksBreakdownTable, etc.).
 */

import * as React from "react";

export interface StudyPlanCardWeek {
  week_number: number;
  theme: { text_en: string; text_ga?: string | null };
  marking_scheme_focus?: string[];
  estimated_hours?: number;
  lo_codes?: string[];
  recommended_past_papers?: Array<Record<string, unknown>>;
}

export interface StudyPlanCardKCWeight {
  competency: string;
  weight: number;
}

export interface StudyPlanCardData {
  subject: string;
  dialect?: string | null;
  language?: string;
  duration_weeks?: number;
  total_study_hours?: number;
  weeks_plan?: StudyPlanCardWeek[];
  kc_weights?: StudyPlanCardKCWeight[];
  langfuse_trace_id?: string;
  phase?: string;
}

export interface StudyPlanCardProps {
  data: StudyPlanCardData | null;
  loading?: boolean;
  error?: string | null;
  onRequestPlan?: () => void;
}

const SUBJECT_DISPLAY: Record<string, string> = {
  chemistry: "Chemistry (Ceimic)",
  mathematics: "Mathematics (Matamaitic)",
  gaeilge: "Gaeilge",
  computer_science: "Computer Science",
};

export function StudyPlanCard({
  data,
  loading,
  error,
  onRequestPlan,
}: StudyPlanCardProps): React.ReactElement {
  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <p className="text-sm text-slate-500">Generating study plan…</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-4">
        <p className="text-sm text-red-700">Study plan error: {error}</p>
      </div>
    );
  }
  if (!data) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
        <p className="font-medium text-slate-900">No study plan yet</p>
        <p className="mt-1 text-slate-600">
          Select your NCCA Learning Outcome codes above, then click{" "}
          <strong>Generate Study Plan</strong>.
        </p>
        {onRequestPlan ? (
          <button
            type="button"
            className="mt-3 rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
            onClick={onRequestPlan}
          >
            Generate Study Plan
          </button>
        ) : null}
      </div>
    );
  }

  const displayName = SUBJECT_DISPLAY[data.subject] ?? data.subject;
  const weeksPlan = data.weeks_plan ?? [];
  const kcWeights = data.kc_weights ?? [];

  return (
    <section
      aria-label={`${displayName} study plan`}
      className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
    >
      <header className="flex items-baseline justify-between gap-3">
        <h2 className="text-xl font-bold text-slate-900">
          {displayName} — Study plan
        </h2>
        <span className="text-xs text-slate-500">
          {data.duration_weeks ?? weeksPlan.length} weeks ·{" "}
          {(data.total_study_hours ?? 0).toFixed(1)} hrs
        </span>
      </header>

      {data.dialect ? (
        <p className="mt-1 text-sm text-slate-600">
          Dialect: <strong>{data.dialect}</strong>
          {data.language ? ` · Language: ${data.language}` : null}
        </p>
      ) : null}

      {kcWeights.length > 0 ? (
        <div className="mt-4">
          <h3 className="text-sm font-semibold text-slate-800">
            Key competencies
          </h3>
          <ul className="mt-2 space-y-1">
            {kcWeights.map((kc) => (
              <li
                key={kc.competency}
                className="flex items-center gap-2 text-sm text-slate-700"
              >
                <span className="w-44 text-slate-600">{kc.competency}</span>
                <div
                  aria-hidden
                  className="h-2 flex-1 rounded-full bg-slate-100"
                  role="presentation"
                >
                  <div
                    className="h-2 rounded-full bg-indigo-500"
                    style={{
                      width: `${Math.max(0, Math.min(1, kc.weight)) * 100}%`,
                    }}
                  />
                </div>
                <span className="w-10 text-right text-slate-500">
                  {(kc.weight * 100).toFixed(0)}%
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="mt-5">
        <h3 className="text-sm font-semibold text-slate-800">Weekly themes</h3>
        <ol className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
          {weeksPlan.map((week) => (
            <li
              key={week.week_number}
              className="rounded-lg border border-slate-100 bg-slate-50 p-3 text-sm"
            >
              <div className="font-medium text-slate-900">
                Week {week.week_number} ·{" "}
                {week.theme.text_en}
              </div>
              {week.theme.text_ga ? (
                <div className="text-slate-600">{week.theme.text_ga}</div>
              ) : null}
              {week.lo_codes && week.lo_codes.length > 0 ? (
                <div className="mt-1 text-xs text-slate-500">
                  LOs: {week.lo_codes.join(", ")}
                </div>
              ) : null}
            </li>
          ))}
        </ol>
      </div>

      {data.langfuse_trace_id ? (
        <p className="mt-4 text-xs text-slate-400">
          Langfuse trace: <code>{data.langfuse_trace_id}</code>
          {data.phase ? ` · phase: ${data.phase}` : null}
        </p>
      ) : null}
    </section>
  );
}

export default StudyPlanCard;