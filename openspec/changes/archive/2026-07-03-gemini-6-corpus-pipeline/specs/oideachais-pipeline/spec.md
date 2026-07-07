## ADDED Requirements

### Requirement: Gemini 6-corpus filesystem pipeline

The system SHALL provide an end-to-end pipeline for the 6 Gemini Deep
Research sub-corpora (law / medical / politics / culture / technology
/ other) processing **224 PDFs** (57+54+47+30+24+12) totalling ~78 MB.

The pipeline SHALL be organised into 7 stages:

1. **VLM/OCR** — `qwen3-vl-8b` workhorse (the v4 registry's text-heavy fallback)
2. **BAML extraction** — 6 per-corpus functions on 2 BAML files
3. **DuckLake** — 5 tables per corpus × 6 corpora = 30 tables
4. **LanceDB** — 6 per-corpus embedding tables (BGE-large), 224 vectors
5. **Graphiti temporal** — 6 per-corpus episode streams, 224 episodes; `event_time` from PDF prose (NOT file mtime)
6. **Cognee cognify** — 6 per-corpus datasets
7. **FalkorDB cross-corpus** — unified graph spanning all 6 corpora

#### Scenario: The 6 L1 ingestion assets yield 224 rows total

- **WHEN** `dagster asset materialize --select 'gemini_*_ingested'`
- **THEN** `gemini_law_ingested` SHALL yield 57 rows
- **AND** `gemini_medical_ingested` SHALL yield 54 rows
- **AND** `gemini_politics_ingested` SHALL yield 47 rows
- **AND** `gemini_culture_ingested` SHALL yield 30 rows
- **AND** `gemini_technology_ingested` SHALL yield 24 rows
- **AND** `gemini_other_ingested` SHALL yield 12 rows
- **AND** the sum SHALL equal 224

#### Scenario: Graphiti event_time comes from PDF prose, not mtime

- **GIVEN** a Gemini law PDF with a section `// the incident occurred on 2023-05-15`
- **WHEN** the L2 BAML extraction runs + Graphiti episode is created
- **THEN** the episode's `event_time` SHALL be `2023-05-15` (from prose)
- **AND** the file mtime SHALL NOT influence `event_time`

### Requirement: 2 BAML files for Gemini-corpus extraction

The system SHALL provide 2 BAML files at
`cianfhoghlaim/baml/processing/`:

1. `legal_case_profile.baml` — `class LegalCaseProfile`, `class MedicalCaseProfile`, `class TimelineEvent`, `class StatuteReference`, `enum CaseCategory`, `enum Jurisdiction`
2. `topic_profile.baml` — `class PoliticalTopicProfile`, `class CultureTopicProfile`, `class TechTopicProfile`, `enum PoliticalTopic`, `enum CultureTopic`, `enum TechTopic`

#### Scenario: The BAML project compiles both new files

- **WHEN** `cd cianfhoghlaim && uv run baml-cli generate`
- **THEN** `from cianfhoghlaim.baml_client.types import LegalCaseProfile, MedicalCaseProfile, TimelineEvent, StatuteReference, PoliticalTopicProfile, CultureTopicProfile, TechTopicProfile` SHALL succeed

### Requirement: 9 dev marimo notebooks for the 6 Gemini corpora

The system SHALL provide 9 dev notebooks across 6 corpus subdirectories:

- `notebooks/dashboards/law/01_law_corpus_overview.py` (57 PDFs)
- `notebooks/dashboards/medical/01_medical_corpus_overview.py` (54)
- `notebooks/dashboards/politics/01_politics_corpus_overview.py` (47)
- `notebooks/dashboards/culture/01_culture_corpus_overview.py` (30)
- `notebooks/dashboards/technology/01_technology_corpus_overview.py` (24)
- `notebooks/dashboards/other/01_other_corpus_overview.py` (12)
- `notebooks/dashboards/law/02_cross_corpus_timeline.py` (Plotly timeline; PDF-content event_time)
- `notebooks/dashboards/law/03_jurisdictional_map.py` (choropleth of 6 jurisdictions)
- `notebooks/dashboards/law/04_pattern_detection.py` (Cognee cross-corpus patterns)

#### Scenario: All 9 notebooks open and show 224 total PDFs

- **WHEN** `for f in dashboards/{law,medical,politics,culture,technology,other}/0[1234]_*.py; do marimo parse "$f"; done`
- **THEN** all 9 files SHALL parse without syntax errors

#### Scenario: The jurisdictional choropleth distributes 224 cases

- **WHEN** `marimo run dashboards/law/03_jurisdictional_map.py`
- **THEN** the choropleth SHALL map Ireland / Northern Ireland / UK /
  EU / CROSS_BORDER cases proportionally across the 224 PDFs

### Requirement: Per-corpus category + jurisdiction filename heuristic

The `gemini_corpus_source.py` SHALL classify each PDF by:

- **corpus** — the parent directory name (law / medical / politics /
  culture / technology / other)
- **jurisdiction** — `echr`/`european` → EU, `belfast`/`qub`/`ni_` →
  NI, `ucl`/`uk_` → UK, `dual`/`cross_border` → CROSS_BORDER,
  else → IRELAND
- **category** — corpus-specific (legal_strategy / medical_malpractice /
  policy / governance / software / OTHER)

#### Scenario: A law PDF with `qub_discrimination.pdf` maps to NI

- **GIVEN** the file `leabharlann/gemini_deep_research/law/qub_discrimination.pdf`
- **WHEN** the DLT source runs
- **THEN** `row.jurisdiction == "NORTHERN_IRELAND"`
- **AND** `row.category == "DISCRIMINATION"`
- **AND** `row.corpus == "law"`
