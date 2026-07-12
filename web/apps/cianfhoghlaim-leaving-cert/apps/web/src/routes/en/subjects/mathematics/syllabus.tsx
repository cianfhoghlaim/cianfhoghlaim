// /en/subjects/mathematics/syllabus — Mathematics per-subject NCCA syllabus + learning outcomes viewer.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject interactive web surface for the 6 BIEP v1 LC subjects.

import * as React from "react";
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/en/subjects/mathematics/syllabus")({
  component: MathematicsSyllabusPage,
});

function MathematicsSyllabusPage() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <h1 className="text-2xl font-bold text-slate-900">Mathematics — Syllabus</h1>
      <p className="text-slate-600">
        The NCCA Mathematics syllabus + learning outcomes viewer.
        Source: the per-subject BAML extraction
        (<code>qpack_mathematics.baml</code>) over the
        NCCA + SEC PDFs in the per-subject corpus.
      </p>
      <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
        Syllabus viewer placeholder — wires into the per-subject
        <code> extract_curriculum_syllabus </code>
        BAML output via the per-subject Convex schema.
      </div>
    </div>
  );

// (no further navigation)
