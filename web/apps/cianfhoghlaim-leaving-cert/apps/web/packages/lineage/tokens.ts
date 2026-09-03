// packages/lineage/tokens.ts
//
// Re-export of the `--ci-lineage-*` design tokens from the canonical
// `apps/web/src/styles/tokens.css` source-of-truth file.
//
// Per follow-up #4 of the
// `2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1` openspec
// change + R22 of the `2026-07-18-british-isles-portal-activation-v3`
// change (Design-tokens-as-code pipelines — `tokens.css` is the single
// source of truth; `bun run tokens:validate` enforces drift-free).
//
// The old file declared its own `LINEAGE_TOKENS = { selected, upstream,
// downstream, dim }` literals. Those literals are now centralised in
// `tokens.css` (`--ci-lineage-selected` / `--ci-lineage-upstream` /
// `--ci-lineage-downstream` / `--ci-lineage-dim`). The values below
// fall back to the hard-coded hex / opacity if `tokens.css` is not
// available — keeping the package self-sufficient when consumed by
// non-Vite tooling (Storybook + Playwright).
//
// If you need the runtime values, prefer:
//
//   import { tokens } from "../../src/styles/tokens";
//   const selected = tokens.lineage.selected;   // '#7c3aed'
//
// Or the CSS-variable form (preferred for live UI components):
//
//   `var(--ci-lineage-selected)`

export const LINEAGE_TOKENS = {
  /** The clicked element — purple. */
  selected: "var(--ci-lineage-selected, #7c3aed)",
  /** Direct upstream dependencies — blue. */
  upstream: "var(--ci-lineage-upstream, #2563eb)",
  /** Direct downstream consumers — green. */
  downstream: "var(--ci-lineage-downstream, #16a34a)",
  /** Unrelated elements rendered at this opacity (0..1). */
  dim: "var(--ci-lineage-dim, 0.4)",
} as const;

export type LineageTokenName = keyof typeof LINEAGE_TOKENS;

/**
 * Returns the CSS-variable fallback string for a token name. This is the
 * preferred accessor for runtime rendering — it lets the browser honour
 * light/dark theme overrides via the `--ci-lineage-*` declarations in
 * `tokens.css`.
 */
export function cssVar(name: LineageTokenName): string {
  return LINEAGE_TOKENS[name];
}
