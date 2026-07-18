// packages/lineage/tokens.ts
//
// The 4 CocoInsight-style color tokens for the BIEP v1 lineage viewer.
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R32 (CocoInsight-style click-to-highlight).
//
// The selector order (CSS specificity is identical for all 4 so source order
// wins) is:
//   selected  (purple, the clicked element)
//   upstream  (blue,    direct upstream dependencies)
//   downstream (green,  direct downstream consumers)
//   dim       (40% opacity, unrelated)

export const LINEAGE_TOKENS = {
  // The 4 colors that powers the click-to-highlight state machine.
  // Aligned with the existing `--ci-*` token family so Storybook can render
  // them next to the other `<Ci*>` components.
  selected: "var(--ci-lineage-selected, #7c3aed)", // purple
  upstream: "var(--ci-lineage-upstream, #2563eb)", // blue
  downstream: "var(--ci-lineage-downstream, #16a34a)", // green
  dim: "var(--ci-lineage-dim, 0.4)", // 40% opacity

  // Layout dimensions (also token-backed so Storybook can override).
  leftPaneWidth: "minmax(320px, 1fr)",
  rightPaneWidth: "minmax(320px, 1fr)",
  pdfViewerHeight: "min(40vh, 480px)",
} as const;

export type LineageTokenName = keyof typeof LINEAGE_TOKENS;

/**
 * Returns the CSS variable string for a token name. Falls back to the
 * hard-coded value if `--ci-lineage-*` is not defined.
 */
export function cssVar(name: LineageTokenName): string {
  return LINEAGE_TOKENS[name];
}
