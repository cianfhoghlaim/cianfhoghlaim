// CiTextbookPanel.stories.tsx — Clair Obscur material library
import type { Meta, StoryObj } from "@storybook/react";
import { CiTextbookPanel } from "./textbook-panel";

const meta: Meta<typeof CiTextbookPanel> = {
  title: "UI/CiTextbookPanel",
  component: CiTextbookPanel,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiTextbookPanel>;

export const Parchment: Story = {
  args: { title: "Mathematics 2024", material: "parchment",
    children: <p>Algebra · Calculus · Probability · Statistics · Geometry</p> },
};
export const Slate: Story = {
  args: { title: "Geometry", material: "slate",
    children: <p>Euclidean geometry · Trigonometry · Vectors</p> },
};
export const GoldLeaf: Story = {
  args: { title: "Leaving Cycle Overview", material: "gold-leaf",
    children: <p>All 6 NCCA LC priority subjects + their BAML schemas</p> },
};
export const Knotwork: Story = {
  args: { title: "Celtic Education Timeline", material: "knotwork",
    children: <p>From Aistear → Tertiary</p> },
};
