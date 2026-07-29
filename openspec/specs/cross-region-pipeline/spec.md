## Purpose

This umbrella spec extends `cianfhoghlaim-pipeline` (the British Isles scoped pipeline) into a 6-region federation (British Isles + European Union + European Nations + Commonwealth + Americas + Global Official). It defines the canonical path contract, source_id shape, partition contract, DuckLake namespace shape, and cross-nation BAML classifier that all new DLT sources in the 6 supported regions must obey.
## Requirements
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

### Requirement: Canonical source_id shape

The system SHALL give every new DLT source a `source_id` of the form:

```text
<region>.<jurisdiction>.<domain>.<source_slug>
```

where each token matches the canonical path contract above and the
`source_slug` is the same snake_case slug as the filename (without the
`.py` extension). The full `source_id` MUST match the regex
`^[a-z0-9]+(\.[a-z0-9]+){3,}$` and SHALL be stable across
re-materialisations (the source_id is the canonical primary key
column on the asset).

#### Scenario: A new source has a stable source_id

- **WHEN** the Dagster asset for
  `dlt/european_nations/ukr/education/ministry_education_science.py`
  materialises
- **THEN** its asset key SHALL be
  `european_nations.ukr.education.ministry_education_science`
- **AND** the `source_id` column SHALL equal `european_nations.ukr.education.ministry_education_science`
  on every row

#### Scenario: A new source_id never reuses a legacy uppercase code

- **WHEN** a developer adds a new source with jurisdiction `IRL`
  (uppercase ISO 3166-1 alpha-3) or `IE` (uppercase 2-letter)
- **THEN** the contract validation in `dg check yaml` SHALL reject
  the source
- **AND** the canonical jurisdiction code for Ireland SHALL remain
  `ireland` (the British Isles legacy name) — NOT `irl`

### Requirement: Canonical partition contract

The system SHALL partition every new regional pipeline on the
canonical 4-axis `MultiPartitionsDefinition`:

```text
{
  "region": StaticPartitionsDefinition(<the 6 regions>),
  "jurisdiction": StaticPartitionsDefinition(<the per-region list>),
  "domain": StaticPartitionsDefinition(<the 8 domains>),
  "language": StaticPartitionsDefinition(<the per-jurisdiction official languages>),
}
```

The `language` axis MUST contain the jurisdiction's official language
code(s). For EU institutional sources, the `language` axis MUST
contain the 24 EU official language codes. The
`MultiPartitionsDefinition` is composed at scaffold time by the
`CelticIngestionComponent` from the YAML defs.

#### Scenario: A new EU nations source partitions by jurisdiction + domain + language

- **WHEN** the `european_nations.fra.law.legifrance` asset is
  materialised
- **THEN** the partition key SHALL be
  `(jurisdiction="fra", domain="law", language="fr")`
- **AND** the asset_check SHALL enforce that every emitted row's
  `country_code` matches the `jurisdiction` partition

### Requirement: Canonical DuckLake namespace shape

The system SHALL land every new regional source into the canonical
DuckLake namespace:

```text
cianfhoghlaim.<domain>.<region>.<jurisdiction>
```

(or `cianfhoghlaim.<domain>.<region>.<institution>` for institutional
sources). The `region` token in the namespace MUST be one of the 6
canonical regions. Existing British Isles namespaces
(`cianfhoghlaim.education.ie`, `cianfhoghlaim.leaving_cert`,
`cianfhoghlaim.law.ie`, `cianfhoghlaim.medicine.<nation>`) are the
ground-truth examples of this contract.

#### Scenario: A new EU nations source writes to the canonical namespace

- **WHEN** the `european_nations.fra.law.legifrance` DLT source runs
- **THEN** it SHALL write to `cianfhoghlaim.law.european_nations.fra`
- **AND** the dataset_name SHALL be
  `cianfhoghlaim_law_european_nations_fra`

### Requirement: Cross-nation BAML classifier (carried forward)

The system SHALL reuse the existing
[`ExtractCrossNationSpec`](../../../../../cianfhoghlaim/baml/education/cross_nation/multi_nation_curriculum.baml)
+ `AlignOutcomes` + `CompareCurricula` +
`TranslateEducationalContent` + `IdentifyResourceSharing` BAML
functions across the 6 regions. The new global-expansion regions MUST
extend the existing `Nation` enum + `NationEducationLevel` enum +
`QualificationBoard` enum + `CurriculumFramework` enum (or, if the
change touches too many enums, define a parallel `GlobalJurisdiction`
+ `GlobalEducationLevel` enum in
`cianfhoghlaim/baml/global/_shared/jurisdiction.baml`).

#### Scenario: A new global jurisdiction is classified by the BAML cross-nation function

- **WHEN** a new source under `dlt/americas/bra/education/mec.py`
  emits a curriculum specification row
- **THEN** the L2 BAML extraction asset SHALL call
  `b.ExtractCrossNationSpec(document=..., nation="BRA",
   level=BRA_HIGHER_EDUCATION)`
- **AND** the resulting `CrossNationCurriculumSpec` SHALL carry the
  canonical jurisdiction + region + language metadata

### Requirement: Americas pipeline obeys the cross-region contract

The system MUST route every new Americas pipeline through the canonical
cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Americas files live at
`dlt/americas/<jurisdiction>/<domain>/<source>.py` with the canonical
`source_id` + partition + DuckLake namespace contract.

#### Scenario: A new California education source obeys the contract

- **WHEN** a developer adds the CDE source
- **THEN** it MUST be created at
  `dlt/americas/us/us_ca/education/cde.py`
- **AND** its `source_id` MUST be
  `americas.us.us_ca.education.cde`
- **AND** it MUST NOT be created at `dlt/california/cde.py` or any
  other non-conformant path

### Requirement: Commonwealth of Nations pipeline obeys the cross-region contract

The system MUST route every new Commonwealth pipeline through the
canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Commonwealth files live at
`dlt/commonwealth/<iso3>/<domain>/<source>.py` (per-nation) or
`dlt/commonwealth/official/<source>.py` (institutional).

#### Scenario: A new Australian curriculum source obeys the contract

- **WHEN** a developer adds the ACARA source
- **THEN** it MUST be created at `dlt/commonwealth/aus/education/acara.py`
- **AND** its `source_id` MUST be `commonwealth.aus.education.acara`
- **AND** it MUST NOT be created at `dlt/aus/acara.py` or any other
  non-conformant path

### Requirement: EU nations + Ukraine pipeline obeys the cross-region contract

The system MUST route every new per-nation pipeline through the
canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Per-nation files live at
`dlt/european_nations/<iso3>/<domain>/<source>.py` with the
canonical `source_id` + partition + DuckLake namespace contract.

#### Scenario: A new French statute-book source obeys the contract

- **WHEN** a developer adds the Légifrance source
- **THEN** it MUST be created at
  `dlt/european_nations/fra/law/legifrance.py`
- **AND** its `source_id` MUST be `european_nations.fra.law.legifrance`
- **AND** it MUST NOT be created at any legacy path
  (`dlt/eu/fra/law/`, `dlt/europeanunion/fra/law/`, etc.)

### Requirement: EU institutional pipeline obeys the cross-region contract

The system MUST route every new EU institutional pipeline through the
canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. EU institutional files live at
`dlt/european_union/<institution>/<source>.py` and obey the canonical
`source_id` + partition + DuckLake namespace contract.

#### Scenario: A new EU institutional source obeys the contract

- **WHEN** a developer adds a new EMA medicines register source
- **THEN** it MUST be created at
  `dlt/european_union/medicine/ema_medicines_register.py`
- **AND** its `source_id` MUST be
  `european_union.medicine.ema_medicines_register`
- **AND** its asset key MUST be
  `european_union.medicine.ema_medicines_register`
- **AND** it MUST NOT be created at the legacy paths
  (`dlt/eu/`, `dlt/european_union/ema.py`, etc.)

### Requirement: Nigeria pipeline obeys the cross-region contract

The system MUST route every Nigerian pipeline through the canonical
cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Nigerian federal files live at
`dlt/commonwealth/nga/<domain>/<source>.py`; state files live at
`dlt/commonwealth/nga/states/<state_slug>/<domain>/<source>.py`.

#### Scenario: A new Nigerian federal source obeys the contract

- **WHEN** a developer adds the NUC source
- **THEN** it MUST be created at
  `dlt/commonwealth/nga/education/nuc.py`
- **AND** its `source_id` MUST be
  `commonwealth.nga.education.nuc`
- **AND** it MUST NOT be created at `dlt/nigeria/nuc.py` or any
  other non-conformant path

### Requirement: Canada provinces obey the cross-region contract

The system MUST route every new Canadian provincial pipeline
through the canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Provincial files live at
`dlt/commonwealth/can/<prov>/<domain>/<source>.py` with the
canonical `source_id` + partition + DuckLake namespace contract.

#### Scenario: A new Quebec education source obeys the contract

- **WHEN** a developer adds the MEES source
- **THEN** it MUST be created at
  `dlt/commonwealth/can/qc/education/mees.py`
- **AND** its `source_id` MUST be
  `commonwealth.can.qc.education.mees`
- **AND** it MUST NOT be created at `dlt/canada/qc/mees.py` or any
  other non-conformant path

### Requirement: British Isles parity pipeline obeys the cross-region contract

The system MUST route every British Isles per-nation + per-subject
pipeline through the canonical cross-region path contract
declared by the [`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Per-nation + per-subject files live at
`dlt/british_isles/<nation>/<domain>/<source>.py` (matching the
existing British Isles contract).

#### Scenario: A new Scottish per-subject source obeys the contract

- **WHEN** a developer adds a new SQA mathematics source
- **THEN** it MUST be created at
  `dlt/british_isles/scotland/education/subjects/mathematics.py`
- **AND** its `source_id` MUST be
  `british_isles.scotland.education.subjects.mathematics`
- **AND** it MUST NOT be created at
  `dlt/scotland/mathematics.py` or any other non-conformant path

### Requirement: EU full-depth pipeline obeys the cross-region contract

The system MUST route every per-subject DLT source for the EU
nations full-depth expansion through the canonical cross-region
path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec. Per-subject files live at
`dlt/european_nations/<iso3>/education/subjects/<subject>.py`.

#### Scenario: A new Czech mathematics source obeys the contract

- **WHEN** a developer adds the CZE mathematics source
- **THEN** it MUST be created at
  `dlt/european_nations/cze/education/subjects/mathematics.py`
- **AND** its `source_id` MUST be
  `european_nations.cze.education.subjects.mathematics`
- **AND** it MUST NOT be created at `dlt/czechia/mathematics.py` or
  any other non-conformant path

### Requirement: EU multilingual pipeline obeys the cross-region contract

The system MUST route the EU multilingual alignment pipeline through
the canonical cross-region path contract. The bilingual English +
Irish extraction files live at `dlt/european_union/<institution>/`
(unchanged), the bilingual extraction function is in
`baml/european_union/_shared/eu_document.baml`.

#### Scenario: A new bilingual extraction function is added

- **WHEN** a developer adds the
  `ExtractEUDocumentBilingualEnGa` function
- **THEN** it MUST live in
  `baml/european_union/_shared/eu_document.baml`
- **AND** it MUST be importable via
  `from cianfhoghlaim.baml_client import b`
- **AND** the function MUST accept `institution: EUInstitution`
  and `language: EULanguage` parameters

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

### Requirement: Display strings use full jurisdiction names

The system MUST use the full official jurisdiction name in every
**display string** (BAML class + function names, Python class
names, docstrings, BAML prompt bodies, MotherDuck Dive descriptions,
Dagster `metadata.country_name` field, CocoIndex v1 App descriptions).

The system MUST keep the **short ID** (ISO 3166-1 alpha-3 for
countries, `<iso3>_<sub>` for sub-states) in every **identifier**
(file paths, module names, variable names, `source_id` strings, asset
keys, Dagster partition values, DuckLake table names, cache
directory names, BAML parameter names).

#### Scenario: Germany BAML class uses the full name

- **WHEN** the rename change is materialised
- **THEN** the BAML class at `baml/european_nations/deu/education.baml`
  MUST be named `class GermanySubjectCurriculum`
  (NOT `class DEUSubjectCurriculum`)
- **AND** the BAML function MUST be named
  `function ExtractGermanySubjectCurriculum`
- **AND** the BAML parameter MUST still be `nation: string`
  (short ID preserved for compatibility)
- **AND** the BAML prompt body MUST mention "German curriculum"
- **AND** the source_id string MUST still be
  `european_nations.deu.education.<subject>`
- **AND** the Dagster partition value MUST still be `country: ["deu"]`
- **AND** the `defs.yaml` MUST add the new metadata field
  `country_name: "Federal Republic of Germany"`

#### Scenario: Nigeria state class uses the full state name

- **WHEN** the rename change is materialised
- **THEN** the BAML class at
  `baml/european_nations/nga/state.baml` for the Lagos state source
  MUST be named `class LagosStateSubjectCurriculum`
- **AND** the Python class at
  `dlt/european_nations/nga/states/nga_los/education/ministry_of_education.py`
  MUST be named `class LagosStateEducationSource(NationSource)`
- **AND** the `country_name` metadata field MUST be
  `"Lagos State, Federal Republic of Nigeria"`

### Requirement: Sub-state BAML class naming

The system MUST follow the sub-state BAML class naming convention:

- Nigerian states: `<FullStateName>SubjectCurriculum` (e.g.
  `LagosStateSubjectCurriculum`)
- US states: `<FullStateName>SubjectCurriculum` (no "State" suffix
  — "California" alone is unambiguous)
- Canadian provinces: `<FullProvinceName>SubjectCurriculum`
- Australian states: `<FullStateName>` CamelCase for multi-word names
  (e.g. `NewSouthWalesSubjectCurriculum`)

#### Scenario: Lagos State BAML class uses the full state name

- **WHEN** the rename change is materialised
- **THEN** the BAML class at `baml/european_nations/nga/state.baml`
  for the Lagos state MUST be named
  `class LagosStateSubjectCurriculum`
- **AND** the function MUST be named
  `function ExtractLagosStateSubjectCurriculum`
- **AND** the source_id string MUST still be
  `european_nations.nga.states.nga_los.education.<subject>`
  (the short `nga_los` is preserved as the identifier)

## Cross-references

- `cianfhoghlaim-pipeline` — the parent pipeline; this umbrella spec
  extends its scope
- `british-isles-education-pipeline` — the British Isles v1 instance
  of this contract
- `official-media-pipeline` — the sibling official-media region
  (not yet under this contract)
- `european-union-official-language-pipeline` — the EU institutional
  instance of this contract
- `european-nations-ukraine-pipeline` — the EU nations + Ukraine
  instance of this contract
- `docs/agents/cross-nation-content-audit.md` — the BIEP v2 audit
  template
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
