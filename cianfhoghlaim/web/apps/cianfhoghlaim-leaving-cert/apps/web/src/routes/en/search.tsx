// /en/search — Public search index for the Cianfhoghlaim OS
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2 —
// a simple client-side search over the public pages.

import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";
import { useState, useMemo } from "react";

export const Route = createFileRoute("/en/search")({
  component: SearchPage,
});

const PAGES = [
  { path: "/", title: "Home", snippet: "Landing page with 6 subnations of the British Isles" },
  { path: "/en/brown-ajah", title: "Brown Ajah", snippet: "The 8 Brown Ajah members (healers + scholars + Earth-workers)" },
  { path: "/en/diagrams", title: "4 Diagram Modes", snippet: "Concept-map + topic-heatmap + PCLM-flow + question-sankey" },
  { path: "/en/eiraic-treasures", title: "13 Éraic Treasures", snippet: "The 13 magical treasures Lugh demanded as éraic for Cian's death" },
  { path: "/en/key-competencies", title: "5×8 Mastery Matrix", snippet: "The 5 NCCA Key Competencies × 8 NCCA subjects mastery matrix" },
  { path: "/en/key-competencies/emblems", title: "5 Emblems", snippet: "The 5 NCCA Key Competencies emblems (Trí Dé Dána emphasis)" },
  { path: "/en/lore-archive", title: "7 Lineage Clippings", snippet: "The 7 Wikipedia clippings that ground the theming" },
  { path: "/en/map", title: "British Isles Map", snippet: "Accurate map of the 6 subnations + 5 NCCA Key Competencies land-marks" },
  { path: "/en/practice", title: "Practice", snippet: "Start a practice session (subject + topic picker)" },
  { path: "/en/subjects", title: "8 NCCA Subjects", snippet: "Index of all 8 NCCA subjects + 7 legacy compat" },
  { path: "/en/about", title: "About", snippet: "The public about page (operator-only lore referenced)" },
  { path: "/ga/about", title: "About (GA)", snippet: "An leathanach faoin (Gaeilge)" },
];

function SearchPage() {
  const navigate = useNavigate();
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
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          Search the Cianfhoghlaim OS
        </h1>
        <p className="text-slate-400">
          Client-side search index over the public pages
        </p>
      </div>

      <CiTextbookPanel title="Search" material="parchment">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type to search (e.g. 'treasures', 'Brown Ajah', 'mathematics')..."
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