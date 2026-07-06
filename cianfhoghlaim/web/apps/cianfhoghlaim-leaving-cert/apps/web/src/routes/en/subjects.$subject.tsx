// /en/subjects/$subject — Per-subject landing page (8 NCCA subjects + 7 legacy compat)
// Replaces the old themed /en/leaving-cert/{subject} route.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiSemanticPill, CiDetailCell } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/subjects/$subject")({
  component: SubjectPage,
});

const SUBJECT_DATA: Record<string, {
  name: string;
  code: string;
  color: string;
  eiraic: number;
  agent: string;
  dlt: string;
  cocoindex: string;
  baml: string;
  description: string;
  keyCompetencies: Array<{ slug: string; name: string; weight: number }>;
}> = {
  mathematics: {
    name: "Mathematics", code: "LC-MA", color: "var(--ci-subject-mathematics)", eiraic: 3,
    agent: "mathematics", dlt: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex: "cocoindex/mathematics_embedding.py", baml: "baml_src/education/subjects/qpack_mathematics.baml",
    description: "Pure mathematics at Leaving Certificate level: algebra, functions, calculus, probability, statistics, geometry.",
    keyCompetencies: [
      { slug: "information-processing", name: "Information Processing", weight: 94 },
      { slug: "critical-creative-thinking", name: "Critical & Creative Thinking", weight: 84 },
      { slug: "communicating", name: "Communicating", weight: 72 },
      { slug: "personal-effectiveness", name: "Personal Effectiveness", weight: 58 },
      { slug: "working-with-others", name: "Working with Others", weight: 46 },
    ],
  },
  applied_mathematics: {
    name: "Applied Mathematics", code: "LC-AM", color: "var(--ci-subject-applied_mathematics)", eiraic: 4,
    agent: "applied_mathematics", dlt: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex: "cocoindex/applied_mathematics_embedding.py", baml: "baml_src/education/subjects/qpack_applied_mathematics.baml",
    description: "Modelling real-world problems: mechanics, statistics, probability, numerical analysis.",
    keyCompetencies: [
      { slug: "information-processing", name: "Information Processing", weight: 98 },
      { slug: "critical-creative-thinking", name: "Critical & Creative Thinking", weight: 88 },
      { slug: "personal-effectiveness", name: "Personal Effectiveness", weight: 70 },
      { slug: "communicating", name: "Communicating", weight: 64 },
      { slug: "working-with-others", name: "Working with Others", weight: 54 },
    ],
  },
  chemistry: {
    name: "Chemistry", code: "LC-CH", color: "var(--ci-subject-chemistry)", eiraic: 1,
    agent: "chemistry", dlt: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex: "cocoindex/chemistry_embedding.py", baml: "baml_src/education/subjects/qpack_chemistry.baml",
    description: "Atomic structure, bonding, stoichiometry, organic chemistry, equilibrium, rates.",
    keyCompetencies: [
      { slug: "personal-effectiveness", name: "Personal Effectiveness", weight: 89 },
      { slug: "information-processing", name: "Information Processing", weight: 83 },
      { slug: "critical-creative-thinking", name: "Critical & Creative Thinking", weight: 75 },
      { slug: "communicating", name: "Communicating", weight: 63 },
      { slug: "working-with-others", name: "Working with Others", weight: 62 },
    ],
  },
  geography: {
    name: "Geography", code: "LC-GG", color: "var(--ci-subject-geography)", eiraic: 2,
    agent: "geography", dlt: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex: "cocoindex/geography_embedding.py", baml: "baml_src/education/subjects/qpack_geography.baml",
    description: "Physical + regional geography: climate, geomorphology, economic activities, global development.",
    keyCompetencies: [
      { slug: "communicating", name: "Communicating", weight: 86 },
      { slug: "working-with-others", name: "Working with Others", weight: 78 },
      { slug: "information-processing", name: "Information Processing", weight: 72 },
      { slug: "personal-effectiveness", name: "Personal Effectiveness", weight: 66 },
      { slug: "critical-creative-thinking", name: "Critical & Creative Thinking", weight: 68 },
    ],
  },
  history: {
    name: "History", code: "LC-HI", color: "var(--ci-subject-history)", eiraic: 9,
    agent: "history", dlt: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex: "cocoindex/history_embedding.py", baml: "baml_src/education/subjects/qpack_history.baml",
    description: "Modern Irish + European history: Early Modern, Modern, Contemporary periods.",
    keyCompetencies: [
      { slug: "communicating", name: "Communicating", weight: 92 },
      { slug: "critical-creative-thinking", name: "Critical & Creative Thinking", weight: 90 },
      { slug: "working-with-others", name: "Working with Others", weight: 83 },
      { slug: "information-processing", name: "Information Processing", weight: 68 },
      { slug: "personal-effectiveness", name: "Personal Effectiveness", weight: 62 },
    ],
  },
  english: {
    name: "English", code: "LC-EN", color: "var(--ci-subject-english)", eiraic: 7,
    agent: "english", dlt: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex: "cocoindex/english_embedding.py", baml: "baml_src/education/subjects/qpack_english.baml",
    description: "Comprehension, composition, comparative + single text analysis, studied poetry.",
    keyCompetencies: [
      { slug: "communicating", name: "Communicating", weight: 97 },
      { slug: "critical-creative-thinking", name: "Critical & Creative Thinking", weight: 95 },
      { slug: "working-with-others", name: "Working with Others", weight: 88 },
      { slug: "personal-effectiveness", name: "Personal Effectiveness", weight: 72 },
      { slug: "information-processing", name: "Information Processing", weight: 58 },
    ],
  },
  gaeilge: {
    name: "Gaeilge", code: "LC-GA", color: "var(--ci-subject-gaeilge)", eiraic: 8,
    agent: "gaeilge", dlt: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex: "cocoindex/gaeilge_embedding.py", baml: "baml_src/education/subjects/qpack_gaeilge.baml",
    description: "Léamh, scríbhneoireacht, cluastuiscint, litríocht, gramadach.",
    keyCompetencies: [
      { slug: "communicating", name: "Communicating", weight: 100 },
      { slug: "critical-creative-thinking", name: "Critical & Creative Thinking", weight: 78 },
      { slug: "personal-effectiveness", name: "Personal Effectiveness", weight: 76 },
      { slug: "working-with-others", name: "Working with Others", weight: 72 },
      { slug: "information-processing", name: "Information Processing", weight: 48 },
    ],
  },
  computer_science: {
    name: "Computer Science", code: "LC-CS", color: "var(--ci-subject-computer_science)", eiraic: 5,
    agent: "computer_science", dlt: "dlt/british_isles/ireland/ncca_root_pdfs.py",
    cocoindex: "cocoindex/computer_science_embedding.py", baml: "baml_src/education/subjects/qpack_computer_science.baml",
    description: "Algorithms, data structures, computer systems, networks.",
    keyCompetencies: [
      { slug: "information-processing", name: "Information Processing", weight: 100 },
      { slug: "critical-creative-thinking", name: "Critical & Creative Thinking", weight: 86 },
      { slug: "personal-effectiveness", name: "Personal Effectiveness", weight: 82 },
      { slug: "working-with-others", name: "Working with Others", weight: 64 },
      { slug: "communicating", name: "Communicating", weight: 53 },
    ],
  },
};

function SubjectPage() {
  const { subject } = Route.useParams();
  const s = SUBJECT_DATA[subject];

  if (!s) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl text-slate-100">Subject not found</h1>
        <p className="text-slate-400 mt-2">
          The subject "{subject}" is not one of the 8 NCCA Leaving Certificate
          subjects. Try one of: mathematics, applied_mathematics, chemistry,
          geography, history, english, gaeilge, computer_science.
        </p>
        <Link to="/" className="text-emerald-400 underline mt-4 inline-block">
          ← Back to home
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <div className="text-sm text-slate-500 font-mono">cianfhoghlaim / subjects / {subject}</div>
        <h1 className="font-cinzel text-4xl font-bold" style={{ color: s.color }}>
          {s.name}
        </h1>
        <p className="text-slate-400 text-sm font-mono">
          NCCA {s.code} · Éraic tier {s.eiraic}/13 · {s.agent}_agent
        </p>
        <p className="text-slate-300 text-lg">{s.description}</p>
      </div>

      <CiTextbookPanel title="Talk to the ADK Agent" material="knotwork">
        <p className="text-slate-300 mb-3">
          The {s.agent.replace("_", " ")} ADK agent can answer questions
          about the syllabus, past papers, marking schemes + guide you
          through the practice page.
        </p>
        <Link
          to={`/en/agents/${s.agent}`}
          className="inline-block px-4 py-2 rounded-lg font-mono text-sm hover:underline"
          style={{ backgroundColor: s.color + "30", color: s.color }}
        >
          Talk to {s.agent}_agent →
        </Link>
      </CiTextbookPanel>

      <CiTextbookPanel title="5×8 Mastery Matrix (this subject)" material="parchment">
        <p className="text-slate-300 mb-3 text-sm">
          The 5 NCCA Key Competencies for {s.name} (per the BAML
          Get{subject.charAt(0).toUpperCase() + subject.slice(1).replace("_", "")}Prioritisation schema):
        </p>
        <div className="space-y-2">
          {s.keyCompetencies
            .sort((a, b) => b.weight - a.weight)
            .map((kc) => (
              <div key={kc.slug} className="flex items-center gap-2">
                <span className="text-slate-400 w-40 text-sm">{kc.name}</span>
                <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${kc.weight}%`, backgroundColor: s.color }}
                  />
                </div>
                <span className="text-slate-500 text-xs font-mono w-10 text-right">{kc.weight}%</span>
              </div>
            ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="Open the 6-section shell" material="ink-wash">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {[
            { slug: "syllabus", name: "Syllabus" },
            { slug: "past-exams", name: "Past exams" },
            { slug: "marking-schemes", name: "Marking schemes" },
            { slug: "prioritisation", name: "Prioritisation" },
            { slug: "exam-tips", name: "Exam tips" },
            { slug: "pdf-library", name: "PDF library" },
          ].map((sec) => (
            <Link
              key={sec.slug}
              to={`/en/leaving-cert/${subject}/${sec.slug}`}
              className="px-3 py-2 rounded bg-slate-900 border border-slate-700 hover:border-emerald-700 transition-colors text-sm text-slate-300"
            >
              {sec.name} →
            </Link>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}