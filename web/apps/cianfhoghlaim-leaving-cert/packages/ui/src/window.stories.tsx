// CiWindow.stories.tsx — PostHog Navigation 3000 multi-panel
import type { Meta, StoryObj } from "@storybook/react";
import { CiWindow } from "./window";

const meta: Meta<typeof CiWindow> = {
  title: "UI/CiWindow",
  component: CiWindow,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiWindow>;

export const Default: Story = {
  args: {
    title: "Study Plan",
    children: <p>12-week Mathematics HL plan</p>,
    resizable: true,
  },
};
