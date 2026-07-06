// /en/about — About cianfhoghlaim
// Per openspec/changes/cianfhoghlaim-website-rewrite/tasks.md D.2
// Operator-only lineage + public-facing summary.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiSemanticPill } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/about")({
  component: AboutPage,
});

const SUBJECTS = [
  { slug: "mathematics", name: "Mathematics", color: "#2563eb" },
  { slug: "applied_mathematics", name: "Applied Mathematics", color: "#7c3aed" },
  { slug: "chemistry", name: "Chemistry", color: "#16a34a" },
  { slug: "geography", name: "Geography", color: "#ca8a04" },
  { slug: "history", name: "History", color: "#b91c1c" },
  { slug: "english", name: "English", color: "#ea580c" },
  { slug: "gaeilge", name: "Gaeilge", color: "#059669" },
  { slug: "computer_science", name: "Computer Science", color: "#475569" },
];

const FOUNDATIONS = [
  "5 NCCA Key Competencies",
  "SC L1/L2 Programme Statement",
  "SCR Advisory Report",
  "Online Learning Potential",
  "Online Certification Potential",
];

function AboutPage() {
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-4xl font-bold text-emerald-400">
          About cianfhoghlaim
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl">
          A self-hostable consolidation of Leaving Certificate education system resources.
        </p>
      </div>

      <CiTextbookPanel title="What cianfhoghlaim is" material="parchment">
        <p className="text-slate-300 mb-3">
          cianfhoghlaim is the agentic tutorial for the cianfhoghlaim data
          engineering pipeline that backs it. The 9 ADK agents (8 NCCA
          subject specialists + 1 cianfhoghlaim operator) are wired to the
          dlt/ + cocoindex/ + baml_src/ + meaisínfhoghlaim/ pipeline. The
          site IS the demo of the platform itself.
        </p>
        <p className="text-slate-300">
          Anyone can <code className="text-emerald-400">git clone</code> the
          repo and run their own instance. Reduce barriers to education.
        </p>
      </CiTextbookPanel>

      <CiTextbookPanel title="8 NCCA Subjects" material="knotwork">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {SUBJECTS.map((s) => (
            <Link
              key={s.slug}
              to={`/en/subjects/${s.slug}`}
              className="p-2 rounded text-center text-sm transition-colors hover:opacity-80"
              style={{ background: s.color + "20", color: s.color }}
            >
              {s.name}
            </Link>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="5 Foundations" material="gold-leaf">
        <ul className="space-y-1">
          {FOUNDATIONS.map((f) => (
            <li key={f} className="text-slate-300 text-sm">• {f}</li>
          ))}
        </ul>
      </CiTextbookPanel>

      <CiTextbookPanel title="6 Content Types" material="ink-wash">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
          {["Subjects", "Past Papers", "Marking Schemes", "Practice", "Foundations", "Notebooks"].map((ct) => (
            <div key={ct} className="p-2 rounded bg-slate-900 text-center text-slate-300">{ct}</div>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="The architecture (open source)" material="knotwork">
        <p className="text-slate-300 mb-3">
          cianfhoghlaim is built on the open-source agentic stack:
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
          {["TanStack Start", "TanStack AI", "TanStack DB", "CopilotKit v2", "AG-UI", "A2UI", "Convex", "better-auth v1.4", "Cloudflare Workers", "Cloudflare R2", "dlt", "CocoIndex", "baml_src", "meaisínfhoghlaim", "LanceDB", "DuckLake", "MotherDuck", "marimo"].map((t) => (
            <div key={t} className="p-2 rounded bg-slate-900 text-center text-slate-300 font-mono text-xs">{t}</div>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="The pipeline (data engineering)" material="parchment">
        <p className="text-slate-300">
          The 8 subpackages that the website reads from:
        </p>
        <ol className="space-y-2 mt-2 text-sm text-slate-300 font-mono">
          <li>1. <code className="text-amber-400">dlt/</code> — extraction (reads PDFs from leaving_certificate/, writes to MotherDuck)</li>
          <li>2. <code className="text-amber-400">cocoindex/</code> — embeddings (BGE-M3 1024-dim, written to LanceDB)</li>
          <li>3. <code className="text-amber-400">baml_src/</code> — typed extraction schemas (8 qpack_*.baml + 4 eiraic_*.baml + 1 content_types.baml)</li>
          <li>4. <code className="text-amber-400">meaisínfhoghlaim/</code> — 24-entry OCR/VLM registry (the 6-stage PDF processing pipeline)</li>
          <li>5. <code className="text-amber-400">agents/</code> — 9 ADK agents (8 NCCA + 1 cianfhoghlaim operator)</li>
          <li>6. <code className="text-amber-400">notebooks/</code> — 8 NCCA subject marimo notebooks (embedded as interactive widgets)</li>
          <li>7. <code className="text-amber-400">apps/web/</code> — TanStack Start + CopilotKit v2 + AG-UI + A2UI (this app)</li>
          <li>8. <code className="text-amber-400">apps/api/</code> — Hono + oRPC + CopilotKit AG-UI runtime (Cloudflare Workers)</li>
        </ol>
      </CiTextbookPanel>

      <CiTextbookPanel title="The personal lineage (operator-only)" material="gold-leaf">
        <p className="text-slate-400 italic text-sm">
          cianfhoghlaim is built by Cian Mac an Déisigh Uí Liatháin. The
          personal triple-crown lineage (Deacy + Lyons + Conroy) + the
          ard-rí na hÉireann aspirations + the 7 lineage clippings are
          documented in cian_mac_an_déisigh_uí_liatháin/identity/ but
          operator-only — they are not on the public surface. The public
          surface is the educational system itself.
        </p>
      </CiTextbookPanel>

      <section className="text-center pt-8 pb-12">
        <Link
          to="/en/self-host"
          className="inline-block px-6 py-3 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors"
        >
          Get started in 5 minutes →
        </Link>
      </section>
    </div>
  );
}