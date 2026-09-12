## Why

The 2026-09-02 spec-registry audit found 7 `oideachais-*` /
`cianfhoghlaim-*` pairs, of which 3 were single-requirement retirement
markers (resolved by `spec-registry-dedup`). The other 4 — plus
`british-isles-education-pipeline` ↔ `british-isles-education-pipeline-v3`
— are genuine content overlaps where the oideachais side has real
requirements that the cianfhoghlaim side doesn't already state. This
change consolidates each pair by: (a) picking the canonical owner (the
longer, cianfhoghlaim-* side in all 5 cases), (b) ADDing the
oideachais-only content to the canonical via MODIFIED/ADDED
Requirements deltas, then (c) REMOVing all of the oideachais side's
existing requirements and leaving a single retirement marker.

## What Changes

For each of the 5 pairs, the canonical owner (cianfhoghlaim-* /
british-isles-education-pipeline) gains the oideachais-only / v3-only
content via spec deltas; the losing side is converted to a single-
requirement retirement marker pointing at the canonical.

- **Pair 1**: `oideachais-pipeline` (14 reqs) → `cianfhoghlaim-pipeline`
  (54 reqs, canonical). The oideachais-side's unique content is the
  "No legacy 972-LOC ie-namespace duplicate pairs remain" requirement
  with the MD5 hash `c098f82f94909f9ffccee0387b600d9f` and the
  cross-reference stubs that mandate listing other specs in the
  Cross-references section. ADD these to `cianfhoghlaim-pipeline`;
  RETIRE the oideachais side.
- **Pair 2**: `oideachais-baml-schemas` (12 reqs) →
  `cianfhoghlaim-baml-schemas` (19 reqs, canonical). The oideachais-side
  unique content is the 8-jurisdiction-pack BAML surface compilation
  contract and the 50 pre-existing BAML `field: type` errors
  resolution. ADD these to `cianfhoghlaim-baml-schemas`; RETIRE.
- **Pair 3**: `oideachais-marimo-dashboards` (5 reqs) →
  `cianfhoghlaim-marimo-dashboards` (10 reqs, canonical). The
  oideachais-side unique content is the 5 BAML+CocoIndex tutorial
  notebooks at `notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`.
  ADD these to `cianfhoghlaim-marimo-dashboards`; RETIRE.
- **Pair 4**: `oideachais-cognify-knowledge-graph` (4 reqs, already a
  retirement marker pattern) → `cianfhoghlaim-cognify-knowledge-graph`
  (9 reqs, canonical). The oideachais-side Req 1 ("Phase 1 complete —
  9 requirements all functional end-to-end") is a deliberate retirement
  marker and is preserved as the oideachais side's single remaining
  requirement after this change. ADD the Leabharlann sub-corpora
  update + cross-archive edges ownership boundary update to
  `cianfhoghlaim-cognify-knowledge-graph`.
- **Pair 5**: `british-isles-education-pipeline-v3` (21 reqs) →
  `british-isles-education-pipeline` (40 reqs, canonical v1). The
  v3-only content is the 5-milestone M0-M4 plan + the 6-deferred
  M5-M10 + the 4-cadence scheduling policy + the OCR completion
  webhook convention. ADD these to `british-isles-education-pipeline`;
  RETIRE `-v3` (the v1 + v2 + v3 trilogy was the original
  intentional structure; v3 is a milestone tracker, not a permanent
  capability, so its retirement is appropriate).

## Capabilities

### New Capabilities
(none)

### Modified Capabilities

- `cianfhoghlaim-pipeline` — MODIFIED to ADD the no-legacy-duplicate
  invariant and the cross-reference stubs
- `cianfhoghlaim-baml-schemas` — MODIFIED to ADD the 8-jurisdiction
  BAML compilation + the 50-error resolution
- `cianfhoghlaim-marimo-dashboards` — MODIFIED to ADD the 5
  BAML+CocoIndex tutorial notebooks
- `cianfhoghlaim-cognify-knowledge-graph` — MODIFIED to ADD the
  Leabharlann sub-corpora update + the cross-archive edge ownership
- `british-isles-education-pipeline` — MODIFIED to ADD the v3
  milestone structure + OCR webhook convention
- `oideachais-pipeline` — RETIRED (single-requirement retirement
  marker remains)
- `oideachais-baml-schemas` — RETIRED
- `oideachais-marimo-dashboards` — RETIRED
- `oideachais-cognify-knowledge-graph` — RETIRED (its existing Req 1
  was already the retirement marker; REMOVE the other 3)
- `british-isles-education-pipeline-v3` — RETIRED

## Impact

- **Affected specs**: 5 canonical + 5 losing = 10 specs modified
- **Spec count after archive**: `openspec list --specs` drops from
  102 to 97 (5 capabilities retired)
- **Affected code**: none — this change is pure spec-cleanup
- **Re-verify after archive**: each canonical owner SHALL own its
  oideachais-only content; the losing side SHALL exist as a single-
  requirement retirement marker only

## Dependencies

`Blocked by: spec-registry-dedup` (so the 3 simple retirement markers
are already archived before this change runs)
`Blocked by (soft): openspec-1-11-migration`
`Affected repos: cianfhoghlaim`