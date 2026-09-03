// CiStreakFlame.stories.tsx — Duolingo streak indicator
import type { Meta, StoryObj } from "@storybook/react";
import { CiStreakFlame } from "./streak-flame";

const meta: Meta<typeof CiStreakFlame> = {
  title: "UI/CiStreakFlame",
  component: CiStreakFlame,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiStreakFlame>;

export const Fresh: Story = { args: { days: 1 } };
export const Streaking: Story = { args: { days: 14 } };
export const Legendary: Story = { args: { days: 365 } };
