# Tasks: Lakehouse memory-stack deep integration

This change ships in **7 phases**. Each phase is one PR. The order
matches the dependency chain — phases with `- [ ]` that depend on a
prior phase SHALL NOT start until the prior phase merges.

## Phase A — Discovery + spec draft (1 PR)

- [ ] Verify the canonical URI form is `infisical://dev-baile/<svc>/<key>` by reading `.agents/skills/secrets-management/SKILL.md` + the 4 already-migrated stacks (`cognee`, `graphiti`, `falkordb`, `lancedb`)
- [ ] Inventory all 10 affected `secrets.env` files with `bun run validate-stacks --strict --check-grammar` and capture the baseline MIXED count
- [ ] Write `openspec/changes/2026-08-15-lakehouse-memory-stack-deep-integration-v1/{proposal.md, tasks.md}` (this file)
- [ ] Write 4 spec delta files at `openspec/changes/2026-08-15-lakehouse-memory-stack-deep-integration-v1/specs/{agent-memory-systems, agent-platform-cluster, infrastructure-stacks, indexing-and-cognition}/spec.md`
- [ ] Run `openspec validate 2026-08-15-lakehouse-memory-stack-deep-integration-v1 --strict` and confirm exit 0

## Phase B — Secrets contract (1 PR, depends on A)

- [ ] Extend `scripts/seed-infisical-vault.py` to auto-seed the ~30 new keys from the env-var matrix (see proposal.md "The ~30 new Infisical keys" section)
- [ ] Append the 30 new entries to `.infisical.env` in the canonical URI form
- [ ] Run `bun run scripts/init-vault.ts` to push the new keys to `dev-baile`
- [ ] Run `bun run scripts/normalize-infisical-uri.ts` on the 4 mixed-form stacks (`memgraph`, `langfuse`, `mlflow`, `litellm`)
- [ ] Verify `bun run validate-stacks --strict --check-grammar` reports **zero** mixed stacks (was: 4)

## Phase C — Compose + image pin upgrade (1 PR, depends on B)

- [ ] Pin `cognee/cognee:1.2.2` (was `:latest`) in `bonneagar/stacks/cognee/compose.yaml` + add the new OTLP/LanceDB env vars
- [ ] Pin `falkordb/falkordb:v4.18.11` (was `v1.1.2`) + add `command: ["falkordb", "--loadmodule", "/etc/falkordb/vector.so"]` to `bonneagar/stacks/falkordb/compose.yaml` (closes the open prod drift alert)
- [ ] Pin `memgraph/memgraph:3.6.0` (was unpinned) in `bonneagar/stacks/memgraph/compose.yaml`
- [ ] Pin `lance-namespace:v0.9.0` (the Lance Namespace sidecar at lakehouse) in `bonneagar/stacks/lakehouse/lance-sidecar/Dockerfile`
- [ ] Verify all 5 memory backends' composes pass `mise run cic:stack-doctor` with **zero** unpinned-image warnings

## Phase D — Marimo notebook + control panel (1 PR, depends on C)

- [ ] Write `notebooks/24_lakehouse_memory_doctor.py` (~600 LOC) — 5-column grid (cognee / graphiti / lancedb / falkordb / memgraph) + per-backend probe (endpoint ping + container status + last cognify/episode timestamp + vector-index row count) + federated search demo (via `agents/memory_layer.py` `MemoryLayer` Protocol)
- [ ] Extend `notebooks/00_control_panel.py` Tab 5 (Registry) to surface a one-click link to `notebooks/24_lakehouse_memory_doctor.py` and display the latest `stedding/memory-health/<date>.json` summary
- [ ] Run `mise run lint:wasm` (the `wasm-compatibility` skill check) to confirm the notebook is WASM-portable

## Phase E — Deploy automation (1 PR, depends on D)

- [ ] Write `scripts/lakehouse-memory-doctor.ts` (~300 LOC) — CLI probe that returns JSON `{backends: {cognee: {status, latency_ms, last_event}, graphiti: {...}, lancedb: {...}, falkordb: {...}, memgraph: {...}}, summary: {healthy: N/5, failed: [...]}}` and writes to `stedding/memory-health/<utc-ts>.json`
- [ ] Add `mise.toml` task `lakehouse:memory:doctor` → `bun run scripts/lakehouse-memory-doctor.ts`
- [ ] Extend `scripts/deploy-full.sh` + `scripts/deploy-full.ts` Phase 7 (`data-stacks-up`) to invoke the doctor after the 8 supporting stacks come up + fail the phase if any backend reports `not_healthy`
- [ ] Extend `scripts/registry_audit.py` to detect compose-level model hardcodes (regex against `image:` env vars + the `LLM_MODEL=` / `OPENAI_MODEL=` style keys) — closes gap G9
- [ ] Verify `mise run lint:registry --strict` exits 0

## Phase F — Validate + drift (1 PR, depends on E)

- [ ] Run `openspec validate 2026-08-15-lakehouse-memory-stack-deep-integration-v1 --strict` — confirm exit 0
- [ ] Run `mise run cic:stack-doctor --strict --check-grammar` — confirm **zero** mixed stacks + **zero** unpinned-image warnings
- [ ] Run `mise run lint:registry --strict` — confirm **zero** hardcoded model strings across the platform (including compose-level)
- [ ] Run `mise run lint:drift-docs` — confirm the new stack counts / model counts surface in the per-spec AGENTS.md (the `agent-memory-systems` AGENTS.md, `agent-platform-cluster` AGENTS.md, etc.)
- [ ] Run `mise run lint:skills` — confirm the 5 new entries do not break the frontmatter validation

## Phase G — Deploy + archive (1 PR, depends on F)

- [ ] Run `mise run deploy:full --dry-run --phase=7` — dry-run the upgraded Phase 7
- [ ] Run `mise run deploy:full --phase=7` — bring the memory stack up on bunchloch
- [ ] Curl the 5 health endpoints and confirm 200:
  - `http://cognee:8000/health` (Cognee Swagger UI reachable)
  - `http://graphiti:8000/healthcheck` (Graphiti temporal KG API)
  - `http://lakehouse-lance-namespace:8182/v1/info` (Lance Namespace 0.9 contract)
  - `redis-cli -h falkordb ping` (FalkorDB vector-enabled graph)
  - `http://memgraph:7687` (Memgraph 3.x Bolt endpoint)
- [ ] Open `notebooks/24_lakehouse_memory_doctor.py` in marimo and confirm the 5-column grid renders with all 5 backends `Up`
- [ ] Open `notebooks/00_control_panel.py` Tab 5 and confirm the new "Memory Doctor" link surfaces
- [ ] `openspec archive 2026-08-15-lakehouse-memory-stack-deep-integration-v1 --yes`
- [ ] Push the branch (per the canonical agent workflow: never commit + push proactively without explicit user direction — flag this step for the user)

## Phase F+ — Post-archive notes (after archive)

- [ ] Update `.agents/skills/agent-memory-systems/SKILL.md` § "KCG conventions" with a "Post-archive update: 2026-08-15-..." note (per the Skill + openspec alignment requirement in `infrastructure-stacks`)
- [ ] Update `.agents/skills/infrastructure-stacks/SKILL.md` § "The 92-stack inventory" with the new image pins
- [ ] Update `.agents/skills/cognee/SKILL.md` to surface the new env-var matrix
- [ ] Update `.agents/skills/falkordb/SKILL.md` to remove the "Production drift alert" note (now resolved by Phase C)
- [ ] Run `mise run sync:all` to refresh the sync-reports (paths + ccc + cognee + skills + mcp + drift-docs + dagster)