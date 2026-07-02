// /en/eiraic-treasures/$tier — Detail page for one of the 13 éraic treasures
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md + the 13 éraic treasures BAML.

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell, CiSemanticPill } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/eiraic-treasures/$tier")({
  component: EiraicTreasureDetailPage,
});

const TREASURES: Record<string, {
  tier: number;
  treasure: string;
  provenance: string;
  capability: string;
  subject: string;
  color: string;
  tuatha_de: string;
  rationale_en: string;
  source_quote: string;
}> = {
  "1": {
    tier: 1,
    treasure: "Skin of the Pig of Dobar",
    provenance: "Pig of Dobar (Tuatha Dé Danann)",
    capability: "Healing (heals wounds)",
    subject: "Biology",
    color: "var(--ci-subject-chemistry)",
    tuatha_de: "Dian Cecht (healing)",
    rationale_en: "The healing pigskin of Dobar; opens the wound-mending power of the Tuatha Dé's physician. Maps to the Biology subject because both involve the study of life + healing.",
    source_quote: "The skin of the Pig of Dobar that could heal wounds",
  },
  "2": {
    tier: 2,
    treasure: "Skin of the Heifer of Dobar",
    provenance: "Heifer of Dobar (Tuatha Dé Danann)",
    capability: "Pastoral care",
    subject: "Geography",
    color: "var(--ci-subject-geography)",
    tuatha_de: "Manannán mac Lir (sea + land)",
    rationale_en: "The heifer of Dobar; symbol of pastoral land cultivation. Maps to the Geography subject because both involve the study of land + human settlement patterns.",
    source_quote: "The skin of the Heifer of Dobar",
  },
  "3": {
    tier: 3,
    treasure: "Spear of Assal",
    provenance: "Spear of Assal (Tuatha Dé Danann)",
    capability: "Precise reasoning (never misses its mark)",
    subject: "Mathematics",
    color: "var(--ci-subject-mathematics)",
    tuatha_de: "Lugh (samildanach)",
    rationale_en: "The spear that never misses — symbolic of mathematical precision. Maps to the Mathematics subject because both involve proof + rigorous reasoning.",
    source_quote: "The Spear of Assal that never missed",
  },
  "4": {
    tier: 4,
    treasure: "Chariot of the king of Sidrach",
    provenance: "Chariot of Sidrach (Tuatha Dé Danann)",
    capability: "Speed of completion",
    subject: "Applied Mathematics",
    color: "var(--ci-subject-applied_mathematics)",
    tuatha_de: "Lugh (samildanach)",
    rationale_en: "The chariot of Sidrach; symbol of speed. Maps to the Applied Mathematics subject because both involve applying math in time-pressured contexts.",
    source_quote: "The Chariot of the king of Sidrach",
  },
  "5": {
    tier: 5,
    treasure: "Sword of Caladbolg (wielded by Tethra)",
    provenance: "Tethra (Fomorian king)",
    capability: "Algorithmic clarity (the sword of clarity)",
    subject: "Computer Science",
    color: "var(--ci-subject-computer_science)",
    tuatha_de: "— (modern subject)",
    rationale_en: "The sword of Caladbolg; later wielded by Lugh himself after the Second Battle of Mag Tuired. Maps to the Computer Science subject because both involve the clarity of algorithmic thinking.",
    source_quote: "The sword of Caladbolg wielded by Tethra",
  },
  "6": {
    tier: 6,
    treasure: "Seven Pigs of Easmal",
    provenance: "Pigs of Easmal (Tuatha Dé Danann)",
    capability: "Daily practice (regenerate after slaughter)",
    subject: "All subjects (cross-subject)",
    color: "#f59e0b",
    tuatha_de: "Trí Dé Dána (collectively)",
    rationale_en: "The seven pigs that could be slaughtered and eaten daily, only to regenerate. Maps to all subjects because the act of daily practice across all disciplines keeps the mind alive.",
    source_quote: "The seven pigs of Easmal that could be slaughtered and eaten daily, only to regenerate",
  },
  "7": {
    tier: 7,
    treasure: "Whelp of the king of Ioruaidh",
    provenance: "Whelp of Ioruaidh (Tuatha Dé Danann)",
    capability: "Loyalty + tenacity",
    subject: "English",
    color: "var(--ci-subject-english)",
    tuatha_de: "Brigid (poetry + healing)",
    rationale_en: "The whelp of the king of Ioruaidh; symbol of loyalty. Maps to the English subject because the reading + writing of literature demands both loyalty to the text + tenacity in interpretation.",
    source_quote: "The Whelp of the king of Ioruaidh",
  },
  "8": {
    tier: 8,
    treasure: "Cooking spit of the woman of Innis Cera",
    provenance: "Woman of Innis Cera (Tuatha Dé Danann)",
    capability: "Crafted response (the cooking spit + the cauldron)",
    subject: "Gaeilge",
    color: "var(--ci-subject-gaeilge)",
    tuatha_de: "Ogma (eloquence + learning)",
    rationale_en: "The cooking spit of the woman of Innis Cera; symbol of crafted response. Maps to the Gaeilge subject because the writing of Irish requires both craft + care in expression.",
    source_quote: "The cooking spit of the woman of Innis Cera",
  },
  "9": {
    tier: 9,
    treasure: "Helmet + Breastplate of the king of Clochur",
    provenance: "King of Clochur (Fomorian)",
    capability: "Defensive argument (the defensive armour)",
    subject: "History",
    color: "var(--ci-subject-history)",
    tuatha_de: "The Morrígan (war + death)",
    rationale_en: "The armour of the king of Clochur; symbol of defence. Maps to the History subject because the study of history requires both defending one's interpretation + arming against revisionism.",
    source_quote: "The Helmet + Breastplate of the king of Clochur",
  },
  "10": {
    tier: 10,
    treasure: "Three Apples of the Hesperides",
    provenance: "Garden of the Hesperides (Greek myth)",
    capability: "Triple-crown mastery (3 fruits = 3 levels of mastery)",
    subject: "Cross-subject (capped mastery)",
    color: "#fbbf24",
    tuatha_de: "Lugh (samildanach — master of all arts)",
    rationale_en: "The three golden apples of the Hesperides; symbol of the triple-crown mastery (the Attempted → Familiar → Proficient → Mastered ladder capped at the highest level). Maps to cross-subject mastery.",
    source_quote: "The three Apples of the Hesperides",
  },
  "11": {
    tier: 11,
    treasure: "Pigskin Bag of the Healing Well",
    provenance: "Pigskin bag (Tuatha Dé Danann)",
    capability: "Citation rigor (carries the waters of the healing well)",
    subject: "All subjects (citation rigor)",
    color: "#94a3b8",
    tuatha_de: "Dian Cecht (healing)",
    rationale_en: "The pigskin bag that carried the waters of the healing well. Maps to all subjects because academic citation is the pigskin bag of knowledge — it carries the healing waters of citations to the reader.",
    source_quote: "The pigskin bag that held the waters of the healing well",
  },
  "12": {
    tier: 12,
    treasure: "Feather of the Bird of Crannog",
    provenance: "Bird of Crannog (Tuatha Dé Danann)",
    capability: "Recovery from failure (the feather that resurrects the dead)",
    subject: "All subjects (resilience)",
    color: "#10b981",
    tuatha_de: "The Morrígan (war + death — but also rebirth)",
    rationale_en: "The feather of the Bird of Crannog; symbol of resilience. Maps to all subjects because the path of learning involves many failures + the feather of the Bird of Crannog allows recovery from them.",
    source_quote: "The Feather of the Bird of Crannog",
  },
  "13": {
    tier: 13,
    treasure: "Lugh's own Samildanach (master of all arts)",
    provenance: "Lugh (Tuatha Dé Danann)",
    capability: "Universal mastery (master of all arts)",
    subject: "All subjects (universal capstone)",
    color: "#fbbf24",
    tuatha_de: "Lugh (samildanach)",
    rationale_en: "Lugh's own samildanach ('master of all arts'); the capstone treasure. Maps to all subjects as the universal mastery tier. To reach tier 13 the student has mastered the Attempted + Familiar + Proficient + Mastered levels across all 5 NCCA Key Competencies + all 8 NCCA subjects.",
    source_quote: "Lugh's own samildanach — the master of all arts",
  },
};

function EiraicTreasureDetailPage() {
  const { tier } = Route.useParams();
  const t = TREASURES[tier];

  if (!t) {
    throw notFound({ data: { tier } });
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <div className="text-3xl font-mono font-bold" style={{ color: t.color }}>
          Tier {t.tier} / 13
        </div>
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          {t.treasure}
        </h1>
        <p className="text-slate-400 text-base">{t.provenance}</p>
        <p className="text-slate-300 text-lg italic">{t.capability}</p>
      </div>

      <CiTextbookPanel title="The Source Quote" material="parchment">
        <blockquote className="text-slate-300 italic border-l-4 border-amber-700 pl-4">
          "{t.source_quote}"
        </blockquote>
        <p className="text-xs text-slate-500 mt-2 italic">
          Per <em>Lebor Gabála Érenn</em> (the Book of Invasions) + the late romance
          <em> The Fate of the Children of Tuireann</em> (Oidheadh Chloinne Tuireann).
        </p>
      </CiTextbookPanel>

      <CiTextbookPanel title="The Rationale" material="ink-wash">
        <p className="text-slate-300">{t.rationale_en}</p>
      </CiTextbookPanel>

      <CiTextbookPanel title="Mapping" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <CiDetailCell
            icon={<span className="text-2xl">📚</span>}
            title="Subject"
            metadata={t.subject}
            description={`The treasure maps to the ${t.subject} subject via the Brown Ajah theming.`}
          />
          <CiDetailCell
            icon={<span className="text-2xl">⚔</span>}
            title="Tuatha Dé Deity"
            metadata={t.tuatha_de}
            description={`The treasure is associated with ${t.tuatha_de}.`}
          />
        </div>
      </CiTextbookPanel>

      <div className="flex justify-center">
        <Link
          to="/en/eiraic-treasures"
          className="text-emerald-400 hover:text-emerald-300 text-sm"
        >
          ← Back to the 13 Éraic Treasures
        </Link>
      </div>
    </div>
  );
}