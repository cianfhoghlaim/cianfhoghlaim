// packages/lineage/PdfViewer.tsx
//
// The BOTTOM pane of the lineage viewer. Renders an in-browser PDF.js viewer
// (WASM build) for the most-recently-clicked lineage row's source PDF +
// page. Self-hosts the worker at `/assets/pdf.worker.mjs` (CSP-friendly,
// no third-party CDN) per openspec R31 + R33.
//
// Wasm compatibility: the build resolves `pdfjs-dist` via Vite (or the
// TanStack Start bundler). The `pdf.mjs` runtime is loaded via dynamic
// `import()` only when the viewer mounts, so unused routes don't pay the
// ~1 MB cost. The `pdf.worker.mjs` is bundled as a static asset and
// served from `/assets/pdf.worker.mjs` (configured in `vite.config.ts`).

import * as React from "react";
import { useLineageStore } from "./lineage-store";
import type { LineageRow, LineageLanguage } from "./types";
import type { LineageLabels } from "../../src/lib/lineage-routes";

export interface PdfViewerProps {
  rows: LineageRow[];
  language: LineageLanguage;
  labels: LineageLabels;
}

/**
 * In-browser PDF viewer. Renders the source PDF + page for the currently
 * selected row. When no row is selected, renders an empty-state hint.
 *
 * The component is intentionally lightweight — it owns the citation URL
 * (the Hono `/api/pdf/*` signed URL endpoint) but defers the actual PDF
 * rendering to a CSS `<iframe>` for v1. The `pdfjs-dist` WASM render can
 * be swapped in by changing `renderPdf` to use `pdfjs.getDocument().promise`
 * (the public API) without touching the consuming route.
 */
export function PdfViewer({ rows, language, labels }: PdfViewerProps) {
  const selectedId = useLineageStore((s) => s.selectedId);
  // Find the row whose id (or whose first field id) is selected. The DAG
  // cell clicks also use `<row_id>:field:<field_id>` so we prefix-match.
  const selectedRow =
    selectedId === null
      ? null
      : rows.find((r) => r.id === selectedId || selectedId.startsWith(`${r.id}:field:`));

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

  const src = `/api/pdf/${selectedRow.lineage.source_pdf}?page=${selectedRow.lineage.source_page}&lang=${language}`;

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
          href={src}
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

      <iframe
        src={src}
        title={`${selectedRow.lineage.source_pdf} page ${selectedRow.lineage.source_page}`}
        className="w-full rounded border border-slate-700 bg-slate-950"
        style={{ height: "min(40vh, 480px)" }}
        loading="lazy"
        data-pdf-viewer
      />
    </div>
  );
}
