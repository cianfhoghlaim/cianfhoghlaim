// MarimoEmbed.stories.tsx — Cloudflare Workers + Container iframe
import type { Meta, StoryObj } from "@storybook/react";
import { MarimoEmbed } from "./MarimoEmbed";

const meta: Meta<typeof MarimoEmbed> = {
  title: "Web/MarimoEmbed",
  component: MarimoEmbed,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof MarimoEmbed>;

export const Mathematics: Story = {
  args: { subject: "mathematics" },
};
export const Gaeilge: Story = {
  args: { subject: "gaeilge" },
};
