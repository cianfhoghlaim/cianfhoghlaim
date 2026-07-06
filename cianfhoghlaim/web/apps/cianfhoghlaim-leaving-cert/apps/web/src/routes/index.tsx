// /index — cianfhoghlaim landing page
// One unified flow for all visitor types.
// Positioned as: self-hostable consolidation of education system resources
// that helps reduce barriers to education.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell, CiBoonsChoice, CiSemanticPill } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/")({
  component: HomePage,
});

const SUBJECTS = [
  { slug: "mathematics", name: "Mathematics", color: "var(--ci-subject-mathematics)", eiraic: 3 },
  { slug: "applied_mathematics", name: "Applied Mathematics", color: "var(--ci-subject-applied_mathematics)", eiraic: 4 },
  { slug: "chemistry", name: "Chemistry", color: "var(--ci-subject-chemistry)", eiraic: 1 },
  { slug: "geography", name: "Geography", color: "var(--ci-subject-geography)", eiraic: 2 },
  { slug: "history", name: "History", color: "var(--ci-subject-history)", eiraic: 9 },
  { slug: "english", name: "English", color: "var(--ci-subject-english)", eiraic: 7 },
  { slug: "gaeilge", name: "Gaeilge", color: "var(--ci-subject-gaeilge)", eiraic: 8 },
  { slug: "computer_science", name: "Computer Science", color: "var(--ci-subject-computer_science)", eiraic: 5 },
];

function HomePage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 p-6">
      {/* Hero */}
      <section className="text-center pt-12 pb-8">
        <h1 className="font-cinzel text-5xl font-bold text-emerald-400 mb-3">
          cianfhoghlaim
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto">
          A self-hostable consolidation of Leaving Certificate education
          system resources. Built on the open-source agentic stack.
        </p>
        <p className="text-base text-slate-400 max-w-3xl mx-auto mt-3">
          NCCA syllabus + past papers + marking schemes + 8 ADK subject
          agents + Convex real-time + CopilotKit chat. One `git clone`
          away from a full deployment.
        </p>
        <div className="mt-6 flex items-center justify-center gap-3">
          <Link
            to="/en/self-host"
            className="px-5 py-2.5 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
          >
            Self-host in 5 minutes →
          </Link>
          <Link
            to="/en/subjects/mathematics"
            className="px-5 py-2.5 rounded-lg bg-slate-800 text-slate-100 border border-slate-700 hover:border-emerald-700 transition-colors"
          >
            Explore a subject
          </Link>
        </div>
        <p className="text-xs text-slate-500 mt-3 font-mono italic">
          Reduce barriers to education · open source · Convex + TanStack
          Start + CopilotKit v2 + better-auth + 8 NCCA ADK agents
        </p>
      </section>

      {/* 8 NCCA subjects */}
      <CiTextbookPanel
        title="8 NCCA Subjects"
        material="parchment"
      >
        <p className="text-slate-300 mb-4">
          The 8 NCCA Leaving Certificate subjects + their Cianfhoghlaim
          ADK agent + the BAML extraction schema + the CocoIndex
          embeddings. Each subject has its own syllabus + past papers +
          marking schemes + ADK agent + practice page.
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {SUBJECTS.map((s) => (
            <Link
              key={s.slug}
              to={`/en/subjects/${s.slug}`}
              className="p-3 rounded-lg bg-slate-900 border-2 transition-colors hover:border-amber-400"
              style={{ borderColor: s.color }}
            >
              <div className="text-sm font-medium" style={{ color: s.color }}>{s.name}</div>
              <div className="text-xs text-slate-500 font-mono mt-1">
                Éraic {s.eiraic}/13
              </div>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>

      {/* 9 ADK agents */}
      <CiTextbookPanel
        title="9 ADK Agents"
        material="knotwork"
      >
        <p className="text-slate-300 mb-4">
          8 NCCA subject specialists + 1 cianfhoghlaim operator agent (the
          repo self-reference). Each agent is a google.adk.agents.LlmAgent
          with subject-specific tools + 5 NCCA Key Competency mappings.
          The cianfhoghlaim operator agent has access to the README +
          dlt/ + cocoindex/ + baml_src/ + meaisinfhoghlaim/ for repo
          self-reference.
        </p>
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          {SUBJECTS.map((s) => (
            <Link
              key={s.slug}
              to={`/en/agents/${s.slug}`}
              className="px-2 py-1.5 rounded font-mono hover:underline"
              style={{ color: s.color }}
            >
              {s.slug.replace("_", "_")}_agent
            </Link>
          ))}
          <Link
            to="/en/agents/cianfhoghlaim"
            className="px-2 py-1.5 rounded font-mono text-amber-400 hover:underline"
          >
            cianfhoghlaim_operator
          </Link>
        </div>
      </CiTextbookPanel>

      {/* 5 Foundations */}
      <CiTextbookPanel
        title="5 Foundations"
        material="ink-wash"
      >
        <p className="text-slate-300 mb-4">
          5 NCCA root-level PDFs at{" "}
          <code className="text-amber-400">cianfhoghlaim/leaving_certificate/</code>:
          the key competencies + the SC L1/L2 programme statement + the SCR
          advisory report + the online learning potential + the online
          certification potential.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
          {[
            { slug: "key-competencies", name: "5 Key Competencies", color: "#059669" },
            { slug: "sc-l1-l2-programme", name: "SC L1/L2 Programme", color: "#2563eb" },
            { slug: "scr-advisory", name: "SCR Advisory", color: "#b91c1c" },
            { slug: "online-learning", name: "Online Learning", color: "#ca8a04" },
            { slug: "online-certification", name: "Online Certification", color: "#16a34a" },
          ].map((f) => (
            <Link
              key={f.slug}
              to={`/en/foundations/${f.slug}`}
              className="p-2 rounded border text-center text-xs hover:underline"
              style={{ borderColor: f.color, color: f.color }}
            >
              {f.name}
            </Link>
          ))}
        </div>
      </CiTextbookPanel>

      {/* 3-way boon choice — what do you want to do? */}
      <CiTextbookPanel
        title="What do you want to do?"
        material="gold-leaf"
      >
        <CiBoonsChoice
          prompt="Choose your path"
          choices={[
            {
              id: "study",
              label: "Study a subject",
              description: "Browse the syllabus, past papers, marking schemes",
            },
            {
              id: "agent",
              label: "Talk to an ADK agent",
              description: "Ask the 8 NCCA subject agents (or the cianfhoghlaim operator)",
            },
            {
              id: "selfhost",
              label: "Self-host cianfhoghlaim",
              description: "Run your own instance in 5 minutes",
            },
          ]}
          onChoose={(id) => {
            window.location.href =
              id === "study"
                ? "/en/subjects/mathematics"
                : id === "agent"
                ? "/en/agents"
                : "/en/self-host";
          }}
        />
      </CiTextbookPanel>
    </div>
  );
}