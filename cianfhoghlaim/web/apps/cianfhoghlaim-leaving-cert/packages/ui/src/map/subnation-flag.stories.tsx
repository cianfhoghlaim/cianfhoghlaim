// CiSubnationFlag.stories.tsx — 6 subnation flags
import type { Meta, StoryObj } from "@storybook/react";
import { CiSubnationFlag } from "./map/subnation-flag";

const meta: Meta<typeof CiSubnationFlag> = {
  title: "Map/CiSubnationFlag",
  component: CiSubnationFlag,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiSubnationFlag>;

export const Eire: Story = { args: { subnation: "eire" } };
export const Scotland: Story = { args: { subnation: "scotland" } };
export const Wales: Story = { args: { subnation: "wales" } };
export const England: Story = { args: { subnation: "england" } };
