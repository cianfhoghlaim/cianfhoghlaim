// /en/leaving-cert/$subject — Per-subject landing page (the 6-section shell)
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R2.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiProgressRing } from "@cianfhoghlaim/ui";
import { CiDragonBanner } from "@cianfhoghlaim/ui/lore/dragon-banner";

export const Route = createFileRoute("/en/leaving-cert/$subject")({
  component: SubjectPage,
});

const SUBJECT_NAMES: Record<string, { en: string; ga: string }> = {
  mathematics: { en: "Mathematics", ga: "Mata" },
  "applied_mathematics": { en: "Applied Mathematics", ga: "Mata Feidhmíoch" },
  chemistry: { en: "Chemistry", ga: "Ceimic" },
  geography: { en: "Geography", ga: "Tíreolaíocht" },
  history: { en: "History", ga: "Stair" },
  english: { en: "English", ga: "Béarla" },
  gaeilge: { en: "Gaeilge", ga: "Gaeilge" },
  computer_science: { en: "Computer Science", ga: "Ríomheolaíocht" },
  biology: { en: "Biology", ga: "Bitheolaíocht" },
  french: { en: "French", ga: "Fraincis" },
  business: { en: "Business", ga: "Gnó" },
  "construction-studies": { en: "Construction Studies", ga: "Staidéar Tógála" },
};

const SECTIONS = [
  { id: "syllabus", title_en: "Syllabus Analysis", title_ga: "Anailís ar an Siollabas" },
  { id: "past-exams", title_en: "Past Exam Questions", title_ga: "Ceisteanna ón Scrúdú Caite" },
  { id: "marking-schemes", title_en: "Marking Schemes", title_ga: "Scéimeanna Marcála" },
  { id: "prioritisation", title_en: "Topic Prioritisation", title_ga: "Tosaíocht Ábhar" },
  { id: "exam-tips", title_en: "Exam Layout Tips", title_ga: "Leideanna le haghaidh an Scrúdaithe" },
  { id: "pdf-library", title_en: "PDF Library", title_ga: "Leabharlann PDF" },
] as const;

function SubjectPage() {
  const { subject } = Route.useParams();
  const names = SUBJECT_NAMES[subject] ?? { en: subject, ga: subject };
  const isWales = false; // The landing page is for the Éire subnation; Wales is later

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6">
      {/* Hero */}
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          {names.en}
        </h1>
        <p className="text-slate-400 font-mono text-lg">
          {names.ga}
        </p>
        <p className="text-slate-500 text-sm">
          NCCA Leaving Certificate · 6 sections · 4 diagram modes · bilingual EN+GA
        </p>
      </div>

      {/* Progress ring */}
      <div className="flex justify-center">
        <CiProgressRing
          value={42}
          tier="familiar"
          eiraicTier={4}
          label={names.en}
          subjectColor={subject.replace("_", "-")}
        />
      </div>

      {/* 6-section shell */}
      <div className="grid grid-cols-2 gap-4">
        {SECTIONS.map((section) => (
          <Link
            key={section.id}
            to={`/en/leaving-cert/${subject}/${section.id}`}
            className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-emerald-700 transition-colors"
          >
            <h3 className="font-bold text-lg text-slate-100 mb-1">{section.title_en}</h3>
            <p className="text-slate-500 text-sm font-mono text-xs">{section.title_ga}</p>
          </Link>
        ))}
      </div>

      {/* Dragon Banner for Wales (placeholder — only Wales shows it) */}
      {isWales && (
        <div className="flex justify-center pt-4">
          <CiDragonBanner size={64} />
        </div>
      )}
    </div>
  );
}