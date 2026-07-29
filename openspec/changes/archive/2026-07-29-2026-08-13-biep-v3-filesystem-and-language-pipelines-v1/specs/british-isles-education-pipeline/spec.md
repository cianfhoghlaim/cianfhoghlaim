## ADDED Requirements

### Requirement: Filesystem scanner domain (BIEP v3)

The system SHALL provide a canonical `filesystem` domain in the BIEP v3
cross-jurisdiction registry that aggregates the 11 canonical filesystem
DLT sources at `dlt_sources/filesystem/`:

1. `leabharlann_books` — `leabharlann/{gaeilge,aigne}/` (EPUB + preview pairing)
2. `gemini_deep_research` — `leabharlann/gemini_deep_research/`
3. `google_takeout` — `Takeout/<account_label>/` (per-account)
4. `takeout_v1` — `stedding/Takeout/` (multi-account auto-discovery)
5. `email_inbox` — `/srv/mailcow-exports/*.mbox` (4-account email-inbox pipeline)
6. `leaving_cert_source` — filesystem scanner for the Ireland LC PDFs
7. `university_of_galway` — `leabharlann/ollscoil_na_gaillimhe/`
8. `zotero` — `leabharlann/zotero/` (real Zotero storage format)
9. `gemini_corpus_source` — Gemini corpus loader
10. `pdf_download_source` — PDF downloader
11. `previews` — preview pairing

The 3 generic Dagster assets (ingestion + extraction + embedding)
MUST be defined at
`orchestration/defs/2_materials/filesystem_pipelines/generic_filesystem_assets.py`.

The 1 monthly MotherDuck Flight MUST be at
`motherduck/flights/filesystem_monthly_sync_flight.py`.

#### Scenario: Filesystem ingestion produces >= 1 row per run

- **WHEN** the operator runs `mise run filesystem:monthly:sync`
- **THEN** the `filesystem_documents_ingested` asset materialises
- **AND** the 11 filesystem sources emit >= 1 row each
- **AND** the 3 filesystem asset checks pass

### Requirement: Language scanner domain (BIEP v3)

The system SHALL provide a canonical `language` domain in the BIEP v3
cross-jurisdiction registry that aggregates the 19 canonical language
DLT sources at `dlt_sources/language/`:

1. `ainm` — Ainm (Irish place names)
2. `canuint` — Canúint (Irish intonation)
3. `canuint_audio` — Canúint audio samples
4. `canuint_dialect_summary` — Canúint dialect summary
5. `canuint_search` — Canúint lexical search
6. `canuint_word_alignment` — Canúint word alignment
7. `duchas` — Dúchas na hÉireann (Schools' Folklore Collection)
8. `duchas_images` — Dúchas images
9. `gaois` — Gaois (Irish language corpus)
10. `gaois_combined` — Gaois combined
11. `heritage` — Heritage sites
12. `hidden_heritages` — Hidden heritages
13. `local_documents_by_subject` — Local documents by subject
14. `local_education_documents` — Local education documents
15. `logainm` — Logainm (place names database)
16. `tearma` — Téarma (terminology database)
17. `tearma_search` — Téarma search
18. `universal_dependencies` — Universal Dependencies

The 3 generic Dagster assets (ingestion + extraction + embedding)
MUST be defined at
`orchestration/defs/2_materials/language_pipelines/generic_language_assets.py`.

The 1 monthly MotherDuck Flight MUST be at
`motherduck/flights/language_monthly_sync_flight.py`.

#### Scenario: Language ingestion produces >= 1 row per run

- **WHEN** the operator runs `mise run language:monthly:sync`
- **THEN** the `language_documents_ingested` asset materialises
- **AND** the 19 language sources emit >= 1 row each (when the cache is present)
- **AND** the 3 language asset checks pass

### Requirement: Monthly BIEP v3 scheduling for filesystem + language

The system SHALL run the filesystem + language assets on a MONTHLY
cadence (`0 0 1 * *`, 1st of each month 00:00 UTC) per the BIEP v3
scheduling policy. This is more frequent than the yearly education
content cadence because filesystem + language content changes more
often.

#### Scenario: Monthly cron fires for filesystem + language

- **WHEN** the monthly cron fires at 00:00 UTC on the 1st of the month
- **THEN** both the `filesystem_monthly_sync_flight` and
  `language_monthly_sync_flight` MotherDuck Flights run
- **AND** both write status rows to their respective audit tables
- **AND** the BIEP v3 canonical `make_monthly_circulars_automation()`
  AutomationCondition is used

## Cross-references

- `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/` —
  the umbrella change that drove the BIEP v3 systematic download
- `orchestration/automation/biiep_scheduling.py` — the canonical
  BIEP v3 scheduling policy
- `dlt_sources/filesystem/` — the 11 canonical filesystem DLT sources
- `dlt_sources/language/` — the 19 canonical language DLT sources
- `.agents/skills/dlt/SKILL.md` — the DLT conventions
