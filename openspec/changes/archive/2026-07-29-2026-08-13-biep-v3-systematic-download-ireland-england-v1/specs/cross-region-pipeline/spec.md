## MODIFIED Requirements

### Requirement: Canonical cross-region DLT path contract

The system SHALL route every new DLT source for any of the 6 supported
regions through the canonical path contract:

```text
dlt_sources/<region>/<jurisdiction>/<domain>/<source>.py
```

(For new files in the 5 non-British-Isles regions. Existing British Isles
files at `dlt_sources/british_isles/<jurisdiction>/<domain>/<source>.py`
are the canonical home for the British Isles; only new files in the other
5 regions MUST obey this contract.)

where:

- `region ∈ {british_isles, european_union, european_nations, commonwealth, americas, global_official}`
- `jurisdiction` is one of:
  - for `british_isles`: the 8 documented names (`ireland`, `england`,
    `scotland`, `wales`, `northern_ireland`, `jersey`, `guernsey`,
    `isle_of_man`)
  - for `european_nations`, `commonwealth`, `americas`: an ISO
    3166-1 alpha-3 code in lowercase (e.g. `fra`, `deu`, `ukr`, `aus`,
    `can`, `mex`)
  - for sub-national units (e.g. US states): `<iso3>_<sub>` (e.g.
    `us_ca` for California)
  - for institutional regions (`european_union`, `global_official`):
    the institution slug (e.g. `eur_lex`, `eurydice`, `ema`,
    `ecdc`, `oecd`, `who`)
- `domain ∈ {education, law, medicine, statistics, government, site_analysis, filesystem, language}`
- `source` is a snake_case slug of the source

The contract extends (does NOT rename) the existing
`dlt_sources/british_isles/<jurisdiction>/<domain>/<source>.py` pattern
(the post-v7 actual path; the pre-v7 `dlt/british_isles/<nation>/<domain>/<source>.py`
path is retired). The existing British Isles files remain where they are;
only new files in the other 5 regions MUST obey this contract.

#### Scenario: A new EU member state source obeys the contract

- **WHEN** a developer adds a new French statute-book DLT source for
  the EU nations expansion
- **THEN** the file SHALL be created at
  `dlt_sources/european_nations/fra/law/legifrance.py`
- **AND** the source SHALL emit rows tagged with
  `country_code="fra"`, `language` in `{fr, en}`, and the canonical
  DuckLake namespace `cianfhoghlaim.law.fra`

#### Scenario: A new EU institutional source obeys the contract

- **WHEN** a developer adds a new EUR-Lex regulations DLT source
- **THEN** the file SHALL be created at
  `dlt_sources/european_union/eur_lex/regulations.py`
- **AND** the source SHALL emit rows tagged with
  `region="european_union"`, `institution="eur_lex"`, `language`
  in the 24 EU official language codes, and the canonical DuckLake
  namespace `cianfhoghlaim.law.eu.eur_lex`

#### Scenario: A new British Isles source obeys the post-v7 path

- **WHEN** a developer adds a new NCCA Leaving Cycle Mathematics DLT source
- **THEN** the file SHALL be created at
  `dlt_sources/british_isles/ireland/education/ncca_lc_mathematics.py`
  (the post-v7 path; NOT the pre-v7 `dlt/british_isles/ie/...`)
- **AND** the source SHALL emit rows tagged with
  `region="british_isles"`, `jurisdiction="ireland"`, `language` in `{en, ga}`,
  and the canonical DuckLake namespace
  `cianfhoghlaim.education.ireland.leaving_cycle.mathematics`

## ADDED Requirements

### Requirement: BIEP v3 2-axis scope/year partition

The system SHALL partition every BIEP v3 jurisdiction pipeline on the
canonical 2-axis `MultiPartitionsDefinition`:

```text
{
  "scope": DynamicPartitionsDefinition(name="cianhoghlaim_scope"),
  "year": StaticPartitionsDefinition(<2017-2027 + "undated">),
}
```

The partition is defined in `orchestration/partitions_v2.py:39-64` as
`biiep_v3_scope_year_partition`. The `scope` axis uses a
`DynamicPartitionsDefinition` because the 428+ cohort keys
(`<jurisdiction>__<stage>__<subject_slug>__<board>__<qualification_level>__<language>`)
are seeded at runtime by the British Isles Subject Registry. The `year`
axis is static (2017–2027 + "undated") because the curriculum refresh
cadence is on a known annual cycle.

The partition key for a given cohort is built by
`scope_partition_key(jurisdiction, stage, subject_slug, board,
qualification_level, language)` and yields the canonical 6-token shape:

```text
<jurisdiction>__<stage>__<subject_slug>__<board>__<qualification_level>__<language>
```

(e.g. `ireland__leaving_cycle__mathematics__na__higher__en`).

#### Scenario: An Ireland LC Mathematics Higher English 2024 cohort lands in the right partition

- **WHEN** the `ireland_lc_mathematics_higher_en_documents_ingested` asset
  materialises against the 2024 syllabus PDF
- **THEN** the partition key SHALL be
  `(scope="ireland__leaving_cycle__mathematics__na__higher__en", year="2024")`
- **AND** the asset_check SHALL enforce that every emitted row's
  `jurisdiction`, `stage`, `subject_slug`, `board`, `qualification_level`,
  and `language` columns match the `scope` partition

#### Scenario: An England AQA GCSE Mathematics 2025 cohort lands in the right partition

- **WHEN** the `england_gcse_mathematics_aqa_documents_ingested` asset
  materialises against the 2025 spec
- **THEN** the partition key SHALL be
  `(scope="england__gcse__mathematics__aqa__gcse__en", year="2025")`
- **AND** the asset_check SHALL enforce that every emitted row's `board`
  matches `aqa` and `qualification_level` matches `gcse`

### Requirement: Snake_case file naming + metadata sidecar contract (BIEP v3)

The system SHALL land every BIEP v3 PDF and metadata sidecar at the
canonical snake_case path:

```text
s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject_slug>/<language>/<year_or_undated>/<jurisdiction>__<stage>__<subject_slug>__<board_or_na>__<qual_level_or_untiered>__<language>__<year_or_undated>__<sha256[0:8]>.pdf
```

with a sibling `<file>.meta.json` sidecar carrying the metadata fields
(`source_id`, `jurisdiction`, `stage`, `subject_slug`, `board`,
`qualification_level`, `language`, `year`, `source_url`, `crawled_at`,
`byte_size`, `page_count`, `content_hash_sha256`, `publisher`).

The full path MUST match the regex
`^[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+/[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-z0-9_]+__[a-f0-9]{8}\.pdf$`
(strict snake_case separators + lowercase SHA256 prefix).

#### Scenario: An Ireland LC Mathematics Higher English 2024 PDF lands at the canonical path

- **WHEN** the Ireland LC Mathematics Higher English 2024 syllabus PDF is
  ingested
- **THEN** it SHALL be written to
  `s3://garage/cianfhoghlaim/ireland/leaving_cycle/mathematics/en/2024/ireland__leaving_cycle__mathematics__na__higher__en__2024__<sha256[0:8]>.pdf`
- **AND** the sibling `.meta.json` SHALL carry
  `source_id="british_isles.ireland.education.ncca_lc_mathematics"`

#### Scenario: An England AQA GCSE Mathematics 2025 PDF lands at the canonical path

- **WHEN** the England AQA GCSE Mathematics 2025 spec PDF is ingested
- **THEN** it SHALL be written to
  `s3://garage/cianfhoghlaim/england/gcse/mathematics/en/2025/england__gcse__mathematics__aqa__gcse__en__2025__<sha256[0:8]>.pdf`
- **AND** the sibling `.meta.json` SHALL carry
  `source_id="british_isles.england.education.aqa_gcse_mathematics"`
