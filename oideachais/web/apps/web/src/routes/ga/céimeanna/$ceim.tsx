// /ga/céimeanna/$ceim — Stage overview page (Irish locale)
//
// The route path uses ASCII-safe `$ceim` (not `$céim`) because TanStack
// Router's file-based generator requires param names that are valid
// JavaScript identifiers (see https://router.tanstack.com/framework/react/guide/file-based-routing#dynamic-segments).
// `é` is a non-ASCII character and would trigger a "Invalid param name"
// warning in @tanstack/router-cli generate, causing routeTree.gen.ts
// to be regenerated on every build with a mangled identifier — the
// "feedback loop" fixed by issue #7.
import { createFileRoute, notFound } from "@tanstack/react-router";

export const Route = createFileRoute("/ga/céimeanna/$ceim")({
  loader: ({ params }) => {
    const stageMap: Record<string, string> = {
      aistear: "aistear",
      bunscoil: "primary",
      "iar-bhunscoil": "junior_cycle",
      "scoil-daraigh": "senior_cycle",
      ardteistiméireacht: "tertiary",
    };
    const enSlug = stageMap[params.ceim];
    if (!enSlug) throw notFound();
    return { enSlug, irSlug: params.ceim };
  },
  component: StageComponent,
});

function StageComponent() {
  const { ceim } = Route.useParams();
  const stageMap: Record<string, { title_ga: string; description_ga: string }> = {
    aistear: {
      title_ga: "Aistear (Luath-Óige)",
      description_ga: "4 théama × 4 bhanda aoise × ~30 sprioc foghlama × 14 PDF foinseacha + eolaire naíonra + leideanna do thuismitheoirí.",
    },
    bunscoil: {
      title_ga: "Bunscoil",
      description_ga: "Creatlaí Bunscoile NCCA — 12 limistéar curaclaim × 4 chéim. Snáitheanna × torthaí × naisc tras-churaclaim.",
    },
    "iar-bhunscoil": {
      title_ga: "Iar-Bhunscoil",
      description_ga: "18 croí-ábhar + 16 ghearrchúrsa, 2 CBA in aghaidh ábhair, 4 Leibhéal Ghnóthachtála in aghaidh CBA.",
    },
    "scoil-daraigh": {
      title_ga: "Scoil Daraigh",
      description_ga: "50+ ábhar Ardteistiméireachta ar fud 7 dteaghlach. Páipéir scrúdaithe, scéimeanna marcála, tuarascálacha Scrúdaitheora Sinsearaigh.",
    },
    ardteistiméireacht: {
      title_ga: "Ardleibhéal / Tríú",
      description_ga: "Cúrsaí CAO, matraitiúil NUI/HEI, gradaim QQI FET, printíseachtaí, amlíne iarratais.",
    },
  };
  const s = stageMap[ceim] ?? {
    title_ga: ceim,
    description_ga: "—",
  };
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">
        {s.title_ga}
      </h1>
      <p className="text-slate-300 text-lg">{s.description_ga}</p>
    </div>
  );
}
