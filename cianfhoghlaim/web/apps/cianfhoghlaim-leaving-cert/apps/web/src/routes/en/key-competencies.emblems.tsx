// /en/key-competencies/emblems — The 5 NCCA Key Competencies emblems page
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T7.18.
// The 5 emblems represent the 5 NCCA Key Competencies (Trí Dé Dána emphasis).

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/key-competencies/emblems")({
  component: EmblemsPage,
});

const EMBLEMS = [
  {
    code: "KC-CO",
    name_en: "Communicating",
    name_ga: "Cumarsáid",
    tuatha_de: "Brigid",
    tuatha_de_role: "Poetry + healing",
    color: "#059669",
    svg_path: "M 8 16 Q 12 8 16 16 Q 20 24 24 16", // Wave/poetry
    description: "The healing of the language — bilingual EN+GA throughout.",
  },
  {
    code: "KC-IP",
    name_en: "Information Processing",
    name_ga: "Próiseáil Faisnéise",
    tuatha_de: "Ogma",
    tuatha_de_role: "Eloquence + learning (inventor of Ogham)",
    color: "#2563eb",
    svg_path: "M 16 8 L 24 16 L 16 24 L 8 16 Z", // Diamond (Ogham-inspired)
    description: "The healing of the data — Ogma invented Ogham, the earliest Celtic script.",
  },
  {
    code: "KC-CT",
    name_en: "Critical & Creative Thinking",
    name_ga: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
    tuatha_de: "Lugh",
    tuatha_de_role: "Samildanach (master of all arts)",
    color: "#ca8a04",
    svg_path: "M 16 8 L 22 14 L 22 22 L 16 18 L 10 22 L 10 14 Z", // Star/sun
    description: "The healing of the reasoning — Lugh's samildanach is the master of all arts.",
  },
  {
    code: "KC-PE",
    name_en: "Personal Effectiveness",
    name_ga: "Éifeachtacht Phearsanta",
    tuatha_de: "Dian Cecht",
    tuatha_de_role: "Healing (the physician of the Tuatha Dé)",
    color: "#92400e",
    svg_path: "M 8 16 Q 12 8 16 16 Q 20 24 24 16", // Caudal/serpent
    description: "The healing of the discipline — Dian Cecht was the physician.",
  },
  {
    code: "KC-WO",
    name_en: "Working with Others",
    name_ga: "Ag Obair le Daoine Eile",
    tuatha_de: "Trí Dé Dána",
    tuatha_de_role: "Brigid + Dian Cecht + Ogma (collectively)",
    color: "#b91c1c",
    svg_path: "M 8 8 L 24 8 L 24 24 L 8 24 Z M 12 12 L 20 12 L 20 20 L 12 20 Z", // Concentric squares (3 craftsmen)
    description: "The healing of the community — the Trí Dé Dána collectively.",
  },
];

function EmblemsPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          The 5 NCCA Key Competencies Emblems
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          The 5 surviving gifts of the Tuatha Dé Danann. The 3 emphasised
          emblems map to the <strong>Trí Dé Dána</strong> (Brigid + Dian Cecht +
          Ogma) — the Three Gods of Craft. The 5 emblems are the visual
          representation of the cross-subject mastery tier.
        </p>
      </div>

      <CiTextbookPanel title="The 5 Emblems" material="gold-leaf">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {EMBLEMS.map((e) => (
            <Link
              key={e.code}
              to="/en/key-competencies"
              className="flex flex-col items-center p-4 rounded-xl bg-slate-900 border-2 hover:border-amber-400 transition-colors"
              style={{ borderColor: e.color }}
            >
              <svg
                width="80"
                height="80"
                viewBox="0 0 32 32"
                xmlns="http://www.w3.org/2000/svg"
                className="mb-3"
              >
                <circle cx="16" cy="16" r="14" fill={e.color} stroke="#f59e0b" strokeWidth="1" />
                <path
                  d={e.svg_path}
                  fill="none"
                  stroke="#f8fafc"
                  strokeWidth="1.5"
                />
                <text
                  x="16"
                  y="30"
                  fill="#f8fafc"
                  fontSize="3"
                  textAnchor="middle"
                >
                  {e.code}
                </text>
              </svg>
              <h3 className="font-bold text-sm text-slate-100 text-center">{e.name_en}</h3>
              <p className="text-xs text-slate-400 italic text-center">{e.name_ga}</p>
              <p className="text-xs text-slate-500 mt-1 text-center">↔ {e.tuatha_de}</p>
            </Link>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="The Trí Dé Dána Mapping" material="ink-wash">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <CiDetailCell
            icon={<span className="font-cinzel text-2xl text-emerald-400">⚕</span>}
            title="Brigid → Communicating"
            metadata="Poetry + healing"
            description="The healing of the language. Maps to the Communicating competency (the verb + the noun, the word + the song)."
          />
          <CiDetailCell
            icon={<span className="font-cinzel text-2xl text-blue-400">⚒</span>}
            title="Dian Cecht → Personal Effectiveness"
            metadata="Healing (the physician of the Tuatha Dé)"
            description="The healing of the discipline. Maps to the Personal Effectiveness competency (the disciplined study of the self)."
          />
          <CiDetailCell
            icon={<span className="font-cinzel text-2xl text-amber-400">✎</span>}
            title="Ogma → Information Processing"
            metadata="Eloquence + learning (inventor of Ogham)"
            description="The healing of the data. Maps to the Information Processing competency (the processing of language into information)."
          />
        </div>
      </CiTextbookPanel>
    </div>
  );
}