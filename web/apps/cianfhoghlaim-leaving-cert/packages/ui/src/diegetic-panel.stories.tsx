// CiDiegeticPanel.stories.tsx — Hades diegetic UI
import type { Meta, StoryObj } from "@storybook/react";
import { CiDiegeticPanel } from "./diegetic-panel";

const meta: Meta<typeof CiDiegeticPanel> = {
  title: "UI/CiDiegeticPanel",
  component: CiDiegeticPanel,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiDiegeticPanel>;

export const Default: Story = {
  args: { title: "Penalty Detected", children: <p>3 wrong answers in a row</p> },
};
