// /ga/eiraic-treasures — Public page in Irish
// Mirror of /en/eiraic-treasures with bilingual content.

import { createFileRoute } from "@tanstack/react-router";
import { CiTextbookPanel } from "@cianfhoghlaim/ui";

export const Route = createFileRoute("/ga/eiraic-treasures")({
  component: EiraicTreasuresPageGA,
});

const TITLE_GA = "Na 13 Seod Éraic";
const INTRO_GA = "Na 13 seod draíochta a d'iarr Lugh mar éraic (cúiteamh de réir nós) do bhás a athar Cian (an ceann a mhaireann) ag láim Mhac Tuireann. Is iad na 13 seod an tsraith uilechumais de chóras scileanna forásacha an Brown Ajah.";

function EiraicTreasuresPageGA() {
  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <div className="flex flex-col gap-2 items-center text-center">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          {TITLE_GA}
        </h1>
        <p className="text-slate-400 text-lg max-w-3xl">
          {INTRO_GA}
        </p>
      </div>
      <CiTextbookPanel title={TITLE_GA} material="gold-leaf">
        <p className="text-slate-300">
          Tá na 13 seod seo léirithe ar an leathanach Béarla ag{" "}
          <a href="/en/eiraic-treasures" className="text-emerald-400 underline">
            /en/eiraic-treasures
          </a>
          . Tá an leagan Gaeilge ar fáil go luath.
        </p>
      </CiTextbookPanel>
    </div>
  );
}