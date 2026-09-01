// /en/diagrams — The 4 diagram modes (concept-map + heatmap + PCLM flow + sankey)
// Per openspec/changes/cianfhoghlaim-website-rewrite/tasks.md B.12
// Index page for the 4 diagram modes rendered per-subject.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui-kit/lc";

export const Route = createFileRoute("/diagrams")({
  component: DiagramsPage,
});

const DIAGRAM_MODES = [
  {
    id: "concept-map",
    title: "Concept-map",
    description: "Renders the 5 NCCA Key Competencies as root nodes + the per-subject LOs as children.",
    subject: "mathematics",
  },
  {
    id: "topic-heatmap",
    title: "Topic-heatmap",
    description: "Renders question × paper × topic × year as a 2.5D matrix.",
    subject: "chemistry",
  },
  {
    id: "pclm-flow",
    title: "PCLM marking flow",
    description: "Renders the Partial Credit, Logical Marking flowchart per marking scheme.",
    subject: "history",
  },
  {
    id: "question-sankey",
    title: "Question → Topic → Difficulty → Year Sankey",
    description: "Renders the question → topic → difficulty → year Sankey flow.",
    subject: "geography",
  },
];

function DiagramsPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          The 4 Diagram Modes
        </h1>
        <p className="text-slate-300 max-w-3xl">
          Each of the 4 diagram modes is rendered per-subject. The diagrams
          are pre-rendered by the daily_diagram_pre_render Dagster asset.
        </p>
      </div>

      <CiTextbookPanel title="4 Modes" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {DIAGRAM_MODES.map((m) => (
            <Link
              key={m.id}
              to={`/en/leaving-cert/${m.subject}/past-exams`}
              className="p-4 rounded-lg bg-slate-900 border border-slate-700 hover:border-amber-400 transition-colors"
            >
              <div className="text-lg font-bold text-slate-100">{m.title}</div>
              <div className="text-sm text-slate-400 mt-2">{m.description}</div>
              <div className="text-xs text-amber-400 mt-2">View on {m.subject} →</div>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}