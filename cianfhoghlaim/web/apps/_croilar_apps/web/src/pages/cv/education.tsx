import { useTranslation } from "react-i18next";
import { GraduationCap, Calendar, MapPin } from "lucide-react";

const PLACEHOLDER_EDUCATION = [
  {
    institution: "University of Galway",
    degree: "MSc in Artificial Intelligence",
    period: "2026–2027",
    location: "Galway, Ireland",
    description: "Research focus on Irish-language NLP and curriculum knowledge graphs.",
  },
  {
    institution: "University of Galway",
    degree: "Professional Master of Education (PME)",
    period: "2024–2026",
    location: "Galway, Ireland",
    description: "BCS PGC scholarship. Teaching practice in Gaeilge, Mathematics, and Computer Science.",
  },
  {
    institution: "University of Galway (NUI Galway)",
    degree: "Bachelor of Arts (BA) + Higher Diploma (HDip)",
    period: "2013–2023",
    location: "Galway, Ireland",
    description: "Double major. Apple Award recipient for academic excellence.",
  },
];

export function EducationSection() {
  const { t } = useTranslation();

  return (
    <section id="education">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <GraduationCap className="h-6 w-6" />
        {t("cv.education")}
      </h2>
      <div className="space-y-4">
        {PLACEHOLDER_EDUCATION.map((item, i) => (
          <div key={i} className="rounded-xl bg-card border border-border p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2">
              <h3 className="font-semibold text-lg">{item.degree}</h3>
              <span className="flex items-center gap-1 text-sm text-muted-foreground">
                <Calendar className="h-3 w-3" />
                {item.period}
              </span>
            </div>
            <p className="text-primary font-medium mb-1">{item.institution}</p>
            <div className="flex items-center gap-1 text-xs text-muted-foreground mb-2">
              <MapPin className="h-3 w-3" />
              {item.location}
            </div>
            <p className="text-muted-foreground text-sm">{item.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
