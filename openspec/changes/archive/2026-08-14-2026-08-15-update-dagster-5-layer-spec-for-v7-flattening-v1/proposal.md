# Change: Update dagster-5-layer-component spec for v7 flattening

## Why

The `dagster-5-layer-component-architecture` spec currently mandates
`pyproject.toml:[tool.dg].registry_modules = ["cianfhoghlaim.dagster.components"]`,
but the post-v7 flattening left the actual codebase at
`["orchestration.components"]`. Per the `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1`
openspec change, the Python package IS the repo root (no more
`cianfhoghlaim/dagster/` nesting), so the spec's example path is
stale.

This change updates the spec to reflect the post-v7 reality.

## What Changes

- Update the spec's example of `pyproject.toml:[tool.dg].registry_modules`
  from `["cianfhoghlaim.dagster.components"]` to `["orchestration.components"]`.
- Add a footnote explaining the post-v7 flattening.
- Add 1 new Requirement + 3 Scenarios that anchor the post-v7 path as
  the canonical contract (the spec's other Requirements already mention
  the path; this change adds the explicit post-v7 normalization).

## Dependencies

```
Blocked by: none
Blocked by (soft): 2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1 (the related change; this one only updates spec text)
Affected repos: cianfhoghlaim (single repo)
```

## Impact

- Capabilities: MODIFIED `dagster-5-layer-component-architecture` (1 ADDED Requirement)
- Code: 0 lines (spec-only change)
- Risk: zero (text-only edit to an example value; no runtime impact)
