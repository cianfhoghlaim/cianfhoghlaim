// /en/key-competencies — Public Key Competencies matrix (5 × 8)
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// agentic-frontend-frameworks/spec.md R7.

import { createFileRoute } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";
import { CiSemanticPill } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/key-competencies")({
  component: KeyCompetenciesPage,
});

const KEY_COMPETENCIES = [
  {
    slug: "communicating",
    name_en: "Communicating",
    name_ga: "Cumarsáid",
    tuatha_de: "Brigid",
    color: "#059669",
    description: "The healing of the language — bilingual EN+GA throughout.",
  },
  {
    slug: "information-processing",
    name_en: "Information Processing",
    name_ga: "Próiseáil Faisnéise",
    tuatha_de: "Ogma",
    color: "#2563eb",
    description: "The healing of the data — Ogma invented Ogham.",
  },
  {
    slug: "critical-creative-thinking",
    name_en: "Critical & Creative Thinking",
    name_ga: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
    tuatha_de: "Lugh",
    color: "#ca8a04",
    description: "The healing of the reasoning — Lugh's samildanach (master of all arts).",
  },
  {
    slug: "personal-effectiveness",
    name_en: "Personal Effectiveness",
    name_ga: "Éifeachtacht Phearsanta",
    tuatha_de: "Dian Cecht",
    color: "#92400e",
    description: "The healing of the discipline — Dian Cecht was the physician of the Tuatha Dé.",
  },
  {
    slug: "working-with-others",
    name_en: "Working with Others",
    name_ga: "Ag Obair le Daoine Eile",
    tuatha_de: "Trí Dé Dána",
    color: "#b91c1c",
    description: "The healing of the community — the Trí Dé Dána (Brigid + Dian Cecht + Ogma) collectively.",
  },
];

const SUBJECTS = [
  { slug: "mathematics", name_en: "Mathematics", name_ga: "Mata", color: "#2563eb" },
  { slug: "applied_mathematics", name_en: "Applied Math", name_ga: "Mata Feidhmíoch", color: "#7c3aed" },
  { slug: "chemistry", name_en: "Chemistry", name_ga: "Ceimic", color: "#16a34a" },
  { slug: "geography", name_en: "Geography", name_ga: "Tíreolaíocht", color: "#ca8a04" },
  { slug: "history", name_en: "History", name_ga: "Stair", color: "#b91c1c" },
  { slug: "english", name_en: "English", name_ga: "Béarla", color: "#ea580c" },
  { slug: "gaeilge", name_en: "Gaeilge", name_ga: "Gaeilge", color: "#059669" },
  { slug: "computer_science", name_en: "Computer Sci.", name_ga: "Ríomheol.", color: "#475569" },
];

// Cross-subject mastery matrix (placeholder; real values from cross_subject_competency_embedding.py)
const masteryMatrix: Record<string, Record<string, number>> = {
  mathematics: { communicating: 70, "information-processing": 90, "critical-creative-thinking": 80, "personal-effectiveness": 60, "working-with-others": 50 },
  applied_mathematics: { communicating: 60, "information-processing": 95, "critical-creative-thinking": 85, "personal-effectiveness": 70, "working-with-others": 55 },
  chemistry: { communicating: 65, "information-processing": 80, "critical-creative-thinking": 75, "personal-effectiveness": 85, "working-with-others": 60 },
  geography: { communicating: 85, "information-processing": 75, "critical-creative-thinking": 70, "personal-effectiveness": 65, "working-with-others": 75 },
  history: { communicating: 90, "information-processing": 70, "critical-creative-thinking": 90, "personal-effectiveness": 60, "working-with-others": 80 },
  english: { communicating: 95, "information-processing": 60, "critical-creative-thinking": 95, "personal-effectiveness": 70, "working-with-others": 85 },
  gaeilge: { communicating: 100, "information-processing": 50, "critical-creative-thinking": 80, "personal-effectiveness": 75, "working-with-others": 70 },
  computer_science: { communicating: 55, "information-processing": 100, "critical-creative-thinking": 85, "personal-effectiveness": 80, "working-with-others": 65 },
};

function KeyCompetenciesPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          5 Key Competencies × 8 Subjects
        </h1>
        <p className="text-slate-400 text-lg">
          The cross-subject mastery matrix. Public — no auth required.
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          The 5 NCCA Key Competencies are the 5 surviving gifts of the Tuatha Dé Danann.
        </p>
      </div>

      {/* The 5 key competencies as columns */}
      <CiTextbookPanel
        title="The 5 NCCA Key Competencies"
        material="parchment"
      >
        <div className="grid grid-cols-5 gap-2">
          {KEY_COMPETENCIES.map((kc) => (
            <div key={kc.slug} className="p-3 rounded-lg border" style={{ borderColor: kc.color }}>
              <div className="text-sm font-bold text-slate-100" style={{ color: kc.color }}>
                {kc.name_en}
              </div>
              <div className="text-xs text-slate-400 italic">{kc.name_ga}</div>
              <div className="text-xs text-slate-500 mt-1">↔ {kc.tuatha_de}</div>
            </div>
          ))}
        </div>
      </CiTextbookPanel>

      {/* The 5 × 8 mastery matrix */}
      <CiTextbookPanel title="Cross-Subject Mastery Matrix" material="gold-leaf">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left text-slate-400 p-2">Subject</th>
                {KEY_COMPETENCIES.map((kc) => (
                  <th key={kc.slug} className="text-center p-2" style={{ color: kc.color }}>
                    {kc.name_en.split(" ")[0]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {SUBJECTS.map((sub) => (
                <tr key={sub.slug} className="border-t border-slate-700">
                  <td className="p-2 font-medium" style={{ color: sub.color }}>
                    {sub.name_en}
                    <div className="text-xs text-slate-500 font-mono">{sub.name_ga}</div>
                  </td>
                  {KEY_COMPETENCIES.map((kc) => {
                    const value = masteryMatrix[sub.slug]?.[kc.slug] ?? 0;
                    return (
                      <td key={kc.slug} className="p-2 text-center">
                        <CiSemanticPill
                          kind={
                            value >= 90 ? "mastered" :
                            value >= 70 ? "proficient" :
                            value >= 40 ? "familiar" :
                            "attempted"
                          }
                          label={`${value}%`}
                        />
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CiTextbookPanel>

      {/* The 5 Key Competencies descriptions */}
      <div className="grid grid-cols-1 gap-3">
        {KEY_COMPETENCIES.map((kc) => (
          <CiTextbookPanel key={kc.slug} title={kc.name_en} material="knotwork">
            <div className="flex items-start gap-4">
              <div
                className="shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl"
                style={{ background: kc.color }}
              >
                ★
              </div>
              <div>
                <div className="text-xs text-slate-400 italic">{kc.name_ga}</div>
                <div className="text-sm text-slate-300 mt-1">{kc.description}</div>
                <div className="text-xs text-slate-500 mt-1">
                  Brown Ajah member ↔ Tuatha Dé deity: <strong>{kc.tuatha_de}</strong>
                </div>
              </div>
            </div>
          </CiTextbookPanel>
        ))}
      </div>
    </div>
  );
}