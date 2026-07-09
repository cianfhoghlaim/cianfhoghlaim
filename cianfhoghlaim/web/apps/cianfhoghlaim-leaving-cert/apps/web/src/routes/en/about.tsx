// /en/about — About Cianfhoghlaim
// Public-facing summary; professional + minimal theming.
// Per openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/ Step 4.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/about")({
  component: AboutPage,
});

const PRIORITY_SUBJECTS = [
  { slug: "mathematics", name: "Mathematics", ga: "Mata", color: "#2563eb", en_route: "/en/subjects/mathematics", ga_route: "/ga/subjects/mata" },
  { slug: "chemistry", name: "Chemistry", ga: "Ceimic", color: "#16a34a", en_route: "/en/subjects/chemistry", ga_route: "/ga/subjects/ceimic" },
  { slug: "geography", name: "Geography", ga: "Tíreolaíocht", color: "#ca8a04", en_route: "/en/subjects/geography", ga_route: "/ga/subjects/tireolaiocht" },
  { slug: "gaeilge", name: "Gaeilge", ga: "Gaeilge", color: "#059669", en_route: "/en/subjects/gaeilge", ga_route: "/ga/subjects/gaeilge" },
  { slug: "english", name: "English", ga: "Béarla", color: "#ea580c", en_route: "/en/subjects/english", ga_route: "/ga/subjects/bearla" },
  { slug: "computer_science", name: "Computer Science", ga: "Ríomheolaíocht", color: "#475569", en_route: "/en/subjects/computer_science", ga_route: "/ga/subjects/riomheolaiocht" },
];

const FOUNDATIONS = [
  "5 NCCA Key Competencies",
  "SC L1/L2 Programme Statement",
  "SCR Advisory Report",
  "Online Learning Potential",
  "Online Certification Potential",
];

const FOUNDATIONS_GA = [
  "5 Phríochomhardaigh NCCA",
  "Ráiteas Cláir SC L1/L2",
  "Tuarascáil Chomhairleach SCR",
  "An Acmhainn Foghlama Ar Líne",
  "An Acmhainn Deimhnithe Ar Líne",
];

const SUBNATIONS = [
  { name: "Éire", active: true },
  { name: "Northern Ireland", active: false },
  { name: "Scotland", active: false },
  { name: "England", active: false },
  { name: "Wales", active: false },
  { name: "Isle of Man", active: false },
];

function AboutPage() {
  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-4xl font-bold text-emerald-400">
          About Cianfhoghlaim
        </h1>
        <p className="text-xl text-slate-300 max-w-3xl">
          Cianfhoghlaim — Coláiste na Déisigh is a bilingual (EN/GA) agentic
          educational platform for the Irish Leaving Certificate. 6 NCCA LC
          priority subjects, accurate British Isles map, professional
          theming.
        </p>
        <p className="text-slate-400 text-sm">
          A self-hostable consolidation of Leaving Certificate education
          system resources. Reduce barriers to education.
        </p>
      </div>

      <CiTextbookPanel title="The 6 BIEP priority subjects" material="parchment">
        <p className="text-slate-300 mb-3 text-sm">
          The British-Isles Education Pipeline (BIEP) v1 wires the 6 NCCA
          Leaving Certificate priority subjects end-to-end (NCCA + SEC +
          gov.ie + BAML + CocoIndex + marimo + Dagster).
        </p>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {PRIORITY_SUBJECTS.map((s) => (
            <div
              key={s.slug}
              className="p-3 rounded border text-center"
              style={{ borderColor: s.color }}
            >
              <Link
                to={s.en_route as never}
                className="text-base font-bold transition-colors hover:opacity-80"
                style={{ color: s.color }}
              >
                {s.name}
              </Link>
              <div className="text-xs text-slate-400 mt-1">
                {s.ga} ·{" "}
                <Link
                  to={s.ga_route as never}
                  className="underline hover:opacity-80"
                  style={{ color: s.color }}
                >
                  GA mirror
                </Link>
              </div>
            </div>
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="5 NCCA Foundations" material="gold-leaf">
        <ul className="space-y-1 text-sm text-slate-300">
          {FOUNDATIONS.map((f, i) => (
            <li key={f} className="flex items-start gap-2">
              <span className="text-amber-400">•</span>
              <span>
                <span>{f}</span>
                <span className="text-slate-500 italic"> · {FOUNDATIONS_GA[i]}</span>
              </span>
            </li>
          ))}
        </ul>
      </CiTextbookPanel>

      <CiTextbookPanel title="Accurate British Isles map — 6 subnations" material="ink-wash">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
          {SUBNATIONS.map((sub) => (
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
                  v1 active
                </span>
              )}
            </div>
          ))}
        </div>
        <p className="text-slate-500 italic text-xs mt-3">
          The other 5 subnations are deferred to v2 (per the
          `british-isles-education-pipeline` spec, the
          `2026-07-09-cross-nation-content-audit-v1` change, and the
          `agentic-frontend-frameworks` spec surface map).
        </p>
      </CiTextbookPanel>

      <CiTextbookPanel title="The architecture (open source)" material="knotwork">
        <p className="text-slate-300 mb-3">
          Cianfhoghlaim is built on the open-source agentic stack:
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
            "baml 0.223 (typed extraction)",
            "LanceDB",
            "MotherDuck Dives",
            "marimo reactive notebooks",
            "Dagster 1.13 (KCG Components)",
            "Langfuse + MLflow",
            "LiteLLM (unified LLM gateway)",
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

      <CiTextbookPanel title="Professional theming" material="parchment">
        <p className="text-slate-300 text-sm">
          The public surface uses professional + minimal theming. The
          mythology / historical-sources layer is deferred to BIEP-v2 (see
          the <code>2026-07-09-remove-brown-ajah-theming-v1</code> openspec
          change). The accurate British Isles map + the 5 NCCA Key
          Competencies + the 8 NCCA subject colours remain.
        </p>
      </CiTextbookPanel>

      <section className="text-center pt-8 pb-12">
        <Link
          to="/en/self-host"
          className="inline-block px-6 py-3 rounded-lg bg-emerald-600 text-white hover:bg-emerald-500 transition-colors mr-3"
        >
          Self-host in 5 minutes →
        </Link>
        <Link
          to={"/en/subjects/mathematics" as never}
          className="inline-block px-6 py-3 rounded-lg bg-slate-800 text-slate-100 border border-slate-700 hover:border-emerald-700 transition-colors"
        >
          Explore a subject →
        </Link>
      </section>
    </div>
  );
}