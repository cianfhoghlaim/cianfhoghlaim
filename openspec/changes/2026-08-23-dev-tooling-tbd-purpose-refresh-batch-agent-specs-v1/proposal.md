# 2026-08-23 — Fill 10 TBD Purpose fields (agent specs batch) + wire lint:spec:purpose to core:lint

## Why

The Phase 2.3 change filled the 10 data-spec TBDs. 22 TBDs remain,
split across:

- **Agent specs** (this change): 10 specs covering the agent fleet
  surface
- **Infra specs** (Phase 5.1.3): 10 specs covering the IaC + Docker
  surface
- **Oideachais specs** (Phase 5.1.4): 9 specs covering the oideachais
  education surface
- **Already addressed**: dev-tooling-surfaces spec itself (covered
  in Phase 2.3 + Phase 2.4)

This change fills the 10 agent-spec TBDs and **wires `lint:spec:purpose`
into `core:lint`** for the first time (since all remaining TBDs after
this change will be infra + oideachais, and those are addressed in
5.1.3 + 5.1.4).

## The 10 agent specs to update

| Spec | TBD→Purpose |
|:--|:--|
| `drift-remediation` | drift detection + auto-remediation contract |
| `dual-search-architecture` | CCC + Cognee + Firecrawl dual-search workflow |
| `centralize-cross-cutting-docs` | per-area AGENTS.md + per-spec AGENTS.md convention |
| `centralized-model-registry` | the 76-entry canonical model registry |
| `centralized-schema-registry` | BAML as source of truth for schemas |
| `deployment-control-panel` | marimo 5-tab control panel + web UI + CLI |
| `docs-informed-content-generation` | docs → content pipeline |
| `integration-runtime-wiring` | agent runtime → tool integration |
| `meaisinfoghlaim-ocr-htr` | OCR/HTR pipeline surface |
| `repo-hygiene-agent-routing` | the per-spec AGENTS.md + concurrent-write safety |

After this change, `core:lint` can depend on `lint:spec:purpose`
(failing on any remaining TBD in the infra + oideachais batches).

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** the 10 archived changes that created each spec
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. All 10 agent specs have non-TBD Purpose sections
2. `lint:spec:purpose` is added to `core:lint` depends
3. `core:lint` exits 0 (only the infra + oideachais TBDs remain; they're addressed in 5.1.3/5.1.4)
4. `openspec validate 2026-08-23-dev-tooling-tbd-purpose-refresh-batch-agent-specs-v1 --strict` exits 0

## Rollback plan

- `git checkout` the 10 spec files to revert the TBD Purpose fills
- Remove `lint:spec:purpose` from `core:lint` depends