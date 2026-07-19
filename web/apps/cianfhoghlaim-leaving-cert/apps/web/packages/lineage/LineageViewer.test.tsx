// packages/lineage/LineageViewer.test.tsx
//
// Smoke test for the LineageViewer shell — verifies the "no rows" empty
// state renders. Real data tests need a dev server live + the Hono
// endpoint. Per follow-up #5 (R26 + R32 happy-path).

import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
// @testing-library/react requires DOM globals — happy-dom environment
// is configured in vitest.config.ts.
import { LineageViewer } from "./LineageViewer";
import { useLineageStore } from "./lineage-store";
import { BIEP_SUBJECT_BY_SLUG } from "../../src/lib/bi-ep";
import type { LineageLabels } from "../../src/lib/lineage-routes";
import type { LineageRow } from "./types";

const SAMPLE_LABELS: LineageLabels = {
  page_heading: "Document Lineage",
  blurb: "Click any field or DAG node to trace its source PDF.",
  step_preview_heading: "Step-by-step preview",
  dag_heading: "Lineage DAG",
  pdf_viewer_heading: "Source PDF",
  marimo_pill: "marimo",
  motherduck_pill: "MotherDuck",
  click_hint: "Click any field to highlight upstream + downstream.",
  view_source: "View source page",
  not_found: "Subject not found.",
};

describe("<LineageViewer> — empty-state smoke test (R26)", () => {
  it("renders the step-preview pane when given zero rows", () => {
    // Each test must start from a clean store.
    useLineageStore.getState().clear();

    render(
      <LineageViewer
        subject={BIEP_SUBJECT_BY_SLUG.mathematics}
        language="en"
        rows={[] as LineageRow[]}
        labels={SAMPLE_LABELS}
      />,
    );

    // The viewer mounts with data-lineage-viewer (R32 handler hook).
    expect(document.querySelector("[data-lineage-viewer]")).not.toBeNull();
    // The step-preview pane renders as an accessible region with the heading
    // name. aria-label is used as the region's accessible name.
    expect(screen.getByRole("region", { name: /Step-by-step preview/i })).toBeTruthy();
  });

  it("renders the lineage DAG pane", () => {
    useLineageStore.getState().clear();
    render(
      <LineageViewer
        subject={BIEP_SUBJECT_BY_SLUG.gaeilge}
        language="en"
        rows={[]}
        labels={SAMPLE_LABELS}
      />,
    );
    // The DAG pane renders a [role=region] with an aria-label that matches
    // /Lineage.*DAG/i — robust against bilingual labels.
    const dag = screen.getAllByRole("region", { name: /Lineage.*DAG/i });
    expect(dag.length).toBeGreaterThan(0);
  });
});
