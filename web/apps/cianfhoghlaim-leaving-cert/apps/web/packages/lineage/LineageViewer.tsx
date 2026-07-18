// packages/lineage/LineageViewer.tsx
//
// The 3-pane lineage viewer shell. Composes:
//   - `<StepPreview>` (left) — step-by-step BAML extraction preview (R32)
//   - `<LineageDag>` (right) — D3-style grid DAG (R32)
//   - `<PdfViewer>` (bottom) — PDF.js source viewer (R31 + R33)
//
// On click of a field / DAG cell, the Zustand store updates
// `selectedId` + `upstreamIds` + `downstreamIds`. The 3 panes re-render
// with the new visual states (selected purple / upstream blue /
// downstream green / dimmed at 40% opacity).
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R26 + R29 + R30 + R31 + R32 + R33.

import * as React from "react";
import { useLineageStore } from "./lineage-store";
import { StepPreview } from "./StepPreview";
import { LineageDag } from "./LineageDag";
import { PdfViewer } from "./PdfViewer";
import type { LineageRow, LineageViewerProps } from "./types";

export function LineageViewer({ subject, language, rows, labels }: LineageViewerProps) {
  const clearSelection = useLineageStore((s) => s.clear);
  const select = useLineageStore((s) => s.select);

  // Compute the line graph for click-to-highlight: per field, the upstream
  // is the baml_extraction DAG node; the downstream is the marimo_cell DAG
  // node. Other fields in the same row have a `dim` state.
  React.useEffect(() => {
    const unsub = useLineageStore.subscribe((state, prev) => {
      if (state.selectedId === prev.selectedId) return;
      const id = state.selectedId;
      const upstream = new Set<string>();
      const downstream = new Set<string>();
      if (id) {
        const [rowPart, fieldPart] = id.split(":field:");
        const row = rows.find((r) => r.id === rowPart);
        if (row) {
          // Upstream = baml_extraction DAG cell + the PDF page DAG cell.
          upstream.add(`${row.id}:pdf_page`);
          upstream.add(`${row.id}:ocr_chunk`);
          upstream.add(`${row.id}:baml_extraction`);
          // Downstream = marimo_cell + web_component DAG cells.
          downstream.add(`${row.id}:marimo_cell`);
          downstream.add(`${row.id}:web_component`);
          // If a specific field is selected, also flag sibling fields.
          if (fieldPart !== undefined) {
            for (const f of row.fields) {
              if (f.id === id) continue;
              upstream.add(f.id); // siblings are "upstream" of the selection
            }
          }
        }
      }
      // Mutate the store's derived Sets in place by replacing them.
      // We re-use the existing `select` helper with an empty Set first,
      // then set them directly via a side-effect.
      Object.assign(state, {
        selectedId: state.selectedId,
        upstreamIds: upstream,
        downstreamIds: downstream,
      });
    });
    return unsub;
  }, [rows]);

  // Clear the store on unmount so navigating away doesn't leak state.
  React.useEffect(() => () => clearSelection(), [clearSelection]);

  return (
    <div
      className="grid grid-cols-1 lg:grid-cols-2 gap-4"
      onClick={(e) => {
        // Background click clears the selection.
        if (e.target === e.currentTarget) select(null);
      }}
      data-lineage-viewer
    >
      <StepPreview rows={rows} language={language} labels={labels} />
      <LineageDag
        rows={rows}
        language={language}
        labels={labels}
        subjectName={language === "ga" ? subject.name_ga : subject.name}
      />
      <div className="lg:col-span-2">
        <PdfViewer rows={rows} language={language} labels={labels} />
      </div>
    </div>
  );
}
