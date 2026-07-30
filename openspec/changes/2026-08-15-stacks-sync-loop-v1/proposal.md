# 2026-08-15-stacks-sync-loop-v1

## Why

The 7-layer pull-based sync architecture from
`2026-08-15-knowledge-sync-loop-v1` (extended by 3 follow-ups:
`2026-08-15-retroactive-pre-v7-cleanup-v1` for path drift, the
implicit DLT sync, and `2026-08-15-baml-sync-loop-v1` for BAML)
covers 10 of the 14 knowledge surfaces. The biggest remaining gap is
the **IaC stacks surface** — the 87 Docker Compose stacks at
`bonneagar/stacks/` + the 6-file GOLD_STANDARD pattern + the
`stack-doctor.sh` audit.

Stacks drift is silent: when an operator adds a new stack but
forgets `sidecar.yaml` or `secrets.env`, the `stack-doctor.sh`
audit catches it but the report is not surfaced through the sync
loop. The 4 known violators (`browser`, `ludusavi`, `moonlight`,
`storybook`) are still missing files (per the Week 4 audit), and
the `stack-doctor.sh` report shows **109 CRITICALS** at last run.

This change extends the sync loop with **Layer 8 — `sync:stacks`**
that closes the IaC surface gap: detects GOLD_STANDARD violations +
names collisions + the 4 known violators + ingests the stacks
catalog into Cognee + indexes it in CCC + adds a new Dagster asset
+ a new marimo notebook + a new skill.

## What changes

### Section A — The Layer 8 sync loop (5 layers + orchestrator)

The pattern mirrors the existing 7 layers:

#### A.1 — Layer 1: `sync:stacks-drift` (GOLD_STANDARD violation detection)

Detects stacks that don't have all 6 GOLD_STANDARD files:
- `compose.yaml` (required)
- `sidecar.yaml` (required)
- `secrets.env` (required)
- `pangolin.yaml` (required)
- `blueprint.yaml` (required)
- `.env.example` (required)

Plus name collisions (e.g. `meaisínfhoghlaim` with fada vs
`meaisinfhoghlaim` without), legacy `oideachais/` references,
deprecated `infrastructure/` paths.

#### A.2 — Layer 2: `sync:stacks-ccc` (CCC reindex)

Appends the **23rd concept guide** `stack-catalog-search` to
`.cocoindex_code/guides.yml` + runs `bun run ccc:index` for
incremental refresh.

#### A.3 — Layer 3: `sync:stacks-cognee` (Cognee ingestion)

Ingests the 87 stack catalog entries into the **12th Cognee
cluster** `stacks_catalog`. New script: `scripts/cognee_ingest_stacks_catalog.py`.

#### A.4 — Layer 4: `sync:stacks-validate` (stack-doctor audit)

Runs `bash scripts/stack-doctor.sh` + parses the output to validate:
- All 87 stacks have all 6 files
- The 109 CRITICALS are tracked
- The 4 known violators are flagged

#### A.5 — Layer 5: `sync:stacks-health` (stack health)

Reports the per-stack health (GOLD_STANDARD status + drift count +
Cognee cluster populated + CCC indexed).

Plus the orchestrator: `sync:all` runs all 8 layers (was 7) in
sequence + writes a unified 8-layer report.

### Section B — The new artifacts

| Artifact | File | Purpose |
|:--|:--|:--|
| `sync:stacks-drift` | `scripts/sync/stacks-drift.sh` | Layer 1 |
| `sync:stacks-ccc` | `scripts/sync/stacks-ccc.sh` | Layer 2 |
| `sync:stacks-cognee` | `scripts/sync/stacks-cognee.sh` | Layer 3 |
| `sync:stacks-validate` | `scripts/sync/stacks-validate.sh` | Layer 4 |
| `sync:stacks-health` | `scripts/sync/stacks-health.sh` | Layer 5 |
| `sync:stacks` | orchestrator | runs 1-5 in sequence |
| `stacks-sync` skill | `.agents/skills/stacks-sync/SKILL.md` | docs Layer 8 |
| 23rd CCC guide | `stack-catalog-search` | surfaces the 87 stacks |
| 12th Cognee cluster | `stacks_catalog` | the 87 stack catalog entries |
| `stacks_sync_health` asset | `orchestration/defs/sync_assets.py` | Dagster asset |
| `notebooks/27_stacks_sync_dashboard.py` | dashboard | Layer 8 surface |
| `cognee_ingest_stacks_catalog.py` | ingestor | The canonical ingestor |

### Section C — The stacks evolution feedback loop

The system grows its knowledge surface over time via the stacks
evolution feedback loop:

```
stack file modified
  → sync:stacks-cognee detects the change
  → re-cognifies the modified stack into the stacks_catalog cluster
  → sync:stacks-ccc updates the 23rd concept guide
  → The deployment control panel (notebook 24) surfaces the change
```

## Dependencies

```yaml
Blocked by: 2026-08-15-knowledge-sync-loop-v1 (the foundation)
Blocked by (soft): 2026-08-15-retroactive-pre-v7-cleanup-v1
Blocked by (soft): 2026-08-15-baml-sync-loop-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `bash scripts/sync/stacks-drift.sh` reports the 4 known violators
- `bun run ccc:index` succeeds + the 23rd concept guide is loaded
- `cognee-mcp` returns the 12 typed clusters (11 existing + stacks_catalog)
- `bash scripts/sync/stacks-validate.sh` reports the 109 CRITICALS
- `bash scripts/sync/stacks-health.sh` reports per-stack health
- `mise run sync:stacks` runs all 5 sub-layers + produces a unified report
- `mise run sync:all` runs all 8 layers (was 7) + produces a unified 8-layer report
- `mise run lint:skills` reports 58 skills pass (57 + stacks-sync)
- `bash scripts/bring-up-smoke-test.sh` reports "All 7 bring-up steps work"
- `bash scripts/week4-smoke-test.sh` reports "All Week 4 BIEP v3 + sync-loop acceptance gates pass"
- `openspec validate 2026-08-15-stacks-sync-loop-v1 --strict` passes

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1/` (Layer 6 extension)
- `openspec/changes/2026-08-15-baml-sync-loop-v1/` (Layer 7 extension)
- `bonneagar/stacks/` (the 87 stacks)
- `scripts/stack-doctor.sh` (the canonical stack audit)
- `scripts/sync/` (the existing 8 sync scripts)

## Estimated effort

~2 days (1 day per the 2-day rollout).