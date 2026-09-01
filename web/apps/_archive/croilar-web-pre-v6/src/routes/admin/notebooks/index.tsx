import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { fetchSnapshot, type WebStackSnapshot } from "../../../lib/webstack";

export const Route = createFileRoute("/admin/notebooks/")({
  component: NotebooksIndexPage,
});

function NotebooksIndexPage() {
  const [snapshot, setSnapshot] = useState<WebStackSnapshot | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchSnapshot().then((s) => {
      if (!mounted) return;
      setSnapshot(s);
      setLoading(false);
    });
    return () => {
      mounted = false;
    };
  }, []);

  if (loading || !snapshot) {
    return (
      <div className="p-6 flex items-center gap-2 text-muted-foreground">
        <Loader2 className="animate-spin" size={16} />
        Loading…
      </div>
    );
  }

  const notebooks = snapshot.marimoNotebooks;
  const byProject = new Map<string, typeof notebooks>();
  for (const n of notebooks) {
    const list = byProject.get(n.project) ?? [];
    list.push(n);
    byProject.set(n.project, list);
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Marimo Notebooks</h1>
        <p className="text-muted-foreground">
          {notebooks.length} notebooks across the monorepo.
        </p>
      </div>

      {[...byProject.entries()].map(([project, list]) => (
        <section key={project}>
          <h2 className="text-lg font-semibold mb-2 font-mono">{project}</h2>
          <div className="grid grid-cols-3 gap-3">
            {list.map((n) => (
              <Link
                key={`${n.project}:${n.slug}`}
                to="/notebooks/$slug"
                params={{ slug: n.slug }}
                className="bg-card rounded-lg border p-4 hover:border-primary"
              >
                <div className="font-medium">{n.title}</div>
                <div className="text-xs text-muted-foreground font-mono mt-1">
                  {n.slug}
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  {n.cellCount} cells
                </div>
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
