// /en/leaving-cert/$subject/practice/$topic — Practice page
// Per openspec/changes/cianfhoghlaim-website-rewrite/specs/.../spec.md
// R3 + R4. Per-subject CopilotKit chat + practice session with A2UI
// surface rendering for the 5×8 mastery matrix.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiProgressRing, CiSemanticPill } from "@cianfhoghlaim/ui";
import { SubjectChat } from "@/components/chat/SubjectChat";
import { AGENTS } from "@/lib/registry";

export const Route = createFileRoute("/en/leaving-cert/$subject/practice/$topic")({
  component: PracticePage,
});

function PracticePage() {
  const { subject, topic } = Route.useParams();
  const agent = AGENTS.find((a) => a.id === subject);

  if (!agent) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-slate-100">
        <h1 className="text-2xl font-bold text-red-500">Unknown subject: {subject}</h1>
        <Link to="/en/subjects" className="text-emerald-400 underline">
          ← Back to subjects
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Link to={`/en/leaving-cert/${subject}`} className="hover:text-emerald-400">
          ← {agent.name}
        </Link>
        <span>/</span>
        <span className="text-slate-300">Practice · {topic}</span>
      </div>

      <h1
        className="font-cinzel text-3xl font-bold"
        style={{ color: agent.color }}
      >
        {agent.name} — Practice · {topic}
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Subject chat (CopilotKit AG-UI + A2UI) */}
        <CiTextbookPanel title={`${agent.name} Agent (ADK + A2UI)`} material="knotwork">
          <SubjectChat subject={subject} topic={topic} />
        </CiTextbookPanel>

        {/* Mastery display */}
        <CiTextbookPanel title="5×8 Mastery Matrix" material="parchment">
          <p className="text-slate-300 mb-4">
            The {agent.name} 5×8 mastery matrix below is rendered from
            the cocoindex cross_subject_competency_embedding.py output.
            The A2UI surface will display the prioritised learning objectives.
          </p>
          <div className="space-y-2">
            {[
              { kc: "Communicating", ga: "Cumarsáid", color: "#059669", weight: 72 },
              { kc: "Information Processing", ga: "Próiseáil Faisnéise", color: "#2563eb", weight: 94 },
              { kc: "Critical & Creative Thinking", ga: "Smaointeoireacht Chriticiúil", color: "#ca8a04", weight: 84 },
              { kc: "Personal Effectiveness", ga: "Éifeachtacht Phearsanta", color: "#92400e", weight: 58 },
              { kc: "Working with Others", ga: "Ag Obair le Daoine Eile", color: "#b91c1c", weight: 46 },
            ].map((row) => (
              <div key={row.kc} className="flex items-center gap-2">
                <span className="w-40 text-sm" style={{ color: row.color }}>{row.kc}</span>
                <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${row.weight}%`, background: row.color }} />
                </div>
                <span className="w-10 text-right text-xs text-slate-400">{row.weight}%</span>
              </div>
            ))}
          </div>
        </CiTextbookPanel>
      </div>

      <CiTextbookPanel title="3-way boon choice (Khan-class)" material="gold-leaf">
        <p className="text-slate-300 mb-4">
          How would you like to start this {topic} practice session?
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            { id: "worked", title: "Worked Solution", desc: "See the full step-by-step solution + marking scheme", color: "#2563eb" },
            { id: "feedback", title: "Show Me Why", desc: "Get detailed feedback on the answer + 4 graduated hints", color: "#7c3aed" },
            { id: "auto", title: "Auto-Score Me", desc: "Let the {agent.name} agent score your attempt against the 5×8 mastery matrix", color: "#f59e0b" },
          ].map((b) => (
            <button
              key={b.id}
              className="p-3 rounded-lg bg-slate-900 border-2 transition-colors text-left hover:border-amber-400"
              style={{ borderColor: b.color }}
            >
              <div className="text-sm font-bold" style={{ color: b.color }}>{b.title}</div>
              <div className="text-xs text-slate-400 mt-1">{b.desc}</div>
            </button>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}