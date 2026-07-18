// packages/lineage/StepPreview.tsx
//
// The LEFT pane of the lineage viewer. Lists every BAML extraction step
// (curriculum_syllabus, exam_paper_layout, marking_scheme_guideline,
// cross_linguistic_concept, syllabus_diagram) and renders each field with
// its visual state (selected / upstream / downstream / dim).
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R32 (CocoInsight-style click-to-highlight).
//
// State management: subscribes to `useLineageStore` for selection state.
// `colorState` is computed per render via `getColorState(id)`.

import * as React from "react";
import { useLineageStore } from "./lineage-store";
import { LINEAGE_TOKENS } from "./tokens";
import type {
  LineageRow,
  LineageField,
  LineageLanguage,
  LineageColorState,
} from "./types";
import type { LineageLabels } from "../../src/lib/lineage-routes";

export interface StepPreviewProps {
  rows: LineageRow[];
  language: LineageLanguage;
  labels: LineageLabels;
}

export function StepPreview({ rows, language, labels }: StepPreviewProps) {
  const getColorState = useLineageStore((s) => s.getColorState);
  const select = useLineageStore((s) => s.select);

  if (rows.length === 0) {
    return (
      <div
        className="rounded-lg border border-slate-800 bg-slate-900/50 p-6 text-sm text-slate-500"
        role="region"
        aria-label={labels.step_preview_heading}
      >
        <p className="italic">
          No lineage rows have been materialised yet for this subject. Once the
          Dagster pipeline runs, every BAML extraction step lands here.
        </p>
      </div>
    );
  }

  return (
    <div
      className="rounded-lg border border-slate-800 bg-slate-900/50 p-4 overflow-y-auto"
      role="region"
      aria-label={labels.step_preview_heading}
    >
      <h2 className="font-cinzel text-base text-slate-200 mb-3">
        {labels.step_preview_heading}
        <span className="ml-2 text-xs text-slate-500 font-mono">
          {rows.length} steps
        </span>
      </h2>

      <div className="flex flex-col gap-3">
        {rows.map((row) => (
          <article key={row.id} className="rounded-md border border-slate-700 bg-slate-950/60 p-3">
            <header className="flex items-baseline justify-between gap-2 mb-2">
              <h3 className="text-sm font-semibold text-slate-200">
                {language === "ga" ? row.title_ga : row.title}
              </h3>
              <code className="text-xs text-slate-500 font-mono">
                {row.extraction_function}
              </code>
            </header>

            <ul className="flex flex-col gap-1">
              {row.fields.map((field) => (
                <li key={field.id}>
                  <FieldPreviewButton
                    field={field}
                    language={language}
                    colorState={getColorState(field.id)}
                    onSelect={() => select(field.id)}
                  />
                </li>
              ))}
            </ul>

            <footer className="mt-2 flex flex-wrap items-center gap-2 text-xs">
              <Pill label={labels.marimo_pill} value={row.marimo_cell_id} />
              <Pill
                label={labels.motherduck_pill}
                value={`${row.motherduck_ref.dive_name} · ${row.motherduck_ref.flight_name}`}
              />
            </footer>
          </article>
        ))}
      </div>

      <p className="mt-3 text-xs text-slate-500 italic">{labels.click_hint}</p>
    </div>
  );
}

interface FieldPreviewButtonProps {
  field: LineageField;
  language: LineageLanguage;
  colorState: LineageColorState;
  onSelect: () => void;
}

function FieldPreviewButton({ field, language, colorState, onSelect }: FieldPreviewButtonProps) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className="w-full text-left rounded px-2 py-1 transition-colors hover:bg-slate-800/80"
      style={styleFor(colorState)}
      data-field-id={field.id}
      data-color-state={colorState}
    >
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-xs text-slate-400 font-mono">{field.path}</span>
        <span className="text-xs text-slate-500">
          {language === "ga" ? field.label_ga : field.label}
        </span>
      </div>
      <div className="text-sm text-slate-200 truncate">{field.value}</div>
    </button>
  );
}

interface PillProps {
  label: string;
  value: string;
}

function Pill({ label, value }: PillProps) {
  return (
    <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs text-slate-300">
      <span className="text-slate-500 mr-1">{label}:</span>
      <span className="font-mono">{value}</span>
    </span>
  );
}

function styleFor(state: LineageColorState): React.CSSProperties {
  switch (state) {
    case "selected":
      return { borderLeft: `3px solid ${LINEAGE_TOKENS.selected}` };
    case "upstream":
      return { borderLeft: `3px solid ${LINEAGE_TOKENS.upstream}` };
    case "downstream":
      return { borderLeft: `3px solid ${LINEAGE_TOKENS.downstream}` };
    case "dim":
      return { opacity: 0.4 };
    case "default":
    default:
      return {};
  }
}