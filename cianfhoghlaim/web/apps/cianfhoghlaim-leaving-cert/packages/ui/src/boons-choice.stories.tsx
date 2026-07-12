// CiBoonsChoice.stories.tsx — Hades 3-way vertical choice
import type { Meta, StoryObj } from "@storybook/react";
import { CiBoonsChoice } from "./boons-choice";

const meta: Meta<typeof CiBoonsChoice> = {
  title: "UI/CiBoonsChoice",
  component: CiBoonsChoice,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiBoonsChoice>;

export const Default: Story = {
  args: {
    title: "Choose a Path",
    options: [
      { id: "alpha", label: "Alpha", tone: "amber" },
      { id: "beta", label: "Beta", tone: "blue" },
      { id: "gamma", label: "Gamma", tone: "emerald" },
    ],
    onChoose: (id) => console.log("chose", id),
  },
};
