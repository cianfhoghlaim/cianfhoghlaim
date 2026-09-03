// packages/lineage/PdfViewer.tsx
//
// The BOTTOM pane of the lineage viewer. Renders an in-browser PDF.js
// viewer (WASM build) for the most-recently-clicked lineage row's source
// PDF + page. Self-hosts the worker at `/assets/pdf.worker.mjs` (bundled
// at build time by Vite via the `?url` import) — CSP-friendly, no
// third-party CDN — per openspec R31 + R33.
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R31 (PDF.js in-browser viewer with citation deep-links).

import * as React from "react";
// PDF.js is dynamic-imported on mount so the ~1 MB worker + runtime only
// loads when a lineage row is actually selected (R33 — lazy + WASM-compatible).
// eslint-disable-next-line @typescript-eslint/no-explicit-any
import type * as PDFJSType from "pdfjs-dist";
// The `?url` form hands Vite a stable URL for the worker file; the runtime
// fetches it from /assets/pdf.worker.mjs in dev + production.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const PDF_WORKER_URL: string = (await import(
  /* @vite-ignore */ "pdfjs-dist/build/pdf.worker.mjs?url"
)) as any;

import { useLineageStore } from "./lineage-store";
import type { LineageRow, LineageLanguage } from "./types";
import type { LineageLabels } from "../../src/lib/lineage-routes";

export interface PdfViewerProps {
  rows: LineageRow[];
  language: LineageLanguage;
  labels: LineageLabels;
}

// Module-scoped PDF.js instance — lazy initialised on first use, so
// the bundle stays light for routes that never render a PDF.
let pdfjsModule: typeof PDFJSType | null = null;
let workerConfigured = false;

async function loadPdfJs(): Promise<typeof PDFJSType> {
  if (pdfjsModule) return pdfjsModule;
  // Dynamic import keeps the bundle size off the critical path.
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mod = (await import(/* @vite-ignore */ "pdfjs-dist" as any)) as typeof PDFJSType;
  pdfjsModule = mod;
  if (!workerConfigured) {
    mod.GlobalWorkerOptions.workerSrc = PDF_WORKER_URL;
    workerConfigured = true;
  }
  return mod;
}

/**
 * In-browser PDF viewer. Renders the source PDF + page for the currently
 * selected row. When no row is selected, renders an empty-state hint.
 *
 * Architecture (R31 + R33):
 *   - The `<canvas>` is rendered by `pdfjs-dist` (loaded lazily).
 *   - The WASM worker lives at `/assets/pdf.worker.mjs` (self-hosted,
 *     no third-party CDN).
 *   - Citation deep-links use `?page=` URL params so a back-button
 *     restores the same page.
 */
export function PdfViewer({ rows, language, labels }: PdfViewerProps) {
  const selectedId = useLineageStore((s) => s.selectedId);
  // Find the row whose id (or whose first field id) is selected.
  const selectedRow =
    selectedId === null
      ? null
      : rows.find((r) => r.id === selectedId || selectedId.startsWith(`${r.id}:field:`));

  const canvasRef = React.useRef<HTMLCanvasElement | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState<boolean>(false);

  // Render the selected PDF onto the canvas. The effect re-runs whenever
  // the selected row + its source_page changes.
  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !selectedRow) return;

    let cancelled = false;
    setError(null);
    setLoading(true);

    (async () => {
      try {
        const pdfjs = await loadPdfJs();
        const url = `/api/pdf/${selectedRow.lineage.source_pdf}?page=${selectedRow.lineage.source_page}&lang=${language}`;
        const loadingTask = pdfjs.getDocument({ url });
        const doc = await loadingTask.promise;
        if (cancelled) return;
        const page = await doc.getPage(selectedRow.lineage.source_page);
        if (cancelled) return;
        const viewport = page.getViewport({ scale: 1.4 });
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          setError("Could not get canvas 2D context");
          return;
        }
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        // pdfjs-dist v5: `canvas` replaces `canvasContext` in
        // RenderParameters. The previous API was { canvasContext, viewport }.
        await page.render({ canvas, viewport }).promise;
        setLoading(false);
      } catch (err) {
        if (cancelled) return;
        setError((err as Error).message ?? "PDF render failed");
        setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [selectedRow, language]);

  if (!selectedRow) {
    return (
      <div
        className="rounded-lg border border-slate-800 bg-slate-900/50 p-4"
        role="region"
        aria-label={labels.pdf_viewer_heading}
      >
        <h2 className="font-cinzel text-base text-slate-200 mb-2">
          {labels.pdf_viewer_heading}
        </h2>
        <p className="text-sm text-slate-500 italic">
          {labels.click_hint}
        </p>
      </div>
    );
  }

  return (
    <div
      className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 flex flex-col gap-2"
      role="region"
      aria-label={labels.pdf_viewer_heading}
    >
      <header className="flex items-baseline justify-between gap-2">
        <h2 className="font-cinzel text-base text-slate-200">
          {labels.pdf_viewer_heading}
        </h2>
        <a
          href={`/api/pdf/${selectedRow.lineage.source_pdf}?page=${selectedRow.lineage.source_page}&lang=${language}`}
          className="text-xs text-emerald-400 underline hover:opacity-80"
          target="_blank"
          rel="noreferrer"
        >
          {labels.view_source} ↗
        </a>
      </header>

      <div className="text-xs text-slate-500 font-mono">
        {selectedRow.lineage.source_pdf} · p{selectedRow.lineage.source_page} ·
        <span className="ml-1 text-slate-400">{selectedRow.extraction_client}</span>
      </div>

      <div
        className="relative w-full rounded border border-slate-700 bg-slate-950 flex items-center justify-center"
        style={{ minHeight: "min(40vh, 480px)" }}
      >
        <canvas
          ref={canvasRef}
          className="max-w-full"
          data-pdf-viewer
        />
        {loading && !error && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-sm italic">
            {language === "ga" ? "Á lódáil..." : "Loading..."}
          </div>
        )}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center text-rose-400 text-sm">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}
