// /index — Cianfhoghlaim Oideachais landing page
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  component: LandingComponent,
});

function LandingComponent() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-8 h-full">
      <div className="flex flex-col gap-2">
        <h1 className="font-cinzel text-4xl font-bold text-slate-100">
          Fáilte go Cianfhoghlaim Oideachais
        </h1>
        <p className="text-slate-400 text-lg">
          Your bilingual, agentic gateway to the entire Irish education system
          — Aistear, Primary, Junior Cycle, Senior Cycle, and Tertiary. BAML-extracted
          curriculum, exam papers, marking schemes, Chief Examiner reports, CAO points,
          and matriculation rules, all indexed in Cognee + LanceDB and served via
          CopilotKit AGUI.
        </p>
        <p className="text-slate-500 text-sm font-mono">
          Welcome to Cianfhoghlaim Oideachais · Bilingual EN/GA · 5 stages · 50+ LC subjects
        </p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        {STAGES.map((s) => (
          <Link
            key={s.slug}
            to={s.route}
            className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-emerald-700"
          >
            <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
              <span>{s.icon}</span> {s.title_en}
            </h3>
            <p className="text-slate-400 text-sm mb-2 font-mono text-xs">
              {s.title_ga}
            </p>
            <p className="text-slate-500 text-sm">{s.description_en}</p>
            <span className="btn-tactile inline-block text-sm mt-4">Open →</span>
          </Link>
        ))}
      </div>
    </div>
  );
}

const STAGES = [
  {
    slug: "aistear",
    icon: "🌱",
    title_en: "Aistear (Early Childhood)",
    title_ga: "Aistear (Luath-Óige)",
    description_en: "Ages 0-6. 4 themes, 4 age bands, naíonra directory, parent tips.",
    route: "/en/stages/aistear" as const,
  },
  {
    slug: "primary",
    icon: "📘",
    title_en: "Primary",
    title_ga: "Bunscoil",
    description_en: "Ages 4-12. 12 curriculum areas, 4 stages (Junior/Senior Infants → 5th/6th Class).",
    route: "/en/stages/primary" as const,
  },
  {
    slug: "junior_cycle",
    icon: "📗",
    title_en: "Junior Cycle",
    title_ga: "Iar-Bhunscoil",
    description_en: "Ages 12-15. 18 core subjects + 16 short courses, 2 CBAs each.",
    route: "/en/stages/junior-cycle" as const,
  },
  {
    slug: "senior_cycle",
    icon: "🎓",
    title_en: "Senior Cycle",
    title_ga: "Scoil Daraigh",
    description_en: "Ages 15-18. 50+ Leaving Cert subjects, exam papers, marking schemes, Chief Examiner reports.",
    route: "/en/stages/senior-cycle" as const,
  },
  {
    slug: "tertiary",
    icon: "🏛️",
    title_en: "Tertiary",
    title_ga: "Ardteistiméireacht / Tríú",
    description_en: "Post-LC. CAO, NUI/HEI matriculation, QQI FET awards, Apprenticeships.",
    route: "/en/stages/tertiary" as const,
  },
];
