# oideachais-cognify-knowledge-graph Specification

## Purpose
TBD - created by archiving change 2026-07-14-oideachais-cognify-knowledge-graph-v1. Update Purpose after archive.
## Requirements
### Requirement: Phase 1 complete — 9 requirements all functional end-to-end

The system SHALL provide the 9 explicit deliverables for the
`cianfhoghlaim-cognify-knowledge-graph` Phase 1 v1. All 9
requirements of the parent spec SHALL be functional:

1. **R1 — 5-stage cross-stage knowledge graph** (the canonical
   K-12 → university curriculum pipeline).
2. **R2 — Site-analysis cognify** (the
   `cianfhoghlaim_site_analysis` Cognee dataset).
3. **R3 — Leabharlann cognify** (3 corpora: books + zotero +
   takeout).
4. **R4 — Cross-archive FalkorDB edges** (the
   leabharlann-internal 3 + the BIEP cross-archive 3).
5. **R5 — Cross-archive graph query API** (the FastAPI route at
   `GET /cross-archive-graph/{query}`).
6. **R6 — Daily cognify cron** (the `cognee_cron_sensor`
   Dagster asset firing at 02:00 UTC).
7. **R7 — BAML TypeBuilder dynamic schema**
   (`GenerateCognifySchema` + `ExecuteCognify({{@@dynamic}})`).
8. **R8 — DLT → Cognee → Memgraph multi-destination fan-out**
   (4 destinations in 1 pipeline run).
9. **R9 — Runtime evals + auto-retry loop** (the 6 deterministic
   runtime evals + BAML auto-retry pattern).

The Phase 1 deliverables are:

  **5 stage-specific cognify adapters** at
  `storage/cognify/cognee_integration/`:
  - `aistear_cognify.py` (Stage 1: Early Childhood 0-6; 4 themes;
    4 edge types)
  - `primary_cognify.py` (Stage 2: Primary 5-12; 6 curricular
    areas; 5 edge types)
  - `junior_cycle_cognify.py` (Stage 3: JC 12-15; 21 subjects;
    6 edge types including the `PREPARES_FOR→SC` bridge)
  - `senior_cycle_cognify.py` (Stage 4: SC/LC 15-18; 42 LC
    subjects; 7 edge types including `ASSESSED_BY→ExamQuestion`)
  - `university_cognify.py` (Stage 5: Tertiary 18+; 8 universities
    + 5 TUs + QQI L6-10 + CAO + SOLAS apprenticeships; 8 edge
    types)

  **3 leabharlann-aware cognify orchestrators** at
  `storage/cognify/rules/`:
  - `leabharlann_official_media.py` (wraps `official_media_cognify`
    + adds 2 leabharlann-aware edge types)
  - `leabharlann_authors_archive.py` (wraps `author_archive_cognify`
    + dispatches across the 6 corpora + adds 2 leabharlann-aware
    edge types)
  - `leabharlann_culture_heritage.py` (wraps `culture_cognify` +
    adds place/person slug normalisation + stage correlation +
    2 leabharlann-aware edge types)

  **3 BIEP cross-archive FalkorDB edge rules** in
  `storage/cognify/rules/cross_archive_biep_edges.py`:
  - Edge 1: `(:SCLearningOutcome) -[:REFERENCED_IN]-> (:LeabharlannDoc)`
    (BIEP → leabharlann, 60% token-overlap heuristic)
  - Edge 2: `(:LCSubject) -[:ANNOUNCED_BY]-> (:OfficialMediaSource)`
    (BIEP → official-media, exact subject_code ↔ topic_tags match)
  - Edge 3: `(:LeabharlannAuthor) -[:COREFERS_WITH]-> (:CultureHeritagePerson)`
    + `(:LeabharlannDoc) -[:ABOUT]-> (:CultureHeritagePlace)`
    (leabharlann → culture-heritage, slug-match heuristic)

  **1 marimo notebook for the cognify visualisation** at
  `notebooks/10_cognify/01_knowledge_graph.py`
  (~429 LOC; 9-panel dashboard with 60-node synthetic KG fallback).

#### Scenario: All 5 stage cognify adapters AST-parse

- **GIVEN** the 5 stage cognify adapters exist at
  `storage/cognify/cognee_integration/{aistear,primary,junior_cycle,senior_cycle,university}_cognify.py`
- **WHEN** the user runs `ast.parse(open(f).read())` for each
- **THEN** all 5 files parse without SyntaxError

#### Scenario: All 3 leabharlann cognify rules AST-parse

- **GIVEN** the 3 leabharlann cognify orchestrators exist at
  `storage/cognify/rules/leabharlann_{official_media,authors_archive,culture_heritage}.py`
- **WHEN** the user runs `ast.parse(open(f).read())` for each
- **THEN** all 3 files parse without SyntaxError

#### Scenario: The cross-archive FalkorDB rules file AST-parses

- **GIVEN** the cross-archive rules file exists at
  `storage/cognify/rules/cross_archive_biep_edges.py`
- **WHEN** the user runs `ast.parse(open(f).read())`
- **THEN** the file parses without SyntaxError
- **AND** the file exposes the 3 public entry-point functions
  `build_biep_references_leabharlann_query()`,
  `build_lc_subject_announced_by_query()`,
  `build_leabharlann_corefers_culture_query()` +
  `build_leabharlann_about_culture_place_query()`

#### Scenario: The marimo notebook AST-parses

- **GIVEN** the marimo notebook exists at
  `notebooks/10_cognify/01_knowledge_graph.py`
- **WHEN** the user runs `ast.parse(open(f).read())`
- **THEN** the file parses without SyntaxError

#### Scenario: CLI discovery finds the new notebook

- **GIVEN** the marimo notebook exists and
  `notebooks/cli.py` has been updated to include
  `10_cognify` in its `GROUPS` tuple
- **WHEN** the user runs
  `uv run cianfhoghlaim-marimo list 10_cognify`
- **THEN** the output includes `10_cognify/01_knowledge_graph.py`
- **AND** the count line reads `1 notebooks in 10_cognify/`

#### Scenario: Existing 15 notebooks still AST-parse

- **GIVEN** the 15 pre-existing notebooks at
  `notebooks/{03_leaving_cert,06_observability,07_educational_stages,09_official_media,13_baml_cocoindex_tutorial}/`
- **WHEN** the user runs `ast.parse(open(f).read())` for each
- **THEN** all 15 files still parse without SyntaxError
  (no regression introduced by this change)

#### Scenario: Cognify spec coverage summary surfaces all 9 requirements

- **GIVEN** the marimo notebook renders
- **WHEN** the user opens the dashboard
- **THEN** the bottom coverage panel SHALL display all 9
  requirements with ✅ markers:
  - R1 — 5-stage cross-stage KG (8 cross-stage edges)
  - R2 — Site-analysis cognify (separate Cognee dataset)
  - R3 — Leabharlann cognify (3 corpora)
  - R4 — Cross-archive FalkorDB edges (3 BIEP cross-archive
    + 3 leabharlann-internal)
  - R5 — Cross-archive graph query API
  - R6 — Daily cognify cron (02:00 UTC)
  - R7 — BAML TypeBuilder dynamic schema
  - R8 — DLT → Cognee → Memgraph fan-out
  - R9 — Runtime evals + auto-retry loop

### Requirement: Leabharlann cognify *(updated from "3 corpora" to "6 sub-corpora")*

The system SHALL cognify the **6 leabharlann sub-corpora**
(`aigne/`, `gaeilge/`, `gemini_deep_research/`, `mata/`,
`ollscoil_na_gaillimhe/`, `zotero/` — totaling 225 documents on disk
per the canonical `cianfhoghlaim-leabharlann` spec) into the
corresponding Cognee datasets. Each sub-corpora gets a dedicated
cognify pass + Dagster asset.

#### Scenario: Books cognify (covers `gaeilge/` + `aigne/`)

- **GIVEN** the `leabharlann_books` dlt source has materialised
- **WHEN** the `cognify_leabharlann_books` Dagster asset runs
- **THEN** the rows from both `gaeilge/` (57 PDFs + 2 MDs + 37 PNG
      previews) and `aigne/` (7 PDFs) subdirs are added to the
      Cognee dataset `leabharlann_books` and `cognify()` is called

#### Scenario: Zotero cognify (covers `zotero/`)

- **GIVEN** the `leabharlann_zotero` dlt source has materialised
- **WHEN** the `cognify_leabharlann_zotero` Dagster asset runs
- **THEN** the rows from the `zotero/` subdir (294 MB, 117 PDFs in
      real Zotero storage format) are added to the Cognee dataset
      `leabharlann_zotero` and `cognify()` is called

#### Scenario: Takeout cognify (covers `gemini_deep_research/`)

- **GIVEN** the `leabharlann_takeout_v1` dlt source has materialised
- **WHEN** the `cognify_leabharlann_takeout` Dagster asset runs
- **THEN** the rows from the `gemini_deep_research/` subdir (79 MB,
      Gemini deep research PDFs) are added to the Cognee dataset
      `leabharlann_takeout` and `cognify()` is called

#### Scenario: UoG artefacts cognify (covers `ollscoil_na_gaillimhe/`)

- **GIVEN** the `leabharlann_university_of_galway` dlt source has
      materialised
- **WHEN** the `cognify_leabharlann_uog` Dagster asset runs
- **THEN** the rows from the `ollscoil_na_gaillimhe/` subdir (2.2 GB,
      5 sub-subdirs: education, irish, mata, past,
      software_development — the UoG artefacts) are added to the
      Cognee dataset `leabharlann_uog` and `cognify()` is called

#### Scenario: Mata cognify (covers `mata/`)

- **GIVEN** the `leabharlann_mata` dlt source has materialised
- **WHEN** the `cognify_leabharlann_mata` Dagster asset runs
- **THEN** the rows from the `mata/` subdir (47 documents) are added
      to the Cognee dataset `leabharlann_mata` and `cognify()` is
      called

#### Scenario: All 6 sub-corpora covered

- **WHEN** all 6 cognify Dagster assets have materialised
- **THEN** the Cognee datasets total 6 (`leabharlann_books` +
      `leabharlann_zotero` + `leabharlann_takeout` +
      `leabharlann_uog` + `leabharlann_mata` + `leabharlann_aigne`),
      one per sub-corpora
- **AND** the total document count across the 6 datasets is ≥ 225
      (matches the on-disk leabharlann corpus count per the canonical
      leabharlann spec)

### Requirement: Cross-archive edges (FalkorDB) *(updated ownership boundary)*

The system SHALL populate FalkorDB with deterministic cross-archive
edges between the **6 leabharlann sub-corpora** (aigne + gaeilge +
gemini_deep_research + mata + ollscoil_na_gaillimhe + zotero) AND
the BIEP cross-archive edges.

**Ownership boundary** (declared by this consolidation change):

- The **leabharlann change**
  (`openspec/changes/2026-07-15-cianfhoghlaim-leabharlann-v1/`) owns
  the 4 leabharlann-X cross-archive rules at
  `storage/cognify/rules/`:
  - `leabharlann_cross_archive.py` (the 3 leabharlann-internal edges:
    CITES-arxiv + TEACHES-title + CITES-URL)
  - `leabharlann_official_media.py` (TakeoutDoc-CITES-GeminiReport)
  - `leabharlann_culture_heritage.py` (the 2 leabharlann →
    culture-heritage edges: `LeabharlannAuthor-COREFERS_WITH-CultureHeritagePerson`
    + `LeabharlannDoc-ABOUT-CultureHeritagePlace`)
  - `leabharlann_authors_archive.py`

- The **cognify change**
  (`openspec/changes/2026-07-14-cianfhoghlaim-cognify-knowledge-graph-v1/`)
  owns the 2 BIEP-X cross-archive rules:
  - `cross_archive_biep_edges.py` (the 2 BIEP edges:
    `SCLearningOutcome-REFERENCED_IN-LeabharlannDoc` +
    `LCSubject-ANNOUNCED_BY-OfficialMediaSource`) — **the
    leabharlann → culture-heritage edges (formerly the 3rd edge in
    this file) are owned by the leabharlann change via
    `leabharlann_culture_heritage.py`**; the actual code
    consolidation (removing the duplicate from
    `cross_archive_biep_edges.py`) is a follow-up task deferred to
    a separate change
  - `university_cross_archive.py` (UoGArtifact-MATCHES-CourseDescriptor)

#### Scenario: arxiv_id match creates CITES edge (leabharlann-internal)

- **GIVEN** a Zotero paper with `arxiv_id=2504.02890` and a Gemini deep
      research report that cites
      `https://arxiv.org/abs/2504.02890`
- **WHEN** the `cross_archive_edges` Dagster asset runs
- **THEN** a `(:GeminiReport)-[:CITES {arxiv_id: "2504.02890"}]->(:ZoteroPaper)`
      edge is created in FalkorDB (owned by
      `leabharlann_cross_archive.py`)

#### Scenario: Module title match creates TEACHES edge (leabharlann-internal)

- **GIVEN** a UoG artefact with `module_title="Handwritten Text
      Recognition for Irish"` and a Zotero paper with `title="Handwritten
      Text Recognition (HTR) for Irish-Langu"`
- **WHEN** the `cross_archive_edges` Dagster asset runs
- **THEN** a `(:UoGArtifact)-[:TEACHES {match_kind: "title"}]->(:ZoteroPaper)`
      edge is created in FalkorDB (60% token-overlap heuristic,
      owned by `leabharlann_cross_archive.py`)

#### Scenario: URL match creates CITES edge (leabharlann-internal)

- **GIVEN** a Takeout document whose body contains
      `https://gemini-report.example/abc` and a Gemini report whose
      `cited_urls` includes the same URL
- **WHEN** the `cross_archive_edges` Dagster asset runs
- **THEN** a `(:TakeoutDoc)-[:CITES {url: "..."}]->(:GeminiReport)`
      edge is created in FalkorDB (owned by
      `leabharlann_official_media.py`)

#### Scenario: leabharlann → culture-heritage edges (owned by leabharlann change)

- **GIVEN** a LeabharlannAuthor row with `surname_forename_slug`
      matching a culture-heritage claim's `_person_key` slug
- **WHEN** the `cognify_leabharlann_culture_heritage_rows` function
      runs (owned by the leabharlann change at
      `storage/cognify/rules/leabharlann_culture_heritage.py`)
- **THEN** a `(:LeabharlannAuthor)-[:COREFERS_WITH {match_kind: "surname_forename_slug"}]->(:CultureHeritagePerson)`
      edge is created in FalkorDB
- **AND** a `(:LeabharlannDoc)-[:ABOUT {match_kind: "place_key"}]->(:CultureHeritagePlace)`
      edge is created in FalkorDB for any LeabharlannDoc whose
      `place_key` matches a culture-heritage place's `_place_key`
      slug

#### Scenario: BIEP → leabharlann edge (owned by cognify change)

- **GIVEN** a `SCLearningOutcome` whose `key_phrases` overlap with a
      `LeabharlannDoc`'s `title` / `key_phrases` by 60%+
- **WHEN** the `build_biep_references_leabharlann_query` function
      runs (owned by the cognify change at
      `storage/cognify/rules/cross_archive_biep_edges.py`)
- **THEN** a `(:SCLearningOutcome)-[:REFERENCED_IN]->(:LeabharlannDoc)`
      edge is created in FalkorDB

#### Scenario: BIEP → official-media edge (owned by cognify change)

- **GIVEN** a `LCSubject` whose `subject_code` matches an
      `OfficialMediaSource`'s `topic_tags` exactly
- **WHEN** the `build_lc_subject_announced_by_query` function runs
      (owned by `cross_archive_biep_edges.py`)
- **THEN** a `(:LCSubject)-[:ANNOUNCED_BY]->(:OfficialMediaSource)`
      edge is created in FalkorDB

### Requirement: PlanetScale Postgres Centralisation (cianfhoghlaim-cognify-knowledge-graph)

The system SHALL move the 5-stage cross-stage cognify + the 3 leabharlann cognify datasets' Postgres backend to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (row 7: cognee).

#### Scenario: Cognify datasets are reachable from PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** the cognify CLI runs
- **THEN** the cognify datasets table SHALL be in the PlanetScale PG branch
- **AND** the FalkorDB + Graphiti backends SHALL remain unchanged
- **AND** the 3 leabharlann cognify datasets (`cianfhoghlaim_leabharlann`, `cianfhoghlaim_official_media`, `cianfhoghlaim_academic_history`) SHALL be queryable via the same REST endpoints

