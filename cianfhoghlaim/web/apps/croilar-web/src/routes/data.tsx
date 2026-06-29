import { createFileRoute } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { BarChart3, Clock, Activity, ExternalLink } from "lucide-react";
import { PipelineStatusSection } from "@/pages/data/pipeline-status";

export const Route = createFileRoute("/data")({
  component: DataPage,
});

const PLACEHOLDER_ASSETS = [
  { name: "spotify_ingestion", group: "music", status: "idle" as const, lastRun: "—" },
  { name: "soundcloud_ingestion", group: "music", status: "idle" as const, lastRun: "—" },
  { name: "youtube_ingestion", group: "music", status: "idle" as const, lastRun: "—" },
  { name: "track_metadata_embedded", group: "music", status: "idle" as const, lastRun: "—" },
  { name: "cv_pdf_ingestion", group: "cv", status: "idle" as const, lastRun: "—" },
  { name: "cv_extraction", group: "cv", status: "idle" as const, lastRun: "—" },
  { name: "cv_search_index", group: "cv", status: "idle" as const, lastRun: "—" },
  { name: "placement_ingestion", group: "teaching", status: "idle" as const, lastRun: "—" },
  { name: "teaching_extraction", group: "teaching", status: "idle" as const, lastRun: "—" },
  { name: "teaching_search", group: "teaching", status: "idle" as const, lastRun: "—" },
  { name: "id_document_verification", group: "identity", status: "idle" as const, lastRun: "—" },
  { name: "oideachais_assets_embedded", group: "cross-link", status: "idle" as const, lastRun: "—" },
  { name: "meaisinfhoghlaim_assets_embedded", group: "cross-link", status: "idle" as const, lastRun: "—" },
];

const SCHEDULES = [
  { name: "Daily Music Ingestion", cron: "0 3 * * *", assets: "spotify_ingestion, soundcloud_ingestion, youtube_ingestion, track_metadata_embedded" },
  { name: "Weekly CV Refresh", cron: "0 4 * * 0", assets: "cv_pdf_ingestion, cv_extraction, cv_search_index" },
  { name: "Monthly Identity Check", cron: "0 5 1 * *", assets: "id_document_verification" },
];

function DataPage() {
  const { t } = useTranslation();

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-5xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">{t("data.title")}</h1>
          <p className="text-muted-foreground text-lg">{t("data.subtitle")}</p>
          <a
            href="https://dagster.cianfhoghlaim.ie"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 mt-4 px-4 py-2 rounded-lg bg-card border border-border hover:border-primary/50 transition-colors text-sm"
          >
            <ExternalLink className="h-4 w-4" />
            {t("data.dagsterUi")}
          </a>
        </header>

        <div className="grid grid-cols-3 gap-4 mb-12">
          <StatCard
            icon={<BarChart3 className="h-5 w-5 text-emerald-400" />}
            label={t("data.assetsCount")}
            value={PLACEHOLDER_ASSETS.length}
          />
          <StatCard
            icon={<Clock className="h-5 w-5 text-cyan-400" />}
            label={t("data.schedulesCount")}
            value={SCHEDULES.length}
          />
          <StatCard
            icon={<Activity className="h-5 w-5 text-amber-400" />}
            label={t("data.lastRun")}
            value="—"
          />
        </div>

        <PipelineStatusSection assets={PLACEHOLDER_ASSETS} />

        <section className="mt-12">
          <h2 className="text-2xl font-bold mb-6">{t("data.schedules")}</h2>
          <div className="space-y-4">
            {SCHEDULES.map((s) => (
              <div key={s.name} className="rounded-xl bg-card border border-border p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold">{s.name}</h3>
                  <code className="text-xs bg-muted px-2 py-1 rounded">{s.cron}</code>
                </div>
                <p className="text-sm text-muted-foreground">{s.assets}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string | number }) {
  return (
    <div className="rounded-xl bg-card border border-border p-4 text-center">
      <div className="inline-flex items-center justify-center mb-2">{icon}</div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  );
}
