# Change: Lakehouse memory-stack deep integration (Cognee + Graphiti + FalkorDB + Memgraph + LanceDB)

## Why

The agent-memory-systems + agent-platform-cluster + indexing-and-cognition
openspec specs each describe pieces of the 5-backend memory + 8-stack
agent-platform-cluster integration, but the on-disk surface has **9
operational gaps** that make deployment brittle and operator toil high:

1. **Mixed-form secrets** — `bonneagar/stacks/memgraph/secrets.env`,
   `langfuse/secrets.env`, `mlflow/secrets.env`, and `litellm/secrets.env`
   still use the legacy Jinja `{{ infisical:///key?path=/svc }}` form
   instead of the Locket-canonical `infisical://dev-baile/<svc>/<key>`
   form. `bun run validate-stacks --strict --check-grammar` reports them
   as **MIXED**.
2. **Unpinned images** — `cognee/compose.yaml` uses `:latest`; the
   `graphiti` compose still references `Neo4j` URIs in some comments;
   `falkordb` compose pins `v1.1.2` but the upstream has shipped
   `v4.18.11` (verified live 2026-06-29 by the falkordb skill). Image
   Pinning Policy requires semver on every line.
3. **FalkorDB vector.so not loaded** — `falkordb/compose.yaml` does NOT
   load `vector.so`, so vector queries silently fail in production. The
   `falkordb` SKILL.md flags this as an "open production drift alert
   since Wave 1".
4. **Inconsistent observability coverage** — `memgraph/secrets.env` and
   `falkordb/secrets.env` have no `OTEL_EXPORTER_OTLP_ENDPOINT` /
   `LANGFUSE_*` env vars; the otelcol → logfire + langfuse fan-out
   (per `agent-observability` skill) is partial.
5. **No marimo doctor** — no single screen surfaces the health of all 5
   memory backends. Operators have to `docker compose ps` + curl each
   endpoint manually.
6. **No mise task for memory-stack health** — operators have no
   one-command doctor.
7. **PlanetScale PG centralisation wiring is partial** — only the
   `lakehouse` stack has the PlanetScale `DATABASE_URL` override; the
   other 3 target stacks (cognee, langfuse, mlflow) declared in the
   umbrella spec R7 do not yet have the optional override path.
8. **No automated Infisical seed** — the 30+ new keys required for the
   full coverage matrix are not in `scripts/seed-infisical-vault.py`;
   operators must add them by hand via the Infisical UI.
9. **Compose-level model hardcodes are not audited** —
   `mise run lint:registry` only audits `agents/`, `baml_src/`,
   `notebooks/`, `web/`, `orchestration/`, `spaces/`,
   `meaisinfhoghlaim/`. A compose.yaml that hardcodes
   `openai/gpt-4o-mini` slips through.

This change closes all 9 gaps in one cohesive change with explicit
secrets contracts + a single marimo doctor + a `mise run` task + the
openspec spec deltas that drive them.

## What Changes

- **Phase B** — Migrate 4 remaining mixed-form stacks (memgraph,
  langfuse, mlflow, litellm) from Jinja to canonical URI form.
  Extend `.infisical.env` with the ~30 new entries from the env-var
  matrix. Extend `scripts/seed-infisical-vault.py` so the new keys
  can be auto-seeded.
- **Phase C** — Pin every `image:` line in the 5 memory backends'
  `compose.yaml` files to semver. Add `--loadmodule /etc/falkordb/vector.so`
  to `falkordb/compose.yaml` (closes the open prod drift alert). Extend
  memgraph secrets.env to add OTLP + Langfuse + Enterprise license env vars.
- **Phase D** — Write `notebooks/24_lakehouse_memory_doctor.py` (~600
  LOC) — 5-column grid + per-backend probe + federated search demo.
  Extend `notebooks/00_control_panel.py` Tab 5 (Registry) to surface a
  one-click link to the doctor.
- **Phase E** — Write `scripts/lakehouse-memory-doctor.ts` (~300 LOC) —
  CLI probe + JSON health report at `stedding/memory-health/<utc-ts>.json`.
  Add `mise.toml` task `lakehouse:memory:doctor`. Extend `deploy-full.sh`
  + `deploy-full.ts` Phase 7 to invoke the doctor + fail on non-healthy.
  Extend `scripts/registry_audit.py` to flag compose-level model hardcodes.
- **Phase F** — Run the 4 gates: `openspec validate --strict`,
  `mise run cic:stack-doctor --strict --check-grammar`,
  `mise run lint:registry --strict`, `mise run lint:drift-docs`.
- **Phase G** — Deploy + archive. Curl the 5 health endpoints. Open
  the marimo notebook in browser. `openspec archive --yes`.

The change adds 4 Requirements to `agent-memory-systems`, 1 to
`agent-platform-cluster`, 3 to `infrastructure-stacks`, and 1 to
`indexing-and-cognition`. See the per-spec delta files for full text.

## Dependencies

```
Blocked by: none
Blocked by (soft):
  - 2026-08-13-knowledge-graph-population-activation-v1 (brings the
    cognee stack up; this change layers deep integration on top)
  - 2026-08-13-bonneagar-infra-remediation-v3 (current IaC remediation
    pass; ensures the IaC tests in bonneagar pass before our archive)
Affected repos: cianfhoghlaim (single repo; no cross-repo-sync.md needed
  because the IaC is in bonneagar/ subdirectory of the same repo)
```

The change CAN archive as soon as the 4 spec gates pass + the 4
quality gates pass + the 5 health endpoints return 200.

## Impact

- Capabilities: MODIFIED `agent-memory-systems` (2 ADDED Requirements),
  MODIFIED `agent-platform-cluster` (1 ADDED Requirement),
  MODIFIED `infrastructure-stacks` (3 ADDED Requirements),
  MODIFIED `indexing-and-cognition` (1 ADDED Requirement).
- Code: 8 new files (4 spec deltas + 1 marimo notebook + 1 TS doctor
  + 1 openspec proposal + 1 openspec tasks) + 25 edits to existing files.
- Risk: low-medium — pure additive + migration. No model registry
  changes, no Dagster asset changes, no agent fleet changes. Mitigated
  by the 4 quality gates + the per-stack `secrets.env` migration script
  (`scripts/normalize-infisical-uri.ts`) which is idempotent.

## Out of scope (deferred to other changes)

- Rebalancing the 5 v1 CocoIndex Apps (`upstream-package-monitoring` scope)
- Regenerating `litellm/config/config.yaml` from `MODEL_REGISTRY`
  (handled by the existing `cic:meaisin:litellm-regenerate` task)
- Moving cognee / langfuse / mlflow to PlanetScale PG as the **primary**
  store — this change only wires the optional `DATABASE_URL` override
  path (the R7 follow-through from `planetscale-postgres-data-strategy`)
- The `iac:bootstrap-pangolin-client` invocation (already in
  `agent-platform-cluster` R)
- Adding new stacks to the 92-stack inventory (the 5 backends are
  already there; this change only upgrades them)

## Cross-references

- `openspec/specs/agent-memory-systems/spec.md` — the 5-backend memory router
- `openspec/specs/agent-platform-cluster/spec.md` — the 8-stack cluster + 3 agent surfaces
- `openspec/specs/indexing-and-cognition/spec.md` — CCC + Cognee + OpenCode agent registry
- `openspec/specs/infrastructure-stacks/spec.md` — the 92-stack catalogue + GOLD_STANDARD
- `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 — the umbrella for PlanetScale PG centralisation
- `.agents/skills/agent-memory-systems/SKILL.md` — the router skill
- `.agents/skills/cognee/SKILL.md` — Cognee 1.2.2 (verified 2026-08-15)
- `.agents/skills/graphiti/SKILL.md` — graphiti-core 0.29.2 (verified 2026-08-15)
- `.agents/skills/lancedb/SKILL.md` — Lance Namespace 0.9 contract
- `.agents/skills/falkordb/SKILL.md` — FalkorDB 4.18.11 + the open vector.so drift alert
- `.agents/skills/memgraph/SKILL.md` — Memgraph 3.x + MAGE
- `.agents/skills/infrastructure-stacks/SKILL.md` — the 6-file GOLD_STANDARD
- `.agents/skills/secrets-management/SKILL.md` — Infisical v0.161.9 + Locket