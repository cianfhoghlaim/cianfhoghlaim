## ADDED Requirements

### Requirement: Phase 1 complete — 9 requirements all functional end-to-end

The system SHALL provide the 9 explicit deliverables for the
`oideachais-cognify-knowledge-graph` Phase 1 v1. All 9
requirements of the parent spec SHALL be functional:

1. **R1 — 5-stage cross-stage knowledge graph** (the canonical
   K-12 → university curriculum pipeline).
2. **R2 — Site-analysis cognify** (the
   `oideachais_site_analysis` Cognee dataset).
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