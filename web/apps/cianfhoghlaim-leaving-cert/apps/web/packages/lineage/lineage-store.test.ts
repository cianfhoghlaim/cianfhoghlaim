// packages/lineage/lineage-store.test.ts
//
// Tests for the CocoInsight-style click-to-highlight state machine.
// Per follow-up #5 of openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1.
// Per openspec R32 (CocoInsight-style click-to-highlight) + R33 (WASM-compatible).

import { describe, expect, it } from "vitest";
import { useLineageStore } from "./lineage-store";

const TEST_ID_A = "mathematics:ExtractCurriculumSyllabus:syllabus:1";
const TEST_ID_B = "mathematics:ExtractCurriculumSyllabus:syllabus:1:module_topics[0].name_en";
const TEST_ID_UNRELATED = "chemistry:ExtractExamPaperLayout:paper-1";

describe("useLineageStore — click-to-highlight state machine", () => {
  it("starts in the default state (no selection)", () => {
    const { getColorState, selectedId, upstreamIds, downstreamIds } =
      useLineageStore.getState();
    expect(selectedId).toBeNull();
    expect(upstreamIds.size).toBe(0);
    expect(downstreamIds.size).toBe(0);
    expect(getColorState(TEST_ID_A)).toBe("default");
  });

  it("select(id) sets selectedId and populates the store", () => {
    useLineageStore.getState().select(TEST_ID_A);
    expect(useLineageStore.getState().selectedId).toBe(TEST_ID_A);
    expect(useLineageStore.getState().getColorState(TEST_ID_A)).toBe("selected");
  });

  it("select(null) clears the selection", () => {
    useLineageStore.getState().select(TEST_ID_A);
    useLineageStore.getState().select(null);
    const { getColorState, selectedId } = useLineageStore.getState();
    expect(selectedId).toBeNull();
    expect(getColorState(TEST_ID_A)).toBe("default");
  });

  it("clear() resets all three pieces of state", () => {
    useLineageStore.getState().select(TEST_ID_A);
    useLineageStore.getState().clear();
    const { selectedId, upstreamIds, downstreamIds } = useLineageStore.getState();
    expect(selectedId).toBeNull();
    expect(upstreamIds.size).toBe(0);
    expect(downstreamIds.size).toBe(0);
  });

  it("getColorState returns 'dim' for unrelated IDs when any selection is active", () => {
    useLineageStore.getState().select(TEST_ID_B);
    const { getColorState } = useLineageStore.getState();
    // The actually-selected field
    expect(getColorState(TEST_ID_B)).toBe("selected");
    // An unrelated field (different row + different field) reports
    // 'dim' — that's the per-R32 contract: when a selection exists,
    // everything that isn't up/downstream from it is dimmed.
    expect(getColorState(TEST_ID_UNRELATED)).toBe("dim");
    // Same row, same field → 'selected'.
    expect(getColorState(TEST_ID_B)).toBe("selected");
  });

  it("getColorState returns 'default' for every ID when selectedId is null", () => {
    useLineageStore.getState().clear();
    const { getColorState } = useLineageStore.getState();
    expect(getColorState(TEST_ID_A)).toBe("default");
    expect(getColorState(TEST_ID_B)).toBe("default");
    expect(getColorState(TEST_ID_UNRELATED)).toBe("default");
  });

  it("selecting the same id twice is idempotent on the state shape", () => {
    useLineageStore.getState().select(TEST_ID_A);
    useLineageStore.getState().select(TEST_ID_A);
    expect(useLineageStore.getState().selectedId).toBe(TEST_ID_A);
  });
});
