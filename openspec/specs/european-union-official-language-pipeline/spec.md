# european-union-official-language-pipeline Specification

## Purpose
TBD - created by archiving change 2026-07-11-european-union-official-language-pipeline-v1. Update Purpose after archive.
## Requirements
### Requirement: 24 EU official languages

The system MUST treat the 24 EU official language codes
(`bg`, `hr`, `cs`, `da`, `nl`, `en`, `et`, `fi`, `fr`, `de`, `el`,
`hu`, `ga`, `it`, `lv`, `lt`, `mt`, `pl`, `pt`, `ro`, `sk`, `sl`,
`es`, `sv`) as the canonical `language` partition for every EU
institutional source.

#### Scenario: A new EU institutional source partitions by 24 languages

- **WHEN** the EUR-Lex regulations DLT source emits a regulation
  available in 12 of the 24 official languages
- **THEN** the system MUST emit 12 rows, one per
  `(celex_id, language)`
- **AND** the `language` column MUST be one of the 24 EU official
  language codes
- **AND** the DuckLake table MUST be
  `cianfhoghlaim.law.european_union.eur_lex`

### Requirement: EUR-Lex multilingual ingestion

The system MUST provide DLT sources at
`dlt/european_union/eur_lex/{regulations,directives,decisions,treaties,cjeu_case_law}.py`
that crawl the EUR-Lex portal (`eur-lex.europa.eu`) and emit one row
per `(celex_id, language)` for every regulation, directive, decision,
treaty, or CJEU case law document available in at least one EU
official language.

#### Scenario: A EUR-Lex regulation appears in 8 languages

- **WHEN** the EUR-Lex regulations DLT source ingests Regulation
  (EU) 2024/903
- **THEN** the system MUST emit 8 rows, one per available language
- **AND** each row MUST include `celex_id`, `language`, `title`,
  `publication_date`, `source_url`, `content_hash`,
  `document_type="regulation"`, `official_status="in_force"`
- **AND** the source MUST honour `USE_LOCAL_SCRAPES=true` falling
  back to `stedding/ingest_queue/eu/eur_lex/<lang>/`

### Requirement: Eurydice / Cedefop education information

The system MUST provide DLT sources at
`dlt/european_union/education/{eurydice,cedefop,school_education_gateway}.py`
that crawl the Eurydice network
(`eurydice.eacea.ec.europa.eu`), Cedefop (`cedefop.europa.eu`), and
the School Education Gateway, and emit one row per national
education-system entry.

#### Scenario: A new Eurydice entry is extracted

- **WHEN** the Eurydice DLT source ingests a new national education
  structure page for Italy
- **THEN** the system MUST emit a row with
  `country_code="ita"`, `language="en"` (the Eurydice default
  English edition), `document_type="national_education_structure"`,
  and `source_url` pointing at the Eurydice entry
- **AND** the row MUST include the cross-link to the Italian edition
  when one exists

### Requirement: EMA + ECDC medicine

The system MUST provide DLT sources at
`dlt/european_union/medicine/{ema_medicines_register,ecdc_surveillance,european_health_data_space}.py`
that crawl the European Medicines Agency
(`ema.europa.eu`) + European Centre for Disease Prevention &
Control (`ecdc.europa.eu`) + the European Health Data Space portal.

#### Scenario: A new EMA-issued medicine entry is extracted

- **WHEN** the EMA medicines register DLT source ingests a new
  centrally authorised medicine
- **THEN** the system MUST emit one row per language edition
  (EMA publishes the same medicine record in at least 24 editions)
- **AND** each row MUST include `medicine_name`, `active_substance`,
  `atc_code`, `authorisation_status`, `language`,
  `document_type="epar"` (European Public Assessment Report),
  `source_url`, `content_hash`

### Requirement: Eurostat statistics

The system MUST provide a DLT source at
`dlt/european_union/statistics/eurostat.py` that crawls the Eurostat
data browser (`ec.europa.eu/eurostat`) and emits one row per
dataset × language edition.

#### Scenario: A new Eurostat dataset is ingested

- **WHEN** the Eurostat DLT source ingests dataset `educ_uoe_grad02`
- **THEN** the system MUST emit one row per available language
  edition of the dataset metadata page
- **AND** each row MUST include `dataset_id`, `language`,
  `last_updated`, `source_url`, `content_hash`,
  `document_type="dataset_metadata"`

### Requirement: Publications Office + Europa portal

The system MUST provide DLT sources at
`dlt/european_union/publications_office/{eu_publications,cellar_documents}.py`
and `dlt/european_union/government/{europa_portal,commission_press,parliament_documents,council_documents}.py`
that crawl the Publications Office of the EU
(`publications.europa.eu`) + the Europa portal + the 3 EU institutions'
press / document release streams.

#### Scenario: A Council document is ingested in 3 languages

- **WHEN** the Council documents DLT source ingests a Council
  Decision published in English, French, and German
- **THEN** the system MUST emit 3 rows (one per language edition)
- **AND** each row MUST include `document_id`, `language`,
  `institution="council"`, `document_type="decision"`,
  `publication_date`, `source_url`, `content_hash`

### Requirement: Multilingual EU document extraction

The system MUST provide a BAML extraction function
`ExtractEUDocument(language: EULanguage, text: string) -> EUDocument`
at `baml/european_union/_shared/eu_document.baml` that
extracts the canonical multilingual-document class from any EU
institutional source.

#### Scenario: A EUR-Lex regulation is BAML-extracted in 8 languages

- **WHEN** the EUR-Lex regulations DLT source yields 8 rows for a
  given `celex_id`
- **THEN** the L2 BAML extraction asset MUST call
  `b.ExtractEUDocument(language=<each>, text=<each>)`
- **AND** each resulting `EUDocument` MUST carry the
  `language`, `title`, `summary`, `publication_date`, and
  `official_status` fields

### Requirement: Bilingual English + Irish BAML extraction

The system MUST provide a bilingual `BilingualTextEnGa` BAML class
that captures EU institutional documents in both English and Irish
(Gaeilge) for later alignment with the British Isles Ireland +
Northern Ireland corpus.

A new `ExtractEUDocumentBilingualEnGa` function MUST populate
both the `en` and `ga` fields when both are available, and
populate the `language_availability` map when only one is.

#### Scenario: EUR-Lex regulation available in both English and Irish

- **WHEN** the bilingual extraction function is called on a
  EUR-Lex regulation available in both English and Irish
- **THEN** the resulting `EUExtractableBilingualDocument` MUST
  have `title.en` + `title.ga` populated
- **AND** the `language_availability` map MUST show
  `{en: "full", ga: "full"}`

### Requirement: Per-source `language_availability` metadata

The system MUST carry `language_availability` metadata on every EU
institutional DLT source documenting which of the 24 EU official
languages (including Irish) are available. Irish (`ga`) MUST show
`"full"` coverage for EUR-Lex, Eurydice, Cedefop, EMA, Eurostat,
Publications Office, Council, Parliament, Commission, Europa
Portal, and School Education Gateway. English (`en`) MUST show
`"full"` coverage for all 12 EU institutional sources.

#### Scenario: Irish coverage audit

- **WHEN** the `irish_coverage_monitor.py` L2 asset runs
- **THEN** it MUST emit one row per (institution, language)
  pair for the 24 EU official languages
- **AND** every row MUST carry the `language_availability` value
  from the source's metadata

