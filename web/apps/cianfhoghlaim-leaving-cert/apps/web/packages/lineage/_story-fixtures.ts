// packages/lineage/_story-fixtures.ts
// Shared fixtures + labels for the lineage viewer stories.

import type { LineageLabels } from "../../src/lib/lineage-routes";
import type { LineageRow } from "./types";

export const SAMPLE_LABELS_EN: LineageLabels = {
  page_heading: "Document Lineage",
  blurb: "Click any field or DAG node to trace its source PDF, BAML extraction, marimo cell, and MotherDuck pipeline.",
  step_preview_heading: "Step-by-step preview",
  dag_heading: "Lineage DAG",
  pdf_viewer_heading: "Source PDF",
  marimo_pill: "marimo",
  motherduck_pill: "MotherDuck",
  click_hint: "Click any field to highlight upstream + downstream.",
  view_source: "View source page",
  not_found: "Subject not found.",
};

export function makeRows(subject: string, count: number): LineageRow[] {
  return Array.from({ length: count }, (_, i) => ({
    id: `${subject}:step-${i}`,
    extraction_function: [
      "ExtractCurriculumSyllabus",
      "ExtractExamPaperLayout",
      "ExtractMarkingSchemeGuideline",
      "ExtractCrossLinguisticConcept",
      "ExtractSyllabusDiagram",
    ][i % 5]!,
    extraction_client: "ExtractEn",
    title: `Extraction step ${i + 1}`,
    title_ga: `Céim eastósctha ${i + 1}`,
    lineage: {
      source_pdf: `leaving_cert/${subject}/en/SCSEC25_sample.pdf`,
      source_page: i + 1,
      extraction_function: "ExtractCurriculumSyllabus",
      extraction_client: "ExtractEn",
      extracted_at: "1970-01-01T00:00:00.000Z",
      confidence: 0.9,
      chunk_id: null,
      subject,
      language: "EN",
    },
    marimo_cell_id: `${subject}_topic_frequency_cell`,
    motherduck_ref: {
      dive_name: `${subject}_syllabus_topics`,
      flight_name: "lc_pdf_sync_flight",
      dive_url: `https://app.motherduck.com/dive/${subject}_syllabus_topics`,
    },
    fields: Array.from({ length: 3 }, (_, j) => ({
      id: `${subject}:step-${i}:field-${j}`,
      path: `module_topics[${i}].learning_outcomes[${j}]`,
      value: `Sample value ${i}.${j}`,
      label: `Field ${j + 1}`,
      label_ga: `Réimse ${j + 1}`,
    })),
  }));
}
