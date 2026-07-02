// /en/subjects — Index page listing all 8 NCCA subjects
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R1.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/subjects")({
  component: SubjectsPage,
});

const SUBJECTS = [
  { slug: "mathematics", name_en: "Mathematics", name_ga: "Mata", color: "#2563eb", deity: "The Dagda" },
  { slug: "applied_mathematics", name_en: "Applied Mathematics", name_ga: "Mata Feidhmíoch", color: "#7c3aed", deity: "Lugh (samildanach)" },
  { slug: "chemistry", name_en: "Chemistry", name_ga: "Ceimic", color: "#16a34a", deity: "Dian Cecht" },
  { slug: "geography", name_en: "Geography", name_ga: "Tíreolaíocht", color: "#ca8a04", deity: "Manannán mac Lir" },
  { slug: "history", name_en: "History", name_ga: "Stair", color: "#b91c1c", deity: "The Morrígan" },
  { slug: "english", name_en: "English", name_ga: "Béarla", color: "#ea580c", deity: "Brigid" },
  { slug: "gaeilge", name_en: "Gaeilge", name_ga: "Gaeilge", color: "#059669", deity: "Ogma" },
  { slug: "computer_science", name_en: "Computer Science", name_ga: "Ríomheolaíocht", color: "#475569", deity: "— (modern subject)" },
];

function SubjectsPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          The 8 NCCA Subjects
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          The 8 NCCA Leaving Certificate subjects — each mapped to one of the
          8 Brown Ajah members of the White Tower.
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
          cianfhoghlaim-leaving-cert-portal/spec.md Requirement R1
        </p>
      </div>

      <CiTextbookPanel title="The 8 NCCA Subjects" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {SUBJECTS.map((s) => (
            <Link
              key={s.slug}
              to={`/en/leaving-cert/${s.slug}`}
              className="p-4 rounded-xl bg-slate-900 border-2 hover:border-amber-400 transition-colors"
              style={{ borderColor: s.color }}
            >
              <h3 className="font-bold text-base text-slate-100">{s.name_en}</h3>
              <p className="text-xs text-slate-400 italic mt-1">{s.name_ga}</p>
              <p className="text-xs text-slate-500 mt-2">↔ {s.deity}</p>
              <p className="text-xs font-mono mt-1" style={{ color: s.color }}>
                {s.color}
              </p>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="The 7 Legacy Compat Subjects" material="parchment">
        <p className="text-slate-300 mb-4">
          The 2026 LC exam window ships 7 legacy compat subjects + 8 new NCCA subjects.
          The 7 legacy compat subjects are:
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {[
            { slug: "irish", name_en: "Irish", name_ga: "Gaeilge" },
            { slug: "biology", name_en: "Biology", name_ga: "Bitheolaíocht" },
            { slug: "french", name_en: "French", name_ga: "Fraincis" },
            { slug: "business", name_en: "Business", name_ga: "Gnó" },
            { slug: "construction-studies", name_en: "Construction Studies", name_ga: "Staidéar Tógála" },
          ].map((s) => (
            <Link
              key={s.slug}
              to={`/en/leaving-cert/${s.slug}`}
              className="p-2 rounded-lg bg-slate-900 border border-slate-700 hover:border-emerald-700 transition-colors"
            >
              <div className="text-sm font-medium text-slate-100">{s.name_en}</div>
              <div className="text-xs text-slate-400 italic">{s.name_ga}</div>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}