import { DurableObjectGeoClickSchemaType } from "@repo/data-ops/zod-schema/links";
import { create } from "zustand";

type GeoClickStore = {
  clicks: DurableObjectGeoClickSchemaType[];
  addClicks: (clicks: DurableObjectGeoClickSchemaType[]) => void;
  resetClicks: () => void;
};

export const useGeoClickStore = create<GeoClickStore>((set) => ({
  clicks: [],

  addClicks: (clicks) =>
    set((state) => {
      const updated = [...state.clicks, ...clicks];
      if (updated.length > 1000) {
        // Drop oldest
        return { clicks: updated.slice(-1000) };
      }
      return { clicks: updated };
    }),

  resetClicks: () => set({ clicks: [] }),
}));
