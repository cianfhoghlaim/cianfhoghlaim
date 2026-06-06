import { useTranslation } from "react-i18next";
import { Users, Mail, ExternalLink } from "lucide-react";

const PLACEHOLDER_REFERENCES = [
  {
    name: "Dr. Jane Smith",
    title: "Head of Computer Science, University of Galway",
    email: "j.smith@universityofgalway.ie",
    relationship: "MSc Supervisor",
  },
  {
    name: "Prof. Liam Ó Briain",
    title: "Director, Acadamh na hOllscolaíochta Gaeilge",
    email: "l.obriain@ollscoilnagaillimhe.ie",
    relationship: "PME Programme Director",
  },
];

export function ReferencesSection() {
  const { t } = useTranslation();

  return (
    <section id="references">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Users className="h-6 w-6" />
        {t("cv.references")}
      </h2>
      <div className="grid md:grid-cols-2 gap-4">
        {PLACEHOLDER_REFERENCES.map((ref, i) => (
          <div key={i} className="rounded-xl bg-card border border-border p-6">
            <h3 className="font-semibold text-lg mb-1">{ref.name}</h3>
            <p className="text-primary text-sm mb-1">{ref.title}</p>
            <p className="text-xs text-muted-foreground mb-3">{ref.relationship}</p>
            <div className="flex items-center gap-2">
              <Mail className="h-3 w-3 text-muted-foreground" />
              <a
                href={`mailto:${ref.email}`}
                className="text-sm text-muted-foreground hover:text-primary transition-colors inline-flex items-center gap-1"
              >
                {ref.email}
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
