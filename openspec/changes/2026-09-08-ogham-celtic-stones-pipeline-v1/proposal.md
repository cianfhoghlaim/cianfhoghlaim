# Change: Ogham Celtic Stones Pipeline (CISP + Megalithic Portal → Anam Particles)

## Why

The 1,200+ Ogham stones of the British Isles represent the most distinctive
unported content surface from the previous sruth game research. The CISP
(Celtic Inscribed Stones Project at UCL) + the Megalithic Portal
(community-contributed GPS-tagged stones) together cover ~1,200 inscribed
stones + ~30,000 megalithic sites.

Currently:
- No DLT source for either CISP or Megalithic Portal exists
- No BAML extractor for Ogham inscriptions or aicme affinity exists
- No Convex table for `ogham_stones` or `anam_particles` exists
- No educational agent for Ogham stones exists
- No marimo dashboard for Ogham stones exists

This change builds the canonical ingestion + extraction + embedding +
agent surface for both datasets.

## What changes

- **Ogham Celtic Stones Pipeline** (NEW capability
  `ogham-celtic-stones-pipeline`): 2 DLT sources, 2 BAML
  extractors, 1 CocoIndex v1 App, 1 Dagster asset module,
  1 marimo dashboard, 1 educational agent, 1 Convex table
  set, 1 spatial-grid utility.

- **Convex tables** (capability
  `ogham-celtic-stones-pipeline`): `ogham_stones`,
  `anam_particles`, `stone_visits` (location-based game
  feature), `cisp_records`, `megalithic_records`.

- **BAML extractors** (capability
  `ogham-celtic-stones-pipeline`): `ExtractCISPStone` +
  `ExtractOghamInscription` extending
  `baml/celtic/mythology.baml` from change 1.

- **Ogham Stone Agent** (capability
  `meaisinfhoghlaim-agent-frameworks`): new ADK agent with
  6 tools: `query_ogham_stone`, `extract_aicme_affinity`,
  `generate_anam_particle`, `find_nearby_stones`,
  `classify_inscription`, `render_stone_card`.

- **Spatial grid utility** (capability
  `ogham-celtic-stones-pipeline`): a new
  `notebooks/_shared/spatial_grid.py` helper implementing
  the Bucket Key Algorithm from the SpacetimeDB Ogham
  research (`⌊Lat×100⌋×1,000,000 + ⌊Long×100⌋` for 0.01° ≈
  1.11km cells) + Haversine proximity + 9-bucket Moore
  neighborhood query.

- **Celtic Language Pipeline extension** (capability
  `celtic-language-pipeline`): extends the 7 source groups
  to 9 (adds CISP + Megalithic Portal).

## Out of scope

- The Familiar Dynamic NFT System (separate change 5).
- The geography / history curriculum binding (change 1).
- The Web3 token layer (explicitly rejected).

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-09-01-celtic-mythology-content-system-v1` (the parent change that creates `baml/celtic/mythology.baml`).

`Blocked by: 2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1`.

`Affected repos: cianfhoghlaim`
```

## Impact

- Affected specs:
  - NEW: `ogham-celtic-stones-pipeline` (6 ADDED Requirements)
  - `celtic-language-pipeline` (2 ADDED Requirements)
  - `meaisinfhoghlaim-agent-frameworks` (1 ADDED Requirement)
- Affected code/config:
  - `dlt/language/cisp/` (NEW; 3 files)
  - `dlt/language/megalithic_portal/` (NEW; 3 files)
  - `baml/celtic/mythology.baml` (extended from change 1)
  - `cocoindex_flows/biep_parity/ogham_stones_embedding.py` (NEW)
  - `orchestration/defs/2_materials/ogham_stones_assets.py` (NEW)
  - `notebooks/34_ogham_stones_dashboard.py` (NEW)
  - `notebooks/_shared/spatial_grid.py` (NEW)
  - `agents/meaisinfhoghlaim/educational/ogham_stone_agent.py` (NEW)
  - `web/apps/cianfhoghlaim-mmo/convex/ogham_stones.ts` (NEW)
  - `web/apps/cianfhoghlaim-mmo/convex/anam_particles.ts` (NEW)
  - `web/apps/cianfhoghlaim-mmo/convex/stone_visits.ts` (NEW)

## Cross-references

- `docs/research/game/SpacetimeDB Ogham Stone Game Integration.md`
- `docs/research/game/Ogham Crypto MMO Research.md`
- `openspec/changes/2026-09-01-celtic-mythology-content-system-v1/`
- `openspec/changes/2026-09-29-familiar-dynamic-nft-system-v1/`