# Change: pipeline-sister-repo-handoff — Sister-repo handoff & orchestration mirror

> **Status:** umbrella change that subsumes the completed
> `cianchosaint-handoff-v1` change + the in-progress
> `2026-09-13-cianchosaint-orchestration-init-v1`. This umbrella
> provides the cross-repo contract + the consolidated handoff plan.

## Why

Cianfhoghlaim is 104 GB / 41,610 files / 505,785 ccc-indexed chunks.
It has absorbed the BIEP, CIANCHEILTIS, CIANCHOSAINT, CIANDLITHE,
GEMINI HACKATHON, and TUATHA work. Refactoring requires a verified
filesystem inventory (not doc claims) of what's canonically
cianfhoghlaim vs sister-owned vs shared-stack. This umbrella
codifies that inventory + the cross-fork orchestration mirror.

Without this umbrella, every sister-repo bootstrap is bespoke +
drift-prone (each sister recreates the openspec + mise + bonneagar
infrastructure from scratch). With it, all sisters inherit the
sister-shared contract + the cianfhoghlaim surface spec.

## What Changes

- Adds the cross-batch sister-handoff contract: BIEP stays in
  cianfhoghlaim, CIANCHEILTIS bilingual coverage stays, Tuatha +
  8 NCCA agents stay, Bonneagar IaC stays, sister repos
  (cianchosaint + ciandlithe + ciancheiltis + tuatha + gemini-hackathon)
  inherit the shared stack via the `sister-shared` umbrella spec.
- Mirrors the cianfhoghlaim 5-layer Dagster defs shape
  (1_ingestion + 2_materials + 3_model_lifecycle + 4_asset_generation
  + 5_agent_ops) into cianchosaint's orchestration/defs/ so both
  forks have the same CLI surface for `dg list defs`.
- Consolidates all tasks from `cianchosaint-handoff-v1` ✓ (complete)
  and `2026-09-13-cianchosaint-orchestration-init-v1` (7/9) into
  one tasks.md below.
- Records the inventory in `design.md` so future agents can resume
  against an authoritative file-level source-of-truth.

## Capabilities

### New Capabilities

- `sister-shared` — the umbrella spec for the cross-repo shared
  surface. Captures the 5 Requirements: 4-tier ModelProviderRouter,
  JurisdictionPipelineBase wholesale-copy convention,
  cocoindex_flows/_shared wholesale-copy convention, openspec
  workflow shared, bonneagar/stacks/ GOLD_STANDARD shared.

- `cianfhoghlaim` — the umbrella spec for the canonical
  cianfhoghlaim surface. Captures the 4 Requirements: BIEP stays,
  CIANCHEILTIS bilingual alignment stays, Tuatha + 8 NCCA agents
  stay, Bonneagar IaC stays.

## Impact

- **Affected changes**: 2 bundled (1 complete + 1 in-progress) +
  this umbrella
- **Affected repos**: cianfhoghlaim + cianchosaint
- **Affected code**:
  - `cianchosaint/orchestration/defs/__init__.py` (mirror of
    cianfhoghlaim's `Definitions` loader)
  - `cianchosaint/orchestration/defs/{1_ingestion,2_materials,
    3_model_lifecycle,4_asset_generation,5_agent_ops}/` (empty
    directories for now, ready for the per-sensor assets)
  - `cianchosaint/orchestration/defs/licence_enforcement_sensor.py`
    (relocated from the old top-level to `2_materials/`)

## Out of scope (follow-up changes)

- Per-sensor assets in cianchosaint's 5-layer defs (the 7 sensors
  from `2026-08-13-cianchosaint-orchestration-init-v1/proposal.md`)
  — separate openspec change once the mirror directory structure
  is in place.
- Sister-shared spec materialization into ciancheiltis + ciandlithe
  — follow-up `ciancheiltis-sister-handoff-v1` and
  `ciandlithe-sister-handoff-v1` once cianchosaint is complete.

## Dependencies

`Blocked by: none` (this is the foundational cross-repo umbrella).
`Affected repos: cianfhoghlaim + cianchosaint.`

## Cross-repo sync

This change ships the cianfhoghlaim-side + cianchosaint-side
mirror. The umbrella spec is consumed cross-repo:

  - `cianchosaint/` consumes the 5-layer defs mirror
  - `ciandlithe/` consumes the openspec workflow shared
  - `ciancheiltis/` consumes the openspec workflow shared + the
    `_shared` import convention
  - `tuatha/` consumes the openspec workflow shared
  - `gemini-hackathon/` consumes the openspec workflow shared

## Verification

```bash
cd ~/dev/cianchosaint
openspec validate pipeline-sister-repo-handoff --strict
# Expected: pass (validates against the cianchosaint-side mirror)

cd ~/dev/cianchosaint
dg list defs
# Expected: returns the relocated licence_enforcement_sensor + 5
#   empty layer namespaces (not empty like before)
```
