---
name: stacks-sync
description: |
  The Layer 8 sync loop for the 89 Docker Compose stacks at
  `bonneagar/stacks/`. Validates the 6-file GOLD_STANDARD pattern
  (compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml +
  blueprint.yaml + .env.example) + surfaces drift via 5 sub-layers +
  ingests the stack catalog into Cognee + indexes it in CCC. Use
  when adding/removing a stack, debugging a stack validation
  failure, or asking "how do I keep the IaC surface in sync?".
  Triggers: 'stack sync', 'GOLD_STANDARD check', 'stack-doctor
  drift', 'stacks-sync', 'validate stack', 'Locket sidecar',
  'Pangolin resource', 'stack-catalog search'.
---

# `stacks-sync` — Layer 8 of the knowledge-sync-loop

> **Layer 8 of the 8-layer pull-based sync architecture.**
> Validates the 89 Docker Compose stacks at `bonneagar/stacks/` +
> the 6-file GOLD_STANDARD pattern + the `stack-doctor.sh` audit.
> Closes the IaC surface gap detected in the Week 4 audit.

## When to load

Load this skill when:

- You add or remove a stack at `bonneagar/stacks/`
- You need to run `bash scripts/stack-doctor.sh` to validate the
  6-file GOLD_STANDARD pattern
- You debug a missing `sidecar.yaml` / `secrets.env` /
  `pangolin.yaml` / `blueprint.yaml` / `.env.example`
- You run `mise run sync:stacks` (the orchestrator)
- You ask "how do I check the IaC surface health?"
- You wire a new Dagster asset or marimo notebook for the IaC layer
- You update `notebooks/24_deployment_control_panel.py` to add the
  stacks layer status

## The 5 sub-layers

| Layer | Sync script | Mise task | Purpose |
|:--|:--|:--|:--|
| 1 | `scripts/sync/stacks-drift.sh` | `mise run sync:stacks-drift` | Detect GOLD_STANDARD violations + name collisions + legacy `oideachais/` refs |
| 2 | `scripts/sync/stacks-ccc.sh` | `mise run sync:stacks-ccc` | Append the **23rd CCC concept guide** `stack-catalog-search` + reindex |
| 3 | `scripts/sync/stacks-cognee.sh` | `mise run sync:stacks-cognee` | Ingest the 89 stack catalogs into the **12th Cognee cluster** `stacks_catalog` |
| 4 | `scripts/sync/stacks-validate.sh` | `mise run sync:stacks-validate` | Run `stack-doctor.sh` + parse the output (109 CRITICALS) |
| 5 | `scripts/sync/stacks-health.sh` | `mise run sync:stacks-health` | Per-stack health report (GOLD_STANDARD status + drift count) |
| orchestrator | `scripts/sync/stacks.sh` | `mise run sync:stacks` | Runs all 5 sub-layers + writes a unified report |

## The 6-file GOLD_STANDARD pattern

Every stack at `bonneagar/stacks/<name>/` MUST ship with all 6 of:

| File | Purpose |
|:--|:--|
| `compose.yaml` | Docker Compose definition (required — gates the rest) |
| `sidecar.yaml` | Locket sidecar config (secrets injection at runtime) |
| `secrets.env` | Secret references (every value MUST be `infisical://dev-baile/...`) |
| `pangolin.yaml` | Pangolin resource labels (the 6-label pattern) |
| `blueprint.yaml` | Komodo blueprint (per-stack rollout config) |
| `.env.example` | Documented env-var template (no real values) |

The 4 known violators (per the Week 4 audit) are `browser`,
`ludusavi`, `moonlight`, `storybook`. `bash scripts/sync/stacks-drift.sh`
surfaces all violators + the per-stack missing-files list.

## Quick start

```bash
# Run the orchestrator (all 5 sub-layers + unified report)
mise run sync:stacks

# Run an individual sub-layer
mise run sync:stacks-drift      # detect violators
mise run sync:stacks-ccc        # update CCC concept guide
mise run sync:stacks-cognee     # ingest stack catalogs to Cognee
mise run sync:stacks-validate   # run stack-doctor.sh
mise run sync:stacks-health     # per-stack health

# Verify the 6-file GOLD_STANDARD pattern (the canonical CI gate)
mise run cic:stack-doctor       # alias for stack-doctor.sh
mise run validate-stacks        # same gate, alternate alias

# View the unified report
ls -t stedding/sync-reports/stacks-*.md | head -1
```

## The stacks evolution feedback loop

```
stack file modified under bonneagar/stacks/<stack>/
  → sync:stacks-cognee detects the change (via file mtime)
  → re-cognifies the modified stack into stacks_catalog
  → sync:stacks-ccc updates the 23rd concept guide
  → notebooks/24_deployment_control_panel.py surfaces the change
```

## Canonical artifacts

| Artifact | Path |
|:--|:--|
| Spec | `openspec/specs/stacks-sync-loop/spec.md` |
| Change proposal | `openspec/changes/2026-08-15-stacks-sync-loop-v1/proposal.md` |
| Ingestor | `scripts/cognee_ingest_stacks_catalog.py` |
| Dagster asset | `orchestration/defs/sync_assets.py::stacks_sync_health` |
| Dashboard | `notebooks/sync_health.py` (Stacks tab) |
| Control panel integration | `notebooks/24_deployment_control_panel.py` (statuses["stacks"]) |
| CCC guide | `.cocoindex_code/guides.yml::stack-catalog-search` (23rd) |
| Stack audit | `scripts/stack-doctor.sh` |
| IaC root | `bonneagar/AGENTS.md` (the 94-stack catalogue) |

## DO NOT

- **Never** hand-edit `.env` files. Use `infisical://dev-baile/...`
  refs in `secrets.env` + Locket sidecar injection at runtime.
- **Never** create a stack without all 6 GOLD_STANDARD files — the
  `cic:stack-doctor` gate will fail on the next push.
- **Never** reference `infrastructure/stacks/` (pre-v7 path) — use
  `bonneagar/stacks/` after the 2026-07-17 v7 flattening.
- **Never** add a stack with a fada character (e.g.
  `meaisínfhoghlaim`) — the ASCII `meaisinfhoghlaim` is canonical.
- **Never** skip `mise run sync:stacks` after a stack edit — the
  stacks evolution feedback loop only runs when invoked.

## Skill pointers

- [`infrastructure-stacks`](.agents/skills/infrastructure-stacks/SKILL.md)
  — the 6-file GOLD_STANDARD contract
- [`ccc`](.agents/skills/ccc/SKILL.md) — semantic code search
- [`dagster`](.agents/skills/dagster/SKILL.md) — the
  `stacks_sync_health` asset
- [`motherduck`](.agents/skills/motherduck/SKILL.md) — the lakehouse
- [`pangolin`](.agents/skills/pangolin/SKILL.md) — Pangolin resource
  labels (the 6-label pattern)
- [`komodo`](.agents/skills/komodo/SKILL.md) — Komodo blueprints
- [`secrets-management`](.agents/skills/secrets-management/SKILL.md) —
  Infisical + Locket sidecar pattern
- [`openspec`](../openspec/AGENTS.md) — the spec change workflow
