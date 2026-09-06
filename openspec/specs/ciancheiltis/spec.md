# ciancheiltis Specification

## Purpose

`ciancheiltis` (Irish *[cian]* + *[Cheiltis]* — "long-distance
Celtic-ness") is a tangential branch of `cianfhoghlaim` dedicated to
**bilingual government publications required by law** in the Celtic-language
jurisdictions of the British Isles and at the EU level (where Irish is a
treaty language). The pipeline crawls, ingests, extracts, aligns and
surfaces Welsh-, Irish-, Scottish Gaelic- and Manx-language content
published by national and subnational authorities, statutory language
bodies, terminology databases, and the courts.

It is distinct from `celtic-language-pipeline` (curated Celtic-language
corpora — Gaois, Dúchas, Heritage, Canuint, UD, Local documents, Celtic
curriculum) and from `british-isles-education-pipeline` (Leaving Cert +
A-Level + GCSE + National 5 + WJEC + CCEA education content).

## Requirements

### Requirement: 6-phase language-pair staging
The system MUST organise the ciancheiltis work as six staged phases, one
per language pair, in this order:

| # | Jurisdiction | Language pair | Sister bodies |
|---|---|---|---|
| 1 | 🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales | `en-cy` | Welsh Language Commissioner, Coleg Cymraeg Cenedlaethol, Senedd Cymru, Hwb |
| 2 | 🇮🇪 Republic of Ireland | `en-ga` | Foras na Gaeilge, Gaois, Téarma, Teanglann |
| 3 | 🇬🇧 Northern Ireland | `en-ga` | Comhairle na Gaelscolaíochta (CnaG), Education Authority NI |
| 4 | 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland | `en-gd` | Bòrd na Gàidhlig, Stòrlann Nàiseanta, DASG, Sabhal Mòr Ostaig |
| 5 | 🇮🇲 Isle of Man | `en-gv` | Culture Vannin, Learn Manx, Bunscoill Ghaelgagh |
| 6 | 🇪🇺 EU (Irish as treaty language) | `en-ga` | EUR-Lex `GA/TXT`, europarl.europa.eu `..._GA.html`, IATE, TED |

Each phase MUST inherit the source-ground-truth pattern of the previous
phase (the en-cy Phase 1 ships first because it has the largest statutory
footprint and matches the language of the umbrella project's Welsh-medium
learning surface).

#### Scenario: Wales becomes Phase 1
- **WHEN** the user runs `mise run ciancheiltis:phase -- 1`
- **THEN** the system MUST run the en-cy DLT sources
- **AND** MUST seed `lancedb://md:cianfhoghlaim/ciancheiltis/en_cy` LanceDB table
- **AND** MUST trigger the en-cy `ExtractCiancheiltisBilingualPage` BAML function
- **AND** MUST run the RAGAS ≥ 0.70 asset check before promoting to next phase

### Requirement: 10-theme taxonomy
The system MUST classify every ingested bilingual document by exactly one
of ten themes:

| # | Theme | Example |
|---|---|---|
| T1 | Legislation | WSI, UKSI, uksro, ISB Acts |
| T2 | Policy / consultations | White papers, Green papers, Senedd/NI Executive consultations |
| T3 | Education | Hwb CfW, CfE, NCCA, CCEA, DESC, language-medium portals |
| T4 | Healthcare | NHS Wales, NHS Scotland, HSE (Ireland), patient-info PDFs |
| T5 | Language bodies | Welsh Language Commissioner, Bòrd na Gàidhlig, Foras na Gaeilge, Culture Vannin, CnaG |
| T6 | Terminology | Termau Cymru, Téarma, Teanglann, IATE |
| T7 | Courts & Tribunals | HMCTS Welsh, NI Courts Service, Scottish Courts, Courts Service Ireland |
| T8 | Local government | Welsh LAs, NI councils, Scottish councils, Irish councils, IoM councils |
| T9 | Public broadcasting & culture | S4C, BBC ALBA, TG4, RTÉ Raidió na Gaeltachta |
| T10 | Statistics & public records | Bilingual census tables, NISRA Gaeilge, NRS Scottish Gaelic |

Every DLT source MUST declare its `theme` (one of T1–T10) and the schema
column for the classification is `theme_code`.

#### Scenario: All 10 themes ship in en-cy Phase 1
- **WHEN** the en-cy Phase 1 pipeline runs
- **THEN** at least one DLT source MUST exist per T1–T10 theme
- **AND** the MotherDuck Dive MUST show a row count per theme

### Requirement: Canonical file layout under `dlt_sources/ciancheiltis/`
The system MUST place each phase under `dlt_sources/ciancheiltis/<phase>/`
and shared helpers under `dlt_sources/ciancheiltis/_shared/`. Each phase
directory MUST contain one DLT source per theme that has bilingual
content for the phase's language pair.

```text
dlt_sources/ciancheiltis/
├── clarin_uk/                    # cross-domain language corpora (PR0.1)
├── en_cy/                        # Phase 1 — Wales (en-cy)
├── en_ga_roi/                    # Phase 2 — Republic of Ireland (en-ga)
├── en_ga_ni/                     # Phase 3 — Northern Ireland (en-ga)
├── en_gd/                        # Phase 4 — Scotland (en-gd)
├── en_gv/                        # Phase 5 — Isle of Man (en-gv)
├── en_ga_eu/                     # Phase 6 — EU (en-ga)
└── _shared/                      # language_detector, opaque_url_scanner, gov_wales_waf_bypass
```

#### Scenario: A new Phase source obeys the layout
- **WHEN** a developer adds a Phase 4 (en-gd) education source
- **THEN** the source MUST live at `dlt_sources/ciancheiltis/en_gd/education.py`
- **AND** MUST register `theme_code = "T3"` (Education)
- **AND** MUST declare `language_pair = "en-gd"` in its `@dlt.source` decorator

### Requirement: Content-based language detection
The system MUST detect the language of a page by **content** (a
lingua-py heuristic on the first 5 KB of the body) and MUST **NOT**
trust any `language` metadata tag. This is required because
`legislation.gov.uk/uksi/2007/1484/made` (UK Statutory Instrument
2007 No. 1484 — *The Citizenship Oath and Pledge (Welsh Language) Order
2007*) ships with `metadata["language"] = "eng"` while the body is
predominantly Welsh.

The `dlt_sources/ciancheiltis/_shared/language_detector.py` module is
the single canonical implementation.

#### Scenario: SI 2007/1484 is correctly detected as Welsh-bilingual
- **WHEN** the en-cy Phase 1 source fetches
  `https://www.legislation.gov.uk/uksi/2007/1484/made`
- **THEN** the language detector MUST classify the body as
  predominantly `cy` (Welsh) — confirmed by `Llw teyrngarwch`,
  `Cadarnhad teyrngarwch`, and `Adduned` markers in the second-half of
  the page
- **AND** MUST emit a `metadata_language_mismatch` warning flag

### Requirement: Opaque-URL scanner
The system MUST scan the URL surface for **opaque numeric / slug-only
slugs** that hide their language pair (`/uksi/2007/1484/made`,
`/wsi/2007/2044/made`, etc.) and MUST seed these into the per-phase
discovery checklist. The
`dlt_sources/ciancheiltis/_shared/opaque_url_scanner.py` module is the
single canonical implementation.

#### Scenario: Welsh SI enumeration discovers opaque slugs
- **WHEN** the en-cy Phase 1 opaque-URL scanner runs
- **THEN** it MUST discover at least one canonical Welsh-language SIs
  via `firecrawl_map` over `https://www.legislation.gov.uk/wsi`
- **AND** the discovered slugs MUST land in
  `stedding/discovery/ciancheiltis_en_cy_wsi_seeds.jsonl`

### Requirement: gov.wales WAF bypass
The system MUST handle the `gov.wales` CloudFront + AWS WAF + CAPTCHA
surface (confirmed broken for plain HTTP per
`openspec/research/2026-06-28-browserbase-program-2/SHARED_DISCOVERY_LOG.md:492`)
by falling back to (a) `firecrawl_interact` with profile-aware browser
session and (b) the Hwb mirror at `hwb.gov.wales`. The
`dlt_sources/ciancheiltis/_shared/gov_wales_waf_bypass.py` module is the
single canonical implementation.

#### Scenario: gov.wales WAF fallback engages
- **WHEN** the en-cy Phase 1 source requests a `gov.wales/...` page and
  receives 403 or a CAPTCHA challenge
- **THEN** the system MUST first try `firecrawl_interact` with the
  gov_wales_waf_bypass profile
- **AND** on failure MUST fall back to the `hwb.gov.wales` mirror
- **AND** MUST log the WAF event to `stedding/waf_events/gov_wales.jsonl`

### Requirement: CLARIN-UK + cross-domain linguistic bridges
The system MUST integrate the CLARIN-UK Celtic resource family
(`https://www.clarin.ac.uk/resource-families/celtic-languages/`) as a
ground-truth bilingual corpus provider, alongside the Cadhan Aonair
treebanks (UD Irish + UD Welsh + UD Scottish Gaelic + UD Breton + UD
Manx) and the Foclóir Gàidhlig-Gaeilge cross-Celtic dictionary at
`https://kevinscannell.com/files/gd2ga.pdf`.

These land under `dlt_sources/ciancheiltis/clarin_uk/` with one
`@dlt.source` per major resource family. They are NOT licensed CC-BY or
public-domain in every case — license MUST be modelled as a first-class
schema column and ingestion MUST be gated on license allowance.

#### Scenario: CLARIN-UK Celtic corpora land in the lakehouse
- **WHEN** the `clarin_uk_corpora` source runs
- **THEN** at least 10 distinct CLARIN-UK corpora MUST be ingested
- **AND** each row MUST carry `language_pair`, `license`, `corpus_size_mb`,
  `has_bilingual_text`, `download_url` columns
- **AND** the LanceDB companion table MUST be
  `lancedb://md:cianfhoghlaim/clarin_uk_corpora`

### Requirement: BAML extraction suite
The system MUST provide one BAML extraction function per phase, named
`ExtractCiancheiltisBilingualPage`, plus a shared extraction function
`ExtractBilingualExplanatoryNote(en_note, cy_note)` patterned on the
Ireland education `ExtractCrossLinguisticConcept` template. Functions
MUST be declared in `baml_src/british_isles/_shared/ciancheiltis.baml`
(shared) and `baml_src/british_isles/<jurisdiction>/ciancheiltis_<phase>.baml`
(per-phase).

The BAML client MUST route per language:
- `cy` → `gemma-4-26B-A4B` (Welsh-aware multilingual MoE)
- `ga` → `uccix-mistral-24b` (modern Irish)
- `gd` → `gemma-4-26B-A4B`
- `gv` → `gemma-4-26B-A4B` with Manx few-shot

#### Scenario: en-cy Phase 1 extraction routes to Gemma for Welsh
- **WHEN** a user calls `ExtractCiancheiltisBilingualPage(page, language="cy")`
- **THEN** the BAML compiler MUST route to the `ciancheiltisCyExtract` client
- **AND** the client MUST use `gemma-4-26B-A4B` model

### Requirement: CocoIndex v1 R1-R4 conformance
Each phase's CocoIndex App MUST conform to R1-R4 (the canonical contract
in `oideachais-cocoindex-v1` skill):
- **R1**: Imports `from ._lifespan import shared_lifespan`
- **R2**: Uses `BAAI/bge-m3` embedder (1024-d, multilingual incl. CY/GA/GD/GV)
- **R3**: Wraps every flow as `@coco.fn(memo=True, deps=...)`
- **R4**: Mounts each LanceDB table via `mount_table_target(...)` with
  `conformance_required=True`

#### Scenario: All 6 CocoIndex Apps pass R1-R4
- **WHEN** the `cocoindex_v1_conformance` App runs against the 6 phase Apps
- **THEN** every App MUST satisfy R1+R2+R3+R4 (verified by
  `dg check yaml` + the conformance test harness)

### Requirement: Dagster 5-layer asset graph per phase
Each phase MUST have a complete 5-layer Dagster asset graph following the
`CelticIngestionComponent` + `CelticMaterialsComponent` +
`CelticModelLifecycleComponent` + `CelticAssetGenerationComponent` +
`CelticAgentOpsComponent` pattern (per the British Isles Education
Pipeline spec).

Asset checks (one per phase) MUST gate ≥ 0.70 RAGAS bilingual-pair score
and ≥ 500 bilingual pairs seeded.

#### Scenario: en-cy Phase 1 RAGAS gate fires
- **WHEN** the en-cy `bilingual_pairs_seeded_check` asset check runs
- **THEN** it MUST block asset materialisation unless RAGAS ≥ 0.70
- **AND** it MUST block unless ≥ 500 bilingual `(en, cy)` paragraph-level
  pairs are present in the lakehouse

### Requirement: MotherDuck Dive + Flight per phase
Each phase MUST ship one MotherDuck Dive (`ciancheiltis_<phase>_dive.py`)
and one MotherDuck Flight (`ciancheiltis_<phase>_flight`). The Dive
MUST show, per theme (T1-T10): row count, language-pair coverage
percentage, metadata-language-match rate.

#### Scenario: en-cy Dive renders theme coverage
- **WHEN** the user opens `ciancheiltis_en_cy_dive`
- **THEN** the Dive MUST show a 10-row theme table with row counts and
  coverage percentages
- **AND** MUST highlight themes where the metadata-language-mismatch
  rate exceeds 5%

### Requirement: Cross-pipeline integration with cianfhoghlaim
The system MUST integrate with the existing BIEP and celtic-language-pipeline
surfaces via the shared `bilingual_concept_registry.py`. Newly discovered
bilingual pairs MUST land in
`stedding/education/bilingual_concepts/ciancheiltis_<phase>__<theme>.jsonl`
without overwriting the existing Ireland (en-ga) JSONL files.

The cross-linguistic edge table from `meaisinfhoghlaim/alignment/schema.py`
(`BilingualTopicEdge`, key `(concept_id, language_pair)`) MUST be
extended with a new dimension `source = "ciancheiltis"`.

#### Scenario: en-cy pairs land in the bilingual concept registry
- **WHEN** the en-cy Phase 1 BAML extraction produces 100 bilingual pairs
- **THEN** they MUST land in
  `stedding/education/bilingual_concepts/ciancheiltis_en_cy__<theme>.jsonl`
- **AND** the `bilingual_coverage_audit.py` gate MUST include the new
  source in its scoring (≥ 0.95 threshold)

### Requirement: DO NOT
The system MUST NOT introduce absolute cross-package namespaces
(`from cianfhoghlaim.dlt_sources...`) inside ciancheiltis source files —
all imports MUST be relative to the ciancheiltis subtree or via the
shared `dlt_sources/common/` helpers.

The system MUST NOT mark a phase complete based on URL count alone —
RAGAS bilingual-pair coverage is the canonical completion gate.
