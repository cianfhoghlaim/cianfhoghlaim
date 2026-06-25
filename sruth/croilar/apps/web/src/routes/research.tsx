import { createFileRoute, Link } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { FlaskConical, Brain, ExternalLink } from "lucide-react";
import { CrossLinksSection } from "@/pages/research/crosslinks";

export const Route = createFileRoute("/research")({
  component: ResearchPage,
});

function ResearchPage() {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">{t("research.title")}</h1>
          <p className="text-muted-foreground text-lg">{t("research.subtitle")}</p>
        </header>

        <div className="grid md:grid-cols-2 gap-6 mb-12">
          <Link
            to="/research"
            className="group rounded-2xl bg-card border border-border hover:border-emerald-700/50 transition-colors p-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-full bg-emerald-600/10">
                <FlaskConical className="h-6 w-6 text-emerald-400" />
              </div>
              <h2 className="text-xl font-bold">{t("research.educationPlatform")}</h2>
            </div>
            <p className="text-muted-foreground text-sm mb-4">
              Cross-linked curriculum data, exam papers, marking schemes, and
              Celtic-language coverage from the oideachais subproject. Filtered by
              author &ldquo;Cian de Búrca.&rdquo;
            </p>
            <span className="inline-flex items-center gap-1 text-emerald-400 text-sm">
              <ExternalLink className="h-3 w-3" />
              oideachais/data_platform
            </span>
          </Link>

          <div className="rounded-2xl bg-card border border-border hover:border-cyan-700/50 transition-colors p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-full bg-cyan-600/10">
                <Brain className="h-6 w-6 text-cyan-400" />
              </div>
              <h2 className="text-xl font-bold">{t("research.mlAi")}</h2>
            </div>
            <p className="text-muted-foreground text-sm mb-4">
              OCR, ASR/TTS alignment, and RAG embeddings from the meaisínfhoghlaim
              subproject. Cross-referenced with CV achievements and teaching records.
            </p>
            <span className="inline-flex items-center gap-1 text-cyan-400 text-sm">
              <ExternalLink className="h-3 w-3" />
              meaisínfhoghlaim/agents
            </span>
          </div>
        </div>

        <CrossLinksSection />
      </div>
    </div>
  );
}
