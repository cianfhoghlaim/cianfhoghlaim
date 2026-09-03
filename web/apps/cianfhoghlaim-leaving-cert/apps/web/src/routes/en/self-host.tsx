// /en/self-host — Self-host cianfhoghlaim in 5 minutes
// Per openspec/changes/cianfhoghlaim-website-rewrite/tasks.md D.3
// Updated for the cianfhoghlaim-website-rewrite direction.

import { createFileRoute } from "@tanstack/react-router";
import { CiTextbookPanel, CiSemanticPill } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/self-host")({
  component: SelfHostPage,
});

const STEPS = [
  {
    n: 1,
    title: "Clone + install",
    minutes: 2,
    code: `git clone https://github.com/cianfhoghlaim/cianfhoghlaim.git
cd cianfhoghlaim
bun install`,
    description: "Clones the repo with the 8 NCCA subjects + 5 root-level PDFs + 6 content types + 9 ADK agents. Installs all deps.",
  },
  {
    n: 2,
    title: "Configure the data plane",
    minutes: 1,
    code: `cp .env.example .env
# Edit .env with your Cloudflare R2 + Convex + better-auth secrets
bun run configure`,
    description: "Sets up CF R2 bucket bindings + Convex deployment + better-auth v1.4 with Pocket ID OIDC discovery URL.",
  },
  {
    n: 3,
    title: "Start the dev environment",
    minutes: 1,
    code: `bun run dev
# Web: http://localhost:3082
# API: http://localhost:8787`,
    description: "Starts the Vite web dev server + the Hono oRPC API server. Both are wired to the same CopilotKit runtime + the 9 ADK agents + the dlt/ + cocoindex/ + baml_src/ data engineering pipeline.",
  },
];

const FEATURES = [
  { name: "8 NCCA subjects", desc: "Maths + Applied Maths + Chemistry + Geography + History + English + Gaeilge + Computer Science" },
  { name: "5 root-level PDFs", desc: "Key Competencies + SC L1/L2 + SCR Advisory + Online Learning + Online Certification" },
  { name: "6 content types", desc: "Subjects / Past Papers / Marking Schemes / Practice / Foundations / Notebooks" },
  { name: "9 ADK agents", desc: "8 NCCA subject specialists + 1 cianfhoghlaim operator" },
  { name: "Cloudflare Workers + R2", desc: "Production deploy target for the API + the PDFs" },
  { name: "Convex + better-auth + Pocket ID OIDC", desc: "Real-time state + auth" },
  { name: "CopilotKit v2 + AG-UI + A2UI", desc: "Agent chat with declarative UI surfaces (the dojo.ag-ui.com pattern)" },
  { name: "TanStack Start + AI + DB", desc: "Full SSR + streaming + server functions + reactive client store" },
  { name: "dlt + CocoIndex + baml_src + meaisínfhoghlaim", desc: "The 8-subpackage data engineering pipeline backing the surface" },
];

const AGENTS = [
  { id: "student", blurb: "Learning for myself — explore the 8 NCCA subjects + the 5×8 mastery matrix + practice items.", color: "#10b981" },
  { id: "teacher", blurb: "Educator with a classroom — class management tools + curriculum-aligned content + AI tutor (cianfhoghlaim operator agent).", color: "#3b82f6" },
  { id: "family", blurb: "Supporting my child — dashboard to track progress + 6 content types per subject.", color: "#f59e0b" },
  { id: "school", blurb: "AI-powered solutions — school-wide insights + 9 ADK agents + data engineering pipeline.", color: "#a855f7" },
];

function SelfHostPage() {
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-3xl font-bold text-slate-100">
          Self-host cianfhoghlaim
        </h1>
        <p className="text-slate-300 max-w-3xl">
          A self-hostable consolidation of Leaving Certificate education
          system resources. Built on the open-source agentic stack.
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          3 steps · ~5 minutes · ~250 MB Docker images
        </p>
      </div>

      {/* Steps */}
      {STEPS.map((s) => (
        <CiTextbookPanel
          key={s.n}
          title={`Step ${s.n}: ${s.title}`}
          material="parchment"
        >
          <p className="text-slate-300 mb-3">{s.description}</p>
          <pre className="bg-slate-950 border border-slate-800 rounded p-3 text-xs text-emerald-300 font-mono whitespace-pre-wrap">
{s.code}
          </pre>
        </CiTextbookPanel>
      ))}

      {/* Features */}
      <CiTextbookPanel title="What you get" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {FEATURES.map((f) => (
            <div
              key={f.name}
              className="p-3 rounded-lg bg-slate-900 border border-slate-700"
            >
              <div className="text-sm font-bold text-emerald-300">{f.name}</div>
              <div className="text-xs text-slate-400 mt-1">{f.desc}</div>
            </div>
          ))}
        </div>
      </CiTextbookPanel>

      {/* License */}
      <CiTextbookPanel title="Open Source" material="gold-leaf">
        <p className="text-slate-300 mb-3">
          cianfhoghlaim is licensed under the BUSL-1.1 with a 4-year
          transition to AGPL v3. Anyone can fork + self-host + adapt the
          system for their own country / curriculum / language.
        </p>
        <p className="text-slate-400 text-sm">
          The personal triple-crown lineage (Deacy + Lyons + Conroy) +
          the ard-rí na hÉireann aspirations + the 7 lineage clippings
          are documented but operator-only (not deployed to the public
          surface). The public surface is the educational system itself.
        </p>
      </CiTextbookPanel>
    </div>
  );
}