// /en/practice/$subject — Practice / essay editor (Cianfhoghlaim Oideachais)
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/en/practice/$subject")({
  component: PracticeComponent,
});

function PracticeComponent() {
  const { subject } = Route.useParams();
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        Practice — {subject.replace("-", " ")}
      </h1>
      <p className="text-slate-400">
        Write an essay-style answer and have it scored against the BAML SubjectRubric.
        Powered by baml.ScoreEssayAgainstRubric (uses Claude Sonnet 4 for nuanced grading).
      </p>
      <textarea
        className="w-full h-48 bg-slate-800 border border-slate-700 rounded-lg p-4 text-slate-100 font-mono text-sm resize-none"
        placeholder="Write your essay here…"
      />
      <button className="btn-tactile w-fit">Submit for Scoring</button>
    </div>
  );
}
