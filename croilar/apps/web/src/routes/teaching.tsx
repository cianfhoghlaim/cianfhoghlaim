import { createFileRoute } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { School, MessageSquare, BookOpen } from "lucide-react";
import { PlacementsSection } from "@/pages/teaching/placements";
import { FeedbackSection } from "@/pages/teaching/feedback";

export const Route = createFileRoute("/teaching")({
  component: TeachingPage,
});

function TeachingPage() {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">{t("teaching.title")}</h1>
          <p className="text-muted-foreground text-lg">{t("teaching.subtitle")}</p>
        </header>

        <nav className="flex flex-wrap gap-2 justify-center mb-12">
          {[
            { id: "placements", icon: <School className="h-4 w-4" />, label: t("teaching.placements") },
            { id: "feedback", icon: <MessageSquare className="h-4 w-4" />, label: t("teaching.feedback") },
            { id: "curriculum", icon: <BookOpen className="h-4 w-4" />, label: t("teaching.curriculum") },
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
          <PlacementsSection />
          <FeedbackSection />

          <section id="curriculum">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <BookOpen className="h-6 w-6" />
              {t("teaching.curriculum")}
            </h2>
            <div className="rounded-xl bg-card border border-border p-6">
              <p className="text-muted-foreground">
                Curriculum materials designed during school placements — extracted
                from teaching PDFs via BAML. Includes lesson plans, assessment
                rubrics, and differentiated resources for Gaeilge, Mathematics, and
                Computer Science.
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
