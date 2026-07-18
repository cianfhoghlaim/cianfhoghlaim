// packages/lineage/index.ts
//
// Re-exports for the BIEP v1 lineage viewer package. The route in
// `apps/web/src/routes/{en,ga}/leaving-cert/$subject/lineage.tsx`
// imports from this barrel.

export { LineageViewer } from "./LineageViewer";
export { StepPreview } from "./StepPreview";
export { LineageDag } from "./LineageDag";
export { PdfViewer } from "./PdfViewer";
export { useLineageStore } from "./lineage-store";
export { LINEAGE_TOKENS, cssVar } from "./tokens";
export type {
  LineageRow,
  LineageField,
  LineageTrace,
  LineageLanguage,
  LineageColorState,
  LineageDagNode,
  LineageDagEdge,
  LineageViewerProps,
} from "./types";
