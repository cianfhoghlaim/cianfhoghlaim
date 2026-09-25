// /ga/portal — Central portal entry route (the British Isles portal)
//
// Gaeilge (Irish) version of routes/en/portal/index.tsx.
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/.

import * as React from "react";
import { Link, createFileRoute } from "@tanstack/react-router";
import {
  CiRealmMap,
  CiStageBreadcrumbs,
  CiLCSubjectGrid,
  CiTextbookPanel,
  CiSubnationFlag,
  type EducationalStage,
} from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/ga/portal/")({
  component: CentralPortalGa,
});

function CentralPortalGa() {
  const [activeSubnation, setActiveSubnation] = React.useState<
    "eire" | "northern-ireland" | "scotland" | "england" | "wales" | "isle-of-man"
  >("eire");
  const [currentStage, setCurrentStage] = React.useState<EducationalStage>("leaving_cycle");

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8 p-6">
      <section className="text-center pt-12 pb-6">
        <h1 className="font-cinzel text-5xl font-bold text-emerald-400 mb-3">
          Tairseach na Breataine Móire
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl mx-auto">
          An pointe iontrála láir d'acmhainní Cianfhoghlaim Leaving Certificate.
        </p>
        <p className="text-sm text-slate-500 max-w-3xl mx-auto mt-3 font-mono">
          6 fho-shláth · 5 chéim oideachais · 6 ábhar LC · 4 MotherDuck Dive + 1 Flight laethúil · 4 BIEP CocoIndex v1 Apps
        </p>
      </section>

      <CiTextbookPanel
        title="Léarscáil Chruinn na Breataine Móire"
        material="knotwork"
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-2xl p-6">
            <CiRealmMap
              activeSubnation={activeSubnation}
              onSubnationClick={(sn) => {
                if (sn) setActiveSubnation(sn);
              }}
            />
          </div>
          <div className="space-y-3">
            <CiTextbookPanel title="Na 6 Fho-shláth" material="parchment">
              <div className="space-y-2">
                {[
                  { slug: "eire" as const, name_ga: "Éire", active: true },
                  { slug: "northern-ireland" as const, name_ga: "Tuaisceart Éireann", active: false },
                  { slug: "scotland" as const, name_ga: "Albain", active: false },
                  { slug: "england" as const, name_ga: "Sasana", active: false },
                  { slug: "wales" as const, name_ga: "an Bhreatain Bheag", active: false },
                  { slug: "isle-of-man" as const, name_ga: "Ellan Vannin", active: false },
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
                      {sub.name_ga}
                    </span>
                    {sub.active && <span className="ml-auto text-xs text-amber-400">v1 gníomhach</span>}
                    {!sub.active && <span className="ml-auto text-xs text-slate-500">Céim 2</span>}
                  </button>
                ))}
              </div>
            </CiTextbookPanel>
          </div>
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel
        title="5 Chéim Oideachais"
        material="parchment"
      >
        <CiStageBreadcrumbs
          currentStage={currentStage}
          language="ga"
          onStageClick={(stage) => setCurrentStage(stage)}
        />
      </CiTextbookPanel>

      <CiTextbookPanel
        title="An Timthriall Sinsearach — 6 Ábhar NCCA (BIEP v1)"
        material="gold-leaf"
      >
        <CiLCSubjectGrid language="ga" />
      </CiTextbookPanel>

      <section className="text-center pt-6 pb-12">
        <p className="text-base text-slate-400 max-w-3xl mx-auto">
          Is é seo an pointe iontrála do Leaving Cycle. Cliceáil ábhar ar bith chun
          dul chuig a dhromchla <code className="font-mono">{`<ábhar>`}</code>-specific
          (syllabus / scrúdpháipéir / scéimeanna marcála / plean staidéir). Tá na 5 chéim
          eile (Aistear + Ardleibhéal) curtha siar go Céim 2.
        </p>
        <Link
          to="/en/map"
          className="inline-block mt-4 px-5 py-2.5 rounded-lg bg-slate-800 text-slate-100 border border-slate-700 hover:border-emerald-700 transition-colors"
        >
          Oscail an léarscáil mhionsonraithe →
        </Link>
      </section>
    </div>
  );
}
