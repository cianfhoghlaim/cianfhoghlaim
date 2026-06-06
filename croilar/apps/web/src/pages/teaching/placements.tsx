import { useTranslation } from "react-i18next";
import { School, Calendar, MapPin } from "lucide-react";

const PLACEHOLDER_PLACEMENTS = [
  {
    school: "Coláiste Iognáid (The Jes)",
    location: "Galway City",
    period: "Semester 1, 2025",
    subjects: "Gaeilge, Mathematics",
    description: "Post-primary teaching practice at a co-educational secondary school. Delivered lessons in Gaeilge and Mathematics to Junior Cycle and Leaving Certificate students.",
  },
  {
    school: "Coláiste na Coiribe",
    location: "Galway City",
    period: "Semester 2, 2026",
    subjects: "Computer Science, Gaeilge",
    description: "Gaelscoil teaching practice. Delivered Computer Science through the medium of Irish. Developed bilingual programming resources (Python + Gaeilge).",
  },
];

export function PlacementsSection() {
  const { t } = useTranslation();

  return (
    <section id="placements">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <School className="h-6 w-6" />
        {t("teaching.placements")}
      </h2>
      <div className="space-y-4">
        {PLACEHOLDER_PLACEMENTS.map((p, i) => (
          <div key={i} className="rounded-xl bg-card border border-border p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2">
              <h3 className="font-semibold text-lg">{p.school}</h3>
              <span className="flex items-center gap-1 text-sm text-muted-foreground">
                <Calendar className="h-3 w-3" />
                {p.period}
              </span>
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground mb-2">
              <MapPin className="h-3 w-3" />
              {p.location}
            </div>
            <p className="text-sm text-muted-foreground mb-2">{p.description}</p>
            <div className="flex flex-wrap gap-1">
              {p.subjects.split(", ").map((s) => (
                <span key={s} className="px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary">
                  {s}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
