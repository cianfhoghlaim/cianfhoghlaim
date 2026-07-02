// /en/key-competencies — Public Key Competencies matrix (5 × 8)
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// agentic-frontend-frameworks/spec.md R7.

import { createFileRoute } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";
import {
  getMasteryForCell,
  getMasteryForSubject,
  getMasteryRowAverage,
  KEY_COMPETENCY_SLUGS,
  MASTERY_MATRIX,
  SUBJECT_SLUGS,
  type KeyCompetencySlug,
  type SubjectSlug,
} from "@cianfhoghlaim/i18n/mastery";

export const Route = createFileRoute("/en/key-competencies")({
  component: KeyCompetenciesPage,
});

const KEY_COMPETENCIES: ReadonlyArray<{
  slug: KeyCompetencySlug;
  name_en: string;
  name_ga: string;
  tuatha_de: string;
  color: string;
  description: string;
}> = [
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

const SUBJECTS: ReadonlyArray<{
  slug: SubjectSlug;
  name_en: string;
  name_ga: string;
  color: string;
}> = [
  { slug: "mathematics", name_en: "Mathematics", name_ga: "Mata", color: "#2563eb" },
  { slug: "applied_mathematics", name_en: "Applied Math", name_ga: "Mata Feidhmíoch", color: "#7c3aed" },
  { slug: "chemistry", name_en: "Chemistry", name_ga: "Ceimic", color: "#16a34a" },
  { slug: "geography", name_en: "Geography", name_ga: "Tíreolaíocht", color: "#ca8a04" },
  { slug: "history", name_en: "History", name_ga: "Stair", color: "#b91c1c" },
  { slug: "english", name_en: "English", name_ga: "Béarla", color: "#ea580c" },
  { slug: "gaeilge", name_en: "Gaeilge", name_ga: "Gaeilge", color: "#059669" },
  { slug: "computer_science", name_en: "Computer Sci.", name_ga: "Ríomheol.", color: "#475569" },
];

type MasteryTier = "mastered" | "proficient" | "familiar" | "attempted";

function tierFor(value: number): MasteryTier {
  if (value >= 90) return "mastered";
  if (value >= 70) return "proficient";
  if (value >= 40) return "familiar";
  return "attempted";
}

const TIER_BAR: Record<MasteryTier, string> = {
  mastered: "#10b981",
  proficient: "#3b82f6",
  familiar: "#f59e0b",
  attempted: "#64748b",
};

const TIER_LABEL: Record<MasteryTier, string> = {
  mastered: "Mastered",
  proficient: "Proficient",
  familiar: "Familiar",
  attempted: "Attempted",
};

function MasteryBar({
  value,
  showLabel = true,
  width = "w-full",
}: {
  value: number;
  showLabel?: boolean;
  width?: string;
}) {
  const tier = tierFor(value);
  const color = TIER_BAR[tier];
  return (
    <div className={`flex flex-col gap-1 ${width}`}>
      {showLabel && (
        <div className="flex items-baseline justify-between gap-1">
          <span className="text-xs font-mono font-bold text-slate-100">{value}%</span>
          <span className="text-[9px] uppercase tracking-wider text-slate-500">
            {TIER_LABEL[tier]}
          </span>
        </div>
      )}
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${value}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

function getColumnAverage(competency: KeyCompetencySlug): number {
  const sum = SUBJECT_SLUGS.reduce(
    (acc, s) => acc + getMasteryForCell(s, competency),
    0,
  );
  return Math.round(sum / SUBJECT_SLUGS.length);
}

function getOverallAverage(): number {
  const sum = SUBJECT_SLUGS.reduce((acc, s) => acc + getMasteryRowAverage(s), 0);
  return Math.round(sum / SUBJECT_SLUGS.length);
}

function KeyCompetenciesPage() {
  const overallAverage = getOverallAverage();
  const columnAverages = KEY_COMPETENCY_SLUGS.map((kc) => ({
    slug: kc,
    value: getColumnAverage(kc),
  }));

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
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr>
                <th className="text-left text-slate-400 p-2 align-bottom">Subject</th>
                {KEY_COMPETENCIES.map((kc) => (
                  <th key={kc.slug} className="text-center p-2 align-bottom" style={{ color: kc.color }}>
                    <div className="text-[11px] font-bold leading-tight">
                      {kc.name_en.split(" ")[0]}
                    </div>
                    <div className="text-[9px] text-slate-500 italic font-normal mt-0.5">
                      {kc.tuatha_de}
                    </div>
                  </th>
                ))}
                <th className="text-center p-2 align-bottom bg-slate-900/60 rounded-t-lg">
                  <div className="text-[11px] font-bold text-amber-400 leading-tight">
                    Row Avg
                  </div>
                  <div className="text-[9px] text-slate-500 italic font-normal mt-0.5">
                    subject
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
              {SUBJECTS.map((sub) => {
                const rowAvg = getMasteryRowAverage(sub.slug);
                const row = getMasteryForSubject(sub.slug);
                return (
                  <tr key={sub.slug} className="border-t border-slate-700">
                    <td className="p-2 font-medium align-middle" style={{ color: sub.color }}>
                      {sub.name_en}
                      <div className="text-xs text-slate-500 font-mono">{sub.name_ga}</div>
                    </td>
                    {KEY_COMPETENCIES.map((kc) => {
                      const value = row[kc.slug];
                      return (
                        <td key={kc.slug} className="p-2 align-middle">
                          <MasteryBar value={value} />
                        </td>
                      );
                    })}
                    <td className="p-2 align-middle bg-slate-900/40">
                      <MasteryBar value={rowAvg} />
                    </td>
                  </tr>
                );
              })}
              {/* Per-column average row */}
              <tr className="border-t-2 border-amber-700/60 bg-slate-900/30">
                <td className="p-2 font-bold text-amber-400 align-middle">
                  Column Avg
                  <div className="text-[10px] text-slate-500 font-mono font-normal">
                    competency
                  </div>
                </td>
                {columnAverages.map(({ slug, value }) => (
                  <td key={slug} className="p-2 align-middle">
                    <MasteryBar value={value} />
                  </td>
                ))}
                {/* Overall platform average */}
                <td className="p-2 align-middle bg-amber-900/20 border-l border-amber-700/40">
                  <div className="flex flex-col gap-1 w-full">
                    <div className="flex items-baseline justify-between gap-1">
                      <span className="text-xs font-mono font-bold text-amber-300">
                        {overallAverage}%
                      </span>
                      <span className="text-[9px] uppercase tracking-wider text-amber-500/80">
                        Platform
                      </span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${overallAverage}%`,
                          background: "linear-gradient(90deg, #f59e0b, #fbbf24)",
                        }}
                      />
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex flex-wrap items-center justify-center gap-3 text-[10px] text-slate-500">
          <span className="flex items-center gap-1">
            <span className="inline-block w-3 h-1.5 rounded-full" style={{ backgroundColor: TIER_BAR.mastered }} />
            Mastered ≥90
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-3 h-1.5 rounded-full" style={{ backgroundColor: TIER_BAR.proficient }} />
            Proficient ≥70
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-3 h-1.5 rounded-full" style={{ backgroundColor: TIER_BAR.familiar }} />
            Familiar ≥40
          </span>
          <span className="flex items-center gap-1">
            <span className="inline-block w-3 h-1.5 rounded-full" style={{ backgroundColor: TIER_BAR.attempted }} />
            Attempted &lt;40
          </span>
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

      <div className="text-center text-xs text-slate-600 italic pb-4">
        Values sourced from <code className="font-mono">packages/i18n/src/mastery.ts</code>
        {" "}(v1 fallback — the live pipeline will eventually be{" "}
        <code className="font-mono">cross_subject_competency_embedding.py</code>).
      </div>
    </div>
  );
}

export default KeyCompetenciesPage;