// TranslationToggle.stories.tsx — bilingual EN↔GA toggle
import type { Meta, StoryObj } from "@storybook/react";
import { CiTranslationToggle } from "./TranslationToggle";

const meta: Meta<typeof CiTranslationToggle> = {
  title: "Web/TranslationToggle",
  component: CiTranslationToggle,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiTranslationToggle>;

export const English: Story = {
  args: { currentLocale: "en" },
};
export const Gaeilge: Story = {
  args: { currentLocale: "ga" },
};
