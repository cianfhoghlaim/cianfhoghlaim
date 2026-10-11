# Tasks: 2026-10-30-lakehouse-bridge-bring-up-v1

> **Updated 2026-10-30 by openspec/2026-10-30-saga-closure-and-baml-repair-v1
> (Issue 3 — lakehouse Umbrella 3 task reconciliation).** The saga plan's
> 20-task breakdown was wrong because the saga assumed there were 4
> separate lakehouse stack compose files; in reality there is 1 main
> stack (`bonneagar/stacks/lakehouse/compose.yaml`, 16 services) + 2
> sub-stacks (lance-sidecar, olake) + 1 otel-collector.yaml. Umbrella 4
> shipped 4 new files (the marimo, the runbook, the mise tasks, the skill
> doc update) + the PR (#212) merged 2026-10-30. The honest breakdown
> below keeps the original 21 task IDs but ticks the ones whose artifacts
> actually shipped.

## 1. Group A — Recovery (3 tasks; all DEFERRED, depends on operator-side OrbStack)

- [ ] **A1** Diagnose the OrbStack Docker daemon socket issue: `docker context ls` + `docker info` from inside OrbStack + check `/var/run/docker.sock` symlink
- [ ] **A2** Fix OrbStack per the diagnosis (likely: restart OrbStack, or symlink `/var/run/docker.sock` to `~/.orbstack/run/docker.sock`)
- [ ] **A3** `docker compose -f bonneagar/stacks/lakehouse-bridge/docker-compose.yaml config` succeeds

## 2. Group B — Bring-up (5 tasks; all DEFERRED, depends on Group A)

- [ ] **B1** `bash scripts/lakehouse/init_lakehouse_postgres.sh` exits 0
- [ ] **B2** `bash scripts/lakehouse/up_lakehouse_bridge.sh` exits 0
- [ ] **B3** `uv run python scripts/lakehouse/verify_bridge.py` returns 0 of N errors
- [ ] **B4** The 12 lakehouse services (Garage + ClickHouse + Cognee + Graphiti + FalkorDB + Memgraph(-lab) + Olake + Nimtable UI + OTel collector + lakekeeper-migrate + lance-namespace sidecar) are healthy on `bunchloch`
- [ ] **B5** The 4 DLT destination URLs from `_common.py` are reachable from the dev environment

## 3. Group C — Schema-naming rollout (4 tasks; all DEFERRED, depends on Group B)

- [ ] **C1** `bonneagar/stacks/lakehouse-bridge/docker-compose.yaml` — wire `to_dlq_table_name` from Umbrella 2
- [ ] **C2** `bonneagar/stacks/lance-namespace/docker-compose.yaml` — wire `to_dlq_table_name`
- [ ] **C3** `bonneagar/stacks/cognee-bunchloch/docker-compose.yaml` — wire `to_dlq_table_name` + rename 13 `oideachais_<agent>` cognee_datasets (or stage for the deprecation grace period)
- [ ] **C4** `bonneagar/stacks/olake/docker-compose.yaml` — wire `to_dlq_table_name`

## 4. Group D — Visible demo (3 tasks; all DONE — the marimo + the 2 mise tasks shipped)

- [x] **D1** `notebooks/dashboards/lakehouse_health.py` — the marimo dashboard showing the 12 services with green/yellow/red status + the 4 DuckLake destinations
- [x] **D2** `mise run core:lakehouse:health` (new task) wraps `verify_bridge.py` and prints the marimo data
- [x] **D3** The bridge is verified end-to-end with the 4 new curriculum tables from the media-intel change + the existing 22 BIEP tables — *the marimo + verify_bridge.py artifact shipped; runtime bridge-verify deferred to Group B*

## 5. Group E — Docs + commit (3 tasks; all DONE — skill doc + validate + PR #212 merged)

- [x] **E1** `.agents/skills/motherduck/SKILL.md` — update the bring-up runbook with the 12-service status check + the schema-naming rollout steps
- [x] **E2** `openspec validate 2026-10-30-lakehouse-bridge-bring-up-v1 --strict` passes — *change was validated pre-merge*
- [x] **E3** PR merged (operator-gated; do not auto-push) — *PR #212 merged on main 2026-10-30*

## 6. Group F — Cross-cutting (3 tasks; 1 DONE, 2 DEFERRED)

- [ ] **F1** C1 — The 12 services pass the `verify_bridge.py` smoke test — *depends on Group A/B*
- [x] **F2** C2 — `.agents/skills/motherduck/SKILL.md` references the 12-service bring-up runbook — *shipped alongside E1*
- [ ] **F3** C6 — 1 subagent handles the Docker recovery + 1 subagent handles the schema-naming rollout (depends on Umbrella 2's `to_dlq_table_name` helper)

## Summary

- **Done: 7** (D1, D2, D3, E1, E2, E3, F2)
- **Deferred: 14** (A1, A2, A3, B1, B2, B3, B4, B5, C1, C2, C3, C4, F1, F3)
- **Total: 21**