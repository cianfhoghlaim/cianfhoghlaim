// packages/lineage/StepPreview.stories.tsx
// 2 Storybook stories for the StepPreview left pane.

import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { StepPreview } from "./StepPreview";
import type { LineageRow } from "./types";
import { SAMPLE_LABELS_EN } from "./_story-fixtures";

const meta: Meta<typeof StepPreview> = {
  title: "Packages/Lineage/StepPreview",
  component: StepPreview,
};
export default meta;

type Story = StoryObj<typeof StepPreview>;

export const Mathematics3Steps: Story = {
  args: {
    language: "en",
    labels: SAMPLE_LABELS_EN,
    rows: SAMPLE_LABELS_EN && makeRows("mathematics", 3),
  },
};
