// /en/subjects/gaeilge/study-plan — Gaeilge per-subject study plan generator.
//
// Per the 2026-09-01-cianfhoghlaim-nua-end-to-end-showcase-v1 change
// (Phase 1, §3.4 + §4.3.3 of tasks.md). Renders the canonical Phase 1
// `<StudyPlanCard>` A2UI surface backed by the Hono
// `/api/copilotkit/lc/gaeilge/get_study_plan` endpoint. Threads the
// Irish dialect through the planner (Phase 1 forwards; Phase 6 wires
// the oral-plan companion call).

import * as React from "react";
import { createFileRoute } from "@tanstack/react-router";

import { StudyPlanCard } from "../../../src/components/study-plan/StudyPlanCard";
import { useStudyPlan } from "../../../src/hooks/useStudyPlan";

export const Route = createFileRoute("/lc/gaeilge/study-plan")({
  component: GaeilgeStudyplanPage,
});

function GaeilgeStudyplanPage(): React.ReactElement {
  const { data, loading, error, request } = useStudyPlan("gaeilge");
  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 p-6">
      <h1 className="text-2xl font-bold text-slate-900">
        Gaeilge — Study plan
      </h1>
      <p className="text-slate-600">
        Gaeilge study plan generator (LC Higher Level). Calls the
        canonical Phase 1 planner at
        <code> agents/adk/subjects/lc/planner.py::generate_study_plan</code>
        via the Hono
        <code> /api/copilotkit/lc/gaeilge/get_study_plan </code>
        endpoint. Dialect dispatch (Connacht / Munster / Ulster /
        Standard) is threaded through the planner.
      </p>
      <StudyPlanCard
        data={data}
        loading={loading}
        error={error}
        onRequestPlan={() =>
          request({
            duration_weeks: 16,
            dialect: "connacht",
            language: "en_and_ga",
          })
        }
      />
    </div>
  );
}