// CiFocusMode.stories.tsx — Khan Academy Focus Mode
import type { Meta, StoryObj } from "@storybook/react";
import { CiFocusMode } from "./focus-mode";

const meta: Meta<typeof CiFocusMode> = {
  title: "UI/CiFocusMode",
  component: CiFocusMode,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiFocusMode>;

export const Default: Story = {
  args: { children: <p>Focus on Question 3 of 12</p> },
};
