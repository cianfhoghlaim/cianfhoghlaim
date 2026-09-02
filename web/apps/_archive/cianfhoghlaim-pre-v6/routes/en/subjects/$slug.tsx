// /en/subjects/$slug — Subject detail page (English locale)
import { createFileRoute, notFound } from "@tanstack/react-router";

export const Route = createFileRoute("/en/subjects/$slug")({
  loader: ({ params }) => {
    const s = LC_SUBJECTS.find((x) => x.slug === params.slug);
    if (!s) throw notFound();
    return { subject: s };
  },
  component: SubjectComponent,
});

function SubjectComponent() {
  const { subject } = Route.useLoaderData();
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        {subject.name_en}
      </h1>
      <p className="text-slate-400 font-mono text-sm">{subject.name_ga}</p>
      <div className="grid grid-cols-3 gap-4 mt-2 text-sm">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="text-slate-500 text-xs mb-1">Awarding Body</div>
          <div className="text-slate-200">{subject.awarding_body}</div>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="text-slate-500 text-xs mb-1">Levels</div>
          <div className="text-slate-200">{subject.levels.join(", ")}</div>
        </div>
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="text-slate-500 text-xs mb-1">Marking Style</div>
          <div className="text-slate-200">{subject.marking_style}</div>
        </div>
      </div>
      <div className="mt-4 flex flex-col gap-2">
        <a
          href={`/en/past-papers/${subject.slug}`}
          className="btn-tactile inline-block text-sm w-fit"
        >
          Past papers →
        </a>
        <a
          href={`/en/marking-schemes/${subject.slug}`}
          className="btn-tactile inline-block text-sm w-fit"
        >
          Marking schemes →
        </a>
        <a
          href={`/en/examiner-reports/${subject.slug}`}
          className="btn-tactile inline-block text-sm w-fit"
        >
          Chief Examiner reports →
        </a>
        <a
          href={`/en/practice/${subject.slug}`}
          className="btn-tactile inline-block text-sm w-fit"
        >
          Practice (essay + score) →
        </a>
      </div>
    </div>
  );
}

const LC_SUBJECTS = [
  { slug: "mathematics", name_en: "Mathematics", name_ga: "Matamaitic", awarding_body: "SEC", levels: ["foundation", "ordinary", "higher"], marking_style: "EQUATION_STEPS" },
  { slug: "irish", name_en: "Irish (Gaeilge)", name_ga: "Gaeilge", awarding_body: "SEC", levels: ["foundation", "ordinary", "higher"], marking_style: "RUBRIC_PCLM_IRISH" },
  { slug: "english", name_en: "English", name_ga: "Béarla", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "PCLM" },
  { slug: "biology", name_en: "Biology", name_ga: "Bitheolaíocht", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "KEYWORD_MATCH_DIAGRAM" },
  { slug: "french", name_en: "French", name_ga: "Fraincis", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "COMPREHENSION_EXPRESSION" },
  { slug: "history", name_en: "History", name_ga: "Stair", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "SRP" },
  { slug: "business", name_en: "Business", name_ga: "Gnó", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "SECTION_B_KEYWORD" },
  { slug: "construction-studies", name_en: "Construction Studies", name_ga: "Staidéar Tógála", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "DIAGRAM_SKETCH_STEPS" },
  { slug: "german", name_en: "German", name_ga: "Gearmáinis", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "COMPREHENSION_EXPRESSION" },
  { slug: "chemistry", name_en: "Chemistry", name_ga: "Ceimic", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "BALANCED_EQUATION_STATE_SYMBOLS" },
  { slug: "physics", name_en: "Physics", name_ga: "Fisic", awarding_body: "SEC", levels: ["ordinary", "higher"], marking_style: "DEFINITION_UNIT_FORMULA" },
  { slug: "applied-mathematics", name_en: "Applied Mathematics", name_ga: "Matamaitic Fheidhmeach", awarding_body: "SEC", levels: ["higher"], marking_style: "EQUATION_STEPS" },
];
