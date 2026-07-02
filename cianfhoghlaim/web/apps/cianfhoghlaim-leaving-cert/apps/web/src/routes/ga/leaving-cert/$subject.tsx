// /ga/leaving-cert/{subject} — Per-subject landing page in Irish
// Mirror of /en/leaving-cert/{subject} with bilingual EN+GA content.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiProgressRing } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/ga/leaving-cert/$subject")({
  component: SubjectPageGA,
});

const SUBJECT_NAMES_GA: Record<string, { en: string; ga: string }> = {
  mathematics: { en: "Mathematics", ga: "Mata" },
  applied_mathematics: { en: "Applied Mathematics", ga: "Mata Feidhmíoch" },
  chemistry: { en: "Chemistry", ga: "Ceimic" },
  geography: { en: "Geography", ga: "Tíreolaíocht" },
  history: { en: "History", ga: "Stair" },
  english: { en: "English", ga: "Béarla" },
  gaeilge: { en: "Gaeilge", ga: "Gaeilge" },
  computer_science: { en: "Computer Science", ga: "Ríomheolaíocht" },
  irish: { en: "Irish (legacy)", ga: "Gaeilge" },
  biology: { en: "Biology", ga: "Bitheolaíocht" },
  french: { en: "French", ga: "Fraincis" },
  business: { en: "Business", ga: "Gnó" },
  construction_studies: { en: "Construction Studies", ga: "Staidéar Tógála" },
};

const SECTIONS_GA = [
  { id: "syllabus", title_en: "Syllabus Analysis", title_ga: "Anailís ar an Siollabas" },
  { id: "past-exams", title_en: "Past Exam Questions", title_ga: "Ceisteanna ón Scrúdú Caite" },
  { id: "marking-schemes", title_en: "Marking Schemes", title_ga: "Scéimeanna Marcála" },
  { id: "prioritisation", title_en: "Topic Prioritisation", title_ga: "Tosaíocht Ábhar" },
  { id: "exam-tips", title_en: "Exam Layout Tips", title_ga: "Leideanna le haghaidh an Scrúdaithe" },
  { id: "pdf-library", title_en: "PDF Library", title_ga: "Leabharlann PDF" },
];

function SubjectPageGA() {
  const { subject } = Route.useParams();
  const names = SUBJECT_NAMES_GA[subject] ?? { en: subject, ga: subject };

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          {names.ga}
        </h1>
        <p className="text-slate-400 font-mono text-lg">
          {names.en}
        </p>
        <p className="text-slate-500 text-sm">
          Ardteistiméireacht NCCA · 6 rannóg · 4 mód léaráide · dátheangach EN+GA
        </p>
      </div>

      <div className="flex justify-center">
        <CiProgressRing
          value={42}
          tier="familiar"
          eiraicTier={4}
          label={names.ga}
          subjectColor={subject.replace("_", "-")}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {SECTIONS_GA.map((section) => (
          <Link
            key={section.id}
            to={`/ga/leaving-cert/${subject}/${section.id}`}
            className="bg-slate-800 border border-slate-700 rounded-xl p-6 hover:border-emerald-700 transition-colors"
          >
            <h3 className="font-bold text-lg text-slate-100 mb-1">{section.title_ga}</h3>
            <p className="text-slate-500 text-sm font-mono text-xs">{section.title_en}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}