// packages/lineage/LineageDag.tsx
//
// The RIGHT pane of the lineage viewer. Renders the DAG of intermediate
// extraction stages:
//
//   pdf_page → ocr_chunk → baml_extraction → marimo_cell → web_component
//
// Implemented as a lightweight 5-column grid (rather than D3 force layout)
// for v1 — the DAG shape is fixed, deterministic, and renders cleanly with
// plain CSS. The D3 force layout from the original CocoInsight UI is
// preserved as a future enhancement (R-Future-D3-Force).
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R32 (CocoInsight-style click-to-highlight).

import * as React from "react";
import { useLineageStore } from "./lineage-store";
import { LINEAGE_TOKENS } from "./tokens";
import type {
  LineageRow,
  LineageLanguage,
  LineageColorState,
} from "./types";
import type { LineageLabels } from "../../src/lib/lineage-routes";

export interface LineageDagProps {
  rows: LineageRow[];
  language: LineageLanguage;
  labels: LineageLabels;
  /** Subject name for the DAG header (e.g. "Mathematics"). */
  subjectName: string;
}

const STAGE_KIND = [
  "pdf_page",
  "ocr_chunk",
  "baml_extraction",
  "marimo_cell",
  "web_component",
] as const;

const STAGE_LABEL: Record<typeof STAGE_KIND[number], string> = {
  pdf_page: "PDF page",
  ocr_chunk: "OCR chunk",
  baml_extraction: "BAML",
  marimo_cell: "Marimo",
  web_component: "Web",
};

const STAGE_LABEL_GA: Record<typeof STAGE_KIND[number], string> = {
  pdf_page: "Leathanach PDF",
  ocr_chunk: "Bloc OCR",
  baml_extraction: "BAML",
  marimo_cell: "Marimo",
  web_component: " Gréasán",
};

export function LineageDag({ rows, language, labels, subjectName }: LineageDagProps) {
  const getColorState = useLineageStore((s) => s.getColorState);
  const selectedId = useLineageStore((s) => s.selectedId);

  // Per-row, build the 5 stages. The "baml_extraction" cell anchors the
  // row ID; the other 4 stage cells are style-only (purely visual — the
  // provenance carries the row→cell mapping).
  return (
    <div
      className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 overflow-y-auto"
      role="region"
      aria-label={labels.dag_heading}
    >
      <h2 className="font-cinzel text-base text-slate-200 mb-3">
        {labels.dag_heading}
        <span className="ml-2 text-xs text-slate-500 font-mono">
          {rows.length} rows · {STAGE_KIND.length} stages
        </span>
      </h2>

      <div className="flex flex-col gap-2">
        <StageHeader subjectName={subjectName} language={language} />

        {rows.length === 0 ? (
          <p className="text-sm text-slate-500 italic">No DAG rows to display.</p>
        ) : (
          rows.map((row) => (
            <DagRowStrip
              key={row.id}
              row={row}
              language={language}
              selectedId={selectedId}
              getColorState={getColorState}
            />
          ))
        )}
      </div>

      <p className="mt-3 text-xs text-slate-500 italic">{labels.click_hint}</p>
    </div>
  );
}

interface StageHeaderProps {
  subjectName: string;
  language: LineageLanguage;
}

function StageHeader({ subjectName, language }: StageHeaderProps) {
  return (
    <div className="grid grid-cols-[auto_repeat(5,minmax(0,1fr))] gap-1 text-xs text-slate-500 font-mono">
      <span className="text-right pr-2">row</span>
      {STAGE_KIND.map((kind) => (
        <span key={kind} className="px-2 truncate text-center">
          {language === "ga" ? STAGE_LABEL_GA[kind] : STAGE_LABEL[kind]}
        </span>
      ))}
      <span className="sr-only">{subjectName}</span>
    </div>
  );
}

interface DagRowStripProps {
  row: LineageRow;
  language: LineageLanguage;
  selectedId: string | null;
  getColorState: (id: string) => LineageColorState;
}

function DagRowStrip({ row, language, selectedId, getColorState }: DagRowStripProps) {
  // The "row anchor" color is driven by the row-level selection: if any
  // field in this row is selected, the whole strip is "selected". Otherwise
  // we look at the baml_extraction cell — the most common click target.
  const stripState: LineageColorState = selectedId && selectedId.startsWith(row.id)
    ? "selected"
    : "default";

  return (
    <div
      className="grid grid-cols-[auto_repeat(5,minmax(0,1fr))] gap-1 items-stretch"
      style={stripStyle(stripState)}
      data-row-id={row.id}
    >
      <button
        type="button"
        onClick={() => useLineageStore.getState().select(row.id)}
        className="text-right pr-2 text-xs text-slate-300 font-mono truncate hover:underline"
        title={row.extraction_function}
      >
        {language === "ga" ? row.title_ga : row.title}
      </button>
      {STAGE_KIND.map((kind) => (
        <DagStageCell
          key={kind}
          row={row}
          kind={kind}
          language={language}
          getColorState={getColorState}
        />
      ))}
    </div>
  );
}

interface DagStageCellProps {
  row: LineageRow;
  kind: typeof STAGE_KIND[number];
  language: LineageLanguage;
  getColorState: (id: string) => LineageColorState;
}

function DagStageCell({ row, kind, language, getColorState }: DagStageCellProps) {
  const cellId = `${row.id}:${kind}`;
  const colorState = getColorState(cellId);

  // The BAML cell carries the row's first field id; that lets us click it
  // and have the selection propagate to the matching field in the left pane.
  const onSelect = () => {
    const bamlFieldId = row.fields[0]?.id;
    if (bamlFieldId) {
      useLineageStore.getState().select(`${row.id}:field:${bamlFieldId}`);
    } else {
      useLineageStore.getState().select(cellId);
    }
  };

  // Resolve the displayed text from the row by stage kind.
  const display = (() => {
    switch (kind) {
      case "pdf_page":
        return `${row.lineage.source_pdf.split("/").pop() ?? "…"}:p${row.lineage.source_page}`;
      case "ocr_chunk":
        return `chunk ${row.lineage.chunk_id ?? "—"}`;
      case "baml_extraction":
        return row.extraction_function;
      case "marimo_cell":
        return row.marimo_cell_id;
      case "web_component":
        return language === "ga" ? "comhpháirt gréasáin" : "web component";
    }
  })();

  return (
    <button
      type="button"
      onClick={onSelect}
      className="rounded border border-slate-700 px-2 py-1 text-xs text-slate-200 hover:border-slate-500 transition-colors"
      style={cellStyle(colorState)}
      data-cell-id={cellId}
      data-color-state={colorState}
    >
      {display}
    </button>
  );
}

function stripStyle(state: LineageColorState): React.CSSProperties {
  if (state === "selected") {
    return { borderTop: `2px solid ${LINEAGE_TOKENS.selected}` };
  }
  return {};
}

function cellStyle(state: LineageColorState): React.CSSProperties {
  switch (state) {
    case "selected":
      return { borderColor: LINEAGE_TOKENS.selected, backgroundColor: "rgba(124, 58, 237, 0.15)" };
    case "upstream":
      return { borderColor: LINEAGE_TOKENS.upstream, backgroundColor: "rgba(37, 99, 235, 0.12)" };
    case "downstream":
      return { borderColor: LINEAGE_TOKENS.downstream, backgroundColor: "rgba(22, 163, 74, 0.12)" };
    case "dim":
      return { opacity: 0.4 };
    case "default":
    default:
      return {};
  }
}
