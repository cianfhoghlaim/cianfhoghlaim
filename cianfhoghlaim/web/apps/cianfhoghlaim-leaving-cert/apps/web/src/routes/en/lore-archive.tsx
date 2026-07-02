// /en/lore-archive — Public summary of the 7 lineage clippings
// Per the user's explicit instruction, the 7 lineage clippings at
// cian_mac_an_deisigh_ui_liathain/identity/lineage/references/clippings/
// are part of the theming but the PERSONAL lineage is operator-only.
// This page shows the public-facing summary of the 7 mythological
// clippings — not the personal lineage.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel, CiDetailCell } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/en/lore-archive")({
  component: LoreArchivePage,
});

const CLIPPINGS = [
  {
    file: "tuatha_de_danann-wikipedia.md",
    name: "Tuatha Dé Danann",
    irish: "Tuatha Dé Danann",
    description: "The supernatural race of pre-Christian Irish mythology — the gods of the Gaels. Includes the 13 treasures (Lia Fáil + spear of Lugh + sword of Nuada + cauldron of the Dagda). The 8 NCCA ADK agents are mapped to the 8 Brown Ajah members who are the 8 Tuatha Dé deities.",
    wiki: "https://en.wikipedia.org/wiki/Tuatha_D%C3%A9_Danann",
  },
  {
    file: "cian-wikipedia.md",
    name: "Cian (the enduring one)",
    irish: "Cian (an ceann a mhaireann)",
    description: "Son of Dian Cecht + father of Lugh. The platform name Cianfhoghlaim (cian fhoglaim = 'enduring learning') is grounded in the Cian → Lugh lineage. Cian → Lugh → the threefold gift of knowledge + skill + prophecy that the platform preserves through BAML extraction + DLT ingestion + Dagster orchestration + Cognee cognify.",
    wiki: "https://en.wikipedia.org/wiki/Cian_(mythology)",
  },
  {
    file: "aos_si-wikipedia.md",
    name: "Aos Sí (the folk of the mounds)",
    irish: "Aos Sí (pobal na gcnoc)",
    description: "The supernatural race of medieval Irish folklore. After the Tuatha Dé were defeated by the Milesians, they withdrew into the burial mounds (the sídhe). The Cian → Lugh → 13 éraic treasures are part of this withdrawal mythology. The sídhe are the burial mounds of Connacht (Grianan of Aileach + the barony of Moycullen).",
    wiki: "https://en.wikipedia.org/wiki/Aos_S%C3%AD",
  },
  {
    file: "ui_liathain-wikipedia.md",
    name: "Uí Liatháin",
    irish: "Uí Liatháin",
    description: "Early kingdom of Munster. The Lyons surname belongs to the Uí Anmchada sept of the Uí Meic Caille. Two royal seats: Castlelyons (Caisleán Ó Liatháin) in East Cork + Killaliathan Church in Limerick. The Uí Liatháin colonized Wales + Cornwall + Devon alongside the proto-Déisi (per the Historia Brittonum).",
    wiki: "https://en.wikipedia.org/wiki/U%C3%AD_Liath%C3%A1in",
  },
  {
    file: "deisi-wikipedia.md",
    name: "Déisi",
    irish: "Déisi",
    description: "Vassal social class in early medieval Ireland. The Déisi Muman colonized Waterford + South Tipperary. The Déisi Tuisceart became the Dál gCais → Brian Boru. The Uí Dhéisigh (the Deacy surname) are a sept of the Déisi Muman resettled in south Connacht (Co. Galway) during the 12th century. Eamonn Deacy Park in Galway memorializes the late Éamonn 'Chick' Deacy.",
    wiki: "https://en.wikipedia.org/wiki/D%C3%A9isi",
  },
  {
    file: "delbhna_tir_dha_locha-wikipedia.md",
    name: "Delbhna Tír Dhá Locha",
    irish: "Delbhna Tír Dhá Locha",
    description: "Tuath in Gaelic Ireland in Connemara, Co. Galway. The two lochs: Lough Corrib + Galway Bay. Kings took the surname Mac Con Raoi (anglicised Conroy + King). One of the sea-kings of Connacht alongside O'Malleys, O'Dowds, O'Flahertys. The Delbhna Tír Dhá Locha tuath is the home base of the Cian lineage.",
    wiki: "https://en.wikipedia.org/wiki/Delbhna_T%C3%ADr_Dh%C3%A1_Locha",
  },
  {
    file: "leath_cuinn_and_leath_moga-wikipedia.md",
    name: "Leath Cuinn + Leath Moga",
    irish: "Leath Chuinn + Leath Mhoga",
    description: "The 5th-century division of Ireland. Conn Cétchathach ('Conn of the Hundred Battles') divided Ireland between his son Art mac Cuinn (Leath Cuinn: Connacht + Ulster + Meath) and Mogha Nuadat (Leath Moga: Munster + Leinster). The Esker Riada (Dublin Bay ↔ Galway Bay) was the dividing line. Conn is the common ancestor of both the Connachta and the Uí Néill — the basis of the Cianfhoghlaim claim of Rí Chonnachta (King of Connacht) under Arthur Griffith's dual-monarchy framework.",
    wiki: "https://en.wikipedia.org/wiki/Leath_Cuinn_and_Leath_Moga",
  },
];

function LoreArchivePage() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          The 7 Lineage Clippings Archive
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          The 7 Wikipedia clippings at
          <code className="text-amber-400 mx-2">cian_mac_an_deisigh_ui_liathain/identity/lineage/references/clippings/</code>
          that ground the Brown Ajah + Trí Dé Dána + Éraic Treasures theming.
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          Public summary — the personal lineage is operator-only (see docs/CIANFHLOGHLAIM_LORE.md)
        </p>
      </div>

      <CiTextbookPanel title="The 7 Clippings" material="parchment">
        <div className="space-y-3">
          {CLIPPINGS.map((c) => (
            <CiDetailCell
              key={c.file}
              icon={<span className="text-2xl">📜</span>}
              title={c.name}
              metadata={c.irish}
              description={c.description}
            />
          ))}
        </div>
      </CiTextbookPanel>

      <CiTextbookPanel title="The Brown Ajah Connection" material="ink-wash">
        <p className="text-slate-300 mb-3">
          The 7 clippings map to the 7 Tuatha Dé Danann deities + the
          8th (Computer Science, a modern subject without a direct
          mythological mapping). The personal lineage (the triple-crown
          union of Deacy + Lyons + Conroy) is the operator's own
          documented heritage — referenced in the lore document but
          NOT displayed on the public surface (per the privacy
          constraint in the openspec change).
        </p>
        <Link
          to="/en/brown-ajah"
          className="inline-block mt-2 px-4 py-2 rounded-lg bg-amber-700 text-amber-100 hover:bg-amber-600 transition-colors"
        >
          See the 8 Brown Ajah members →
        </Link>
      </CiTextbookPanel>
    </div>
  );
}