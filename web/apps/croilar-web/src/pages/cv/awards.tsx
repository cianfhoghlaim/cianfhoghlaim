import { useTranslation } from "react-i18next";
import { Award, Calendar } from "lucide-react";

const PLACEHOLDER_AWARDS = [
  {
    title: "Apple Award",
    issuer: "Apple Inc.",
    year: "2019",
    description: "Recognition for academic excellence and digital creativity at NUI Galway.",
  },
  {
    title: "BCS PGC Scholarship",
    issuer: "British Computer Society",
    year: "2024",
    description: "Postgraduate Certificate scholarship for computing educators.",
  },
  {
    title: "Teaching Council Registration",
    issuer: "The Teaching Council, Ireland",
    year: "2026",
    description: "Full registration as a post-primary teacher in Ireland (Gaeilge, Mathematics, Computer Science).",
  },
];

export function AwardsSection() {
  const { t } = useTranslation();

  return (
    <section id="awards">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Award className="h-6 w-6" />
        {t("cv.awards")}
      </h2>
      <div className="space-y-4">
        {PLACEHOLDER_AWARDS.map((award, i) => (
          <div key={i} className="rounded-xl bg-card border border-border p-6">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-lg">{award.title}</h3>
              <span className="flex items-center gap-1 text-sm text-muted-foreground">
                <Calendar className="h-3 w-3" />
                {award.year}
              </span>
            </div>
            <p className="text-primary text-sm mb-1">{award.issuer}</p>
            <p className="text-muted-foreground text-sm">{award.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
