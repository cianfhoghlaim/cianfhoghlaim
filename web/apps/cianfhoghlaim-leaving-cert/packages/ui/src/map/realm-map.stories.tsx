// CiRealmMap.stories.tsx — accurate British Isles map (R7)
import type { Meta, StoryObj } from "@storybook/react";
import { CiRealmMap } from "./map/realm-map";

const meta: Meta<typeof CiRealmMap> = {
  title: "Map/CiRealmMap",
  component: CiRealmMap,
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof CiRealmMap>;

export const EireActive: Story = { args: { activeSubnation: "eire" } };
export const ScotlandHover: Story = { args: { activeSubnation: "scotland" } };
export const WalesFlag: Story = { args: { activeSubnation: "wales" } };
