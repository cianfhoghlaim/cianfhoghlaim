// /en/agents — 9 ADK agents index (8 NCCA subject specialists + 1 cianfhoghlaim operator)
// Per the user's instruction: cianfhoghlaim website is the agentic tutorial for the repo

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell } from "@cianfhoghlaim/ui-kit/lc";

export const Route = createFileRoute("/agents")({
  component: AgentsIndex,
});

const AGENTS = [
  { slug: "mathematics", name: "Mathematics Agent", color: "var(--ci-subject-mathematics)", desc: "Pure mathematics at LC: algebra, functions, calculus, probability." },
  { slug: "applied_mathematics", name: "Applied Mathematics Agent", color: "var(--ci-subject-applied_mathematics)", desc: "Modelling real-world problems: mechanics, statistics, probability." },
  { slug: "chemistry", name: "Chemistry Agent", color: "var(--ci-subject-chemistry)", desc: "Atomic structure, bonding, stoichiometry, organic chemistry." },
  { slug: "geography", name: "Geography Agent", color: "var(--ci-subject-geography)", desc: "Physical + regional geography: climate, geomorphology, development." },
  { slug: "history", name: "History Agent", color: "var(--ci-subject-history)", desc: "Modern Irish + European history: Early Modern, Modern, Contemporary." },
  { slug: "english", name: "English Agent", color: "var(--ci-subject-english)", desc: "Comprehension, composition, comparative + single text, poetry." },
  { slug: "gaeilge", name: "Gaeilge Agent", color: "var(--ci-subject-gaeilge)", desc: "Léamh, scríbhneoireach, cluastuiscint, litríocht, gramadach." },
  { slug: "computer_science", name: "Computer Science Agent", color: "var(--ci-subject-computer_science)", desc: "Algorithms, data structures, computer systems, networks." },
  { slug: "cianfhoghlaim", name: "cianfhoghlaim Operator Agent", color: "#f59e0b", desc: "The repo self-reference agent. Has access to the README + dlt/ + cocoindex/ + baml_src/ + meaisinfhoghlaim/. The 9th ADK agent." },
];

function AgentsIndex() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <div className="text-sm text-slate-500 font-mono">cianfhoghlaim / agents</div>
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          9 ADK Agents
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          8 NCCA Leaving Certificate subject specialists + 1 cianfhoghlaim
          operator agent. The cianfhoghlaim website is the agentic tutorial
          for the repo itself.
        </p>
      </div>

      <CiTextbookPanel title="The 9 Agents" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {AGENTS.map((a) => (
            <Link
              key={a.slug}
              to={`/en/agents/${a.slug}`}
              className="p-4 rounded-lg bg-slate-900 border-2 hover:border-amber-400 transition-colors"
              style={{ borderColor: a.color }}
            >
              <h3 className="font-bold text-base" style={{ color: a.color }}>
                {a.name}
              </h3>
              <p className="text-xs text-slate-400 font-mono mt-1">
                {a.slug}_agent
              </p>
              <p className="text-sm text-slate-300 mt-2">{a.desc}</p>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}