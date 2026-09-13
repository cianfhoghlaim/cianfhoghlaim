# Tasks: pipeline-knowledge-graph-indexing

> Cross-batch KG + indexing cognition cleanup.
> Absorbs `2026-08-10-knowledge-graph-population-v1` (0/16) +
> `2026-08-13-knowledge-graph-population-activation-v1` (0/16) +
> `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` (0/31).

## 1. KG population (from knowledge-graph-population-v1)

- [ ] **G1.1** Wire the 4 missing per-stage cognify adapters (only `cross_stage_cognify` has a `defs.yaml`)
- [ ] **G1.2** Activate the 8 hand-coded `BRIDGE` edges
- [ ] **G1.3** Migrate 30 + 8 equivalences into Cognee
- [ ] **G1.4** Wire 7 ad-hoc `cognee_ingest*.py` scripts as Dagster sensors
- [ ] **G1.5** Update `openspec/specs/cianfhoghlaim-cognify-knowledge-graph/spec.md` +7 ADDED Requirements

## 2. KG activation (from knowledge-graph-population-activation-v1)

- [ ] **G2.1** Bring up `bonneagar/stacks/cognee/` (compose up)
- [ ] **G2.2** Register the 5 missing per-stage cognify `defs.yaml` files
- [ ] **G2.3** Activate 8 BRIDGE cross-stage edges + 38 cross-jurisdiction equivalences + 7 ingest sensors
- [ ] **G2.4** Add real bilingual prompts to `baml_src/_shared/cognee_ingest_*.baml` (currently stubbed for Gaeilge)
- [ ] **G2.5** Update `openspec/specs/british-isles-education-pipeline-v3/spec.md` +2 ADDED Requirements (5-stage cognify graph populated; bilingual EN+GA extraction uses Gaeilge client)

## 3. Indexing cognition cleanup (from count-drift-rebase-and-indexing-cognition-cleanup-v1)

- [ ] **C3.1** Rebaseline 7 stale count claims across 4 AGENTS.md files (pre-existing drift left alone by Changes 1+2)
- [ ] **C3.2** Correct 8 internal inconsistencies in `.agents/skills/INDEXING_AND_COGNITION.md` (outdated file/chunk/MCP/skill counts, dead path references)
- [ ] **C3.3** Update 7 MODIFIED lines across 4 AGENTS.md files (count updates only)
- [ ] **C3.4** 1 MODIFIED `.agents/skills/INDEXING_AND_COGNITION.md` (8 corrections)

## 4. Verification

- [ ] Run `openspec validate pipeline-knowledge-graph-indexing --strict` — pass
- [ ] Run `mise run lint:drift-docs` — pass

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianfhoghlaim
openspec validate pipeline-knowledge-graph-indexing --strict
```
