// /en/portal — Central portal entry route (the British Isles portal)
//
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R17 + R19.
//
// Renders:
//   1. The British Isles map (CiRealmMap) — 6 subnations, 5 NCCA Key Competency
//      land-marks, with Éire active + 5 subnations as coming-soon
//   2. The 5-stage breadcrumb (CiStageBreadcrumbs) — Aistear + Primary + JC +
//      Leaving Cycle + Tertiary, with the 2 deferred stages marked v2
//   3. The 6-LC-subject grid (CiLCSubjectGrid) — Mathematics, Chemistry,
//      Geography, Gaeilge, English, Computer Science
//
// At portal.cianfhoghlaim.ie (per cross-repo-sync.md, this is bound via
// the bonneagar `portal-cloudflare-r2` stack — Cloudflare free tier; R2
// for PDFs; Hono issues signed URLs).
//
// This is the SINGLE ENTRY POINT into the BIEP per-subject surfaces
// (routes/en/subjects/<subject>/{index,syllabus,exam-papers,...}.tsx).

import * as React from "react";
import { Link, createFileRoute } from "@tanstack/react-router";
import {
  CiRealmMap,
  CiStageBreadcrumbs,
  CiLCSubjectGrid,
  CiTextbookPanel,
  CiSubnationFlag,
  type EducationalStage,
} from "@cianfhoghlaim/ui-kit/lc";
import {
  CiPdfLibraryPanel,
  DEFAULT_MATHEMATICS_ASSETS,
} from "../../src/components/CiPdfLibraryPanel";
import { PORTAL_MARIMO_BASE } from "../../src/lib/portal-marimo";

export const Route = createFileRoute("/portal/")({
  component: CentralPortalEn,
});

function CentralPortalEn() {
  const [activeSubnation, setActiveSubnation] = React.useState<
    "eire" | "northern-ireland" | "scotland" | "england" | "wales" | "isle-of-man"
  >("eire");
  const [currentStage, setCurrentStage] = React.useState<EducationalStage>("leaving_cycle");

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 p-6">
      {/* Hero */}
      <section className="text-center pt-12 pb-6">
        <h1 className="font-cinzel text-5xl font-bold text-emerald-400 mb-3">
          The British Isles Portal
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto">
          The central entry point to the Cianfhoghlaim Leaving Certificate resources.
        </p>
        <p className="text-sm text-slate-500 max-w-3xl mx-auto mt-3 font-mono">
          6 subnations · 5 educational stages · 6 LC subjects · 4 MotherDuck Dives + 1 daily Flight · 4 BIEP CocoIndex v1 Apps
        </p>
      </section>

      {/* British Isles map */}
      <CiTextbookPanel
        title="The Accurate British Isles Map"
        material="knotwork"
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-2xl p-6">
            <CiRealmMap
              activeSubnation={activeSubnation}
              onSubnationClick={(sn) => {
                // Only Éire is active in v1 (per R19 of the openspec change).
                // Subnations stay clickable but show a "Coming soon" toast.
                if (sn) {
                  setActiveSubnation(sn);
                  if (sn !== "eire") {
                    console.log(`[portal] Subnation ${sn} is v2 deferred. Clicking opens an info panel.`);
                  }
                }
              }}
            />
          </div>
          <div className="space-y-3">
            <CiTextbookPanel title="The 6 Subnations" material="parchment">
              <div className="space-y-2">
                {[
                  { slug: "eire" as const, name_en: "Éire", active: true },
                  { slug: "northern-ireland" as const, name_en: "Northern Ireland", active: false },
                  { slug: "scotland" as const, name_en: "Scotland", active: false },
                  { slug: "england" as const, name_en: "England", active: false },
                  { slug: "wales" as const, name_en: "Wales", active: false },
                  { slug: "isle-of-man" as const, name_en: "Isle of Man", active: false },
                ].map((sub) => (
                  <button
                    key={sub.slug}
                    type="button"
                    onClick={() => setActiveSubnation(sub.slug)}
                    aria-pressed={sub.slug === activeSubnation}
                    className="flex w-full items-center gap-2 rounded-lg p-2 text-left transition-colors hover:bg-slate-800"
                  >
                    <CiSubnationFlag subnation={sub.slug} size={20} />
                    <span className={`text-sm ${sub.active ? "text-emerald-400 font-medium" : "text-slate-400"}`}>
                      {sub.name_en}
                    </span>
                    {sub.active && <span className="ml-auto text-xs text-amber-400">v1 active</span>}
                    {!sub.active && <span className="ml-auto text-xs text-slate-500">Phase 2</span>}
                  </button>
                ))}
              </div>
            </CiTextbookPanel>
          </div>
        </div>
      </CiTextbookPanel>

      {/* 5-stage breadcrumb */}
      <CiTextbookPanel
        title="5 Educational Stages (Aistear → Tertiary)"
        material="parchment"
      >
        <CiStageBreadcrumbs
          currentStage={currentStage}
          language="en"
          onStageClick={(stage) => setCurrentStage(stage)}
        />
      </CiTextbookPanel>

      {/* 6 LC subjects grid */}
      <CiTextbookPanel
        title="Leaving Cycle — 6 NCCA Subjects (BIEP v1 in-scope)"
        material="gold-leaf"
      >
        <CiLCSubjectGrid language="en" />
      </CiTextbookPanel>

      {/* Marimo + PDF library (R14 + R15) */}
      <CiTextbookPanel
        title="Phase 2 — Marimo notebooks + R2 PDF library (Mathematics preview)"
        material="parchment"
      >
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Marimo embed */}
          <section className="rounded-xl border border-slate-700 bg-slate-900 p-4">
            <header className="mb-3 flex items-center justify-between">
              <h3 className="font-bold text-slate-100">
                Marimo study tool — Mathematics
              </h3>
              <a
                href={`${PORTAL_MARIMO_BASE}/mathematics`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-amber-400 hover:text-amber-300"
              >
                Open fullscreen ↗
              </a>
            </header>
            <div className="aspect-[4/3] w-full overflow-hidden rounded-lg border border-slate-700 bg-slate-950">
              <iframe
                src={`${PORTAL_MARIMO_BASE}/mathematics?embed=true`}
                title="Marimo Mathematics notebook"
                className="h-full w-full"
                loading="lazy"
                sandbox="allow-scripts allow-same-origin allow-popups"
              />
            </div>
            <p className="mt-2 text-[10px] text-slate-500 font-mono">
              Deployed via Cloudflare Workers + Container at {PORTAL_MARIMO_BASE}/mathematics
            </p>
          </section>

          {/* PDF library */}
          <CiPdfLibraryPanel
            assets={DEFAULT_MATHEMATICS_ASSETS}
            language="en"
          />
        </div>
      </CiTextbookPanel>

      {/* Footer */}
      <section className="text-center pt-6 pb-12">
        <p className="text-base text-slate-400 max-w-3xl mx-auto">
          The British Isles Portal is the single entry point for the Leaving Cycle.
          Click any subject to navigate to its <code className="font-mono">{`<subject>`}</code>-specific surface
          (syllabus / exam-papers / marking-schemes / study-plan). The remaining 5 stages
          (Aistear + Tertiary) are deferred to Phase 2 — flagged above.
        </p>
        <Link
          to="/en/map"
          className="inline-block mt-4 px-5 py-2.5 rounded-lg bg-slate-800 text-slate-100 border border-slate-700 hover:border-emerald-700 transition-colors"
        >
          Open the detailed British Isles map →
        </Link>
      </section>
    </div>
  );
}
