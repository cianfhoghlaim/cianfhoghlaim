# Change: Celtic Mythology Content System (Tuatha Dé Danann + Irish Kingdoms + LC/A-Level Geography)

## Why

The Cianfhoghlaim platform's content surface for Celtic mythology and Irish
provincial history is currently a thin documentation layer. The Pent-Elemental
Cosmology in `agents/tuatha/` is real, but:

- The 25 deities (Irish/Scottish/Welsh/Manx/English) have no canonical
  BAML extraction surface
- Irish provincial / dynastic history (Tuatha Dé Danann, Uí Liatháin,
  Déisí, Aileach, kings + kingdoms through the centuries) is not modelled
- The Leaving Certificate Geography syllabus + English A-Level Geography
  syllabus are not mirrored as a curriculum binding
- There is no interactive British Isles map with drill-down through
  subnations → subprovinces → subcounties
- There is no GeoAI / DuckDB-via-Ibis-DuckLake geospatial analysis surface
  for the Geography syllabuses

The Celtic Mythology MMO Research (~38KB) + 4 supplementary game research
docs (~150KB) + the existing BAML extraction schema for the 6 Celtic
languages together represent a 200KB content corpus that has no canonical
implementation surface in the active platform.

This change builds the canonical extraction + storage + presentation
surface for all of it.

## What changes

- **Celtic Mythology Content System** (NEW capability
  `celtic-mythology-content-system`): a BAML-as-SSOT schema
  library for 6 Celtic pantheons + Irish dynastic history +
  5 Geographic themes (geomorphology / climate / population /
  economy / culture), BAML extractors for 8 functions, a
  CocoIndex v1 embedding App, Dagster assets, a marimo
  dashboard, and an educational agent that exposes 6 tools.

- **Irish Dynastic History Module** (capability
  `celtic-mythology-content-system`): the canonical BAML
  extractors for the 6 dynastic families (Tuatha Dé Danann,
  Uí Liatháin, Déisí, Aileach, Uí Néill, Eóganachta), the 4
  provincial kingdoms (Leinster / Munster / Connacht /
  Ulster), and the 1,500-year timeline from the 4th century
  AD to the 12th-century Norman arrival.

- **Geography Curriculum Binding** (capability
  `celtic-mythology-content-system`): the canonical mapping
  from Leaving Certificate Geography (5 core units + 4
  elective units) + English A-Level Geography (7 topics) +
  Scottish CfE Higher Geography (5 areas) + Welsh WJEC
  Geography (3 themes) to the BIEP v3 `lessonObjective` table.

- **Interactive British Isles Map** (capability
  `celtic-mythology-content-system`): a marimo + Altair
  visualisation with 4 drill-down levels (subnation →
  subprovince → subcounty → settlement) covering 6 nations
  (Ireland / Scotland / Wales / England / Isle of Man /
  Cornwall).

- **GeoAI + DuckDB Spatial Analysis** (capability
  `celtic-mythology-content-system`): a `notebooks/_shared/
  geoai.py` helper that wraps ibis + DuckDB + DuckLake for
  OGC API Features queries, raster overlay, and 12 standard
  GeoAI operations (buffer / intersect / distance /
  centroid / area / simplify / union / dissolve / convex
  hull / voronoi / kriging / hotspot).

- **Celtic Mythology Agent** (capability
  `meaisinfhoghlaim-agent-frameworks`): new ADK agent at
  `agents/meaisinfhoghlaim/educational/celtic_mythology_agent.py`
  with 8 tools (extract_deity, extract_geis, extract_ogham_
  inscription, extract_irish_dynasty, extract_geography_
  outcome, query_settlement, render_british_isles_map,
  run_geoai_op).

- **Fibo + ComfyUI Asset Generation** (capability
  `celtic-asset-generation`): extension to enable Bria Fibo
  for mythology-themed asset generation; flip
  `local/image/fibo` from `false` → `true` in
  `deployment-choice.yaml`.

- **BAML SSOT for Celtic Mythology** (capability
  `centralized-schema-registry`): the 8 BAML functions live
  at `baml/celtic/mythology.baml` (NEW) and
  `baml/celtic/irish_history.baml` (NEW); Pydantic + Zod
  are codegen only; no duplicate hand-written classes.

## Out of scope

- The Ogham Celtic Stones Pipeline (separate change
  `2026-09-08-ogham-celtic-stones-pipeline-v1`).
- The Familiar Dynamic NFT System (separate change
  `2026-09-29-familiar-dynamic-nft-system-v1`).
- The 6 deferred BIEP v3 jurisdictions (issue #140).
- The English BIEP v3 milestones M3 + M4 (execute-only).
- Re-enabling Qwen DashScope API (issue #147).

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-08-15-meaisinfhoghlaim-to-machine-learning-rename-v1` (the agent rename change — this change adds 1 new agent and 4 new BAML files).

`Blocked by: 2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1` (the 4-stage rollout — the Geography curriculum binding extends the BIEP v3 lessonObjective surface).

`Blocked by (soft): 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1` (the MiniMax-only refactor — the Celtic Mythology Agent routes through the minimax LiteLLM gateway).

`Affected repos: cianfhoghlaim`
```

## Impact

- Affected specs:
  - NEW: `celtic-mythology-content-system` (9 ADDED Requirements)
  - `meaisinfhoghlaim-agent-frameworks` (2 ADDED Requirements)
  - `centralized-schema-registry` (1 ADDED Requirement)
  - `celtic-asset-generation` (1 ADDED Requirement)
- Affected code/config:
  - `baml/celtic/mythology.baml` (NEW; 8 BAML functions)
  - `baml/celtic/irish_history.baml` (NEW; 6 BAML functions)
  - `baml/celtic/geography_curriculum.baml` (NEW; 4 BAML functions)
  - `agents/meaisinfhoghlaim/educational/celtic_mythology_agent.py` (NEW)
  - `agents/meaisinfhoghlaim/educational/irish_history_agent.py` (NEW)
  - `agents/meaisinfhoghlaim/educational/educational_geography_agent.py` (NEW)
  - `cocoindex_flows/biep_parity/mythology_embedding.py` (NEW; R1-R4)
  - `orchestration/defs/2_materials/mythology_assets.py` (NEW)
  - `notebooks/30_mythology_dashboard.py` (NEW)
  - `notebooks/31_irish_history_timeline.py` (NEW)
  - `notebooks/32_british_isles_map.py` (NEW)
  - `notebooks/33_educational_geography.py` (NEW)
  - `notebooks/_shared/geoai.py` (NEW; 12 GeoAI ops)
  - `notebooks/_shared/geo.py` (NEW; ITM/OSGB36→WGS84 + OGC API client)
  - `notebooks/_shared/curriculum.py` (NEW; LC + A-Level + CfE + WJEC)
  - `deployment-choice.yaml` (1 line: `local/image/fibo: true`)
  - `bonneagar/stacks/fibo-server/` (NEW; 6-file GOLD_STANDARD)
- No secret values written to disk: all `infisical://dev-baile/...`
  refs hydrated by mise + Locket.

## Cross-references

- `openspec/specs/celtic-mythology-content-system/spec.md` —
  the capability spec (9 ADDED Requirements)
- `openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md` —
  2 ADDED Requirements (Celtic Mythology Agent + Geography Agent)
- `openspec/specs/centralized-schema-registry/spec.md` —
  1 ADDED Requirement (BAML SSOT for mythology + history)
- `openspec/specs/celtic-asset-generation/spec.md` —
  1 ADDED Requirement (Fibo enablement for mythology assets)
- `openspec/changes/2026-08-15-meaisinfhoghlaim-to-machine-learning-rename-v1/`
- `openspec/changes/2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1/`
- `docs/research/game/British Isles Mythology MMO Research.md`
- `docs/research/game/Web3 Gamified Education & Asset Generation.md`
- `.agents/skills/celtic-language-ai/SKILL.md`
- `.agents/skills/marimo/SKILL.md`