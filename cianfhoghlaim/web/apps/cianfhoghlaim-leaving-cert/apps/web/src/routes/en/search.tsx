// /en/search — Search the cianfhoghlaim site
// Per the new branding: cianfhoghlaim, not Cianfhoghlaim OS.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";
import { useState, useMemo } from "react";

export const Route = createFileRoute("/en/search")({
  component: SearchPage,
});

const PAGES = [
  { path: "/", title: "Home", snippet: "Self-hostable consolidation of LC education resources" },
  { path: "/en/foundations", title: "5 Foundations", snippet: "5 NCCA root-level programme PDFs" },
  { path: "/en/foundations/key-competencies", title: "5 Key Competencies", snippet: "Communicating, Information Processing, etc." },
  { path: "/en/foundations/sc-l1-l2-programme", title: "SC L1/L2 Programme", snippet: "Senior Cycle programme statement" },
  { path: "/en/foundations/scr-advisory", title: "SCR Advisory", snippet: "Chief Examiner commentary" },
  { path: "/en/foundations/online-learning", title: "Online Learning", snippet: "NCCA online learning potential" },
  { path: "/en/foundations/online-certification", title: "Online Certification", snippet: "NCCA certification + reporting potential" },
  { path: "/en/subjects/mathematics", title: "Mathematics", snippet: "Pure mathematics at LC" },
  { path: "/en/subjects/applied_mathematics", title: "Applied Mathematics", snippet: "Real-world problem modelling" },
  { path: "/en/subjects/chemistry", title: "Chemistry", snippet: "Atomic structure, bonding, organic" },
  { path: "/en/subjects/geography", title: "Geography", snippet: "Physical + regional geography" },
  { path: "/en/subjects/history", title: "History", snippet: "Modern Irish + European history" },
  { path: "/en/subjects/english", title: "English", snippet: "Comprehension, composition, poetry" },
  { path: "/en/subjects/gaeilge", title: "Gaeilge", snippet: "Léamh, scríbhneoireacht, cluastuiscint" },
  { path: "/en/subjects/computer_science", title: "Computer Science", snippet: "Algorithms, data structures, systems" },
  { path: "/en/agents", title: "9 ADK Agents", snippet: "8 NCCA subject specialists + 1 operator" },
  { path: "/en/agents/cianfhoghlaim", title: "cianfhoghlaim Operator Agent", snippet: "The repo self-reference agent" },
  { path: "/en/self-host", title: "Self-host in 5 minutes", snippet: "git clone + bun install + bun run dev" },
];

function SearchPage() {
  const [query, setQuery] = useState("");

  const results = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase();
    return PAGES.filter((p) =>
      p.title.toLowerCase().includes(q) ||
      p.snippet.toLowerCase().includes(q) ||
      p.path.toLowerCase().includes(q),
    );
  }, [query]);

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-emerald-400">
          Search cianfhoghlaim
        </h1>
        <p className="text-slate-400">
          {PAGES.length} pages indexed · client-side search
        </p>
      </div>

      <CiTextbookPanel title="Search" material="parchment">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type to search (e.g. 'mathematics', 'Brown Ajah', 'Éraic', 'self-host')..."
          className="w-full px-4 py-3 rounded-lg bg-slate-800 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-700"
        />
        {query && (
          <p className="text-sm text-slate-500 mt-2">
            {results.length} result{results.length !== 1 ? "s" : ""} for "{query}"
          </p>
        )}
        {results.length > 0 && (
          <div className="space-y-2 mt-4">
            {results.map((r) => (
              <Link
                key={r.path}
                to={r.path}
                className="block p-3 rounded-lg bg-slate-900 border border-slate-700 hover:border-emerald-700 transition-colors"
              >
                <div className="text-sm font-medium text-slate-100">{r.title}</div>
                <div className="text-xs text-slate-400 font-mono">{r.path}</div>
                <div className="text-xs text-slate-500 mt-1">{r.snippet}</div>
              </Link>
            ))}
          </div>
        )}
        {query && results.length === 0 && (
          <p className="text-slate-500 italic mt-2">
            No results. Try a different search term.
          </p>
        )}
      </CiTextbookPanel>
    </div>
  );
}