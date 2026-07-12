// CiLCSubjectGrid.stories.tsx — 6 BIEP v1 LC subjects grid (R19)
import type { Meta, StoryObj } from "@storybook/react";
import { CiLCSubjectGrid } from "./lc-subject-grid";

const meta: Meta<typeof CiLCSubjectGrid> = {
  title: "Central portal/CiLCSubjectGrid",
  component: CiLCSubjectGrid,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiLCSubjectGrid>;

export const English: Story = { args: { language: "en" } };
export const Gaeilge: Story = { args: { language: "ga" } };
