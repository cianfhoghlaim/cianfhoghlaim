// /en/examiner-reports/$subject (Cianfhoghlaim Oideachais)
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/en/examiner-reports/$subject")({
  component: ExaminerReportsComponent,
});

function ExaminerReportsComponent() {
  const { subject } = Route.useParams();
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        Chief Examiner Reports — {subject.replace("-", " ")}
      </h1>
      <p className="text-slate-400">
        Annual Chief Examiner Reports for every LC subject. Extracted by BAML
        (ExtractExaminerReportInsights) and indexed in Cognee.
      </p>
    </div>
  );
}
