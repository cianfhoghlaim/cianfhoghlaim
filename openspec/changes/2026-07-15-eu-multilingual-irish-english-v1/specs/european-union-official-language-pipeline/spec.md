## ADDED Requirements

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
