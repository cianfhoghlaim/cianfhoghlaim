---
title: 'Oideachais Pipeline Capability'
domain: 'architecture'
status: 'stable'
description: 'Capability spec for the oideachais data lakehouse. See docs/00-core/CLAUDE.md for the quadrant map and docs/02-data-platform/ for the canonical data-platform docs.'
read_when:
  - working in oideachais/
  - adding a new source or asset
truth: sole
updated: '2026-06-13'
supersedes:
  - docs/OIDEACHAIS_SPEC.md
ccc_query_hints:
  - oideachais capability requirements
---

# Oideachais Pipeline Capability

## Overview

The oideachais data lakehouse is one of the 5 quadrants in the
Cianfhoghlaim monorepo. This file is the **capability spec** for it.
For the architecture / topology / how-it-works, see
[`docs/02-architecture/OIDEACHAIS_PIPELINE.md`](OIDEACHAIS_PIPELINE.md)
and [`docs/02-data-platform/data-architecture.md`](../02-data-platform/data-architecture.md).

## Requirements

### Requirement: Domain-First Asset-Key Convention

The system SHALL identify every asset by a domain-first key tuple
`["{nation_code}", "{domain}", "{entity_slug}", ...]`.

- `nation_code` ∈ `ie | ni | en | sct | wls | iom | jey | ggy`
- `domain` ∈ `education | medicine | law | statistics | site_analysis`

The source of truth for asset keys is `oideachais/sources.yaml`. The
legacy `["ireland", …]` and `["uk", "education", "northern_ireland", …]`
keys remain resolvable via a one-shot backwards-compat alias in
`oideachais/dagster_defs/definitions.py`.

#### Scenario: Domain-first key for an Irish education asset
- **GIVEN** `oideachais/dagster_defs/assets/ie/education/curriculum_dlt_assets.py::create_cycle_asset("senior_cycle")`
- **WHEN** registered with the SourceFactory
- **THEN** the new key is `["ie", "education", "senior_cycle"]`
- **AND** the legacy `["ireland", "curriculum", "senior_cycle"]` is still resolvable

#### Scenario: Domain-first key for a Northern Ireland CCEA asset
- **GIVEN** `oideachais/dlt_sources/uk/northern_ireland/ccea_curriculum.py::ni_curriculum_source`
- **WHEN** the SourceFactory emits the corresponding Dagster asset
- **THEN** the new key is `["ni", "education", "ccea", "pages"]`
- **AND** the legacy `["uk", "education", "northern_ireland", "ccea_pages"]` is still resolvable

### Requirement: Single `oideachais` DB with per-domain schemas

The system SHALL register a single `md:oideachais` (MotherDuck) database
and a single `ducklake:oideachais` (Garage S3) catalog, with schemas of
the form `oideachais.{domain}.{nation}`. DLT `dataset_name` MAY remain
per-source for fine-grained state, but the underlying DuckLake schema
SHALL be the dotted-triple.

#### Scenario: One attach, one query
- **GIVEN** the API reader at `oideachais/api/ducklake_reader.py`
- **WHEN** the SPA requests a Leaving Cert subject
- **THEN** the reader does a single `ATTACH 'oideachais'` (or `ducklake:oideachais`)
- **AND** reads `oideachais.education.ie.leaving_cert WHERE subject = ?`

#### Scenario: New domain schema is auto-created
- **GIVEN** a new DLT run for `oideachais/dlt_sources/domains/medicine/ie/hse.py`
- **WHEN** the pipeline runs
- **THEN** DuckLake creates the schema `oideachais.medicine.ie` on first write
- **AND** the table is discoverable by `marimo` against `md:oideachais`

### Requirement: Test-Covered Pipeline Graph

The system SHALL have automated pytest coverage of the DLT/Dagster asset
graph, runnable under `USE_LOCAL_SCRAPES=true` against a temporary
DuckLake fixture (no live network, no production schema mutation).

#### Scenario: All Phase 1b tests pass in CI
- **GIVEN** `bun run test` (or `mise run test`)
- **WHEN** the test runner executes
- **THEN** all 16+ pytests in `oideachais/tests/`, `tuatha/tests/`,
  `croilar/tests/`, `tests/sources/` are green

#### Scenario: Cross-namespace guard
- **GIVEN** a DLT source under `oideachais/dlt_sources/`
- **WHEN** the cross-namespace test runs
- **THEN** the test fails if any source imports `oideachais.data_platform.*`

### Requirement: Source-Factory Single Source of Truth

The system SHALL maintain `oideachais/sources.yaml` as the canonical
source registry, and `oideachais/dlt_utils/source_factory.py` as the
single 7-method factory that turns a YAML id into a runtime artefact.

#### Scenario: Adding a new source requires only a YAML edit
- **GIVEN** a new entry in `sources.yaml` for a new public endpoint
- **WHEN** the operator runs `python -m oideachais.sources.sources_validation`
- **THEN** the report shows: DLT source present, Dagster asset present,
  LanceDB table wired, Cognee dataset wired, marimo notebook present,
  pytest present (or "missing artefact" for the follow-on work)

#### Scenario: Bad YAML entry rejected at load time
- **GIVEN** an entry with an unknown `kind` or unknown `nation_code`
- **WHEN** `SourceFactory.from_yaml(...)` is called
- **THEN** the factory raises `pydantic.ValidationError` with the offending field

### Requirement: Law Domain is Statutory Only (MVP)

The system SHALL provide a `law/` domain in `sources.yaml` containing
**only statutory** law sources: `irish_statute_book` (IE),
`legislation` (NI/EN/SCT/WLS), `doj` (IE), `lawreform` (IE). Case law
(court judgments, tribunals, BAILII mirrors) SHALL NOT be ingested by
this change.

#### Scenario: Law domain in sources.yaml
- **GIVEN** the `sources.yaml` file
- **WHEN** the operator runs `python -m oideachais.sources.sources_validation --filter domain=law`
- **THEN** only statutory entries appear

#### Scenario: Case law entry rejected
- **GIVEN** a hypothetical `ie.law.courts` entry
- **WHEN** the SourceFactory loads the YAML
- **THEN** the factory raises a `pydantic.ValidationError` because `ie.law.courts` is not in the MVP law allowlist
