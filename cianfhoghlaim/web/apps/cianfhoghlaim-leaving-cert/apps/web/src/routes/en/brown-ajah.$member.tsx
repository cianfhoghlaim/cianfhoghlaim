// /en/brown-ajah/$member — Detail page for one of the 8 Brown Ajah members
// Per docs/BROWN_AJAH_THEMING.md — the 8 NCCA subject specialists
// are the 8 Brown Ajah members of the White Tower.

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell, CiSemanticPill } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/brown-ajah/$member")({
  component: BrownAjahMemberDetailPage,
});

const MEMBERS: Record<string, {
  name: string;
  irish_name: string;
  role: string;
  subject: string;
  color: string;
  description_en: string;
  description_ga: string;
  lore_en: string;
  related_eiraic: number[];
  era: string;
}> = {
  "the-dagda": {
    name: "The Dagda",
    irish_name: "An Dagda",
    role: "Cauldron of plenty — the all-provider",
    subject: "Mathematics",
    color: "var(--ci-subject-mathematics)",
    description_en: "The Dagda ('the Good God') is the father-figure of the Tuatha Dé Danann. He possesses the Cauldron of Plenty which never empties — the source of all nourishment, both physical and intellectual.",
    description_ga: "Is é An Dagda ('an tDia Maith') athair na dTuath Dé Danann. Is leis an gCoire Flúirseach nach ídíonn riamh — foinse gach cothaithe, idir chorp agus intleacht.",
    lore_en: "The Dagda was one of the leaders of the Tuatha Dé at the Second Battle of Mag Tuired. His cauldron is one of the four magical treasures brought from the four northern cities (Falias + Gorias + Finias + Murias).",
    related_eiraic: [1, 6, 11],  // Pig of Dobar (healing) + 7 Pigs of Easmal + Pigskin bag
    era: "Tuatha Dé Danann (pre-Christian)",
  },
  "lugh": {
    name: "Lugh (samildanach)",
    irish_name: "Lugh (samildanach)",
    role: "Master of all arts — the polymath",
    subject: "Applied Mathematics",
    color: "var(--ci-subject-applied_mathematics)",
    description_en: "Lugh is the samildanach — 'master of all arts'. Son of Cian (the 'enduring one') and Ethniu (daughter of Balor). Lugh led the Tuatha Dé to victory at the Second Battle of Mag Tuired by slaying Balor with a sling-stone.",
    description_ga: "Is samildanach Lugh — 'máistir gach ealaíne'. Mac Cian (an ceann a mhaireann) agus Ethniu (iníon Bhaloir). Stiúraigh Lugh na Tuath Dé chun bua ag Dara Chath Mag Tuired trí Bhalor a mharú le cloch shlinc.",
    lore_en: "The platform name Cianfhoghlaim (cian fhoglaim = 'enduring learning') is grounded in the Cian → Lugh lineage. Cian ('enduring') → Lugh ('master of all arts') → the threefold gift of knowledge + skill + prophecy that the platform preserves through BAML extraction + DLT ingestion + Dagster orchestration + Cognee cognify.",
    related_eiraic: [3, 4, 10, 13],  // Spear of Assal + Chariot + 3 Apples + samildanach
    era: "Tuatha Dé Danann (pre-Christian)",
  },
  "dian-cecht": {
    name: "Dian Cecht",
    irish_name: "Dian Cecht",
    role: "The healer — physician of the Tuatha Dé",
    subject: "Chemistry",
    color: "var(--ci-subject-chemistry)",
    description_en: "Dian Cecht is the physician of the Tuatha Dé Danann. Father of Cian (the 'enduring one'). He healed the wounded at the Second Battle of Mag Tuired by placing them in a well of healing herbs.",
    description_ga: "Is é Dian Cecht lia an Tuath Dé Danann. Athair Cian (an ceann a mhaireann). Chneasaigh sé na créachta ag an Dara Chath Mag Tuired trí iad a chur i dtobar de luibheanna cneasaithe.",
    lore_en: "Dian Cecht killed his son Miach (who surpassed him in medicine) out of jealousy — a powerful allegory for the cost of medical progress + the importance of ethics in healing.",
    related_eiraic: [1, 11],  // Pig of Dobar (healing) + Pigskin bag of the healing well
    era: "Tuatha Dé Danann (pre-Christian)",
  },
  "brigid": {
    name: "Brigid",
    irish_name: "Brigid",
    role: "Poetry + healing — the word-smith",
    subject: "English",
    color: "var(--ci-subject-english)",
    description_en: "Brigid is the goddess of poetry, healing, and smithcraft. The Trí Dé Dána ('Three Gods of Craft') = Brigid (poetry) + Dian Cecht (medicine) + Ogma (eloquence).",
    description_ga: "Is bandia na filíochta, an chneasaíochta agus an ghabha í Brigid. An Trí Dé Dána ('Trí Dhia na gCeard') = Brigid (filíocht) + Dian Cecht (leigheas) + Ogma (aelódacht).",
    lore_en: "Brigid is also the goddess of the hearth, of poetry, of healing, and of the forge. In Christian Ireland she became St. Brigid of Kildare — a remarkable syncretism between the Tuatha Dé Danann deity and the Christian saint.",
    related_eiraic: [1, 7],  // Pig of Dobar (healing) + Whelp of Ioruaidh (loyalty)
    era: "Tuatha Dé Danann (pre-Christian)",
  },
  "ogma": {
    name: "Ogma",
    irish_name: "Ogma",
    role: "Eloquence + learning — inventor of Ogham",
    subject: "Gaeilge",
    color: "var(--ci-subject-gaeilge)",
    description_en: "Ogma is the god of eloquence and learning. He invented the Ogham script — the earliest Celtic writing system, consisting of strokes along an edge. Father of Cairbre Cenn Cait, one of the great poets of the Tuatha Dé.",
    description_ga: "Is dia na haelódachta agus an foghlama é Ogma. Chum sé an script Ogham — an chéad chóras scríbhneoireachta Ceilteach, ina bhfuil stríoca feadh imeall. Athair Cairbre Cenn Cait, duine de na mórfhíltí den Tuath Dé.",
    lore_en: "The Ogham script is the foundation of the Gaeilge subject's Information Processing competency. Each Ogham stroke represents a letter of the early Irish alphabet.",
    related_eiraic: [8],  // Cooking spit of Innis Cera (crafted response)
    era: "Tuatha Dé Danann (pre-Christian)",
  },
  "manannan-mac-lir": {
    name: "Manannán mac Lir",
    irish_name: "Manannán mac Lir",
    role: "The sea — the tide of memory",
    subject: "Geography",
    color: "var(--ci-subject-geography)",
    description_en: "Manannán mac Lir is the god of the sea. He is the foster-father of Lugh and the lord of the Otherworld (Tír Tairngire). He possesses a magical boat (Scuabtuinne) and a cloak of invisibility (Étaoinn).",
    description_ga: "Is dia na farraige é Manannán mac Lir. Is é athair altrama Lugh agus tiarna an Domhain Eile (Tír Tairngire). Tá bád draíochta (Scuabtuinne) agus brat dochraice (Étaoinn) aige.",
    lore_en: "Manannán's horse Enbarr is one of the three magical horses of the Tuatha Dé (along with Lugh's horse and Dagda's horse). The sea-as-memory motif is central to the Geography subject's study of how landscape shapes human settlement.",
    related_eiraic: [2],  // Heifer of Dobar (pastoral care)
    era: "Tuatha Dé Danann (pre-Christian)",
  },
  "the-morrigan": {
    name: "The Morrígan",
    irish_name: "An Morrígan",
    role: "War + death (and rebirth)",
    subject: "History",
    color: "var(--ci-subject-history)",
    description_en: "The Morrígan is the goddess of war, death, and rebirth. She often appeared as a crow flying over the battlefield, and prophesied the death of individual warriors.",
    description_ga: "Is bandia cogaidh, báis agus athbheochana í An Morrígan. D'érigh sí go minic mar fhiach ag eitilt os cionn an chatha agus rinne sí fáistine bhás trodaigh aonair.",
    lore_en: "The Morrígan's appearance at the Second Battle of Mag Tuired — where she saw Lugh's champion rise — prefigures the History subject's study of pivotal battles + the role of prophecy in shaping historical outcomes.",
    related_eiraic: [9, 12],  // Armour of Clochur + Feather of Bird of Crannog
    era: "Tuatha Dé Danann (pre-Christian)",
  },
  "computer-science": {
    name: "(modern subject)",
    irish_name: "(ábhar nua-aimseartha)",
    role: "Algorithmic clarity",
    subject: "Computer Science",
    color: "var(--ci-subject-computer_science)",
    description_en: "Computer Science is a modern subject (post-1940) without a direct Tuatha Dé Danann deity mapping. The closest mythological reference is the algorithmic clarity of Lugh's samildanach ('master of all arts') — the most polymathic of the Tuatha Dé.",
    description_ga: "Is ábhar nua-aimseartha é Ríomheolaíocht (i ndiaidh 1940) gan mhapaíocht dhíreach dia Tuath Dé Danann. Is é an chur chuige is gaire ná soiléireacht algartamach samildanach Lugh — an ceann is ilchríche de na Tuath Dé.",
    lore_en: "The closest connection to a Tuatha Dé deity is the Sword of Caladbolg (wielded by Tethra, later by Lugh) — symbol of algorithmic clarity + the master of all arts.",
    related_eiraic: [5],  // Sword of Caladbolg
    era: "Modern subject (post-1940)",
  },
};

function BrownAjahMemberDetailPage() {
  const { member } = Route.useParams();
  const m = MEMBERS[member];

  if (!m) {
    throw notFound({ data: { member } });
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <div className="text-3xl font-mono font-bold" style={{ color: m.color }}>
          Brown Ajah
        </div>
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          {m.name}
        </h1>
        <p className="text-slate-400 font-mono text-lg italic">{m.irish_name}</p>
        <p className="text-slate-300 text-base max-w-2xl">
          {m.role}
        </p>
        <p className="text-slate-500 text-sm font-mono">
          Maps to the <strong>{m.subject}</strong> NCCA Leaving Cert subject
        </p>
      </div>

      <CiTextbookPanel title="Description" material="parchment">
        <p className="text-slate-300">{m.description_en}</p>
        <p className="text-slate-500 text-sm font-mono italic mt-4">
          {m.description_ga}
        </p>
      </CiTextbookPanel>

      <CiTextbookPanel title="Lore" material="ink-wash">
        <p className="text-slate-300 italic">{m.lore_en}</p>
      </CiTextbookPanel>

      <CiTextbookPanel title="Mapping" material="knotwork">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <CiDetailCell
            icon={<span className="text-2xl">📚</span>}
            title="Subject"
            metadata={m.subject}
            description={`The Brown Ajah member maps to the ${m.subject} NCCA subject via the theming.`}
          />
          <CiDetailCell
            icon={<span className="text-2xl">⚔</span>}
            title="Era"
            metadata={m.era}
            description={`The ${m.name} is ${m.era}.`}
          />
        </div>
        <div className="mt-4">
          <h3 className="text-sm font-bold text-slate-100 mb-2">
            Related Éraic Treasures:
          </h3>
          <div className="flex flex-wrap gap-2">
            {m.related_eiraic.map((tier) => (
              <Link key={tier} to="/en/eiraic-treasures/$tier" params={{ tier: tier.toString() }}>
                <CiSemanticPill kind="eiraic" label={`Tier ${tier}`} />
              </Link>
            ))}
          </div>
        </div>
      </CiTextbookPanel>

      <div className="flex justify-center">
        <Link
          to="/en/brown-ajah"
          className="text-emerald-400 hover:text-emerald-300 text-sm"
        >
          ← Back to the 8 Brown Ajah members
        </Link>
      </div>
    </div>
  );
}