# oideachais-pipeline Specification

## Purpose
TBD - created by archiving change 2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1. Update Purpose after archive.
## Requirements
### Requirement: No legacy 972-LOC ie-namespace duplicate pairs remain in `dlt/british_isles/ireland/education/`

The `dlt/british_isles/ireland/education/` package SHALL NOT
contain byte-identical or near-identical duplicate files. Specifically
the legacy duplicate pair:

- `curriculum_source.py` (972 LOC, byte-identical to `curriculum.py` per
  MD5 `c098f82f94909f9ffccee0387b600d9f`) — DELETED
- `exam_source_update.py` (0-byte stub) — DELETED

…is removed entirely, and the 11 importers that referenced the deleted
files are rewritten to point at `curriculum.py` (the kept surface).

#### Scenario: Filesystem directory contains no legacy duplicates

- **WHEN** a developer runs `ls dlt/british_isles/ireland/education/`
- **THEN** zero entries SHALL match `*curriculum_source*`
- **AND** zero entries SHALL match `*exam_source_update*`
- **AND** the directory listing SHALL contain exactly one `curriculum.py`
      (the canonical 972-LOC surface)

#### Scenario: Import graph is consolidated against `curriculum.py`

- **GIVEN** `curriculum.py` defines `_crawl_source` at line 57 +
      `crawl_source()` + `parallel_scrape_subject()` + `_classify_pdf()` +
      `crawl_cycle()` + `crawl_subject()` + `build_subject_urls()` and the
      `curriculum_source` `@dlt.source` function at line 600
- **WHEN** a developer runs `grep -rn "from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum_source\|from cianfhoghlaim.dlt.british_isles.ireland.education.exam_source_update" cianfhoghlaim/`
- **THEN** zero matches SHALL appear (excluding the historical openspec
      archive under `openspec/changes/archive/*`)

#### Scenario: The 11 importers work against `curriculum.py`

- **WHEN** any of the 11 importers imports `_crawl_source`
- **THEN** `from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source`
      SHALL succeed (the kept surface defines the symbol)
- **AND** each importer SHALL continue to expose the same domain
      behaviour as before the duplicate-file deletion (WRC pages, courts
      forms, judgements, citizens info, etc.)

### Requirement: Canonical endpoint_recovery helper

The cianfhoghlaim-pipeline capability MUST expose the
`dlt/common/endpoint_recovery` helper as the canonical entry point
for every DLT source's outbound network call. The helper MUST be
importable from `cianfhoghlaim.dlt.common.endpoint_recovery` and
MUST be the only place the British Isles + EU + Commonwealth + EU
nations + Americas DLT sources are permitted to call out to live
endpoints.

#### Scenario: A new EU nation source uses the helper

- **WHEN** a developer adds a new EU nation DLT source
- **THEN** the source MUST call
  `from cianfhoghlaim.dlt.common.endpoint_recovery import endpoint_recovery`
- **AND** the source MUST route every outbound HTTP request through
  `endpoint_recovery.fetch(...)`
- **AND** the source MUST NOT import `requests` or `httpx` directly

### Requirement: EU pilot + Ukraine per-subject depth upgrade

The cianfhoghlaim-pipeline capability MUST cross-reference the
[`2026-07-15-eu-pilot-upgrade-v1`](../../../openspec/changes/2026-07-15-eu-pilot-upgrade-v1/)
change (the upgrade of the 6 EU pilot countries + Ukraine to
BIEP per-subject depth + the fill-in of physics + biology for the
3 BI nations).

#### Scenario: A new file in the EU pilot upgrade obeys the contract

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `european-nations-ukraine-pipeline` as the EU nations entry point

### Requirement: Americas pipeline cross-referenced from cianfhoghlaim-pipeline

The cianfhoghlaim-pipeline capability MUST cross-reference the new
Americas pipeline
([`americas-california-pipeline`](../../../specs/americas-california-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the Americas expansion obeys the contract

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `americas-california-pipeline`

### Requirement: Commonwealth pipeline cross-referenced from oideachais-pipeline

The oideachais-pipeline capability MUST cross-reference the new
Commonwealth pipeline
([`commonwealth-pipeline`](../../../specs/commonwealth-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the Commonwealth expansion obeys the contract

- **WHEN** a developer reads the oideachais-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `commonwealth-pipeline`

### Requirement: EU nations + Ukraine pipeline cross-referenced from cianfhoghlaim-pipeline

The cianfhoghlaim-pipeline capability MUST cross-reference the new EU
nations + Ukraine pipeline
([`european-nations-ukraine-pipeline`](../../../specs/european-nations-ukraine-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the EU nations expansion obeys the contract

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `european-nations-ukraine-pipeline`

### Requirement: EU institutional pipeline cross-referenced from cianfhoghlaim-pipeline

The cianfhoghlaim-pipeline capability MUST cross-reference the new EU
institutional pipeline
([`european-union-official-language-pipeline`](../../../specs/european-union-official-language-pipeline/spec.md))
and the EU nations + Ukraine pipeline
([`european-nations-ukraine-pipeline`](../../../specs/european-nations-ukraine-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the EU expansion obeys the contract

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `european-union-official-language-pipeline` AND
  `european-nations-ukraine-pipeline`

### Requirement: Nigeria pipeline cross-referenced from oideachais-pipeline

The oideachais-pipeline capability MUST cross-reference the new
Nigeria pipeline
([`commonwealth-pipeline`](../../../specs/commonwealth-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the Nigeria expansion obeys the contract

- **WHEN** a developer reads the oideachais-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `commonwealth-pipeline` as the Commonwealth entry point

### Requirement: Canada provinces cross-referenced from cianfhoghlaim-pipeline

The cianfhoghlaim-pipeline capability MUST cross-reference the new
Canada-provinces change
([`commonwealth-pipeline`](../../../specs/commonwealth-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the Canada expansion obeys the contract

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `commonwealth-pipeline` as the Commonwealth entry point

### Requirement: British Isles parity pipeline cross-referenced from cianfhoghlaim-pipeline

The cianfhoghlaim-pipeline capability MUST cross-reference the new
British Isles parity change
([`british-isles-education-pipeline`](../../../specs/british-isles-education-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the BI parity expansion obeys the contract

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `british-isles-education-pipeline` as the BIEP entry point

### Requirement: EU full-depth expansion cross-referenced from cianfhoghlaim-pipeline

The cianfhoghlaim-pipeline capability MUST cross-reference the EU
full-depth expansion
([`european-nations-ukraine-pipeline`](../../../specs/european-nations-ukraine-pipeline/spec.md))
in the `## Cross-references` section.

#### Scenario: A new file in the EU expansion obeys the contract

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `european-nations-ukraine-pipeline` as the EU nations entry point

### Requirement: EU multilingual pipeline cross-referenced

The cianfhoghlaim-pipeline capability MUST cross-reference the new
EU multilingual pipeline.

#### Scenario: Cross-references list updates

- **WHEN** a developer reads the cianfhoghlaim-pipeline spec
- **THEN** the `## Cross-references` section MUST list
  `european-union-official-language-pipeline` as the EU
  institutional entry point

