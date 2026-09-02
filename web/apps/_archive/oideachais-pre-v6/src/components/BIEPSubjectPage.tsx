// apps/web/src/components/BIEPSubjectPage.tsx
// The shared BIEP per-subject page renderer. Used by:
//   - /en/subjects/{mathematics,chemistry,geography,gaeilge,english,computer_science}.tsx
//   - /ga/subjects/{mata,ceimic,tireolaiocht,gaeilge,bearla,riomheolaiocht}.tsx
// Renders: subject header + 5×8 mastery matrix + 5 BIEP visualizations +
// marimo notebook embed + the 5 NCCA Key Competencies summary.
//
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1.

import * as React from "react";
import { Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiSemanticPill } from "@cianfhoghlaim/ui-kit/lc";
import {
  getMasteryForCell,
  KEY_COMPETENCY_SLUGS,
  type KeyCompetencySlug,
} from "../../../../packages/i18n/src/mastery";
import {
  type BIEPSubjectDef,
  type BIEPLanguage,
} from "../lib/bi-ep";

const KC_COLOR: Record<KeyCompetencySlug, string> = {
  "communicating": "#059669",
  "information-processing": "#2563eb",
  "critical-creative-thinking": "#ca8a04",
  "personal-effectiveness": "#92400e",
  "working-with-others": "#b91c1c",
};

const KC_LABEL_EN: Record<KeyCompetencySlug, string> = {
  "communicating": "Communicating",
  "information-processing": "Information Processing",
  "critical-creative-thinking": "Critical & Creative Thinking",
  "personal-effectiveness": "Personal Effectiveness",
  "working-with-others": "Working with Others",
};

const KC_LABEL_GA: Record<KeyCompetencySlug, string> = {
  "communicating": "Cumarsáid",
  "information-processing": "Próiseáil Faisnéise",
  "critical-creative-thinking": "Smaointeoireacht Chriticiúil agus Chruthaitheach",
  "personal-effectiveness": "Éifeachtacht Phearsanta",
  "working-with-others": "Ag Obair le Daoine Eile",
};

const LANG_DIR: Record<BIEPLanguage, "ltr"> = { en: "ltr", ga: "ltr" };

interface BIEPSubjectPageProps {
  subject: BIEPSubjectDef;
  language: BIEPLanguage;
}

export function BIEPSubjectPage({ subject, language }: BIEPSubjectPageProps) {
  const heading = subject.client.bilingual[language].heading;
  const title = subject.client.bilingual[language].title;
  const blurb = subject.client.bilingual[language].blurb;
  const linkedLang: "en" | "ga" = language === "en" ? "ga" : "en";

  const visualizations = [
    subject.client.visualizations.topic_frequency,
    subject.client.visualizations.exam_paper_difficulty,
    subject.client.visualizations.marking_scheme_complexity,
    subject.client.visualizations.cross_linguistic_mapping,
    subject.client.visualizations.asset_generator,
  ];

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6" lang={language} dir={LANG_DIR[language]}>
      {/* ── Subject header ───────────────────────────────────────────── */}
      <header className="flex flex-col gap-2">
        <div className="text-sm text-slate-500 font-mono">
          BIEP v1 · {subject.code} · NCCA LC {subject.level.toUpperCase()}
        </div>
        <h1
          className="font-cinzel text-4xl font-bold"
          style={{ color: subject.color }}
        >
          {heading}
        </h1>
        <h2 className="font-cinzel text-xl text-slate-300">{title}</h2>
        <p className="text-slate-400 text-base">{blurb}</p>
        <div className="flex flex-wrap items-center gap-2 mt-2 text-sm text-slate-500 font-mono">
          <CiSemanticPill kind="eiraic" label={`Éraic tier ${subject.eiraic_tier}/13`} />
          <CiSemanticPill kind="eiraic" label={`${subject.primary_agent}_agent`} />
          <CiSemanticPill kind="eiraic" label={subject.client.table_ref.ducklake_schema} />
          <Link
            to={`/${linkedLang}/about` as never}
            className="underline hover:opacity-80"
            style={{ color: subject.color }}
          >
            {language === "ga" ? "EN" : "GA"} mirror →
          </Link>
        </div>
      </header>

      {/* ── 5×8 mastery matrix (per-subject row) ────────────────────── */}
      <CiTextbookPanel title="5×8 Mastery Matrix (this subject)" material="parchment">
        <p className="text-slate-300 mb-3 text-sm">
          {language === "ga"
            ? "An 5 Phríochomhardaigh NCCA don ábhar seo (fíor sonraí ón maighdeanas máistreachta 5×8)."
            : "The 5 NCCA Key Competencies for this subject (real values from the 5×8 mastery matrix)."}
        </p>
        <div className="space-y-2">
          {subject.key_competencies
            .slice()
            .sort((a, b) => b.weight - a.weight)
            .map((kc) => {
              const kcSlug = kc.slug as KeyCompetencySlug;
              return (
                <div key={kc.slug} className="flex items-center gap-2">
                  <span className="text-slate-400 w-44 text-sm">
                    {language === "ga" ? KC_LABEL_GA[kcSlug] : KC_LABEL_EN[kcSlug]}
                  </span>
                  <div className="flex-1 h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${kc.weight}%`, backgroundColor: KC_COLOR[kcSlug] }}
                    />
                  </div>
                  <span className="text-slate-500 text-xs font-mono w-10 text-right">
                    {kc.weight}%
                  </span>
                </div>
              );
            })}
        </div>
      </CiTextbookPanel>

      {/* ── Per-subject BAML / DLT / Notebook metadata ──────────────── */}
      <CiTextbookPanel title="Pipeline integration (BAML + DLT + marimo)" material="ink-wash">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
          <div className="p-3 rounded bg-slate-900">
            <div className="text-xs uppercase tracking-wider text-emerald-400 font-bold">
              BAML
            </div>
            <code className="text-xs text-slate-300 break-all">
              {subject.client.baml.baml_path}
            </code>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              {subject.client.baml.functions.map((fn) => (
                <li key={fn}>
                  <code>{fn}</code>
                </li>
              ))}
            </ul>
          </div>
          <div className="p-3 rounded bg-slate-900">
            <div className="text-xs uppercase tracking-wider text-blue-400 font-bold">
              DLT
            </div>
            <code className="text-xs text-slate-300 break-all">
              {subject.client.dlt.dlt_path}
            </code>
            <ul className="mt-2 space-y-1 text-xs text-slate-400">
              {subject.client.dlt.resources.map((r) => (
                <li key={r}>
                  <code>{r}</code>
                </li>
              ))}
            </ul>
          </div>
          <div className="p-3 rounded bg-slate-900">
            <div className="text-xs uppercase tracking-wider text-amber-400 font-bold">
              marimo
            </div>
            <code className="text-xs text-slate-300 break-all">
              {subject.client.notebook.python_module}
            </code>
            <p className="mt-2 text-xs text-slate-400">
              Embed served from <code>{subject.client.notebook_embed.embed_url}</code> at{" "}
              {subject.client.notebook_embed.full_height}px tall. Reads{" "}
              <code>engine=&quot;{subject.client.kcg_patterns.mo_sql_engine}&quot;</code> via{" "}
              <code>mo.sql()</code>.
            </p>
          </div>
        </div>
      </CiTextbookPanel>

      {/* ── 5 BIEP visualizations ───────────────────────────────────── */}
      <section className="flex flex-col gap-4">
        <h2 className="font-cinzel text-2xl text-slate-100">
          {language === "ga"
            ? "5 léirshamhlú don ábhar seo"
            : "5 visualisations for this subject"}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {visualizations.map((viz) => (
            <CiTextbookPanel
              key={viz.id}
              title={language === "ga" ? viz.title_ga : viz.title}
              material="knotwork"
            >
              <p className="text-slate-300 text-sm">{viz.description}</p>
              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                {viz.baml_function && (
                  <CiSemanticPill
                    kind="eiraic"
                    label={`BAML: ${viz.baml_function}`}
                  />
                )}
                <CiSemanticPill
                  kind="eiraic"
                  label={`marimo cell: ${viz.marimo_cell}`}
                />
              </div>
            </CiTextbookPanel>
          ))}
        </div>
      </section>

      {/* ── marimo notebook embed ────────────────────────────────────── */}
      <CiTextbookPanel title="Live marimo notebook" material="gold-leaf">
        <p className="text-slate-300 text-sm mb-3">
          {language === "ga"
            ? `Leabhar nótaí marimo beo le haghaidh ${title}. Ionsáite ó ${subject.client.notebook.python_module}.`
            : `Live marimo notebook for ${title}. Embedded from ${subject.client.notebook.python_module}.`}
        </p>
        <div
          className="w-full rounded-lg border border-slate-700 overflow-hidden bg-slate-950"
          style={{ height: subject.client.notebook_embed.full_height }}
        >
          <iframe
            src={subject.client.notebook_embed.embed_url}
            title={`${subject.name} marimo notebook`}
            className="w-full h-full"
            loading="lazy"
          />
        </div>
      </CiTextbookPanel>

      {/* ── 5 NCCA Key Competencies (cross-subject context) ────────── */}
      <section className="flex flex-col gap-3">
        <h3 className="text-sm uppercase tracking-wider text-slate-400 font-bold">
          {language === "ga"
            ? "Comhthéacs na 5 bPríochomhardaigh NCCA (tras-ábhar)"
            : "The 5 NCCA Key Competencies (cross-subject context)"}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {KEY_COMPETENCY_SLUGS.map((kc: KeyCompetencySlug) => {
            const value = getMasteryForCell(subject.slug, kc);
            return (
              <div
                key={kc}
                className="flex items-center gap-2 p-2 rounded border"
                style={{ borderColor: KC_COLOR[kc] }}
              >
                <span
                  className="shrink-0 w-3 h-3 rounded-full"
                  style={{ backgroundColor: KC_COLOR[kc] }}
                />
                <span className="text-sm text-slate-200">
                  {language === "ga" ? KC_LABEL_GA[kc] : KC_LABEL_EN[kc]}
                </span>
                <span className="ml-auto text-xs text-slate-500 font-mono">
                  {value}%
                </span>
              </div>
            );
          })}
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <footer className="text-center text-xs text-slate-600 italic mt-4">
        {language === "ga"
          ? `Sonraí ón BIEP v1 (${subject.client.table_ref.ducklake_database}.${subject.client.table_ref.ducklake_schema}.*). Foinse oscailte faoi BUSL-1.1.`
          : `Data sourced from the BIEP v1 (${subject.client.table_ref.ducklake_database}.${subject.client.table_ref.ducklake_schema}.*). Open source under BUSL-1.1.`}
      </footer>
    </div>
  );
}
