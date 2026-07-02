// /en/diagrams — Index of the 4 diagram modes
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R3.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/diagrams")({
  component: DiagramsPage,
});

const DIAGRAM_MODES = [
  {
    mode: "concept-map",
    name_en: "Concept-map",
    name_ga: "Léarscáil choincheap",
    description_en: "Renders the 5 NCCA Key Competencies as root nodes with the per-subject LOs as children.",
    subject_color: "var(--ci-subject-mathematics)",
  },
  {
    mode: "topic-heatmap",
    name_en: "Topic-heatmap",
    name_ga: "Teaschárta ábhar",
    description_en: "Renders question × paper × topic × year as a 2.5D matrix.",
    subject_color: "var(--ci-subject-geography)",
  },
  {
    mode: "pclm-flow",
    name_en: "PCLM marking flow",
    name_ga: "Sreabh marcála PCLM",
    description_en: "Renders the Partial Credit, Logical Marking flowchart per marking scheme.",
    subject_color: "var(--ci-subject-history)",
  },
  {
    mode: "question-sankey",
    name_en: "Question → Topic → Difficulty → Year Sankey",
    name_ga: "Sankey Ceist → Ábhar → Deacracht → Bliain",
    description_en: "Renders the question → topic → difficulty → year Sankey flow.",
    subject_color: "var(--ci-subject-applied_mathematics)",
  },
];

function DiagramsPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          The 4 Diagram Modes
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          The 4 per-subject diagram modes for the Cianfhoghlaim OS.
          Each mode is pre-rendered daily by the
          <code className="text-amber-400 mx-2">daily_diagram_pre_render</code>
          Dagster asset.
        </p>
      </div>

      <CiTextbookPanel title="The 4 Modes" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DIAGRAM_MODES.map((m) => (
            <Link
              key={m.mode}
              to="/en/leaving-cert/mathematics/syllabus"
              className="p-5 rounded-xl bg-slate-900 border-2 hover:border-amber-400 transition-colors"
              style={{ borderColor: m.subject_color }}
            >
              <h3 className="font-bold text-lg text-slate-100">{m.name_en}</h3>
              <p className="text-xs text-slate-400 italic mt-1">{m.name_ga}</p>
              <p className="text-sm text-slate-300 mt-3">{m.description_en}</p>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}