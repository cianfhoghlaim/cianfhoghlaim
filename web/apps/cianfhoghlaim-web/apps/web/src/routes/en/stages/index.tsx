// /en/stages — Stage index (English locale)
import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/en/stages/")({
  component: EnStagesIndexComponent,
});

function EnStagesIndexComponent() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-3xl font-bold text-slate-100">Stages</h1>
      <p className="text-slate-400">Five stages of the Irish education system.</p>
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
  { slug: "aistear", icon: "🌱", title: "Aistear (Early Childhood)", subtitle: "Ages 0-6 · 4 themes · 4 age bands", route: "/en/stages/aistear" },
  { slug: "primary", icon: "📘", title: "Primary", subtitle: "Ages 4-12 · 12 curriculum areas", route: "/en/stages/primary" },
  { slug: "junior-cycle", icon: "📗", title: "Junior Cycle", subtitle: "Ages 12-15 · 18 subjects", route: "/en/stages/junior-cycle" },
  { slug: "senior-cycle", icon: "🎓", title: "Senior Cycle", subtitle: "Ages 15-18 · 50+ subjects", route: "/en/stages/senior-cycle" },
  { slug: "tertiary", icon: "🏛️", title: "Tertiary", subtitle: "CAO · QQI FET · Apprenticeship · NUI/HEI", route: "/en/stages/tertiary" },
];
