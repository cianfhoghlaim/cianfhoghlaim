# Spec Delta — oideachais-leabharlann

## ADDED Requirements

### Requirement: Leabharlann Corpus Location (v4)

The system SHALL expose the leabharlann (personal archive) corpus at `cianfhoghlaim/leabharlann/{aigne,gaeilge,gemini_deep_research,mata,ollscoil_na_gaillimhe,zotero}/` (6 subdirs × 216 documents = 12 + 45 + 11 + 20 + 8 + 120). The corpus previously lived at `/leabharlann/` at repo root.

#### Scenario: dlt source resolution

- **WHEN** Dagster materialises a leabharlann asset
- **THEN** the dlt source module is `cianfhoghlaim.pipelines.ingest.leabharlann.{books,zotero,takeout_v1,university_of_galway,gemini_deep_research,google_takeout}` (formerly `sruth.oideachais.dlt_sources.leabharlann.*`)
- **AND** the CocoIndex embedding flow is `cianfhoghlaim.embeddings.leabharlann` (formerly `sruth.oideachais.cocoindex_flows.leabharlann_embedding`)
- **AND** the directory-watch sensor is `cianfhoghlaim.pipelines.sensors.leabharlann` (formerly `sruth/oideachais/dagster_defs/sensors/leabharlann_sensors.py`)

### Requirement: Plan 1 All 6 Leabharlann Subdirs Active (v4)

The system SHALL activate all 6 leabharlann subdirs in Plan 1 — `aigne/`, `gaeilge/`, `gemini_deep_research/`, `mata/`, `ollscoil_na_gaillimhe/`, `zotero/`. Each subdir's dlt source + BAML extraction + CocoIndex flow is wired and runnable.

#### Scenario: All 6 sources in Plan 1

- **WHEN** Plan 1 (Ireland + leabharlann) launches
- **THEN** all 6 leabharlann dlt sources ingest their respective documents (216 total)
- **AND** the OCR evaluation harness runs vision vs classical OCR on the leabharlann corpus
- **AND** the results inform Plan 1.5 refactor of the OCR registry