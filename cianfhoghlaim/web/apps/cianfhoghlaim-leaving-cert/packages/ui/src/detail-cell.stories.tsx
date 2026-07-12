// CiDetailCell.stories.tsx — Khan Academy detail cells
import type { Meta, StoryObj } from "@storybook/react";
import { CiDetailCell } from "./detail-cell";

const meta: Meta<typeof CiDetailCell> = {
  title: "UI/CiDetailCell",
  component: CiDetailCell,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiDetailCell>;

export const Default: Story = {
  args: {
    icon: "🎓",
    label: "NCCA Maths HL",
    metadata: "12 topics · 36 past papers · 1 daily Flight",
  },
};
export const WithBadge: Story = {
  args: {
    icon: "📚",
    label: "Past Paper 2024",
    metadata: "Higher Level · 3h duration",
    badge: "v1 active",
  },
};
