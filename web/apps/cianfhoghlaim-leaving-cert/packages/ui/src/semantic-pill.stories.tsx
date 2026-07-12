// CiSemanticPill.stories.tsx — Khan Academy status pills
import type { Meta, StoryObj } from "@storybook/react";
import { CiSemanticPill } from "./semantic-pill";

const meta: Meta<typeof CiSemanticPill> = {
  title: "UI/CiSemanticPill",
  component: CiSemanticPill,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiSemanticPill>;

export const Informational: Story = { args: { tone: "info", children: "v1 active" } };
export const Success: Story = { args: { tone: "success", children: "drift-free" } };
export const Warning: Story = { args: { tone: "warning", children: "Phase 2" } };
export const Error: Story = { args: { tone: "error", children: "build failed" } };
