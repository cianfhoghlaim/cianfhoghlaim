import { createFileRoute } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { GraduationCap, Award, BookOpen, Users, Download, Search } from "lucide-react";
import { EducationSection } from "@/pages/cv/education";
import { AwardsSection } from "@/pages/cv/awards";
import { PublicationsSection } from "@/pages/cv/publications";
import { ReferencesSection } from "@/pages/cv/references";

export const Route = createFileRoute("/cv")({
  component: CvPage,
});

function CvPage() {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">{t("cv.title")}</h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto mb-6">
            Bilingual (English + Gaeilge) CV extracted via BAML from source PDFs.
          </p>

          <div className="flex items-center justify-center gap-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder={t("cv.searchPlaceholder")}
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-card border border-border text-sm"
              />
            </div>
            <a
              href="#"
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm"
            >
              <Download className="h-4 w-4" />
              {t("cv.downloadPdf")}
            </a>
          </div>
        </header>

        <nav className="flex flex-wrap gap-2 justify-center mb-12">
          {[
            { id: "education", icon: <GraduationCap className="h-4 w-4" />, label: t("cv.education") },
            { id: "awards", icon: <Award className="h-4 w-4" />, label: t("cv.awards") },
            { id: "publications", icon: <BookOpen className="h-4 w-4" />, label: t("cv.publications") },
            { id: "references", icon: <Users className="h-4 w-4" />, label: t("cv.references") },
          ].map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-card border border-border hover:border-primary/50 transition-colors text-sm"
            >
              {item.icon}
              {item.label}
            </a>
          ))}
        </nav>

        <div className="space-y-16">
          <EducationSection />
          <AwardsSection />
          <PublicationsSection />
          <ReferencesSection />
        </div>
      </div>
    </div>
  );
}
