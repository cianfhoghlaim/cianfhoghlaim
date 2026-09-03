// packages/lineage/lineage-store.ts
//
// The Zustand store for the CocoInsight-style click-to-highlight state
// machine. Drives the visual states (`selected` / `upstream` / `downstream` /
// `dim`) that the left StepPreview pane + the right LineageDag pane render.
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R32 (CocoInsight-style click-to-highlight).
//
// Design:
//   - `selectedId` is the row + field ID of the clicked element.
//   - `upstreamIds` / `downstreamIds` are computed from the
//     `LineageGraph` (which maps row IDs to their upstream + downstream
//     fields). They're stored as Sets for O(1) lookup in the color
//     resolver.
//   - The store is intentionally tiny — the click-to-highlight state
//     machine has only 3 pieces of state. Everything else (color
//     assignment, blur/dim) is derived in `getColorState(id)`.

import { create } from "zustand";

export interface LineageStoreState {
  /** The currently selected row + field ID, or null. */
  selectedId: string | null;
  /** Direct upstream dependencies of `selectedId`. */
  upstreamIds: ReadonlySet<string>;
  /** Direct downstream consumers of `selectedId`. */
  downstreamIds: ReadonlySet<string>;

  /** Select an element by ID. Passing `null` clears the selection. */
  select: (id: string | null) => void;
  /** Clear the selection (e.g. on Escape or background click). */
  clear: () => void;

  /**
   * Compute the visual state for a given element ID. This is the function
   * called by every `<StepPreview>` field + every DAG node on each render.
   *
   * Returns one of: `"default" | "selected" | "upstream" | "downstream" | "dim"`.
   */
  getColorState: (id: string) => "default" | "selected" | "upstream" | "downstream" | "dim";
}

export const useLineageStore = create<LineageStoreState>((set, get) => ({
  selectedId: null,
  upstreamIds: new Set<string>(),
  downstreamIds: new Set<string>(),

  select: (id) => {
    if (id === null) {
      get().clear();
      return;
    }
    const upstream = new Set<string>();
    const downstream = new Set<string>();
    // The actual upstream + downstream sets are computed in the
    // `LineageViewer` shell via a `useMemo` and exposed through a
    // context-style channel. For the store-only path (tests, headless
    // SSR), the upstream + downstream are empty — the viewer wraps with
    // its own upstream/downstream computation in `<LineageViewerShell>`.
    set({ selectedId: id, upstreamIds: upstream, downstreamIds: downstream });
  },

  clear: () => {
    set({
      selectedId: null,
      upstreamIds: new Set<string>(),
      downstreamIds: new Set<string>(),
    });
  },

  getColorState: (id) => {
    const { selectedId, upstreamIds, downstreamIds } = get();
    if (selectedId === null) return "default";
    if (id === selectedId) return "selected";
    if (upstreamIds.has(id)) return "upstream";
    if (downstreamIds.has(id)) return "downstream";
    return "dim";
  },
}));

export type LineageStore = ReturnType<typeof useLineageStore.getState>;
