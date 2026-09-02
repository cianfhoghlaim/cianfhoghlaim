// /ga/céimeanna — Stage index (Irish locale)
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/céimeanna/")({
  component: GaIndexComponent,
});

function GaIndexComponent() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">Céimeanna</h1>
      <p className="text-slate-400">Cúig chéim den chóras oideachais Éireannaigh.</p>
      <div className="grid grid-cols-2 gap-4">
        {STAGES.map((s) => (
          <Link
            key={s.slug}
            to={s.route}
            className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden group hover:border-emerald-700"
          >
            <h3 className="font-bold text-xl mb-2 flex items-center gap-2">
              <span>{s.icon}</span> {s.title}
            </h3>
            <p className="text-slate-500 text-sm">{s.subtitle}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

const STAGES = [
  { slug: "aistear", icon: "🌱", title: "Aistear (Luath-Óige)", subtitle: "0-6 bliana · 4 théama · 4 bhanda aoise", route: "/ga/céimeanna/aistear" },
  { slug: "bunscoil", icon: "📘", title: "Bunscoil", subtitle: "4-12 bliana · 12 limistéar curaclaim", route: "/ga/céimeanna/bunscoil" },
  { slug: "iar-bhunscoil", icon: "📗", title: "Iar-Bhunscoil", subtitle: "12-15 bliana · 18 n-ábhar", route: "/ga/céimeanna/iar-bhunscoil" },
  { slug: "scoil-daraigh", icon: "🎓", title: "Scoil Daraigh", subtitle: "15-18 bliana · 50+ ábhar", route: "/ga/céimeanna/scoil-daraigh" },
  { slug: "ardteistiméireacht", icon: "🏛️", title: "Ardteistiméireacht / Tríú", subtitle: "CAO · QQI FET · Printíseacht · NUI/HEI", route: "/ga/céimeanna/ardteistiméireacht" },
];
