// packages/lineage/PdfViewer.stories.tsx
// 1 Storybook story for the PdfViewer bottom pane.

import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { PdfViewer } from "./PdfViewer";
import { SAMPLE_LABELS_EN, makeRows } from "./_story-fixtures";

const meta: Meta<typeof PdfViewer> = {
  title: "Packages/Lineage/PdfViewer",
  component: PdfViewer,
};
export default meta;

type Story = StoryObj<typeof PdfViewer>;

export const MathematicsSyllabusPage14: Story = {
  args: {
    language: "en",
    labels: SAMPLE_LABELS_EN,
    rows: makeRows("mathematics", 1),
  },
};
