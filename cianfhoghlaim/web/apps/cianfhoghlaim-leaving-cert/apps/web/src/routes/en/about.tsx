// /en/about — Public About page (English)
// Per openspec/changes/2026-07-02-public-about-route and
// openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md Requirement R11.
//
// Renders the Brown Ajah Wheel of Time theming summary + the 6 subnations
// + the 13 éraic treasures + the 5 NCCA Key Competencies — without exposing
// any operator-only lineage. The lore document at docs/CIANFHLOGHLAIM_LORE.md
// is operator-only and is not linked from this page.
//
// Per the public-surface privacy constraint (CIANFHLOGHLAIM_LORE.md §Privacy),
// the regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]` and the family surnames
// `Deacy`, `Lyons`, `Morris`, `Conroy` must not appear anywhere on the page.

import { createFileRoute } from "@tanstack/react-router";
import {
  CiTextbookPanel,
  CiBoonsChoice,
  CiStreakFlame,
  CiDetailCell,
} from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/about")({
  component: AboutPage,
});

interface BilingualName {
  name_en: string;
  name_ga: string;
}

const SUBNATIONS: Array<BilingualName & { slug: string; active: boolean }> = [
  { slug: "eire", name_en: "Éire (Ireland)", name_ga: "Éire", active: true },
  { slug: "northern-ireland", name_en: "Northern Ireland", name_ga: "Tuaisceart Éireann", active: false },
  { slug: "scotland", name_en: "Scotland", name_ga: "Albain", active: false },
  { slug: "england", name_en: "England", name_ga: "Sasana", active: false },
  { slug: "wales", name_en: "Wales (Y Ddraig Goch)", name_ga: "an Bhreatain Bheag", active: false },
  { slug: "isle-of-man", name_en: "Isle of Man (Ellan Vannin)", name_ga: "Ellan Vannin", active: false },
];

const EIRAIC: Array<BilingualName & { tier: number; color: string }> = [
  { tier: 1, name_en: "Pig of Dobar", name_ga: "Muc Dobar", color: "#92400e" },
  { tier: 2, name_en: "Heifer of Dobar", name_ga: "Aghas Dobar", color: "#a16207" },
  { tier: 3, name_en: "Spear of Assal", name_ga: "Sleagh Assail", color: "#b45309" },
  { tier: 4, name_en: "Chariot of Sidrach", name_ga: "Carbad Shidhrigh", color: "#ca8a04" },
  { tier: 5, name_en: "Sword of Caladbolg", name_ga: "Claíomh Caladbolg", color: "#eab308" },
  { tier: 6, name_en: "Seven Pigs of Easmal", name_ga: "Seacht Muc Easmall", color: "#facc15" },
  { tier: 7, name_en: "Whelp of Ioruaidh", name_ga: "Coileán Ioruaidh", color: "#fde047" },
  { tier: 8, name_en: "Spit of Innis Cera", name_ga: "Bior Innis Cera", color: "#fbbf24" },
  { tier: 9, name_en: "Helmet of Clochur", name_ga: "Clogad Chlochuir", color: "#f59e0b" },
  { tier: 10, name_en: "Three Apples of the Hesperides", name_ga: "Trí Úll Hesperides", color: "#f97316" },
  { tier: 11, name_en: "Pigskin Bag of the Healing Well", name_ga: "Mála Mucshlinne an Tobair Leighis", color: "#ea580c" },
  { tier: 12, name_en: "Feather of the Bird of Crannog", name_ga: "Cleite Éan an Chrannaigh", color: "#dc2626" },
  { tier: 13, name_en: "Lugh's own Samildanach", name_ga: "Samhildanach Lugh", color: "#b91c1c" },
];

const KEY_COMPETENCIES: Array<BilingualName & {
  slug: string;
  tuatha_de: string;
  color: string;
  description_en: string;
}> = [
  {
    slug: "communicating",
    name_en: "Communicating",
    name_ga: "Cumarsáid",
    tuatha_de: "Brigid",
    color: "#059669",
    description_en: "The healing of the language — bilingual EN+GA throughout.",
  },
  {
    slug: "information-processing",
    name_en: "Information Processing",
    name_ga: "Próiseáil Faisnéise",
    tuatha_de: "Ogma",
    color: "#2563eb",
    description_en: "The healing of the data — Ogma invented Ogham.",
  },
  {
    slug: "critical-creative-thinking",
    name_en: "Critical & Creative Thinking",
    name_ga: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
    tuatha_de: "Lugh",
    color: "#ca8a04",
    description_en: "The healing of the reasoning — Lugh's samildanach (master of all arts).",
  },
  {
    slug: "personal-effectiveness",
    name_en: "Personal Effectiveness",
    name_ga: "Éifeachtacht Phearsanta",
    tuatha_de: "Dian Cecht",
    color: "#92400e",
    description_en: "The healing of the discipline — Dian Cecht was the physician of the Tuatha Dé.",
  },
  {
    slug: "working-with-others",
    name_en: "Working with Others",
    name_ga: "Ag Obair le Daoine Eile",
    tuatha_de: "Trí Dé Dána",
    color: "#b91c1c",
    description_en: "The healing of the community — the Trí Dé Dána (Brigid + Dian Cecht + Ogma) collectively.",
  },
];

const WOT_REFERENCES: Array<BilingualName & { kind: string }> = [
  { kind: "Aes Sedai", name_en: "The Brown Ajah — servants of all", name_ga: "An Brown Ajah — seirbhísigh don uile" },
  { kind: "Amyrlin Seat", name_en: "The orchestrator agent — Amyrlin", name_ga: "An t-orchestrator — Amyrlin" },
  { kind: "Dragon Reborn", name_en: "The student who completes cross-subject mastery", name_ga: "An mac léinn a chuireann máistreacht chrann-ábhar i gcrích" },
  { kind: "Dragon Banner", name_en: "Wales flies the red dragon on white", name_ga: "Cymru ag eitilt an dragan dearg ar bhán" },
  { kind: "Tuatha'an", name_en: "The student as the Irish Traveller — the wagon", name_ga: "An mac léinn mar an Travaller — an veain" },
];

function AboutPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          About Cianfhoghlaim
        </h1>
        <p className="text-slate-400 text-lg">
          The Brown Ajah Wheel of Time theming · the 6 subnations ·
          the 13 éraic treasures · the 5 NCCA Key Competencies
        </p>
        <div className="flex items-center gap-2 text-slate-500 text-sm font-mono italic">
          <CiStreakFlame days={13} />
          <span>Aes Sedai — servants of all</span>
        </div>
      </div>

      {/* The Brown Ajah Wheel of Time theming */}
      <CiTextbookPanel title="The Brown Ajah Theming" material="knotwork">
        <p className="text-slate-300 text-sm leading-relaxed mb-4">
          The Cianfhoghlaim OS is themed on the <strong>Brown Ajah</strong> of
          the Wheel of Time — the healers, scholars, and Earth-workers. The
          theming is grounded in 4 lore references that map the platform
          onto Jordan's cosmology:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {WOT_REFERENCES.map((ref) => (
            <CiDetailCell
              key={ref.kind}
              icon={<span className="text-amber-400">⚙</span>}
              title={ref.kind}
              metadata={ref.name_en}
              description={ref.name_ga}
            />
          ))}
        </div>
      </CiTextbookPanel>

      {/* The 6 subnations of the British Isles */}
      <CiTextbookPanel title="The 6 Subnations of the British Isles" material="parchment">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {SUBNATIONS.map((sub) => (
            <CiDetailCell
              key={sub.slug}
              icon={
                <span
                  className={`w-3 h-3 rounded-full ${sub.active ? "bg-emerald-400" : "bg-slate-500"}`}
                />
              }
              title={sub.name_en}
              metadata={sub.name_ga}
              description={sub.active ? "v1 active" : "Coming soon"}
            />
          ))}
        </div>
      </CiTextbookPanel>

      {/* The 13 éraic treasures */}
      <CiTextbookPanel title="The 13 Éraic Treasures" material="gold-leaf">
        <p className="text-slate-400 text-sm italic mb-4 text-center">
          The 13 magical treasures demanded as the éraic (body-price) — the
          framework for the formative-assessment reward tiers.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {EIRAIC.map((treasure) => (
            <CiDetailCell
              key={treasure.tier}
              icon={
                <span
                  className="w-6 h-6 rounded-full flex items-center justify-center font-cinzel text-xs font-bold text-slate-900"
                  style={{ background: treasure.color }}
                >
                  {treasure.tier}
                </span>
              }
              title={treasure.name_en}
              metadata={treasure.name_ga}
            />
          ))}
        </div>
      </CiTextbookPanel>

      {/* The 5 NCCA Key Competencies — as the 3-way boons choice */}
      <CiTextbookPanel title="The 5 NCCA Key Competencies" material="ink-wash">
        <p className="text-slate-400 text-sm mb-4 text-center">
          Pick 3 to focus on this term — the healing is in the doing.
        </p>
        <CiBoonsChoice
          prompt="Which 3 will you master?"
          choices={[
            {
              id: "communicating",
              label: KEY_COMPETENCIES[0].name_en,
              description: `${KEY_COMPETENCIES[0].tuatha_de} · ${KEY_COMPETENCIES[0].name_ga}`,
              color: KEY_COMPETENCIES[0].color,
            },
            {
              id: "critical-creative-thinking",
              label: KEY_COMPETENCIES[2].name_en,
              description: `${KEY_COMPETENCIES[2].tuatha_de} · ${KEY_COMPETENCIES[2].name_ga}`,
              color: KEY_COMPETENCIES[2].color,
            },
            {
              id: "working-with-others",
              label: KEY_COMPETENCIES[4].name_en,
              description: `${KEY_COMPETENCIES[4].tuatha_de} · ${KEY_COMPETENCIES[4].name_ga}`,
              color: KEY_COMPETENCIES[4].color,
            },
          ]}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 mt-6">
          {KEY_COMPETENCIES.map((kc) => (
            <CiDetailCell
              key={kc.slug}
              icon={
                <span
                  className="w-8 h-8 rounded-full flex items-center justify-center font-cinzel text-sm font-bold text-white"
                  style={{ background: kc.color }}
                >
                  ★
                </span>
              }
              title={kc.name_en}
              metadata={kc.tuatha_de}
              description={kc.name_ga}
            />
          ))}
        </div>
      </CiTextbookPanel>

      <footer className="text-center text-xs text-slate-500 italic pt-4">
        Public surface — no operator-only lore is exposed on this page.
      </footer>
    </div>
  );
}