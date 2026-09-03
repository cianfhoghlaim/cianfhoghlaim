// CiStageBreadcrumbs.stories.tsx — 5-stage education pipeline (R17)
import type { Meta, StoryObj } from "@storybook/react";
import { CiStageBreadcrumbs } from "./stage-breadcrumbs";

const meta: Meta<typeof CiStageBreadcrumbs> = {
  title: "Central portal/CiStageBreadcrumbs",
  component: CiStageBreadcrumbs,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiStageBreadcrumbs>;

export const English: Story = {
  args: { language: "en", currentStage: "leaving_cycle" },
};
export const Gaeilge: Story = {
  args: { language: "ga", currentStage: "leaving_cycle" },
};
export const PrimaryActive: Story = {
  args: { language: "en", currentStage: "primary" },
};
