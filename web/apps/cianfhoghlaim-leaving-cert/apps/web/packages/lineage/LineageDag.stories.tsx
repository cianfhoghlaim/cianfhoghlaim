// packages/lineage/LineageDag.stories.tsx
// 2 Storybook stories for the LineageDag right pane.

import * as React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { LineageDag } from "./LineageDag";
import { SAMPLE_LABELS_EN, makeRows } from "./_story-fixtures";

const meta: Meta<typeof LineageDag> = {
  title: "Packages/Lineage/LineageDag",
  component: LineageDag,
};
export default meta;

type Story = StoryObj<typeof LineageDag>;

export const MathematicsForceLayout: Story = {
  args: {
    language: "en",
    labels: SAMPLE_LABELS_EN,
    rows: makeRows("mathematics", 5),
    subjectName: "Mathematics",
  },
};

export const GaeilgeGA: Story = {
  args: {
    language: "ga",
    labels: SAMPLE_LABELS_EN,
    rows: makeRows("gaeilge", 4),
    subjectName: "Gaeilge",
  },
};
