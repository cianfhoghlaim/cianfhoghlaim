# Change: pipeline-mega-3-modernization — Mega-3 4-stage plane modernization

> **Status:** umbrella change that subsumes 3 dated changes. Each dated
> child keeps its own spec deltas; this change provides the cross-batch
> orchestration contract + the consolidated task list.

## Why

The platform has 5 deeply integrated packages each at production
capability but with ~43,429 LOC of duplication across the 4-stage
education plane (LC + JC + A-Level + GCSE). The Mega-3 rollout is the
canonical de-duplication plan: replace per-subject hand-written code
with 4 stage templates that generate 99 CocoIndex Apps + 46 ADK
agents + 4 Marimo dashboards.

Without this consolidation every new subject addition grows the
duplication linearly; with it every subject addition reuses the
stage template. The 3 dated changes must ship as one milestone
because the templates depend on each other (BAML → CocoIndex →
ADK → Marimo → integration).

## What Changes

- Adds the cross-batch Mega-3 contract: the 3 sequenced mega-changes
  (roadmap → fast-follow → 3a) ship as one milestone.
- Consolidates all tasks from the 3 dated children into one
  tasks.md below.
- Records the dependency graph (Roadmap → Fast-Follow → 3a →
  3b → 3c) in `design.md` so future agents can resume execution
  against the explicit ordering.
- Does NOT modify any of the 3 bundled changes' proposals or tasks —
  each remains a self-contained unit. After archival, the umbrella
  carries the consolidated task list + the per-batch spec deltas.

## Capabilities

### New Capabilities

- `pipeline-mega-3-modernization` — the umbrella spec for the
  Mega-3 4-stage plane modernization contract. Captures the
  cross-batch dependency graph, the LOC deduplication target
  (-25,799 LOC net), and the 5 integration helpers + 12 crown-jewel
  wires + 6 dedup wins.

## Impact

- **Affected changes**: 3 bundled + this umbrella
  - `2026-08-18-mega-3-roadmap-v1`
  - `2026-08-18-mega-3-fast-follow-v1`
  - `2026-08-26-mega-3a-baml-and-adk-v1`
- **Affected code** (once the 3 sequenced mega-changes execute):
  - 4 NEW BAML stage templates (LC + JC + A-Level + GCSE + qpack)
  - 4 CocoIndex stage factories generating 99 Apps
  - 4 Marimo stage dashboards + ~46 auto-generated ADK agents
  - 5 NEW integration helpers (`BAMLFunctionTool`, `marimo_baml`,
    `agent_ui_bridge`, `marimo_to_copilotkit`, `cocoindex_query_api`)
  - 12 NEW crown-jewel wires + 6 dedup wins (-8,833 LOC)
  - 90 ADDED spec requirements across 17 specs (in the dated children)

## Out of scope (follow-up changes)

- Mega-3b + Mega-3c (the remaining 2 sequenced batches after 3a) —
  separate openspec changes to file when 3a completes.

## Dependencies

`Blocked by:` none (this is the foundational consolidation).
`Affected repos:` cianfhoghlaim.

## Cross-repo sync

This change touches ONLY cianfhoghlaim. The BAML stage templates +
ADK agents it produces feed the sister repos (cianchosaint,
ciandlithe, ciancheiltis, tuatha) per their `sister-shared`
contract.

## Verification

```bash
cd ~/dev/cianfhoghlaim
openspec validate pipeline-mega-3-modernization --strict
# Expected: pass
```
