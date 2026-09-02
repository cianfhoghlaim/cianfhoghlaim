// /en/subjects/geography/marking-schemes — Geography per-subject marking scheme (PCLM) viewer + WebMarkingSchemeExplanation.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject interactive web surface for the 6 BIEP v1 LC subjects.

import * as React from "react";
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/lc/geography/marking-schemes")({
  component: GeographyMarkingschemesPage,
});

function GeographyMarkingschemesPage() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <h1 className="text-2xl font-bold text-slate-900">Geography — Marking schemes</h1>
      <p className="text-slate-600">
        Geography marking scheme (PCLM — Partial Credit, Logical
        Marking) viewer. The per-subject
        <code> WebMarkingSchemeExplanation </code>
        BAML function explains how marks are awarded for each answer.
      </p>
      <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
        Marking scheme viewer placeholder — wires into the per-subject
        <code> extract_marking_scheme_guideline </code>
        BAML output via the per-subject Convex schema.
      </div>
    </div>
  );

}
// (no further navigation)
