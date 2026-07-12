// CiProgressRing.stories.tsx — Khan Academy 4-tier mastery
import type { Meta, StoryObj } from "@storybook/react";
import { CiProgressRing } from "./progress-ring";

const meta: Meta<typeof CiProgressRing> = {
  title: "UI/CiProgressRing",
  component: CiProgressRing,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiProgressRing>;

export const Attempted: Story = { args: { tier: "attempted", value: 0.1 } };
export const Familiar: Story = { args: { tier: "familiar", value: 0.5 } };
export const Proficient: Story = { args: { tier: "proficient", value: 0.8 } };
export const Mastered: Story = { args: { tier: "mastered", value: 1 } };
