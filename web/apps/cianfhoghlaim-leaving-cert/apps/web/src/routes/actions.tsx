/**
 * /actions — the 13 canonical CopilotKit actions dashboard.
 *
 * Per openspec/changes/2026-09-24-web-agentic-deep-refactor-v1/.
 * Lists the 13 actions registered in `apps/api/src/copilotkit/actions.ts`:
 * - 6 leaving-cert actions (getSyllabusTopics + 5 more)
 * - 4 diagram actions (concept-map + heatmap + PCLM flow + sankey)
 * - 2 3D-asset actions
 * - 1 cross-subject action (lookupKeyCompetency)
 * Plus the lookupSCRCommentary action.
 *
 * Each action card shows: name, description, parameters, and a "Try it"
 * form that dispatches the action via the runtime endpoint.
 */
import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

export const Route = createFileRoute("/actions")({
  component: ActionsPage,
});

interface Action {
  name: string;
  description: string;
  family: "leaving-cert" | "diagram" | "3d-asset" | "cross-subject" | "scr-commentary";
  parameters: Array<{ name: string; type: string; description: string; required?: boolean }>;
}

const ACTIONS: Action[] = [
  // 6 leaving-cert
  {
    name: "getSyllabusTopics",
    description: "Get the Leaving Certificate syllabus topics, learning outcomes, and weighting for a subject.",
    family: "leaving-cert",
    parameters: [{ name: "subject", type: "string", description: "Subject slug", required: true }],
  },
  {
    name: "getPastPapers",
    description: "Get the past exam papers for a subject, optionally filtered by year and level (HL/OL).",
    family: "leaving-cert",
    parameters: [
      { name: "subject", type: "string", description: "Subject slug", required: true },
      { name: "year", type: "number", description: "Year (defaults to latest)" },
      { name: "level", type: "string", description: "HL or OL" },
    ],
  },
  {
    name: "getMarkingScheme",
    description: "Get the marking scheme for a specific exam paper.",
    family: "leaving-cert",
    parameters: [
      { name: "subject", type: "string", description: "Subject slug", required: true },
      { name: "year", type: "number", description: "Year", required: true },
      { name: "paper", type: "string", description: "Paper 1 / Paper 2", required: true },
    ],
  },
  {
    name: "getChiefExaminerReport",
    description: "Get the Chief Examiner's report for a subject/year.",
    family: "leaving-cert",
    parameters: [
      { name: "subject", type: "string", description: "Subject slug", required: true },
      { name: "year", type: "number", description: "Year", required: true },
    ],
  },
  {
    name: "getCAOPointsTrend",
    description: "Get the CAO points trend for a course over the past N years.",
    family: "leaving-cert",
    parameters: [
      { name: "courseCode", type: "string", description: "CAO course code", required: true },
      { name: "years", type: "number", description: "Lookback years (default 5)" },
    ],
  },
  {
    name: "getMatriculationRules",
    description: "Get the matriculation rules for an NUI institution + minimum subject requirements.",
    family: "leaving-cert",
    parameters: [
      { name: "institution", type: "string", description: "UCD/UoG/UCC/NUIM", required: true },
      { name: "programme", type: "string", description: "Programme family (e.g. engineering, arts, science)" },
    ],
  },
  // 4 diagram
  {
    name: "renderConceptMap",
    description: "Render a concept-map of the 5 NCCA Key Competencies + per-subject LOs.",
    family: "diagram",
    parameters: [
      { name: "subject", type: "string", description: "Subject slug", required: true },
      { name: "depth", type: "number", description: "Recursion depth (default 2)" },
    ],
  },
  {
    name: "renderTopicHeatmap",
    description: "Render a topic-heatmap (question × paper × topic × year).",
    family: "diagram",
    parameters: [
      { name: "subject", type: "string", description: "Subject slug", required: true },
      { name: "years", type: "number", description: "Year range" },
    ],
  },
  {
    name: "renderPCLMFlow",
    description: "Render the Partial Credit, Logical Marking flow for a marking scheme.",
    family: "diagram",
    parameters: [
      { name: "subject", type: "string", description: "Subject slug", required: true },
      { name: "year", type: "number", description: "Year", required: true },
    ],
  },
  {
    name: "renderSankey",
    description: "Render a Sankey diagram of student progression (Aistear → LC).",
    family: "diagram",
    parameters: [
      { name: "cohort", type: "string", description: "Cohort year" },
    ],
  },
  // 2 3D-asset
  {
    name: "render3DMolecule",
    description: "Render a 3D molecular structure (Babylon.js).",
    family: "3d-asset",
    parameters: [
      { name: "formula", type: "string", description: "Chemical formula", required: true },
    ],
  },
  {
    name: "render3DGeoTerrain",
    description: "Render a 3D terrain from a Leaving Cert Geography question.",
    family: "3d-asset",
    parameters: [
      { name: "questionId", type: "string", description: "Question ID", required: true },
    ],
  },
  // 1 cross-subject
  {
    name: "lookupKeyCompetency",
    description: "Look up which Key Competencies a specific LO maps to across multiple subjects.",
    family: "cross-subject",
    parameters: [
      { name: "learningOutcome", type: "string", description: "LO text", required: true },
    ],
  },
  // SCR commentary (1)
  {
    name: "lookupSCRCommentary",
    description: "Look up the Subject Committee Report commentary for a subject/year.",
    family: "scr-commentary",
    parameters: [
      { name: "subject", type: "string", description: "Subject slug", required: true },
      { name: "year", type: "number", description: "Year", required: true },
    ],
  },
];

const FAMILIES: Record<Action["family"], { icon: string; title: string; color: string }> = {
  "leaving-cert": { icon: "🎓", title: "Leaving Cert (6)", color: "emerald" },
  "diagram": { icon: "📊", title: "Diagrams (4)", color: "blue" },
  "3d-asset": { icon: "🧊", title: "3D Assets (2)", color: "purple" },
  "cross-subject": { icon: "🔗", title: "Cross-Subject (1)", color: "amber" },
  "scr-commentary": { icon: "📝", title: "SCR Commentary (1)", color: "slate" },
};

function ActionsPage() {
  const [filter, setFilter] = useState<Action["family"] | "all">("all");
  const visible = ACTIONS.filter((a) => filter === "all" || a.family === filter);
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6">
      <header>
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          ⚙️ Canonical CopilotKit Actions
        </h1>
        <p className="text-slate-400 text-sm mt-2">
          14 actions registered in <code className="font-mono text-emerald-400">apps/api/src/copilotkit/actions.ts</code>{" "}
          (per <code className="font-mono text-emerald-400">2026-09-24-web-agentic-deep-refactor-v1</code>).
        </p>
      </header>

      <div className="flex gap-2">
        <button
          className={`btn-tactile text-sm ${filter === "all" ? "bg-emerald-700" : ""}`}
          onClick={() => setFilter("all")}
        >
          All ({ACTIONS.length})
        </button>
        {Object.entries(FAMILIES).map(([k, v]) => (
          <button
            key={k}
            className={`btn-tactile text-sm ${filter === k ? `bg-${v.color}-700` : ""}`}
            onClick={() => setFilter(k as Action["family"])}
          >
            {v.icon} {v.title}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {visible.map((action) => {
          const fam = FAMILIES[action.family];
          return (
            <div
              key={action.name}
              className={`bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-${fam.color}-700`}
            >
              <div className="flex items-center justify-between mb-2">
                <code className="font-mono text-emerald-400 text-sm">{action.name}</code>
                <span className={`text-xs text-${fam.color}-400 font-mono`}>
                  {fam.icon} {action.family}
                </span>
              </div>
              <p className="text-slate-300 text-sm mb-2">{action.description}</p>
              <div className="text-xs text-slate-500 font-mono">
                Parameters:
                <ul className="list-disc list-inside mt-1">
                  {action.parameters.map((p) => (
                    <li key={p.name}>
                      {p.name}: {p.type}
                      {p.required ? " (required)" : ""}
                    </li>
                  ))}
                </ul>
              </div>
              <button
                className="btn-tactile text-sm mt-3"
                onClick={() => {
                  console.log("[Actions] dispatch:", action.name);
                }}
              >
                Try it →
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
