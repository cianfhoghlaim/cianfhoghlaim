# Per-Domain Dagster Component Migration Plan

> **Per user request ("2 per domain")** — migrate dlt sources to DltLoadCollectionComponent per domain, not all at once.
> **Related:** Plan v6 Phase F4 (merge Dagster), this is the per-domain subplan.

## 1. Domains (in dependency order)

1. **celtic-asset-generation** (5-stage PDF pipeline + BAML)
2. **cianfhoghlaim-pipeline** (the 28 dlt sources)
3. **meaisinfhoghlaim-platform** (agent memory: Cognee + Graphiti)
4. **cognify** (cross-stage cognify: per Wave 7+ finding #5)
5. **tuatha** (crypteolas MMO + game content)
6. **croilar** (multi-persona portfolio)

## 2. Per-domain migration steps

For each domain:
1. Inventory all dlt sources (count + paths + 1-line description)
2. Create a YAML config file per source (per Dagster DltLoadCollectionComponent spec)
3. Add 1 new asset (DltLoadCollectionComponent-based) alongside the existing Python decorator
4. Test: 1-week shadow run (old + new in parallel, compare outputs)
5. Cutover: remove the old asset + Python decorator wrapper
6. Document: update the per-domain asset file + .agents/skills

## 3. celtic-asset-generation (5-stage PDF + BAML) — DOMAIN 1

### Sources to migrate
- `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/official_media/`
- `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/curriculumonline/`
- `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/examinations/`
- `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/ncca/`
- `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/duchas/`
- (likely 5-7 more in the 5-stage pipeline)

### Migration approach
- DltLoadCollectionComponent YAML in `cianfhoghlaim/assets/definitions/components/celtic_pipeline.yaml`
- Each source = 1 `DltLoadCollectionComponent` def
- Same 7-day shadow run pattern
- Per-source tests (validate BAML extraction output unchanged)

## 4. cianfhoghlaim-pipeline (28 dlt sources) — DOMAIN 2

### Sources to migrate
- All 28 dlt sources in `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/`
- Catalog: `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/SOURCES.md` (NEW)

### Migration approach
- DltLoadCollectionComponent YAML in `cianfhoghlaim/assets/definitions/components/dlt_sources.yaml`
- 28 sources × ~1 line each = 28-line YAML
- Use `@multi_asset_check` (per Wave 1 Agent 84 R3) to consolidate the 7+ health checks
- Same shadow + cutover pattern

## 5. meaisinfhoghlaim-platform (Cognee + Graphiti) — DOMAIN 3

### Sources to migrate
- Memory asset checks (7 cognee graph model health checks)
- Graphiti episode ingestion

### Migration approach
- `@multi_asset_check` (per Wave 1 Agent 84 R2) consolidates 7 individual `@asset_check` into 1
- Use the new `DltLoadCollectionComponent` pattern for the Graphiti Neo4j import
- This is the MOST IMPACTFUL migration (consolidates 7 functions into 1)

## 6. cognify (cross-stage cognify) — DOMAIN 4

### Sources to migrate
- The 6 cross-stage cognify assets in `cianfhoghlaim/cognify/`

### Migration approach
- Single DltLoadCollectionComponent for the cognify schedule
- Wave 1 finding #5: "Wave 3 marimo ingestion-health dashboard" — leverage this

## 7. tuatha (crypteolas MMO + game content) — DOMAIN 5

### Sources to migrate
- Crypteolas asset checks + game content ingestion
- MMO asset generation pipeline

### Migration approach
- Less urgent (smaller data flow)
- Same per-domain pattern

## 8. croilar (multi-persona portfolio) — DOMAIN 6

### Sources to migrate
- 3 persona data flows
- Convex sync assets

### Migration approach
- Last (smallest impact)
- Same per-domain pattern

## 9. Risk per domain

| Domain | Risk | Reason |
|---|---|---|
| celtic-asset-generation | HIGH | BAML extraction is fragile; 5-stage pipeline is fragile |
| cianfhoghlaim-pipeline | MED | 28 sources × 1-week shadow = 28 weeks of testing |
| meaisinfhoghlaim-platform | LOW | Consolidates 7 functions into 1 (low surface change) |
| cognify | LOW | Already works |
| tuatha | LOW | Smallest data flow |
| croilar | LOW | Smallest data flow |

## 10. Total timeline (per-domain, parallel where possible)

- 6 domains × 1-week each = 6 weeks minimum
- With 2-person squad on 2 domains in parallel: 3 weeks
- With 1-person squad: 6 weeks

## 11. Next steps

1. Domain 1 (celtic-asset-generation) inventory: list all 5-7 dlt sources in `cianfhoghlaim/pipelines/ingest/_cianfhoghlaim_dlt_sources/`
2. Create the YAML config file with 1 DltLoadCollectionComponent per source
3. Add to `cianfhoghlaim/assets/definitions/components/`
4. Wire into `cianfhoghlaim/assets/definitions.py` (the single unified definitions.py from Plan v6 F4)
5. Shadow run for 1 week
6. Cutover + remove the 5-7 old `assets/definitions.py` Python-decorator versions

## 12. Dependencies

- Requires Plan v5 Phase A (deploy foundations) to be DONE first
- Requires Plan v5 Phase B (P0 + P1 refactors including DltLoadCollectionComponent adoption) to be DONE first
- Specifically depends on B3.4 from Plan v5 (per-domain Dagster Component migration)
