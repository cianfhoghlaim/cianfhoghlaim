// /en/playgrounds — Per-subject sandboxes (iximiuz Labs-inspired)
// Per openspec/changes/cianfhoghlaim-website-rewrite/tasks.md B.11
// Marimo notebooks embedded from the existing 8 NCCA subject notebooks
// at notebooks/leaving_cert/{subject}.py.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiSemanticPill } from "@cianfhoghlaim/ui-kit/lc";
import { AGENTS } from "@/lib/registry";

export const Route = createFileRoute("/playgrounds")({
  component: PlaygroundsPage,
});

function PlaygroundsPage() {
  const subjectAgents = AGENTS.filter((a) => a.id !== "cianfhoghlaim");

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          Playgrounds
        </h1>
        <p className="text-slate-300 max-w-3xl">
          Per-subject sandboxes. Each subject has a marimo notebook
          embedded as an interactive widget. Borrowed from iximiuz Labs'
          "Experiment Freely in Safe Sandboxes" model.
        </p>
      </div>

      <CiTextbookPanel title="8 NCCA Subject Playgrounds" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjectAgents.map((s) => (
            <div
              key={s.id}
              className="p-4 rounded-lg bg-slate-900 border-2"
              style={{ borderColor: s.color }}
            >
              <div className="text-lg font-bold" style={{ color: s.color }}>{s.name}</div>
              <div className="text-xs text-slate-500 italic mb-2">{s.name_ga}</div>
              <div className="text-sm text-slate-300 mb-3">{s.role.slice(0, 100)}...</div>
              <div className="flex items-center gap-2 text-xs">
                <CiSemanticPill kind="eiraic" label={`Éraic ${s.eiraic_tier}/13`} />
                <code className="text-slate-500">{s.notebook_path.split("/").pop()}</code>
              </div>
            </div>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}