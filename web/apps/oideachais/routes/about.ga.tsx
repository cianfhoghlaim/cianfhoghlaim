// /ga/about — About Cianfhoghlaim (Irish-language mirror).
// Public-facing summary; professional + minimal theming.
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/ Step 4.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui-kit/lc";

export const Route = createFileRoute("/about/ga")({
  component: AboutPageGA,
});

const PRIORITY_SUBJECTS_GA = [
  { ga: "Mata", en: "Mathematics", color: "#2563eb", en_route: "/en/subjects/mathematics", ga_route: "/ga/subjects/mata" },
  { ga: "Ceimic", en: "Chemistry", color: "#16a34a", en_route: "/en/subjects/chemistry", ga_route: "/ga/subjects/ceimic" },
  { ga: "Tíreolaíocht", en: "Geography", color: "#ca8a04", en_route: "/en/subjects/geography", ga_route: "/ga/subjects/tireolaiocht" },
  { ga: "Gaeilge", en: "Gaeilge", color: "#059669", en_route: "/en/subjects/gaeilge", ga_route: "/ga/subjects/gaeilge" },
  { ga: "Béarla", en: "English", color: "#ea580c", en_route: "/en/subjects/english", ga_route: "/ga/subjects/bearla" },
  { ga: "Ríomheolaíocht", en: "Computer Science", color: "#475569", en_route: "/en/subjects/computer_science", ga_route: "/ga/subjects/riomheolaiocht" },
];

const FOUNDATIONS_GA = [
  "An Clár Foghlama SC L1/L2",
  "Tuarascáil Chomhairleach an SCR",
  "An Acmhainn Foghlama Ar Líne",
  "An Acmhainn Deimhnithe Ar Líne",
  "5 Phríochomhardaigh NCCA",
];

const SUBNATIONS_GA = [
  { name: "Éire", active: true },
  { name: "Tuaisceart Éireann", active: false },
  { name: "Albain", active: false },
  { name: "Sasana", active: false },
  { name: "an Bhreatain Bheag", active: false },
  { name: "Ellan Vannin", active: false },
];

function AboutPageGA() {
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6" lang="ga">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-4xl font-bold text-emerald-400">
          Faoi Cianfhoghlaim
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl">
          Is ardán oideachais gníomhach (agentic) dátheangach (EN/GA) é
          Cianfhoghlaim — Coláiste na Déisigh d'Ardteistiméireacht na
          hÉireann. 6 ábhar tosaíochta NCCA LC, léarscáil chruinn de na
          hoileáin Breatanacha, téamaí gairmiúla.
        </p>
        <p className="text-slate-400 text-sm">
          Comhdhlúthú féin-óstach de acmhainní an chórais oideachais
          Ardteistiméireachta. Laghdaigh na constaicí ar an oideachas.
        </p>
      </div>

      <CiTextbookPanel title="Na 6 ábhar tosaíochta BIEP" material="parchment">
        <p className="text-slate-300 mb-3 text-sm">
          Tá an píblíne BIEP (British-Isles Education Pipeline) v1 ag
          ceangal na 6 n-ábhar tosaíochta NCCA den chéad lá go dtí an lá
          deireadh (NCCA + SEC + gov.ie + BAML + CocoIndex + marimo +
          Dagster).
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {PRIORITY_SUBJECTS_GA.map((s) => (
            <div
              key={s.en}
              className="p-3 rounded border text-center"
              style={{ borderColor: s.color }}
            >
              <Link
                to={s.ga_route as never}
                className="text-base font-bold transition-colors hover:opacity-80"
                style={{ color: s.color }}
              >
                {s.ga}
              </Link>
              <div className="text-xs text-slate-400 mt-1">
                {s.en} ·{" "}
                <Link
                  to={s.en_route as never}
                  className="underline hover:opacity-80"
                  style={{ color: s.color }}
                >
                  EN mirror
                </Link>
              </div>
            </div>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="5 Bhunús NCCA" material="gold-leaf">
        <ul className="space-y-1 text-sm text-slate-300">
          {FOUNDATIONS_GA.map((f) => (
            <li key={f} className="flex items-start gap-2">
              <span className="text-amber-400">•</span>
              <span>{f}</span>
            </li>
          ))}
        </ul>
      </CiTextbookPanel>

      <CiTextbookPanel title="Léarscáil chruinn de na hoileáin Breatanacha — 6 fhothíreacht" material="ink-wash">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
          {SUBNATIONS_GA.map((sub) => (
            <div
              key={sub.name}
              className={
                "p-2 rounded text-center " +
                (sub.active
                  ? "bg-emerald-700/20 text-emerald-300 border border-emerald-800"
                  : "bg-slate-900 text-slate-500 border border-slate-700")
              }
            >
              {sub.name}
              {sub.active && (
                <span className="ml-2 text-[10px] uppercase tracking-wider text-amber-400">
                  v1 gníomhach
                </span>
              )}
            </div>
          ))}
        </div>
        <p className="text-slate-500 italic text-xs mt-3">
          Tá na 5 fhothíreacht eile curtha ar athló go dtí v2 (féach an
          tsonraíocht `british-isles-education-pipeline`, an t-athrú
          openspec `2026-07-09-cross-nation-content-audit-v1`, agus an
          léarscáil dromchla `agentic-frontend-frameworks`).
        </p>
      </CiTextbookPanel>

      <CiTextbookPanel title="An ailtireacht (foinse oscailte)" material="knotwork">
        <p className="text-slate-300 mb-3">
          Tá Cianfhoghlaim tógtha ar an gcruach gníomhach foinse oscailte:
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
          {[
            "TanStack Start",
            "CopilotKit v2 + AG-UI",
            "Hono + oRPC",
            "Convex",
            "better-auth v1.4",
            "Cloudflare Workers",
            "Cloudflare R2",
            "dlt 1.28 + DuckLake",
            "CocoIndex v1 (BGE-M3 1024-d)",
            "baml 0.223 (eastóscadh clóscríofa)",
            "LanceDB",
            "MotherDuck Dives",
            "marimo (leabhair nótaí imoibríocha)",
            "Dagster 1.13 (Cianfhoghlaim Components)",
            "Langfuse + MLflow",
            "LiteLLM (geata LLM aontaithe)",
          ].map((t) => (
            <div
              key={t}
              className="p-2 rounded bg-slate-900 text-center text-slate-300 font-mono text-xs"
            >
              {t}
            </div>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="Téamaí gairmiúla" material="parchment">
        <p className="text-slate-300 text-sm">
          Úsáideann an dromchla poiblí téamaí gairmiúla + íosta. Tá an
          sraith miotaseolaíochta/foinsí stairiúla curtha ar athló go
          BIEP-v2 (féach an t-athrú openspec{" "}
          <code>2026-07-09-remove-brown-ajah-theming-v1</code>). Fanann
          an léarscáil chruinn de na hoileáin Breatanacha + na 5
          Phríochomhardaigh NCCA + 8 ndathanna ábhar NCCA.
        </p>
      </CiTextbookPanel>

      <section className="text-center pt-8 pb-12">
        <Link
          to="/en/self-host"
          className="inline-block px-6 py-3 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors mr-3"
        >
          Féin-óstáil i 5 nóiméad →
        </Link>
        <Link
          to={"/ga/subjects/mata" as never}
          className="inline-block px-6 py-3 rounded-lg bg-slate-800 text-slate-100 border border-slate-700 hover:border-emerald-700 transition-colors"
        >
          Fiosraigh ábhar →
        </Link>
      </section>
    </div>
  );
}
