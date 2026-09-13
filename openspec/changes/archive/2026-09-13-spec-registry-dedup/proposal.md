## Why

The 2026-09-02 spec-registry audit found 7 spec pairs where an
`oideachais-*` (Celtic education quadrant) spec duplicates content in a
`cianfhoghlaim-*` (consolidated cianfhoghlaim monorepo) spec, plus
2 known typos. Three of those `oideachais-*` specs are already
single-requirement **retirement markers** that explicitly point at
their canonical `cianfhoghlaim-*` successor — the right disposition is
to formally retire those 3 specs (collapse the marker into the canonical
spec, drop the marker). The other 4 pairs are genuine content overlaps
that require a requirement-by-requirement diff to determine the
correct consolidation; that work is deferred to follow-up tasks
(named in `tasks.md` §3) rather than fabricated here. The two named
typos (`meaisinfoghlaim-ocr-htr` and `ciandlithe-dlt-sources-carveout-v1`)
no longer exist as live specs — they've already been renamed, so this
change does NOT carry that work.

## What Changes

- **Retire** the 3 single-requirement retirement-marker specs:
  `oideachais-leabharlann`,
  `oideachais-cocoindex-v1-migration`,
  `oideachais-university-deep-extraction`. Each marker's one
  requirement is a "Phase X complete" check against the canonical
  `cianfhoghlaim-*` successor, so retiring the marker does NOT lose
  any invariant — the canonical successor already owns that check
  (the marker's requirement text is byte-equivalent to the
  canonical's opening sentence in each case).
- **Defer** the 5 deeper content-overlap investigations:
  `oideachais-pipeline` ↔ `cianfhoghlaim-pipeline`,
  `oideachais-baml-schemas` ↔ `cianfhoghlaim-baml-schemas`,
  `oideachais-marimo-dashboards` ↔ `cianfhoghlaim-marimo-dashboards`,
  `oideachais-cognify-knowledge-graph` ↔ `cianfhoghlaim-cognify-knowledge-graph`,
  and `british-isles-education-pipeline` ↔ `british-isles-education-pipeline-v3`.
  Each requires a per-requirement diff that this change does not
  fabricate.

## Capabilities

### New Capabilities
(none — pure spec-cleanup change)

### Modified Capabilities
- `oideachais-leabharlann`: RETIRE — single retirement-marker
  requirement pointing at `cianfhoghlaim-leabharlann` is removed
- `oideachais-cocoindex-v1-migration`: RETIRE — single
  retirement-marker requirement pointing at
  `cianfhoghlaim-cocoindex-v1-migration` is removed
- `oideachais-university-deep-extraction`: RETIRE — single
  retirement-marker requirement pointing at
  `cianfhoghlaim-university-deep-extraction` is removed

## Impact

- **Affected specs**: 3 retired (above) + 5 deferred (the deeper
  content overlaps remain unchanged pending real investigation)
- **Affected code**: none — this change is pure spec-cleanup; no code
  paths are touched.
- **Re-verify after archive**: `openspec list --specs` SHALL drop from
  102 to 99; the deferred deeper-overlap work is tracked in this
  change's `tasks.md` §3 for future sessions.

## Dependencies

`Blocked by: none`
`Blocked by (soft): openspec-1-11-migration` (so the new
`openspec validate --strict` rules and `openspec config.yaml` are in
place before this change's deltas land)
`Affected repos: cianfhoghlaim`