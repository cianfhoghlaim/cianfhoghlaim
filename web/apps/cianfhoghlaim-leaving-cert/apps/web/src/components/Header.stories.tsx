// Header.stories.tsx — the Cianfhoghlaim brand + Streak flame + Translation toggle
import type { Meta, StoryObj } from "@storybook/react";
import { Header } from "./Header";

const meta: Meta<typeof Header> = {
  title: "Web/Header",
  component: Header,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof Header>;

export const English: Story = {
  args: { language: "en" },
};
export const Gaeilge: Story = {
  args: { language: "ga" },
};
