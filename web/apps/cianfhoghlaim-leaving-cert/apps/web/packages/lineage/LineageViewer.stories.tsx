// packages/lineage/LineageViewer.stories.tsx
//
// 3 Storybook stories for the BIEP v1 lineage viewer shell (Phase 6.1).
// Per openspec/changes/2026-07-18-british-isles-portal-activation-v3/ R16
// (Storybook design system, ≥18 stories + bilingual EN+GA labels + dark/light
// themes).
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R32 (CocoInsight click-to-highlight visual states).

import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { LineageViewer } from "./LineageViewer";
import type { LineageRow } from "./types";
import type { LineageLabels } from "../../src/lib/lineage-routes";
import { BIEP_SUBJECT_BY_SLUG } from "../../src/lib/bi-ep";

const SAMPLE_LABELS_EN: LineageLabels = {
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

const SAMPLE_LABELS_GA: LineageLabels = {
  page_heading: "Líníocht Doiciméad",
  blurb: "Cliceáil réimse nó nód DAG ar bith chun a fhoinse PDF, eastóscadh BAML, cill marimo, agus píblíne MotherDuck a rianú.",
  step_preview_heading: "Réamhamharc céim ar chéim",
  dag_heading: "DAG Líníochta",
  pdf_viewer_heading: "PDF Foinse",
  marimo_pill: "marimo",
  motherduck_pill: "MotherDuck",
  click_hint: "Cliceáil réimse ar bith chun súgradh suas agus síos aird a thabhairt.",
  view_source: "Féach ar an leathanach foinse",
  not_found: "Ní bhfuarthas an t-ábhar.",
};

function makeRows(subject: string, count: number): LineageRow[] {
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
      extraction_function: ["ExtractCurriculumSyllabus"][0]!,
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

const meta: Meta<typeof LineageViewer> = {
  title: "Packages/Lineage/LineageViewer",
  component: LineageViewer,
};
export default meta;

type Story = StoryObj<typeof LineageViewer>;

export const Mathematics5StepsEN: Story = {
  args: {
    subject: BIEP_SUBJECT_BY_SLUG.mathematics,
    language: "en",
    rows: makeRows("mathematics", 5),
    labels: SAMPLE_LABELS_EN,
  },
};

export const Gaeilge3StepsGA: Story = {
  args: {
    subject: BIEP_SUBJECT_BY_SLUG.gaeilge,
    language: "ga",
    rows: makeRows("gaeilge", 3),
    labels: SAMPLE_LABELS_GA,
  },
};

export const BilingualSubject: Story = {
  args: {
    subject: BIEP_SUBJECT_BY_SLUG.chemistry,
    language: "en",
    rows: makeRows("chemistry", 7),
    labels: SAMPLE_LABELS_EN,
  },
  parameters: {
    chromatic: { viewports: [320, 768, 1200] },
  },
};
