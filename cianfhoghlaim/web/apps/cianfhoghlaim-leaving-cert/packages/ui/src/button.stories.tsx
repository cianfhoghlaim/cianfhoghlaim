// CiButton.stories.tsx — kan/Duolingo tactile 3D press feedback
import type { Meta, StoryObj } from "@storybook/react";
import { CiButton } from "./button";

const meta: Meta<typeof CiButton> = {
  title: "UI/CiButton",
  component: CiButton,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiButton>;

export const Default: Story = {
  args: { children: "Start studying", onClick: () => {} },
};
export const GA: Story = {
  args: { children: "Cuir tús leis an staidéar", onClick: () => {} },
};
export const Disabled: Story = {
  args: { children: "Disabled", onClick: () => {}, disabled: true },
};
