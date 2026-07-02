// /index — Cianfhoghlaim OS landing page (the Eye of the World)
// Per docs/BROWN_AJAH_THEMING.md, the welcome banner is "The Eye of the
// World" — the first thing the student sees when they enter Tar Valon
// (the Cianfhoghlaim Academy).
//
// Renders the 6 subnations of the British Isles as the landing tiles
// (Éire is the v1 active region; the other 5 are greyed out with
// "Coming soon" badges).

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiButton, CiProgressRing } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/")({
  component: LandingComponent,
});

const SUBNATIONS = [
  {
    slug: "eire",
    flag: "🇮🇪",
    title_en: "Éire (Ireland)",
    title_ga: "Éire",
    color: "var(--ci-subnation-eire)",
    active: true,
    description_en: "Active in v1 — full NCCA LC syllabus + 8 subjects + 6 sections + 4 diagram modes + 2D/3D asset gallery.",
    description_ga: "Gníomhach i v1 — an clár iomlán NCCA LC + 8 ábhar + 6 rannóg + 4 mód léaráide + gailearaí sócmhainní 2T/3T.",
    route: "/en/leaving-cert/mathematics" as const,
  },
  {
    slug: "northern-ireland",
    flag: "🏴󠁧󠁢󠁮󠁩󠁲󠁿",
    title_en: "Northern Ireland",
    title_ga: "Tuaisceart Éireann",
    color: "var(--ci-subnation-northern-ireland)",
    active: false,
    description_en: "Coming in v2 — the Cross-Border Studies + the Belfast node + the partition of the island.",
    description_ga: "Ag teacht i v2 — na Staidéar Chrosteorann + nód Bhéal Feirste + críochdheighilt an oileáin.",
    route: null,
  },
  {
    slug: "scotland",
    flag: "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    title_en: "Scotland",
    title_ga: "Albain",
    color: "var(--ci-subnation-scotland)",
    active: false,
    description_en: "Coming in v3 — the CfE (Curriculum for Excellence) + the Scots Gaelic syllabus.",
    description_ga: "Ag teacht i v3 — an CfE (Curriculum for Excellence) + clár Gàidhlig na hAlba.",
    route: null,
  },
  {
    slug: "england",
    flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    title_en: "England",
    title_ga: "Sasana",
    color: "var(--ci-subnation-england)",
    active: false,
    description_en: "Coming in v4 — the national curriculum + the GCSE syllabus.",
    description_ga: "Ag teacht i v4 — an clár náisiúnta + clár GCSE.",
    route: null,
  },
  {
    slug: "wales",
    flag: "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    title_en: "Wales (Y Ddraig Goch)",
    title_ga: "an Bhreatain Bheag",
    color: "var(--ci-subnation-wales)",
    active: false,
    description_en: "Coming in v5 — the Curriculum for Wales + the Welsh (Cymraeg) syllabus + the Dragon Banner.",
    description_ga: "Ag teacht i v5 — Curaclwm Cymru + clár Cymraeg + an Bannersgi Dreigiau.",
    route: null,
  },
  {
    slug: "isle-of-man",
    flag: "🇮🇲",
    title_en: "Isle of Man (Ellan Vannin)",
    title_ga: "Ellan Vannin",
    color: "var(--ci-subnation-isle-of-man)",
    active: false,
    description_en: "Coming in v6 — the Manx (Gaelg) syllabus + the Tynwald civic studies.",
    description_ga: "Ag teacht i v6 — clár Gaelg + staidéar saoránach an Tinvaal.",
    route: null,
  },
];

function LandingComponent() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-8">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          Fáilte go Cianfhoghlaim
        </h1>
        <p className="text-slate-400 text-lg">
          Your bilingual, agentic gateway to the entire British Isles
          educational system. The 5 NCCA Key Competencies are the 5
          surviving gifts of the Tuatha Dé Danann. The 8 NCCA LC
          subjects are the 8 Brown Ajah members. The 6 subnations are
          the wounded land to be healed through education.
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          Welcome to Cianfhoghlaim · Aes Sedai — servants of all ·
          Brown Ajah of the White Tower
        </p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {SUBNATIONS.map((sub) => {
          const card = (
            <div
              key={sub.slug}
              className={`relative bg-slate-800 border rounded-xl p-6 shadow-xl overflow-hidden group transition-all ${
                sub.active
                  ? "border-emerald-700 hover:border-emerald-500"
                  : "border-slate-700 opacity-50 cursor-not-allowed"
              }`}
            >
              <div className="absolute top-3 right-3 text-4xl">{sub.flag}</div>
              <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
                <span
                  className="w-2 h-8 rounded-full"
                  style={{ backgroundColor: sub.color }}
                />
                {sub.title_en}
              </h3>
              <p className="text-slate-400 text-sm mb-2 font-mono text-xs">
                {sub.title_ga}
              </p>
              <p className="text-slate-500 text-sm">{sub.description_en}</p>
              {!sub.active && (
                <div className="absolute top-3 left-3 px-2 py-1 bg-slate-700 text-slate-400 text-xs rounded">
                  Coming soon
                </div>
              )}
              {sub.active && (
                <span className="inline-block text-sm mt-4 text-emerald-400">
                  Open →
                </span>
              )}
            </div>
          );
          return sub.active && sub.route ? (
            <Link key={sub.slug} to={sub.route}>
              {card}
            </Link>
          ) : (
            <div key={sub.slug}>{card}</div>
          );
        })}
      </div>

      <div className="flex items-center gap-4 mt-4">
        <CiProgressRing value={85} tier="proficient" eiraicTier={4} label="Mathematics" />
        <CiProgressRing value={42} tier="familiar" eiraicTier={7} label="English" />
        <CiProgressRing value={0} tier="attempted" eiraicTier={1} label="Biology" />
      </div>
    </div>
  );
}