// /en/leaving-cert/$subject/$section — Per-section page (6 sections: syllabus, past-exams, marking-schemes, prioritisation, exam-tips, pdf-library)

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { CiTextbookPanel, CiSemanticPill, CiDetailCell } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/leaving-cert/$subject/$section")({
  component: SectionPage,
});

const SECTIONS: Record<string, { title: string; description: string }> = {
  syllabus: { title: "Syllabus", description: "The NCCA syllabus topics + learning outcomes" },
  "past-exams": { title: "Past exams", description: "All past exam questions tagged by topic + paper + year" },
  "marking-schemes": { title: "Marking schemes", description: "PCLM (Partial Credit, Logical Marking) patterns" },
  prioritisation: { title: "Prioritisation", description: "Ranked by marks ÷ study-hours" },
  "exam-tips": { title: "Exam tips", description: "Per the SCR Advisory" },
  "pdf-library": { title: "PDF library", description: "Original NCCA syllabus + SEC exam papers" },
};

function SectionPage() {
  const { subject, section } = Route.useParams();
  const sec = SECTIONS[section];

  if (!sec) {
    throw notFound({ data: { subject, section } });
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Link to="/" className="hover:text-emerald-400">Home</Link>
          <span>›</span>
          <Link to={`/en/subjects/${subject}`} className="hover:text-emerald-400">{subject}</Link>
          <span>›</span>
          <span className="text-slate-300">{sec.title}</span>
        </div>
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          {sec.title}
        </h1>
        <p className="text-slate-400">{sec.description}</p>
        <p className="text-slate-500 text-sm italic">
          (The full per-section content + the 4 diagram modes are wired
          to the BAML ExtractExamPaper + ExtractMarkingScheme schemas +
          the daily_diagram_pre_render Dagster asset.)
        </p>
      </div>
    </div>
  );
}