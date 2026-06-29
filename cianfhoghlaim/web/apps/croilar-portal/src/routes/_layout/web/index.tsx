import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  Cloud,
  Code2,
  Database,
  FileCode,
  Loader2,
  RefreshCw,
} from "lucide-react";
import {
  fetchSnapshot,
  formatRelative,
  PROJECTS,
  type Project,
  type WebStackSnapshot,
} from "../../../lib/webstack";

export const Route = createFileRoute("/_layout/web/")({
  component: WebIndexPage,
});

function WebIndexPage() {
  const [snapshot, setSnapshot] = useState<WebStackSnapshot | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    const load = () =>
      fetchSnapshot().then((s) => {
        if (!mounted) return;
        setSnapshot(s);
        setLoading(false);
      });
    void load();
    const id = setInterval(load, 30_000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  if (loading || !snapshot) {
    return (
      <div className="p-6 flex items-center gap-2 text-muted-foreground">
        <Loader2 className="animate-spin" size={16} />
        Loading web stack snapshot…
      </div>
    );
  }

  const counts: Record<Project, number> = {
    tuatha: 0,
    oideachais: 0,
    croilar: 0,
    meaisinfhoghlaim: 0,
  };
  for (const r of snapshot.tanstackRoutes) {
    if (PROJECTS.includes(r.project as Project)) {
      counts[r.project as Project] += 1;
    }
  }
  const fnCount = (p: Project) =>
    snapshot.convexFunctions.filter((f) => f.project === p).length;
  const bamlCount = (p: Project) =>
    snapshot.bamlSchemas.filter((b) => b.project === p).length;
  const cfCount = (p: Project) =>
    snapshot.cloudflareResources.filter((c) => c.project === p).length;
  const nbCount = (p: Project) =>
    snapshot.marimoNotebooks.filter((n) => n.project === p).length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Web Stack</h1>
          <p className="text-muted-foreground">
            TanStack routes, Convex functions, BAML schemas, Cloudflare
            resources, and marimo notebooks across the monorepo.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <RefreshCw size={12} />
          Snapshot {formatRelative(snapshot.generatedAt)}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {PROJECTS.map((p) => (
          <Link
            key={p}
            to="/web/$project"
            params={{ project: p }}
            className="bg-card rounded-lg border p-4 hover:border-primary transition-colors"
          >
            <div className="font-mono text-xs text-muted-foreground mb-1">
              {p}
            </div>
            <div className="text-3xl font-bold mb-3">{counts[p]}</div>
            <div className="text-xs text-muted-foreground space-y-0.5">
              <div className="flex items-center gap-1.5">
                <FileCode size={12} />
                {counts[p]} routes
              </div>
              <div className="flex items-center gap-1.5">
                <Database size={12} />
                {fnCount(p)} functions
              </div>
              <div className="flex items-center gap-1.5">
                <Code2 size={12} />
                {bamlCount(p)} BAML schemas
              </div>
              <div className="flex items-center gap-1.5">
                <Cloud size={12} />
                {cfCount(p)} Cloudflare
              </div>
              <div className="flex items-center gap-1.5">
                <span>📓</span>
                {nbCount(p)} notebooks
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
