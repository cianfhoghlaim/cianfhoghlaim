import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  Cloud,
  Code2,
  Database,
  FileCode,
  Loader2,
  X,
} from "lucide-react";
import {
  fetchSnapshot,
  formatRelative,
  PROJECTS,
  troubleshoot,
  type ConvexFunction,
  type BamlSchema,
  type MarimoNotebook,
  type Project,
  type TanstackRoute,
  type WebStackSnapshot,
} from "../../../lib/webstack";

export const Route = createFileRoute("/_layout/web/$project")({
  component: WebProjectPage,
});

function WebProjectPage() {
  const { project } = Route.useParams();
  if (!PROJECTS.includes(project as Project)) throw notFound();

  const [snapshot, setSnapshot] = useState<WebStackSnapshot | null>(null);
  const [drawer, setDrawer] = useState<TanstackRoute | null>(null);
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

  const routes = snapshot.tanstackRoutes.filter((r) => r.project === project);
  const fns = snapshot.convexFunctions.filter((f) => f.project === project);
  const baml = snapshot.bamlSchemas.filter((b) => b.project === project);
  const cf = snapshot.cloudflareResources.filter((c) => c.project === project);
  const nb = snapshot.marimoNotebooks.filter((n) => n.project === project);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Link to="/web" className="hover:text-foreground">
          Web
        </Link>
        <span>/</span>
        <span className="text-foreground font-mono">{project}</span>
      </div>

      <section>
        <SectionHeader icon={<FileCode size={18} />} title="TanStack Routes" count={routes.length} />
        <div className="bg-card rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="text-xs text-muted-foreground border-b">
              <tr>
                <th className="text-left p-2">Route</th>
                <th className="text-left p-2">File</th>
                <th className="text-left p-2">Server</th>
                <th className="text-left p-2">Loader</th>
                <th className="text-left p-2">Auth</th>
                <th className="text-right p-2">Lines</th>
                <th className="text-right p-2">Last commit</th>
              </tr>
            </thead>
            <tbody>
              {routes.map((r) => (
                <tr
                  key={`${r.project}:${r.route}`}
                  className="border-b last:border-0 hover:bg-muted/50 cursor-pointer"
                  onClick={() => setDrawer(r)}
                >
                  <td className="p-2 font-mono">{r.route}</td>
                  <td className="p-2 text-muted-foreground text-xs">{r.file}</td>
                  <td className="p-2">{r.isServer ? "yes" : "—"}</td>
                  <td className="p-2">{r.hasLoader ? "yes" : "—"}</td>
                  <td className="p-2">{r.hasAuth ? "yes" : "—"}</td>
                  <td className="p-2 text-right">{r.lines}</td>
                  <td className="p-2 text-right text-xs text-muted-foreground">
                    {formatRelative(r.lastCommitAt)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <SectionHeader icon={<Database size={18} />} title="Convex Functions" count={fns.length} />
        <div className="bg-card rounded-lg border overflow-hidden">
          <table className="w-full text-sm">
            <thead className="text-xs text-muted-foreground border-b">
              <tr>
                <th className="text-left p-2">Name</th>
                <th className="text-left p-2">Kind</th>
                <th className="text-left p-2">File</th>
                <th className="text-right p-2">Lines</th>
              </tr>
            </thead>
            <tbody>
              {fns.map((f) => (
                <tr key={`${f.project}:${f.file}:${f.name}`} className="border-b last:border-0">
                  <td className="p-2 font-mono">{f.name}</td>
                  <td className="p-2 text-xs">{f.kind}</td>
                  <td className="p-2 text-muted-foreground text-xs">{f.file}</td>
                  <td className="p-2 text-right">{f.lines}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <SectionHeader icon={<Code2 size={18} />} title="BAML Schemas" count={baml.length} />
        <div className="grid grid-cols-2 gap-3">
          {baml.map((b) => (
            <div key={b.file} className="bg-card rounded-lg border p-3 text-sm">
              <div className="font-mono text-xs text-muted-foreground mb-1">{b.file}</div>
              <div className="flex gap-3 text-xs">
                <span><b>{b.classCount}</b> classes</span>
                <span><b>{b.functionCount}</b> functions</span>
                <span><b>{b.enumCount}</b> enums</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <SectionHeader icon={<Cloud size={18} />} title="Cloudflare Resources" count={cf.length} />
        <div className="grid grid-cols-3 gap-3">
          {cf.map((c) => (
            <div key={`${c.wranglerConfig}:${c.kind}:${c.name}`} className="bg-card rounded-lg border p-3 text-sm">
              <div className="text-xs text-muted-foreground uppercase">{c.kind}</div>
              <div className="font-mono">{c.name}</div>
              <div className="text-xs text-muted-foreground mt-1 truncate">{c.wranglerConfig}</div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <SectionHeader icon={<span>📓</span>} title="Marimo Notebooks" count={nb.length} />
        <div className="grid grid-cols-3 gap-3">
          {nb.map((n) => (
            <Link
              key={`${n.project}:${n.slug}`}
              to="/notebooks/$slug"
              params={{ slug: n.slug }}
              className="bg-card rounded-lg border p-3 text-sm hover:border-primary"
            >
              <div className="font-medium">{n.title}</div>
              <div className="text-xs text-muted-foreground">{n.slug}</div>
              <div className="text-xs text-muted-foreground mt-1">{n.cellCount} cells</div>
            </Link>
          ))}
        </div>
      </section>

      {drawer ? <TroubleshootDrawer snapshot={snapshot} project={project as Project} route={drawer} onClose={() => setDrawer(null)} /> : null}
    </div>
  );
}

function SectionHeader({ icon, title, count }: { icon: React.ReactNode; title: string; count: number }) {
  return (
    <div className="flex items-center gap-2 mb-2">
      {icon}
      <h2 className="text-lg font-semibold">{title}</h2>
      <span className="text-xs text-muted-foreground">({count})</span>
    </div>
  );
}

function TroubleshootDrawer({
  snapshot,
  project,
  route,
  onClose,
}: {
  snapshot: WebStackSnapshot;
  project: Project;
  route: TanstackRoute;
  onClose: () => void;
}) {
  const t = troubleshoot(snapshot, project, route);
  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 flex justify-end"
      onClick={onClose}
    >
      <div
        className="bg-background w-[480px] h-full p-6 overflow-y-auto border-l"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Troubleshoot</h3>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X size={18} />
          </button>
        </div>
        <div className="text-sm space-y-1 mb-4">
          <div><b>Route:</b> <span className="font-mono">{route.route}</span></div>
          <div className="text-muted-foreground text-xs">{route.file}</div>
          <div className="text-xs text-muted-foreground">
            Last commit: {formatRelative(route.lastCommitAt)}
          </div>
        </div>

        <DrawerSection title={`Convex functions (${t.functions.length})`}>
          {t.functions.length === 0 ? <Empty>No related functions.</Empty> :
            t.functions.map((f: ConvexFunction) => (
              <div key={`${f.file}:${f.name}`} className="font-mono text-xs">
                <span className="text-muted-foreground">{f.kind}</span> {f.name}
                <span className="text-muted-foreground"> · {f.file}</span>
              </div>
            ))}
        </DrawerSection>

        <DrawerSection title={`BAML schemas (${t.baml.length})`}>
          {t.baml.length === 0 ? <Empty>No related schemas.</Empty> :
            t.baml.map((b: BamlSchema) => (
              <div key={b.file} className="font-mono text-xs">
                {b.file}
                <span className="text-muted-foreground">
                  · {b.classCount}c {b.functionCount}f {b.enumCount}e
                </span>
              </div>
            ))}
        </DrawerSection>

        <DrawerSection title={`Marimo notebooks (${t.notebooks.length})`}>
          {t.notebooks.length === 0 ? <Empty>No related notebooks.</Empty> :
            t.notebooks.map((n: MarimoNotebook) => (
              <Link
                key={n.slug}
                to="/notebooks/$slug"
                params={{ slug: n.slug }}
                className="font-mono text-xs block text-primary hover:underline"
              >
                {n.slug}
              </Link>
            ))}
        </DrawerSection>
      </div>
    </div>
  );
}

function DrawerSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-4">
      <h4 className="text-sm font-medium mb-2">{title}</h4>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return <div className="text-xs text-muted-foreground italic">{children}</div>;
}
