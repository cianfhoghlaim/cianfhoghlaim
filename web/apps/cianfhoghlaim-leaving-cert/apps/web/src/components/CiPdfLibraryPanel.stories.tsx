// CiPdfLibraryPanel.stories.tsx — R2 PDF library (R14)
import type { Meta, StoryObj } from "@storybook/react";
import {
  CiPdfLibraryPanel,
  DEFAULT_MATHEMATICS_ASSETS,
} from "./CiPdfLibraryPanel";

const meta: Meta<typeof CiPdfLibraryPanel> = {
  title: "Web/CiPdfLibraryPanel",
  component: CiPdfLibraryPanel,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiPdfLibraryPanel>;

export const DefaultEnglish: Story = {
  args: { assets: DEFAULT_MATHEMATICS_ASSETS, language: "en" },
};
export const DefaultGaeilge: Story = {
  args: { assets: DEFAULT_MATHEMATICS_ASSETS, language: "ga" },
};
export const EmptyList: Story = {
  args: { assets: [], language: "en" },
};
