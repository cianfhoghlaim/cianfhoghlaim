"use client";

// <CiLCSubjectGrid> — the 6 in-scope BIEP v1 LC subjects as a clickable grid
//
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R19.
//
// The 6 in-scope subjects (per BIEP v1) are:
//   - mathematics     - chemistry     - geography
//   - gaeilge         - english       - computer_science
//
// Applied Maths + History are out-of-scope per the existing
// `2026-07-16-biiep-v1-lc-per-subject-web-surface-v1` change and would
// need a follow-up change.
//
// Each card links to the existing per-subject route and surfaces the
// per-subject BAML web schema metadata so the user knows what data
// powers each subject.
//
// Token-driven: uses --ci-subject-<slug> tokens (single source of truth,
// per R22). No hardcoded colours.

import * as React from "react";
import { cn } from "./utils";

export type LCSubjectSlug =
  | "mathematics"
  | "chemistry"
  | "geography"
  | "gaeilge"
  | "english"
  | "computer_science";

export interface LCSubjectDef {
  slug: LCSubjectSlug;
  name_en: string;
  name_ga: string;
  level_en: string;
  level_ga: string;
  href_en: string;
  href_ga: string;
  baml_web_schema: string;
  cocoindex_app: string;
  notebook: string;
  agent: string;
  /** Approximate count of past exam papers in the BIEP lakehouse. */
  paper_count_approx: number;
}

export const LC_SUBJECTS: readonly LCSubjectDef[] = [
  {
    slug: "mathematics",
    name_en: "Mathematics",
    name_ga: "Mata",
    level_en: "Ordinary + Higher",
    level_ga: "Gnáthleibhéal + Ardleibhéal",
    href_en: "/en/subjects/mathematics",
    href_ga: "/ga/subjects/mata",
    baml_web_schema: "baml/education/web/mathematics_web.baml",
    cocoindex_app: "cocoindex/mathematics_embedding.py",
    notebook: "notebooks/12_subject_study_tools/mathematics.py",
    agent: "math_agent (ADK)",
    paper_count_approx: 36,
  },
  {
    slug: "chemistry",
    name_en: "Chemistry",
    name_ga: "Ceimic",
    level_en: "Ordinary + Higher",
    level_ga: "Gnáthleibhéal + Ardleibhéal",
    href_en: "/en/subjects/chemistry",
    href_ga: "/ga/subjects/ceimic",
    baml_web_schema: "baml/education/web/chemistry_web.baml",
    cocoindex_app: "cocoindex/chemistry_embedding.py",
    notebook: "notebooks/12_subject_study_tools/chemistry.py",
    agent: "chem_agent (ADK)",
    paper_count_approx: 30,
  },
  {
    slug: "geography",
    name_en: "Geography",
    name_ga: "Tíreolaíocht",
    level_en: "Ordinary + Higher",
    level_ga: "Gnáthleibhéal + Ardleibhéal",
    href_en: "/en/subjects/geography",
    href_ga: "/ga/subjects/tireolaiocht",
    baml_web_schema: "baml/education/web/geography_web.baml",
    cocoindex_app: "cocoindex/geography_embedding.py",
    notebook: "notebooks/12_subject_study_tools/geography.py",
    agent: "geog_agent (ADK)",
    paper_count_approx: 30,
  },
  {
    slug: "gaeilge",
    name_en: "Gaeilge (Irish)",
    name_ga: "Gaeilge",
    level_en: "Ordinary + Higher (taught in Irish)",
    level_ga: "Gnáthleibhéal + Ardleibhéal (múinte trí Ghaeilge)",
    href_en: "/en/subjects/gaeilge",
    href_ga: "/ga/subjects/gaeilge",
    baml_web_schema: "baml/education/web/gaeilge_web.baml",
    cocoindex_app: "cocoindex/gaeilge_embedding.py",
    notebook: "notebooks/12_subject_study_tools/gaeilge.py",
    agent: "gael_agent (ADK)",
    paper_count_approx: 30,
  },
  {
    slug: "english",
    name_en: "English",
    name_ga: "Béarla",
    level_en: "Ordinary + Higher",
    level_ga: "Gnáthleibhéal + Ardleibhéal",
    href_en: "/en/subjects/english",
    href_ga: "/ga/subjects/bearla",
    baml_web_schema: "baml/education/web/english_web.baml",
    cocoindex_app: "cocoindex/english_embedding.py",
    notebook: "notebooks/12_subject_study_tools/english.py",
    agent: "engl_agent (ADK)",
    paper_count_approx: 30,
  },
  {
    slug: "computer_science",
    name_en: "Computer Science",
    name_ga: "Ríomheolaíocht",
    level_en: "Higher (Ordinary from 2026)",
    level_ga: "Ardleibhéal (Gnáthleibhéal ó 2026)",
    href_en: "/en/subjects/computer_science",
    href_ga: "/ga/subjects/riomheolaiocht",
    baml_web_schema: "baml/education/web/computer_science_web.baml",
    cocoindex_app: "cocoindex/computer_science_embedding.py",
    notebook: "notebooks/12_subject_study_tools/computer_science.py",
    agent: "comp_agent (ADK)",
    paper_count_approx: 12,
  },
] as const;

export interface CiLCSubjectGridProps {
  language: "en" | "ga";
  className?: string;
  onSubjectClick?: (slug: LCSubjectSlug) => void;
}

/**
 * CiLCSubjectGrid renders the 6 in-scope BIEP v1 LC subjects as a clickable
 * 3-column grid. Each card surfaces the BAML schema + CocoIndex app +
 * notebook path so the user knows what data powers each subject.
 *
 * Tokens consumed: --ci-subject-<slug> for the accent border.
 */
export function CiLCSubjectGrid({
  language,
  className,
  onSubjectClick,
}: CiLCSubjectGridProps) {
  return (
    <section
      aria-labelledby="lc-subjects-heading"
      className={cn("space-y-3", className)}
    >
      <header className="flex items-baseline justify-between">
        <h2
          id="lc-subjects-heading"
          className="text-xl font-bold text-slate-100"
        >
          {language === "ga"
            ? "Ábhair an NCCA Leaving Certificate (6)"
            : "6 NCCA Leaving Certificate Subjects"}
        </h2>
        <p className="text-xs text-slate-500 font-mono">
          {language === "ga"
            ? "BAML + BAILE + CocoIndex v1 + marimo"
            : "BAML + BICEP + CocoIndex v1 + marimo"}
        </p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {LC_SUBJECTS.map((subject) => {
          const name = language === "ga" ? subject.name_ga : subject.name_en;
          const level = language === "ga" ? subject.level_ga : subject.level_en;
          const href = language === "ga" ? subject.href_ga : subject.href_en;

          return (
            <a
              key={subject.slug}
              href={href}
              onClick={(e) => {
                if (onSubjectClick) {
                  e.preventDefault();
                  onSubjectClick(subject.slug);
                }
              }}
              data-subject={subject.slug}
              data-baml={subject.baml_web_schema}
              data-cocoindex={subject.cocoindex_app}
              className={cn(
                "group relative flex flex-col gap-2 rounded-xl border-2 bg-slate-900 p-4 transition-all",
                "hover:-translate-y-0.5 hover:shadow-lg",
              )}
              style={{ borderColor: `var(--ci-subject-${subject.slug})` }}
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3
                    className="text-lg font-bold text-slate-100"
                    style={{ color: `var(--ci-subject-${subject.slug})` }}
                  >
                    {name}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">{level}</p>
                </div>
                <span className="rounded-full bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400 font-mono">
                  v1 active
                </span>
              </div>
              <dl className="grid grid-cols-2 gap-1 text-[10px] font-mono text-slate-400">
                <dt className="text-slate-500">BAML</dt>
                <dd className="truncate text-slate-300">{subject.baml_web_schema.split("/").pop()}</dd>
                <dt className="text-slate-500">CocoIndex</dt>
                <dd className="truncate text-slate-300">{subject.cocoindex_app.split("/").pop()}</dd>
                <dt className="text-slate-500">Agent</dt>
                <dd className="truncate text-slate-300">{subject.agent}</dd>
                <dt className="text-slate-500">Marimo</dt>
                <dd className="truncate text-slate-300">{subject.notebook.split("/").pop()}</dd>
              </dl>
              <div className="mt-2 flex items-center justify-between text-[11px]">
                <span className="text-slate-500">
                  {language === "ga"
                    ? `≈${subject.paper_count_approx} scrúdpháipéar`
                    : `≈${subject.paper_count_approx} past papers`}
                </span>
                <span className="opacity-0 transition-opacity group-hover:opacity-100 text-amber-400">
                  {language === "ga" ? "Oscail" : "Open"} →
                </span>
              </div>
            </a>
          );
        })}
      </div>
    </section>
  );
}
