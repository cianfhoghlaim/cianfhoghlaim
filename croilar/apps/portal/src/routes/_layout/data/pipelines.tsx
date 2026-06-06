import { createFileRoute } from "@tanstack/react-router";
import { CheckCircle2, Clock, ExternalLink, Play, RefreshCw, XCircle } from "lucide-react";

export const Route = createFileRoute("/_layout/data/pipelines")({
  component: PipelinesPage,
});

const pipelines = [
  {
    id: "tuath_curriculum",
    name: "Celtic Curriculum",
    project: "tuath",
    status: "success" as const,
    lastRun: "2 hours ago",
    nextRun: "in 22 hours",
    schedule: "Daily 2 AM",
    assets: ["celtic_curriculum", "curriculum_embeddings"],
  },
  {
    id: "tuath_mythology",
    name: "Mythology Content",
    project: "tuath",
    status: "success" as const,
    lastRun: "3 days ago",
    nextRun: "in 4 days",
    schedule: "Weekly Sunday 3 AM",
    assets: ["mythology_content", "mythology_embeddings", "knowledge_graph"],
  },
  {
    id: "crypteolas_github",
    name: "GitHub Intelligence",
    project: "crypteolas",
    status: "success" as const,
    lastRun: "45 min ago",
    nextRun: "in 15 min",
    schedule: "Hourly",
    assets: ["github_repositories", "github_commits", "github_contributors"],
  },
  {
    id: "crypteolas_defi",
    name: "DeFi Protocols",
    project: "crypteolas",
    status: "failed" as const,
    lastRun: "2 hours ago",
    nextRun: "in 13 min",
    schedule: "Every 15 min",
    assets: ["defi_protocols", "defi_pools"],
    error: "Rate limit exceeded on DeFiLlama API",
  },
  {
    id: "crypteolas_prices",
    name: "Token Prices",
    project: "crypteolas",
    status: "running" as const,
    lastRun: "1 min ago",
    nextRun: "-",
    schedule: "Every minute",
    assets: ["defi_prices", "funding_rates"],
  },
  {
    id: "aleyum_artwork",
    name: "Artwork Embeddings",
    project: "aleyum",
    status: "success" as const,
    lastRun: "1 day ago",
    nextRun: "in 23 hours",
    schedule: "Daily 4 AM",
    assets: ["artwork_embeddings"],
  },
];

function PipelinesPage() {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Data Pipelines</h1>
          <p className="text-muted-foreground">Dagster orchestration across all projects</p>
        </div>
        <div className="flex gap-2">
          <a
            href="http://localhost:3000"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 bg-secondary px-3 py-1.5 rounded hover:bg-secondary/80"
          >
            <ExternalLink size={14} />
            Open Dagster UI
          </a>
          <button className="flex items-center gap-2 bg-primary text-primary-foreground px-3 py-1.5 rounded hover:bg-primary/90">
            <RefreshCw size={14} />
            Refresh
          </button>
        </div>
      </div>

      {/* Pipeline List */}
      <div className="space-y-4">
        {pipelines.map((pipeline) => (
          <PipelineCard key={pipeline.id} pipeline={pipeline} />
        ))}
      </div>
    </div>
  );
}

function PipelineCard({ pipeline }: { pipeline: (typeof pipelines)[0] }) {
  return (
    <div className="bg-card rounded-lg border p-4">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <div className="mt-1">
            {pipeline.status === "success" && (
              <CheckCircle2 className="text-status-healthy" size={20} />
            )}
            {pipeline.status === "failed" && (
              <XCircle className="text-status-error" size={20} />
            )}
            {pipeline.status === "running" && (
              <RefreshCw className="text-primary animate-spin" size={20} />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-medium">{pipeline.name}</h3>
              <span className="text-xs bg-secondary px-2 py-0.5 rounded">{pipeline.project}</span>
            </div>
            <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock size={14} />
                {pipeline.schedule}
              </span>
              <span>Last run: {pipeline.lastRun}</span>
              <span>Next run: {pipeline.nextRun}</span>
            </div>
            {pipeline.error && (
              <div className="mt-2 text-sm text-status-error bg-status-error/10 px-2 py-1 rounded">
                {pipeline.error}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button className="flex items-center gap-1 text-sm bg-secondary hover:bg-secondary/80 px-3 py-1.5 rounded">
            <Play size={14} />
            Run Now
          </button>
        </div>
      </div>

      {/* Assets */}
      <div className="mt-4 pt-4 border-t">
        <div className="text-xs text-muted-foreground mb-2">Assets</div>
        <div className="flex flex-wrap gap-2">
          {pipeline.assets.map((asset) => (
            <span
              key={asset}
              className="text-xs bg-secondary px-2 py-1 rounded font-mono"
            >
              {asset}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
