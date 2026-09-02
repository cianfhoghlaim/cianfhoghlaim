// /en/subjects/geography/study-plan — Geography per-subject study plan generator (WebStudyPlan BAML action).
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject interactive web surface for the 6 BIEP v1 LC subjects.

import * as React from "react";
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/lc/geography/study-plan")({
  component: GeographyStudyplanPage,
});

function GeographyStudyplanPage() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <h1 className="text-2xl font-bold text-slate-900">Geography — Study plan</h1>
      <p className="text-slate-600">
        Geography study plan generator. Calls the per-subject
        <code> generateStudyPlan </code>
        Convex action (backed by the per-subject
        <code> WebStudyPlan </code>
        BAML function over
        <code> qpack_geography.baml</code>).
      </p>
      <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
        Study plan generator placeholder — wires into the per-subject
        <code> generateStudyPlan </code>
        Convex action.
      </div>
    </div>
  );

}
// (no further navigation)
