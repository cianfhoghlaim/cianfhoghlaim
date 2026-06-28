import { useTranslation } from "react-i18next";
import { BookOpen, ExternalLink } from "lucide-react";

const PLACEHOLDER_PUBLICATIONS = [
  {
    title: "Celtic Curriculum Graph: A Bilingual Knowledge Graph for Irish Education",
    venue: "Irish Conference on Artificial Intelligence and Cognitive Science (AICS)",
    year: "2025",
    url: "#",
  },
  {
    title: "GaBERT: Fine-Tuning BERT for Irish-Language Educational Content Classification",
    venue: "CELTIC NLP Workshop @ ACL",
    year: "2025",
    url: "#",
  },
];

export function PublicationsSection() {
  const { t } = useTranslation();

  return (
    <section id="publications">
      <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <BookOpen className="h-6 w-6" />
        {t("cv.publications")}
      </h2>
      <div className="space-y-4">
        {PLACEHOLDER_PUBLICATIONS.map((pub, i) => (
          <div key={i} className="rounded-xl bg-card border border-border p-6">
            <h3 className="font-semibold text-lg mb-1">{pub.title}</h3>
            <p className="text-primary text-sm mb-2">{pub.venue} · {pub.year}</p>
            {pub.url !== "#" && (
              <a
                href={pub.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                <ExternalLink className="h-3 w-3" />
                View publication
              </a>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
