// routes/(student)/lc/chemistry/study-plan.tsx — Chemistry per-subject
// study plan page in the consolidated cianfhoghlaim-nua app.
//
// Migrated from web/apps/oideachais/routes/lc/chemistry/study-plan.tsx
// per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
// (Phase 3 of the cianfhoghlaim-nua v6 era plan). Uses the canonical
// @cianfhoghlaim/a2ui catalog (Phase 2) for the A2UI surfaces.

import * as React from "react";
import { createFileRoute } from "@tanstack/react-router";

import {
  StudyPlanCard,
  WeekTimeline,
  MilestoneBadge,
  KCWeightsBar,
  ExamPaperCardGrid,
} from "@cianfhoghlaim/a2ui";

import { useStudyPlan } from "../../../../hooks/useStudyPlan";

export const Route = createFileRoute(
  "/(student)/lc/chemistry/study-plan",
)({
  component: ChemistryStudyplanPage,
});

function ChemistryStudyplanPage(): React.ReactElement {
  const { data, loading, error, request } = useStudyPlan("chemistry");
  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 p-6">
      <h1 className="text-2xl font-bold text-slate-900">
        Chemistry — Study plan
      </h1>
      <p className="text-slate-600">
        Chemistry study plan generator (LC Higher Level). Calls the
        canonical Phase 1 planner at
        <code> agents/adk/subjects/lc/planner.py::generate_study_plan</code>
        via the Hono
        <code> /api/copilotkit/lc/chemistry/get_study_plan </code>
        endpoint.
      </p>

      <StudyPlanCard
        data={data}
        loading={loading}
        error={error}
        onRequestPlan={() => request({ duration_weeks: 12, language: "en" })}
      />

      {data ? (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-800">
            Weekly themes
          </h2>
          <WeekTimeline
            weeks={data.weeks_plan ?? []}
            onSelectWeek={() => undefined}
          />
          {data.kc_weights && data.kc_weights.length > 0 ? (
            <KCWeightsBar items={data.kc_weights} title="Key competencies" />
          ) : null}
          {data.recommended_past_papers &&
          data.recommended_past_papers.length > 0 ? (
            <ExamPaperCardGrid papers={data.recommended_past_papers} />
          ) : null}
        </section>
      ) : null}
    </div>
  );
}