// /ga/lore-archive — Public summary in Irish
// Mirror of /en/lore-archive with bilingual EN+GA content.

import { createFileRoute, Link } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/ga/lore-archive")({
  component: LoreArchivePageGA,
});

function LoreArchivePageGA() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          Cartlann na 7 ghearrthóga sliochta
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          Na 7 gearrthóga Vicipéide a thagann ó{" "}
          <code className="text-amber-400 mx-2">cian_mac_an_deisigh_ui_liathain/identity/lineage/references/clippings/</code>
          a thacaíonn le téamaí an Brown Ajah + Trí Dé Dána + Éraic Treasures.
        </p>
        <p className="text-slate-500 text-sm font-mono italic">
          Achoimre phoiblí — níl an sliocht pearsanta le feiceáil ar an
          dromchla poiblí (féach docs/CIANFHLOGHLAIM_LORE.md)
        </p>
      </div>

      <CiTextbookPanel title="An leagan Béarla" material="parchment">
        <p className="text-slate-300">
          Tá an leagan Béarla iomlán ar fáil ag{" "}
          <Link to="/en/lore-archive" className="text-emerald-400 underline">
            /en/lore-archive
          </Link>
          .
        </p>
      </CiTextbookPanel>
    </div>
  );
}