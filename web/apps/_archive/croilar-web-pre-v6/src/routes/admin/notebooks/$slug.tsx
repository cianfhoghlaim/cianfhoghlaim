import { createFileRoute, Link, notFound } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ArrowLeft, ExternalLink, Loader2 } from "lucide-react";
import { fetchSnapshot, type MarimoNotebook } from "../../../lib/webstack";

export const Route = createFileRoute("/admin/notebooks/$slug")({
  component: NotebookDetailPage,
});

interface ManifestEntry {
  slug: string;
  file: string;
  ok: boolean;
  bytes: number;
  error?: string;
}

interface Manifest {
  generatedAt: string;
  notebooks: ManifestEntry[];
}

function NotebookDetailPage() {
  const { slug } = Route.useParams();
  const [notebook, setNotebook] = useState<MarimoNotebook | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFoundFlag, setNotFoundFlag] = useState(false);
  const [manifestEntry, setManifestEntry] = useState<ManifestEntry | null>(null);
  const [manifestLoading, setManifestLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    fetchSnapshot().then((s) => {
      if (!mounted) return;
      const nb = s.marimoNotebooks.find((n) => n.slug === slug);
      if (!nb) {
        setNotFoundFlag(true);
      } else {
        setNotebook(nb);
      }
      setLoading(false);
    });
    return () => {
      mounted = false;
    };
  }, [slug]);

  useEffect(() => {
    let mounted = true;
    fetch("/wasm/manifest.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((data: Manifest | null) => {
        if (!mounted || !data) {
          setManifestLoading(false);
          return;
        }
        setManifestEntry(data.notebooks.find((n) => n.slug === slug) ?? null);
        setManifestLoading(false);
      })
      .catch(() => setManifestLoading(false));
    return () => {
      mounted = false;
    };
  }, [slug]);

  if (notFoundFlag) throw notFound();
  if (loading) {
    return (
      <div className="p-6 flex items-center gap-2 text-muted-foreground">
        <Loader2 className="animate-spin" size={16} />
        Loading…
      </div>
    );
  }
  if (!notebook) return null;

  const wasmPath = `/wasm/${slug}/index.html`;
  const hasWasm = manifestEntry?.ok === true;
  const lastExport = manifestEntry
    ? new Date(manifestEntry.file).toISOString()
    : null;

  return (
    <div className="p-6 space-y-4">
      <Link
        to="/notebooks"
        className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
      >
        <ArrowLeft size={14} />
        Notebooks
      </Link>
      <div>
        <h1 className="text-2xl font-bold">{notebook.title}</h1>
        <div className="text-sm text-muted-foreground font-mono">
          {notebook.project} / {notebook.slug}
        </div>
        <div className="text-xs text-muted-foreground mt-1">
          {notebook.file} · {notebook.cellCount} cells
          {lastExport ? ` · last exported ${new Date(manifestEntry!.file ?? lastExport).toISOString().slice(0, 10)}` : ""}
        </div>
      </div>

      {manifestLoading ? (
        <div className="bg-card rounded-lg border p-12 flex items-center justify-center text-muted-foreground gap-2">
          <Loader2 className="animate-spin" size={16} />
          Checking WASM bundle…
        </div>
      ) : hasWasm ? (
        <div className="bg-card rounded-lg border overflow-hidden">
          <iframe
            ref={(el) => {
              if (el && !el.dataset.resizeBound) {
                el.dataset.resizeBound = "1";
                const ro = new ResizeObserver(() => {
                  if (el.contentDocument?.documentElement) {
                    const h = el.contentDocument.documentElement.scrollHeight;
                    el.style.height = `${Math.max(480, h + 16)}px`;
                  }
                });
                el.addEventListener("load", () => {
                  try {
                    ro.observe(el.contentDocument!.documentElement);
                  } catch {
                    // cross-origin or sandboxed — fall back to fixed height
                  }
                });
              }
            }}
            src={wasmPath}
            title={notebook.title}
            className="w-full"
            style={{ height: "calc(100vh - 240px)", minHeight: 480, border: 0 }}
            sandbox="allow-scripts allow-same-origin allow-downloads allow-forms allow-popups"
            referrerPolicy="no-referrer"
            loading="lazy"
            allow="fullscreen"
          />
        </div>
      ) : (
        <div className="bg-card rounded-lg border p-6 text-sm space-y-2">
          <div className="font-medium">WASM bundle not yet generated</div>
          <div className="text-muted-foreground">
            Run{" "}
            <code className="font-mono">
              bun run croilar/scripts/export-marimo-wasm.ts
            </code>{" "}
            to emit the WASM bundle for this notebook, then reload.
          </div>
          {manifestEntry?.error ? (
            <div className="text-status-error text-xs">
              Last export error: {manifestEntry.error}
            </div>
          ) : null}
        </div>
      )}

      <div className="text-xs text-muted-foreground flex items-center gap-3">
        <a
          href={wasmPath}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 hover:text-foreground"
        >
          <ExternalLink size={12} />
          Open in new tab
        </a>
        <a
          href={`vscode://file${notebook.file}`}
          className="hover:text-foreground"
        >
          Open source
        </a>
      </div>
    </div>
  );
}
