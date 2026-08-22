# celtic-language-pipeline Specification

## Purpose
The Celtic-language pipeline surface covers Irish + Welsh + Scottish + Manx + Cornish + Breton across the Cianfhoghlaim monorepo. It defines 9 invariants: the canonical Gaois + Celtic language source paths (Logainm, Téarma, Ainm, Gaois, Dúchas, Canúint), the 6-language support matrix, the British Isles education connection (cymraeg for Wales LC, gaidhlig for Scotland LC, gaelg for Isle of Man, kernewek for Cornwall, brezhoneg for Brittany cross-border), the per-language BAML extraction templates, the BAML ensemble fallback chain, the canonical cross-corpus knowledge graph edges, the per-language cognitive layer rules, the per-language Cognee cluster naming, and the per-language marimo notebook convention.

## Requirements
### Requirement: Canonical Gaois + Celtic language pipeline path contract

The system MUST place every Gaois + Celtic language source at one of the
7 canonical paths under `dlt/language/<group>/`:

```text
dlt/language/gaois/                # Gaois APIs (Téarma + Logainm + Ainm)
dlt/language/duchas/                # Dúchas National Folklore Collection
dlt/language/heritage/              # Heritage + Hidden Heritages
dlt/language/canuint/               # Canuint Irish Pronunciation (with word alignment)
dlt/language/ud_celtic/             # Universal Dependencies Celtic Treebanks
dlt/language/local_documents/       # Local documents by subject
dlt/language/celtic_curriculum/     # Celtic curriculum + mythology + grammar + morphology
```

Each source MUST declare its `source_id` as
`celtic.<group>.<source_slug>` and land in the canonical DuckLake
namespace `cianfhoghlaim.celtic.<group>.<table>` (LanceDB companion table
at `cianfhoghlaim.language.<group>_chunks`).

#### Scenario: A new Gaois Téarma source obeys the contract

- **WHEN** a developer adds a new Gaois Téarma extraction source
- **THEN** the DLT source MUST live at `dlt/language/gaois/tearma.py`
- **AND** its `source_id` MUST be `celtic.gaois.tearma`
- **AND** the DuckLake table MUST be `cianfhoghlaim.celtic.gaois.tearma_terms`
- **AND** the LanceDB companion MUST be `cianfhoghlaim.language.gaois_chunks`

### Requirement: 7 source groups ship the full 5-layer pipeline

The system MUST provide, for each of the 7 source groups, all 5 pipeline
layers (DLT → BAML → CocoIndex v1 → MotherDuck Dive → marimo notebook):

| # | Group | DLT path | BAML fns ≥ | CocoIndex App | MotherDuck Dive | Marimo |
|:--|:--|:--|--:|:--|:--|:--|
| 1 | Gaois APIs | `dlt/language/gaois/` | 6 | `cocoindex/gaois_embedding.py` | `gaois_terminology_dive` | `01_gaois_terminology_explorer.py` |
| 2 | Dúchas | `dlt/language/duchas/` | 3 | `cocoindex/duchas_embedding.py` (with bboxes) | `duchas_folklore_dive` | `02_duchas_folklore_with_bboxes.py` |
| 3 | Heritage | `dlt/language/heritage/` | 1 | `cocoindex/heritage_embedding.py` | `heritage_sites_dive` | `03_heritage_sites_map.py` |
| 4 | Canuint | `dlt/language/canuint/` | 1 | `cocoindex/canuint_embedding.py` (audio + text) | `canuint_dialect_dive` | `04_canuint_dialect_player.py` |
| 5 | UD Celtic | `dlt/language/ud_celtic/` | 1 | `cocoindex/ud_celtic_embedding.py` | `ud_celtic_dive` | `05_ud_celtic_treebank_viewer.py` |
| 6 | Local documents | `dlt/language/local_documents/` | 1 | `cocoindex/local_documents_embedding.py` | `local_documents_dive` | `06_local_documents_subject_viewer.py` |
| 7 | Celtic curriculum | `dlt/language/celtic_curriculum/` | 4 | `cocoindex/celtic_curriculum_embedding.py` | `celtic_curriculum_dive` | `07_celtic_curriculum_browser.py` |

Total: 21 new files in the 5-layer pipeline (7 × 3 layers) + 7 MotherDuck
Dives + 7 marimo notebooks = **41 new files**.

#### Scenario: Dúchas gets the bbox alignment

- **WHEN** a developer adds the Dúchas CocoIndex v1 App
- **THEN** the App MUST mount BOTH `cianfhoghlaim.language.duchas_chunks` AND
  `cianfhoghlaim.language.duchas_bboxes` (the 5-level bbox child table)
- **AND** each bbox row MUST carry `page_id` + `region_bbox` + `sentence_bbox`
  + `word_bbox` + `letter_bbox` (with NULL fallbacks for unavailable levels)
- **AND** the MotherDuck Dive MUST aggregate to page-level summaries
  (NOT 74M row word-level data)

### Requirement: BAML extraction per group

The system MUST provide a BAML extraction function for each source group,
routed through the canonical OCR/VLM registry
(`meaisinfhoghlaim.models.registry`):

| Group | Primary BAML function | LlamaSwap routing |
|:--|:--|:--|
| Gaois APIs | `ExtractTearmaTerm` + `ExtractLogainmPlace` + `ExtractAinmBiography` | `uccix-mistral-24b` (Irish) / `gemma-4-26B-A4B` (English) |
| Dúchas | `ExtractDuchasManuscript` + `ExtractDuchasImageBoundingBox` + `ExtractDuchasTranscription` | `molmo2-8b` (diagram pointing) + `dots-ocr` (layout) |
| Heritage | `ExtractHeritageSite` | `gemma-4-26B-A4B` |
| Canuint | `ExtractCanuintWordAlignment` | `qwen3-vl-8b` (audio + text multimodal) |
| UD Celtic | `ExtractUDToken` | `uccix-mistral-24b` (Irish) / `gemma-4-26B-A4B` (Celtic) |
| Local documents | `ExtractLocalDocumentMetadata` | `qwen3-vl-8b` (OCR) |
| Celtic curriculum | `ExtractCelticCurriculum` + `ExtractCelticGrammar` + `ExtractCelticMorphology` | `uccix-mistral-24b` (Irish) / `gemma-4-26B-A4B` (Welsh/Scottish/Breton) |

#### Scenario: Irish-language routing uses UCCIX

- **WHEN** a BAML extraction function is invoked with `language="ga"`
- **THEN** the dispatcher MUST route to `uccix-mistral-24b` (the canonical
  modern Irish-language model per `meaisinfhoghlaim.models.registry`)
- **AND** for non-Irish Celtic (Scottish/Welsh/Breton/Manx) the dispatcher
  MUST route to `gemma-4-26B-A4B` (the multilingual MoE with 6+ Celtic langs)

### Requirement: Re-activate the 2 archived BAML files

The system MUST re-activate `baml/celtic/grammar_patterns.baml` +
`baml/celtic/morphology.baml` (which were archived 2026-06-24 with no
consumer) by:

- Moving both files back from `baml/celtic/_archive/` to `baml/celtic/`
- Removing the ARCHIVED header from the top
- Adding the canonical consumer agents:
  - `meaisinfhoghlaim/agents/celtic_grammar.py` (calls `ExtractCelticGrammar`)
  - `meaisinfhoghlaim/agents/celtic_morphology.py` (calls `ExtractCelticMorphology`)

#### Scenario: Grammar extraction agent is wired

- **WHEN** a developer imports `meaisinfhoghlaim.agents.celtic_grammar`
- **THEN** the module MUST expose `ExtractCelticGrammar` as a callable
- **AND** the agent MUST dispatch through the canonical LlamaSwap router

### Requirement: CocoIndex v1 R1-R4 conformance

Every CocoIndex App in the 7 source groups MUST conform to the R1-R4
contract:

- **R1**: Imports `from ._lifespan import shared_lifespan`
- **R2**: Uses `BAAI/bge-m3` embedder (1024-d)
- **R3**: Wraps every flow as `@coco.fn(memo=True, deps=...)`
- **R4**: Mounts each LanceDB table via `mount_table_target(...)` with
  `conformance_required=True`

#### Scenario: All 7 Apps pass R1-R4 conformance

- **WHEN** the `cocoindex_v1_conformance` App runs against the 7 new Apps
- **THEN** every App MUST satisfy R1+R2+R3+R4 (verified by
  `dg check yaml` + the conformance test harness)

### Requirement: Dagster 5-layer asset graph

Each of the 7 source groups MUST have a complete 5-layer Dagster asset
graph following the `CelticIngestionComponent` + `CelticModelLifecycleComponent`
pattern (per the Irish education pipeline):

```
orchestration/defs/1_ingestion/language/<group>/defs.yaml
orchestration/defs/2_materials/baml_extraction/language/<group>/_assets.py
orchestration/defs/3_model_lifecycle/cocoindex_v1/<group>_embedding/defs.yaml
```

#### Scenario: Dúchas 5-layer pipeline runs end-to-end

- **WHEN** `dg launch --job duchas_full_pipeline` is invoked
- **THEN** the L1 ingestion asset MUST run `duchas_source()` and write to
  DuckLake `cianfhoghlaim.celtic.duchas.manuscripts`
- **AND** the L2 BAML asset MUST run `ExtractDuchasManuscript` over the
  ingested rows and write to DuckLake `cianfhoghlaim.celtic.duchas.bboxes`
- **AND** the L3 CocoIndex App MUST mount
  `cianfhoghlaim.language.duchas_chunks` and `cianfhoghlaim.language.duchas_bboxes`
  in LanceDB
- **AND** the MotherDuck Dive MUST show the new rows in the page-level summary

### Requirement: LlamaSwap + LiteLLM routing shared module

The system MUST provide a shared routing module
`meaisinfhoghlaim/models/routing.py` that dispatches per (source_group,
language) pair to the correct LiteLLM client + model:

```python
# Per-language + per-source routing table
ROUTING_TABLE: dict[tuple[str, str], RoutingConfig] = {
    ("gaois", "ga"): RoutingConfig(client="LlamaSwap", model="uccix-mistral-24b"),
    ("gaois", "en"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B"),
    ("duchas", "*"): RoutingConfig(client="LlamaSwap", model="molmo2-8b"),
    ("canuint", "*"): RoutingConfig(client="LlamaSwap", model="qwen3-vl-8b"),
    ("celtic_curriculum", "ga"): RoutingConfig(client="LlamaSwap", model="uccix-mistral-24b"),
    ("celtic_curriculum", "cy"): RoutingConfig(client="LlamaSwap", model="gemma-4-26B-A4B"),
    # ... etc
}
```

#### Scenario: UCCIX is the default for Irish-language routing

- **WHEN** a CocoIndex App calls `route_language("duchas", "ga")`
- **THEN** the dispatcher MUST return `(client="LlamaSwap", model="uccix-mistral-24b")`
- **AND** the dispatcher MUST fall back to `gemma-4-26B-A4B` if UCCIX is unavailable

### Requirement: DuckLake + S3 destination writes

The system MUST write the 7 source groups' output to the canonical
DuckLake + S3 destination, matching the Irish education pipeline pattern:

- DLT destination: `@dlt.destination(ducklake, credentials=lakehouse_creds)`
- S3 staging: `s3://garage/cianfhoghlaim/language/<group>/<partition>/<file>.jsonl`
- MotherDuck attach string: `md:oideachais` (per `nb_utils.LAKEHOUSE_DUCKDB`)

#### Scenario: Gaois terminology writes to S3 + DuckLake

- **WHEN** the Gaois Téarma DLT source runs
- **THEN** raw rows MUST be staged at `s3://garage/cianfhoghlaim/language/gaois/tearma/<partition>.jsonl`
- **AND** the canonical DuckLake table MUST be
  `cianfhoghlaim.celtic.gaois.tearma_terms`
- **AND** the marimo notebook MUST read from `md:oideachais` via
  `nb_utils.connect_biep_lakehouse()`

### Requirement: Marimo notebooks sample each source type

The system MUST provide 7 marimo notebooks (one per source group) under
`notebooks/16_celtic_language/` that:

- Connect to `md:oideachais` via `nb_utils.connect_biep_lakehouse()`
- Use Ibis-on-DuckDB for queries
- Render Altair 5-panel layouts
- Have a CLI dual-mode (via `nb_utils.cl_argument_parser()` + `nb_utils.run_as_script()`)
- Carry an openspec cross-reference footer

#### Scenario: Dúchas notebook visualises bbox overlays

- **WHEN** `marimo edit 02_duchas_folklore_with_bboxes.py` is opened
- **THEN** the notebook MUST render the manuscript page image with Altair
  bbox overlays at each of the 5 levels (page → region → sentence → word → letter)
- **AND** the notebook MUST provide hover-tooltips showing the Irish
  transcript + English translation per bbox
- **AND** the notebook MUST support CLI invocation:
  `uv run 02_duchas_folklore_with_bboxes.py --collection cbes --page-id 4606492`

