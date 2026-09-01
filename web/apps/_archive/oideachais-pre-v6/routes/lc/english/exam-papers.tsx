// /en/subjects/english/exam-papers — English per-subject past exam paper viewer + discussExamPaper BAML action.
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject interactive web surface for the 6 BIEP v1 LC subjects.

import * as React from "react";
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/lc/english/exam-papers")({
  component: EnglishExampapersPage,
});

function EnglishExampapersPage() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <h1 className="text-2xl font-bold text-slate-900">English — Past exam papers</h1>
      <p className="text-slate-600">
        All English past exam papers tagged by topic + paper + year.
        Click a paper to discuss it via the per-subject
        <code> discussExamPaper </code>
        Convex action (BAML backend).
      </p>
      <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-700">
        Exam paper viewer placeholder — wires into the per-subject
        <code> discussExamPaper </code>
        Convex action backed by the per-subject
        <code> WebExamPaperDiscussion </code>
        BAML function.
      </div>
    </div>
  );

}
// (no further navigation)
