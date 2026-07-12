// CiMapZone.stories.tsx — WoW hex-based claim with decay indicator
import type { Meta, StoryObj } from "@storybook/react";
import { CiMapZone } from "./map-zone";

const meta: Meta<typeof CiMapZone> = {
  title: "UI/CiMapZone",
  component: CiMapZone,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiMapZone>;

export const Claimed: Story = { args: { state: "claimed", hex: "Connacht" } };
export const Decaying: Story = { args: { state: "decaying", hex: "Munstir" } };
export const Lost: Story = { args: { state: "lost", hex: "Leinster" } };
