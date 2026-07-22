// CiSkillTree.stories.tsx — Clair Obscur material library + empire panel hierarchy
import type { Meta, StoryObj } from "@storybook/react";
import { CiSkillTree } from "./skill-tree";

const meta: Meta<typeof CiSkillTree> = {
  title: "UI/CiSkillTree",
  component: CiSkillTree,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiSkillTree>;

export const Default: Story = {
  args: {
    nodes: [
      { id: "5", label: "Communicating" },
      { id: "1", label: "Information Processing", parent: "5" },
      { id: "2", label: "Critical & Creative Thinking", parent: "5" },
      { id: "3", label: "Personal Effectiveness", parent: "5" },
      { id: "4", label: "Working with Others", parent: "5" },
    ],
  },
};
