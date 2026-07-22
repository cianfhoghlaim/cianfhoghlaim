# `cianfhoghlaim-cognify-knowledge-graph` MODIFIED — Update "3 corpora" claim to "6 sub-corpora" + declare leabharlann → culture-heritage edge ownership

> Two updates against the canonical
> `openspec/specs/cianfhoghlaim-cognify-knowledge-graph/spec.md`:
>
> 1. The "Leabharlann cognify" requirement (line 61) and the
>    "Cross-archive edges (FalkorDB)" requirement (line 88) reference
>    "3 leabharlann corpora" — this is stale. The canonical leabharlann
>    spec (`openspec/specs/cianfhoghlaim-leabharlann/spec.md` line 360)
>    exposes the corpus at
>    `leabharlann/{aigne,gaeilge,gemini_deep_research,mata,ollscoil_na_gaillimhe,zotero}/`
>    — that's **6 sub-corpora × 225 documents on disk** (31 + 57 + 54
>    + 47 + 24 + 12).
>
> 2. The cross-archive
>    `(:LeabharlannAuthor)-[:COREFERS_WITH]->(:CultureHeritagePerson)` +
>    `(:LeabharlannDoc)-[:ABOUT]->(:CultureHeritagePlace)` edges are
>    shipped by 2 different files (a duplicate). The ownership
>    boundary is now declared: the leabharlann change owns the 4
>    leabharlann-X rules (incl. `leabharlann_culture_heritage.py`);
>    the cognify change owns the 2 BIEP-X rules
>    (`cross_archive_biep_edges.py` + `university_cross_archive.py`)
>    minus the leabharlann → culture-heritage edges.

## MODIFIED Requirements

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

## Cross-references *(unchanged — pre-existing)*

- [`cianfhoghlaim/cognee_integration/`](../../cianfhoghlaim/cognee_integration/) (the 3 cognify adapters)
- [`cianfhoghlaim/cognify_rules/`](../../cianfhoghlaim/cognify_rules/) (the cross-archive rules)
- [`cianfhoghlaim/graph/`](../../cianfhoghlaim/graph/) (FalkorDB + Memgraph clients)
- [`web/hono-api/src/routes/cross_archive_graph.py`](../../web/hono-api/src/routes/cross_archive_graph.py) (the API route)
- [`.agents/skills/cognee/SKILL.md`](../../.agents/skills/cognee/SKILL.md)
- [`.agents/skills/falkordb/SKILL.md`](../../.agents/skills/falkordb/SKILL.md)
- [`openspec/specs/cianfhoghlaim-leabharlann/spec.md`](cianfhoghlaim-leabharlann/spec.md) (the upstream leabharlann pipeline — the source of truth for the 6 sub-corpora + 225 documents)

## Migrated from (2026-07-06) *(unchanged)*

- `author-archive-cross-corpus-kg` — the `cianfhoghlaim_author_archive` single Cognee dataset pattern was merged into the 5 leabharlann cognify datasets + 3 cross-archive edge types