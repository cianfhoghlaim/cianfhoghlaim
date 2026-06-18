import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { CheckCircle2, Clock, ExternalLink, Loader2, RefreshCw, XCircle } from "lucide-react";
import { fetchSnapshot, type WebStackSnapshot } from "../../../lib/webstack";

export const Route = createFileRoute("/_layout/data/pipelines")({
  component: PipelinesPage,
});

interface DisplayPipeline {
  id: string;
  name: string;
  project: string;
  status: "success" | "failed" | "running";
  lastRun: string;
  schedule: string;
  assets: string[];
}

function buildPipelines(snapshot: WebStackSnapshot | null): DisplayPipeline[] {
  if (!snapshot) return [];
  const groups = new Map<string, DisplayPipeline>();
  for (const fn of snapshot.convexFunctions) {
    if (fn.kind !== "action" && fn.kind !== "internalAction") continue;
    const key = `${fn.project}:${fn.file}`;
    if (groups.has(key)) continue;
    const friendly = fn.file
      .replace(/^.*\/convex\//, "")
      .replace(/\.ts$/, "")
      .replace(/_/g, " ");
    groups.set(key, {
      id: key,
      name: friendly,
      project: fn.project,
      status: "success",
      lastRun: "live",
      schedule: "on cron",
      assets: snapshot.convexFunctions
        .filter((f) => f.file === fn.file)
        .map((f) => f.name),
    });
  }
  return [...groups.values()].sort((a, b) => a.name.localeCompare(b.name));
}

function PipelinesPage() {
  const [snapshot, setSnapshot] = useState<WebStackSnapshot | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchSnapshot().then((s) => {
      if (!mounted) return;
      setSnapshot(s);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="p-6 flex items-center gap-2 text-muted-foreground">
        <Loader2 className="animate-spin" size={16} />
        Loading pipelines…
      </div>
    );
  }

  const pipelines = buildPipelines(snapshot);

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Data Pipelines</h1>
          <p className="text-muted-foreground">
            Convex actions, derived from the live web stack snapshot
          </p>
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
          <button
            onClick={() => window.location.reload()}
            className="flex items-center gap-2 bg-primary text-primary-foreground px-3 py-1.5 rounded hover:bg-primary/90"
          >
            <RefreshCw size={14} />
            Refresh
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {pipelines.length === 0 ? (
          <div className="text-sm text-muted-foreground">
            No Convex actions found. Run{" "}
            <code className="font-mono">bun run croilar/scripts/analyze-web-stack.ts</code> to populate the snapshot.
          </div>
        ) : (
          pipelines.map((pipeline) => <PipelineCard key={pipeline.id} pipeline={pipeline} />)
        )}
      </div>
    </div>
  );
}

function PipelineCard({ pipeline }: { pipeline: DisplayPipeline }) {
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
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-medium">{pipeline.name}</h3>
              <span className="text-xs bg-secondary px-2 py-0.5 rounded">
                {pipeline.project}
              </span>
            </div>
            <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock size={14} />
                {pipeline.schedule}
              </span>
              <span>Source: {pipeline.lastRun}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t">
        <div className="text-xs text-muted-foreground mb-2">Functions</div>
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
