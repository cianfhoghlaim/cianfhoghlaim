// /en/eiraic-treasures — Public page showing the 13 éraic treasures
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
// cianfhoghlaim-leaving-cert-portal/spec.md Requirement R10 + the
// 13 éraic treasures BAML extension (baml/education/_shared/eiraic_treasures.baml).

import { createFileRoute } from "@tanstack/react-router";
import { CiTextbookPanel, CiSemanticPill, CiDetailCell } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/eiraic-treasures")({
  component: EiraicTreasuresPage,
});

const EIRAIC_TREASURES = [
  {
    tier: 1,
    treasure: "Skin of the Pig of Dobar",
    provenance: "Pig of Dobar (Tuatha Dé Danann)",
    capability: "Healing (heals wounds)",
    subject: "Biology",
    color: "var(--ci-subject-chemistry)",
    tuatha_de: "Dian Cecht (healing)",
    rationale_en: "The healing pigskin of Dobar; opens the wound-mending power of the Tuatha Dé's physician. Maps to the Biology subject because both involve the study of life + healing.",
  },
  {
    tier: 2,
    treasure: "Skin of the Heifer of Dobar",
    provenance: "Heifer of Dobar (Tuatha Dé Danann)",
    capability: "Pastoral care",
    subject: "Geography",
    color: "var(--ci-subject-geography)",
    tuatha_de: "Manannán mac Lir (sea + land)",
    rationale_en: "The heifer of Dobar; symbol of pastoral land cultivation. Maps to the Geography subject because both involve the study of land + human settlement patterns.",
  },
  {
    tier: 3,
    treasure: "Spear of Assal",
    provenance: "Spear of Assal (Tuatha Dé Danann)",
    capability: "Precise reasoning (never misses its mark)",
    subject: "Mathematics",
    color: "var(--ci-subject-mathematics)",
    tuatha_de: "Lugh (samildanach)",
    rationale_en: "The spear that never misses — symbolic of mathematical precision. Maps to the Mathematics subject because both involve proof + rigorous reasoning.",
  },
  {
    tier: 4,
    treasure: "Chariot of the king of Sidrach",
    provenance: "Chariot of Sidrach (Tuatha Dé Danann)",
    capability: "Speed of completion",
    subject: "Applied Mathematics",
    color: "var(--ci-subject-applied_mathematics)",
    tuatha_de: "Lugh (samildanach)",
    rationale_en: "The chariot of Sidrach; symbol of speed. Maps to the Applied Mathematics subject because both involve applying math in time-pressured contexts.",
  },
  {
    tier: 5,
    treasure: "Sword of Caladbolg (wielded by Tethra)",
    provenance: "Tethra (Fomorian king)",
    capability: "Algorithmic clarity (the sword of clarity)",
    subject: "Computer Science",
    color: "var(--ci-subject-computer_science)",
    tuatha_de: "— (modern subject)",
    rationale_en: "The sword of Caladbolg; later wielded by Lugh himself after the Second Battle of Mag Tuired. Maps to the Computer Science subject because both involve the clarity of algorithmic thinking.",
  },
  {
    tier: 6,
    treasure: "Seven Pigs of Easmal",
    provenance: "Pigs of Easmal (Tuatha Dé Danann)",
    capability: "Daily practice (regenerate after slaughter)",
    subject: "All subjects (cross-subject)",
    color: "#f59e0b",
    tuatha_de: "Trí Dé Dána (collectively)",
    rationale_en: "The seven pigs that could be slaughtered and eaten daily, only to regenerate. Maps to all subjects because the act of daily practice across all disciplines keeps the mind alive.",
  },
  {
    tier: 7,
    treasure: "Whelp of the king of Ioruaidh",
    provenance: "Whelp of Ioruaidh (Tuatha Dé Danann)",
    capability: "Loyalty + tenacity",
    subject: "English",
    color: "var(--ci-subject-english)",
    tuatha_de: "Brigid (poetry + healing)",
    rationale_en: "The whelp of the king of Ioruaidh; symbol of loyalty. Maps to the English subject because the reading + writing of literature demands both loyalty to the text + tenacity in interpretation.",
  },
  {
    tier: 8,
    treasure: "Cooking spit of the woman of Innis Cera",
    provenance: "Woman of Innis Cera (Tuatha Dé Danann)",
    capability: "Crafted response (the cooking spit + the cauldron)",
    subject: "Gaeilge",
    color: "var(--ci-subject-gaeilge)",
    tuatha_de: "Ogma (eloquence + learning)",
    rationale_en: "The cooking spit of the woman of Innis Cera; symbol of crafted response. Maps to the Gaeilge subject because the writing of Irish requires both craft + care in expression.",
  },
  {
    tier: 9,
    treasure: "Helmet + Breastplate of the king of Clochur",
    provenance: "King of Clochur (Fomorian)",
    capability: "Defensive argument (the defensive armour)",
    subject: "History",
    color: "var(--ci-subject-history)",
    tuatha_de: "The Morrígan (war + death)",
    rationale_en: "The armour of the king of Clochur; symbol of defence. Maps to the History subject because the study of history requires both defending one's interpretation + arming against revisionism.",
  },
  {
    tier: 10,
    treasure: "Three Apples of the Hesperides",
    provenance: "Garden of the Hesperides (Greek myth)",
    capability: "Triple-crown mastery (3 fruits = 3 levels of mastery)",
    subject: "Cross-subject (capped mastery)",
    color: "#fbbf24",
    tuatha_de: "Lugh (samildanach — master of all arts)",
    rationale_en: "The three golden apples of the Hesperides; symbol of the triple-crown mastery (the Attempted → Familiar → Proficient → Mastered ladder capped at the highest level). Maps to cross-subject mastery.",
  },
  {
    tier: 11,
    treasure: "Pigskin Bag of the Healing Well",
    provenance: "Pigskin bag (Tuatha Dé Danann)",
    capability: "Citation rigor (carries the waters of the healing well)",
    subject: "All subjects (citation rigor)",
    color: "#94a3b8",
    tuatha_de: "Dian Cecht (healing)",
    rationale_en: "The pigskin bag that carried the waters of the healing well. Maps to all subjects because academic citation is the pigskin bag of knowledge — it carries the healing waters of citations to the reader.",
  },
  {
    tier: 12,
    treasure: "Feather of the Bird of Crannog",
    provenance: "Bird of Crannog (Tuatha Dé Danann)",
    capability: "Recovery from failure (the feather that resurrects the dead)",
    subject: "All subjects (resilience)",
    color: "#10b981",
    tuatha_de: "The Morrígan (war + death — but also rebirth)",
    rationale_en: "The feather of the Bird of Crannog; symbol of resilience. Maps to all subjects because the path of learning involves many failures + the feather of the Bird of Crannog allows recovery from them.",
  },
  {
    tier: 13,
    treasure: "Lugh's own Samildanach (master of all arts)",
    provenance: "Lugh (Tuatha Dé Danann)",
    capability: "Universal mastery (master of all arts)",
    subject: "All subjects (universal capstone)",
    color: "#fbbf24",
    tuatha_de: "Lugh (samildanach)",
    rationale_en: "Lugh's own samildanach ('master of all arts'); the capstone treasure. Maps to all subjects as the universal mastery tier. To reach tier 13 the student has mastered the Attempted + Familiar + Proficient + Mastered levels across all 5 NCCA Key Competencies + all 8 NCCA subjects.",
  },
];

function EiraicTreasuresPage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          The 13 Éraic Treasures
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          The 13 magical treasures that Lugh demanded as <em>éraic</em> (ritual
          compensation) for the death of his father Cian (the "enduring one") at
          the hands of the Sons of Tuireann. The 13 treasures form the
          universal mastery tier of the Brown Ajah's progressive skill system.
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          Per docs/CIANFHLOGHLAIM_LORE.md (operator-only) + baml/education/_shared/eiraic_treasures.baml
        </p>
      </div>

      <CiTextbookPanel title="The 13 Treasures" material="gold-leaf">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left text-slate-400 p-2">#</th>
                <th className="text-left text-slate-400 p-2">Treasure</th>
                <th className="text-left text-slate-400 p-2">Capability</th>
                <th className="text-left text-slate-400 p-2">Subject</th>
                <th className="text-left text-slate-400 p-2">Tuatha Dé deity</th>
              </tr>
            </thead>
            <tbody>
              {EIRAIC_TREASURES.map((t) => (
                <tr key={t.tier} className="border-t border-slate-700">
                  <td className="p-2 text-center font-mono font-bold" style={{ color: t.color }}>
                    {t.tier}
                  </td>
                  <td className="p-2 font-medium text-slate-100">{t.treasure}</td>
                  <td className="p-2 text-slate-300">{t.capability}</td>
                  <td className="p-2">
                    <CiSemanticPill
                      kind="eiraic"
                      label={t.subject}
                    />
                  </td>
                  <td className="p-2 text-slate-400 italic text-xs">{t.tuatha_de}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="The Rationale — Why these 13 treasures?" material="parchment">
        <div className="grid grid-cols-1 gap-3">
          {EIRAIC_TREASURES.map((t) => (
            <CiDetailCell
              key={t.tier}
              icon={<span className="font-mono font-bold" style={{ color: t.color }}>{t.tier}</span>}
              title={t.treasure}
              metadata={`${t.subject} · ${t.tuatha_de}`}
              description={t.rationale_en}
            />
          ))}
        </div>
      </CiTextbookPanel>
    </div>
  );
}