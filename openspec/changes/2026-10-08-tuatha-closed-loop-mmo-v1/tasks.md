# Tasks: 2026-10-08-tuatha-closed-loop-mmo-v1

## 1. Group A — Dagster asset

- [x] **A1** `orchestration/defs/4_asset_generation/tuatha_realm_asset.py` — the per-subject realm Dagster asset (queries the asset table + builds the realm JSON)

## 2. Group B — ADK agents

- [x] **B1** `tuatha/agents/realm_constructor_agent.py` — the ADK agent that builds realms (the 26th agent in the fleet)
- [x] **B2** `tuatha/agents/quest_pack_agent.py` — the ADK agent that generates BAML quest packs

## 3. Group C — Visible demo

- [x] **C1** `notebooks/dashboards/tuatha_realm_demo.py` — the live demo surface
- [x] **C2** `scripts/tuatha_demo.py` — the CLI demo (`uv run python scripts/tuatha_demo.py --subject mathematics`)

## 4. Group D — Spec materialisation

- [x] **D1** `openspec/specs/tuatha-closed-loop-mmo/spec.md` — 4 Requirements

## 5. Group E — Verification + commit + push

- [x] **E1** `uv run python scripts/tuatha_demo.py --subject mathematics` works
- [x] **E2** `bunx openspec validate 2026-10-08-tuatha-closed-loop-mmo-v1 --strict` passes
- [x] **E3** `git add -A && git commit && git push`
- [x] **E4** Create PR via `gh pr create`
