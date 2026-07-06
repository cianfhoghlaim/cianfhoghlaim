// /en/self-host — Self-host cianfhoghlaim in 5 minutes
// Per the user's instruction: cianfhoghlaim is a self-hostable
// consolidation of education system resources that helps reduce
// barriers to education.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell, CiSemanticPill } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/self-host")({
  component: SelfHostPage,
});

function SelfHostPage() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <div className="text-sm text-slate-500 font-mono">cianfhoghlaim / self-host</div>
        <h1 className="font-cinzel text-4xl font-bold text-emerald-400">
          Self-host cianfhoghlaim
        </h1>
        <p className="text-slate-300 text-lg max-w-3xl">
          A self-hostable consolidation of Leaving Certificate education
          system resources. Anyone can deploy their own instance — for
          a school, a study group, a country, or just yourself.
        </p>
        <p className="text-slate-500 text-sm">
          Reduce barriers to education · open source · MIT
        </p>
      </div>

      <CiTextbookPanel title="3-step install" material="knotwork">
        <ol className="space-y-3 text-slate-300">
          <li className="flex items-start gap-2">
            <span className="text-amber-400 font-mono">1.</span>
            <div>
              <div className="font-mono text-amber-400 mb-1">git clone https://github.com/cianfhoghlaim/cianfhoghlaim.git</div>
              <div className="text-sm text-slate-400">Clones the repo with the 8 NCCA subjects + the 5 root-level PDFs + the 9 ADK agents</div>
            </div>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-400 font-mono">2.</span>
            <div>
              <div className="font-mono text-amber-400 mb-1">cd cianfhoghlaim && bun install</div>
              <div className="text-sm text-slate-400">Installs the 8 cianfhoghlaim subpackages (dlt + cocoindex + baml + agents + notebooks + apps/web + apps/api)</div>
            </div>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-amber-400 font-mono">3.</span>
            <div>
              <div className="font-mono text-amber-400 mb-1">bun run dev</div>
              <div className="text-sm text-slate-400">Starts the 9 ADK agents (8 NCCA + 1 operator) + the Convex conic-leaving-cert deployment + the 4 diagram modes + the 5 NCCA Key Competencies masteryx matrix</div>
            </div>
          </li>
        </ol>
      </CiTextbookPanel>

      <CiTextbookPanel title="What you get" material="parchment">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { name: "8 NCCA subjects", desc: "Maths + Applied Maths + Chemistry + Geography + History + English + Gaeilge + CS" },
            { name: "5 root-level PDFs", desc: "Key Competencies + SC L1/L2 + SCR Advisory + Online Learning + Online Certification" },
            { name: "9 ADK agents", desc: "8 NCCA subject specialists + 1 cianfhoghlaim operator" },
            { name: "4 diagram modes", desc: "Concept-map + topic-heatmap + PCLM-flow + question-sankey" },
            { name: "Practice page", desc: "3-way boon choice + 4 feedback channels + streak flame + 4-tier mastery" },
            { name: "5 NCCA Key Competencies", desc: "Communicating + Information Processing + Critical Thinking + Personal Effectiveness + Working with Others" },
            { name: "British Isles map", desc: "Accurate map of 6 subnations + 5 land-marks + Connacht province detail" },
            { name: "13 éraic tier system", desc: "13-tier mastery progression tied to the 13 Irish mythological treasures" },
          ].map((f) => (
            <CiDetailCell
              key={f.name}
              icon={<span className="text-lg">✓</span>}
              title={f.name}
              metadata=""
              description={f.desc}
            />
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="Architecture" material="ink-wash">
        <p className="text-slate-300 mb-3">
          The cianfhoghlaim architecture is the agentic tutorial for the
          repo itself. The flow is:
        </p>
        <ol className="space-y-2 text-sm text-slate-300 font-mono">
          <li>1. <code className="text-amber-400">dlt/</code> — extract NCCA syllabus + past papers + marking schemes</li>
          <li>2. <code className="text-amber-400">cocoindex/</code> — embed the extracted content into LanceDB (BGE-M3 1024-dim)</li>
          <li>3. <code className="text-amber-400">baml_src/</code> — the typed extraction schemas (8 qpack_*.baml per subject + 4 diagram_renderer.baml + 5 root_pdf_extraction.baml)</li>
          <li>4. <code className="text-amber-400">agents/</code> — the 8 NCCA ADK subject specialists + the 1 cianfhoghlaim operator</li>
          <li>5. <code className="text-amber-400">meaisinfhoghlaim/</code> — the 24-entry OCR/VLM registry + 6 backend adapters</li>
          <li>6. <code className="text-amber-400">apps/web/</code> — TanStack Start + CopilotKit v2 + Convex + better-auth v1.4</li>
          <li>7. <code className="text-amber-400">apps/api/</code> — Hono + oRPC + CopilotKit AG-UI runtime</li>
        </ol>
      </CiTextbookPanel>

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