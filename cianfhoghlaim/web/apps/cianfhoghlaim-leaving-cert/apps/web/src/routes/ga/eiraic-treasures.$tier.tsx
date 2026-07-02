// /ga/eiraic-treasures/$tier — Detail page in Irish for one of the 13 éraic treasures
// Mirror of /en/eiraic-treasures/$tier with bilingual EN+GA content.

import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/ga/eiraic-treasures/$tier")({
  component: EiraicTreasureDetailPageGA,
});

const TREASURES_GA: Record<string, { tier: number; name_en: string; name_ga: string; tuatha_de: string }> = {
  "1": { tier: 1, name_en: "Skin of the Pig of Dobar", name_ga: "Craiceann na Muice Dobar", tuatha_de: "Dian Cecht" },
  "2": { tier: 2, name_en: "Skin of the Heifer of Dobar", name_ga: "Craiceann na Gamhna Dobar", tuatha_de: "Manannán mac Lir" },
  "3": { tier: 3, name_en: "Spear of Assal", name_ga: "Sleá Assal", tuatha_de: "Lugh" },
  "4": { tier: 4, name_en: "Chariot of the king of Sidrach", name_ga: "Carbad Rí Shidraigh", tuatha_de: "Lugh" },
  "5": { tier: 5, name_en: "Sword of Caladbolg", name_ga: "Claíomh Caladbolg", tuatha_de: "—" },
  "6": { tier: 6, name_en: "Seven Pigs of Easmal", name_ga: "Seacht Muic Easmal", tuatha_de: "Trí Dé Dána" },
  "7": { tier: 7, name_en: "Whelp of the king of Ioruaidh", name_ga: "Coileán Rí Ioruaidh", tuatha_de: "Brigid" },
  "8": { tier: 8, name_en: "Cooking spit of the woman of Innis Cera", name_ga: "Bior Rósta na Mná Innis Cera", tuatha_de: "Ogma" },
  "9": { tier: 9, name_en: "Helmet + Breastplate of the king of Clochur", name_ga: "Clogad + Luirech Rí Chlochuir", tuatha_de: "The Morrígan" },
  "10": { tier: 10, name_en: "Three Apples of the Hesperides", name_ga: "Trí Úll Hesperides", tuatha_de: "Lugh" },
  "11": { tier: 11, name_en: "Pigskin Bag of the Healing Well", name_ga: "Mála Craicinn na Tobair Cneasaithe", tuatha_de: "Dian Cecht" },
  "12": { tier: 12, name_en: "Feather of the Bird of Crannog", name_ga: "Cleit Éan Crannog", tuatha_de: "The Morrígan" },
  "13": { tier: 13, name_en: "Lugh's own Samildanach", name_ga: "Samildanach Lugh", tuatha_de: "Lugh" },
};

function EiraicTreasureDetailPageGA() {
  const { tier } = Route.useParams();
  const t = TREASURES_GA[tier];

  if (!t) {
    throw notFound({ data: { tier } });
  }

  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <div className="text-3xl font-mono font-bold text-amber-400">
          Sraith {t.tier} / 13
        </div>
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          {t.name_ga}
        </h1>
        <p className="text-slate-400 text-base italic">
          {t.name_en}
        </p>
        <p className="text-slate-500 text-sm font-mono">↔ {t.tuatha_de}</p>
      </div>

      <CiTextbookPanel title="An leagan Gaeilge" material="parchment">
        <p className="text-slate-300">
          Tá an leagan Béarla ar fáil ag{" "}
          <Link to="/en/eiraic-treasures/$tier" params={{ tier }} className="text-emerald-400 underline">
            /en/eiraic-treasures/{t.tier}
          </Link>
          . Tá an leagan Gaeilge i mbun forbartha.
        </p>
      </CiTextbookPanel>

      <div className="flex justify-center">
        <Link
          to="/ga/eiraic-treasures"
          className="text-emerald-400 hover:text-emerald-300 text-sm"
        >
          ← Ar ais chuig na 13 Seod Éraic
        </Link>
      </div>
    </div>
  );
}