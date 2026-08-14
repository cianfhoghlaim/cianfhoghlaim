# Change: Dagster load-path repair + lakehouse preflight

## Why

The Dagster load path silently skips **18 source YAML files** due to two bugs:

1. **L1 ingestion layer has no `_layer/defs.yaml` mount point.** `orchestration/defs/1_ingestion/` has neither a `defs.yaml` nor a `_layer/defs.yaml` at the root. The 5 Ireland law sources (`1_ingestion/law/ie/{piab,court_rules,legal_aid,courts,judgements}/defs.yaml`) are unreachable by `dg.load_defs()` because every parent directory above them also lacks a mount point.

2. **13 YAML files use `.yaml` extension, not `defs.yaml`.** Dagster 1.13+ `dg.load_defs()` only loads files named exactly `defs.yaml` (verified via the comment in `dbt_project/defs.yaml.planned`: "Dagster only reads files named exactly `defs.yaml`, so this name is inert"). The 6 LC6 subject sources (`1_ingestion/curriculum/lc6/*.yaml`) + 6 grading sources (`2_materials/grading/*.yaml`) + 1 OCR ensemble source (`2_materials/ocr_comparison/.../biiep_ocr_ensemble.yaml`) are all silently dead code.

Additionally, **3 L2 subdirectory mount points are missing** — `2_materials/embedding_pivot/`, `2_materials/england_education/comparators/`, `2_materials/england_education/aqa/`, `2_materials/lc_extraction/lc_subjects/` — each has direct children defs.yaml files but no parent `_layer/defs.yaml` mount.

The lakehouse itself brings up cleanly (per the existing `scripts/smoke_test_lakehouse.py`); the bug is purely in how Dagster mounts its code-location. **No new container, no new dependency, no new openspec semantics** — just the mount points + filename renames.

A separate but related gap: **the L3 cognify + federated_ocr assets will fail-loudly at materialise time** when the BIEP M1-M4 milestones trigger them. The `FAIL-LOUDLY CONTRACT` in `orchestration/components/kcg_cognify_component.py` makes this explicit. They need `automation_condition: manual` so they don't auto-trigger until the cognify stack is brought up.

And finally: **no `mise run lakehouse:preflight` task exists**. Operators must hand-craft a smoke-test invocation to validate the lakehouse is healthy before running BIEP pipelines.

## What Changes

### A — Dagster load-path repair (4 new files + 13 renames + 3 new mount markers)

**Adds 4 L1 `_layer/defs.yaml` files** (DefsFolderComponent mount points):

```
orchestration/defs/1_ingestion/_layer/defs.yaml                  # mount for law/ subtree
orchestration/defs/1_ingestion/law/_layer/defs.yaml             # mount for ie/ subtree
orchestration/defs/1_ingestion/law/ie/_layer/defs.yaml           # mount for 5 IE law sources
orchestration/defs/1_ingestion/curriculum/lc6/_layer/defs.yaml  # mount for 6 LC6 subject sources
```

**Renames 13 YAML files to `defs.yaml`** (content unchanged, only the filename changes):

```
# L1 LC6 sources (6 files) — 1_ingestion/curriculum/lc6/:
english.yaml          → defs.yaml
geography.yaml        → defs.yaml
chemistry.yaml         → defs.yaml
gaeilge.yaml           → defs.yaml
mathematics.yaml       → defs.yaml
computer_science.yaml  → defs.yaml

# L2 grading sources (6 files) — 2_materials/grading/:
english.yaml          → defs.yaml
geography.yaml        → defs.yaml
chemistry.yaml         → defs.yaml
gaeilge.yaml           → defs.yaml
mathematics.yaml       → defs.yaml
computer_science.yaml  → defs.yaml

# L2 OCR ensemble source (1 file) — 2_materials/ocr_comparison/ensemble_comparison/:
biiep_ocr_ensemble.yaml → defs.yaml
```

**Adds 3 L2 `_layer/defs.yaml` files** for subdirs that currently have defs.yaml children but no parent mount:

```
orchestration/defs/2_materials/embedding_pivot/_layer/defs.yaml
orchestration/defs/2_materials/england_education/comparators/_layer/defs.yaml
orchestration/defs/2_materials/england_education/aqa/_layer/defs.yaml
orchestration/defs/2_materials/lc_extraction/lc_subjects/_layer/defs.yaml
```

### B — L3 deferred-asset gates (3 edits)

The L3 cognify + federated_ocr assets must not trigger in BIEP M1-M4. Adds `automation_condition: manual` attribute to the 3 Component dataclasses:

| Component | File | Edit |
|:--|:--|:--|
| `KCGCognifyComponent` | `orchestration/components/kcg_cognify_component.py` | Add `automation_condition: manual` default |
| `CognifyIngestSensorsComponent` | `orchestration/components/kcg_cognify_component.py` | Add `automation_condition: manual` default |
| `CelticFederatedOcrComponent` | `orchestration/components/layer3_model_lifecycle.py` | Add `automation_condition: manual` default |

(Dagster 1.13+ default for `automation_condition` is `eager()`; the explicit `manual` makes them run only when the operator launches them by hand.)

### C — Lakehouse preflight (3 new files + 1 mise task)

**New files**:

- `scripts/lakehouse_preflight.py` — CLI probe that hits the 5 required lakehouse endpoints (Nimtable :3018 + Olake :3901 + LanceDB Viewer :8081 + Lance sidecar :8182 + Lakekeeper :8181) + the 12 postgres databases (the 6 `ducklake_<ns>` + `dagster_local` + `olake_state` + `nimtable` + `langfuse` + `mlflow` + `litellm`) + the 8 Garage buckets (iceberg, lance, ducklake, ducklake-cianfhoghlaim, langfuse-events, langfuse-media, langfuse-exports, mlflow-artifacts). Reports the cognify stack status as `skipped` (graceful) when the cognify stack is intentionally not deployed. Exits 0 if all required probes pass.
- `scripts/audit_lakehouse_buckets.py` — helper that uses `urllib3` to hit the Garage admin API directly (no `awscli` dependency). Returns the bucket list.
- `notebooks/24_lakehouse_preflight.py` — marimo dashboard: the same probes as a visual grid (5 required + 4 optional + 12 databases).

**Mise task**:

```toml
[tasks."lakehouse:preflight"]
description = "Local-bunchloch lakehouse preflight: 5 required lakehouse endpoints + 12 postgres databases + 8 Garage buckets + (graceful) cognify stack status"
run = "python3 scripts/lakehouse_preflight.py"
```

### D — Spec deltas (3 specs × 1 ADDED Requirement each)

- `dagster-5-layer-component-architecture`: ADDED Requirement "Component YAML mount convention" — every parent directory that has Component YAML children MUST have an `_layer/defs.yaml` (DefsFolderComponent) OR a bare `defs.yaml` (Component) at the directory root, AND every loadable Component YAML MUST be named exactly `defs.yaml`.
- `british-isles-education-pipeline-v3`: ADDED Requirement "M1-M4 milestones do not trigger deferred L3 assets" — the `mise run biep:v3:m0..m4` entrypoints SHALL NOT trigger any L3 asset that has `automation_condition: manual` (the cognify + federated_ocr subset).
- `infrastructure-stacks`: ADDED Requirement "Lakehouse preflight task" — `mise run lakehouse:preflight` SHALL exist and validate the 5 required endpoints + 12 databases + 8 buckets before any BIEP pipeline runs.

## Dependencies

```
Blocked by: none
Blocked by (soft): none
Affected repos: cianfhoghlaim (single repo)
```

The change is self-contained:
- No external dependencies (no new openspec change is required before this one can archive)
- The companion change `2026-08-15-update-dagster-5-layer-spec-for-v7-flattening-v1` is a separate issue (the spec drift is informational, not blocking)

## Impact

- Capabilities: 3 MODIFIED specs (each with 1 ADDED Requirement)
- Code: 8 new files (7 defs.yaml + 1 preflight script bundle) + 13 renames + 3 Component edits + 1 mise task + 1 marimo notebook
- Risk: low — purely additive (4 new `defs.yaml` mount files + 1 preflight script + 1 mise task) + pure rename (13 files, no content changes) + 3 explicit `automation_condition: manual` defaults (these are the SAFEST automation_condition values)
- Mitigations: `dg check yaml` is a runnable smoke test that walks every defs.yaml and reports schema errors; `scripts/lakehouse_preflight.py` validates the actual stack health end-to-end

## Out of scope (explicit deferrals)

- **3 `defs.yaml.planned` files** (dbt_project, portal_eval, cocoindex_v1/_schedules) — these are intentional dead-letter markers with rich "what would revive this" comments. Revival requires separate openspec changes (one per revival).
- **L3 cognify stack bringup** — the L3 cognify + federated_ocr assets are marked `automation_condition: manual` in this change. A follow-up `bring-cognify-stack-to-lakehouse-cluster` change can remove the manual flag once the cognify stack (cognee + graphiti + falkordb + lancedb + memgraph) is brought up alongside the lakehouse stack.
- **Pyproject drift** (`registry_modules = ["orchestration.components"]` vs spec's `["cianfhoghlaim.dagster.components"]`) — handled by the companion change `2026-08-15-update-dagster-5-layer-spec-for-v7-flattening-v1`.

## Cross-references

- `openspec/specs/dagster-5-layer-component-architecture/spec.md` — the 5-layer architecture spec
- `openspec/specs/british-isles-education-pipeline-v3/spec.md` — the BIEP v3 milestone entrypoints
- `openspec/specs/infrastructure-stacks/spec.md` — the lakehouse stack inventory
- `scripts/smoke_test_lakehouse.py` — the existing 5-endpoint probe (not modified)
- `orchestration/definitions.py` — the canonical `dg.load_defs()` entrypoint
- `orchestration/components/__init__.py` — the 14-component registry (unchanged)
- `docs/00-cognition/INDEX.md` — the deploy:full 10-phase state machine
