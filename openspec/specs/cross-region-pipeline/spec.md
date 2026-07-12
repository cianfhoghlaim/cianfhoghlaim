## ADDED Requirements

### Requirement: Canonical cross-region DLT path contract

The system SHALL route every new DLT source for any of the 6 supported
regions through the canonical path contract:

```text
dlt/<region>/<jurisdiction>/<domain>/<source>.py
```

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
`dlt/british_isles/<nation>/<domain>/<source>.py` pattern. The existing
British Isles files remain where they are; only new files in the other
5 regions MUST obey this contract.

#### Scenario: A new EU member state source obeys the contract

- **WHEN** a developer adds a new French statute-book DLT source for
  the EU nations expansion
- **THEN** the file SHALL be created at
  `dlt/european_nations/fra/law/legifrance.py`
- **AND** the source SHALL emit rows tagged with
  `country_code="fra"`, `language` in `{fr, en}`, and the canonical
  DuckLake namespace `oideachais.law.fra`

#### Scenario: A new EU institutional source obeys the contract

- **WHEN** a developer adds a new EUR-Lex regulations DLT source
- **THEN** the file SHALL be created at
  `dlt/european_union/eur_lex/regulations.py`
- **AND** the source SHALL emit rows tagged with
  `region="european_union"`, `institution="eur_lex"`, `language`
  in the 24 EU official language codes, and the canonical DuckLake
  namespace `oideachais.law.eu.eur_lex`

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
oideachais.<domain>.<region>.<jurisdiction>
```

(or `oideachais.<domain>.<region>.<institution>` for institutional
sources). The `region` token in the namespace MUST be one of the 6
canonical regions. Existing British Isles namespaces
(`oideachais.education.ie`, `oideachais.leaving_cert`,
`oideachais.law.ie`, `oideachais.medicine.<nation>`) are the
ground-truth examples of this contract.

#### Scenario: A new EU nations source writes to the canonical namespace

- **WHEN** the `european_nations.fra.law.legifrance` DLT source runs
- **THEN** it SHALL write to `oideachais.law.european_nations.fra`
- **AND** the dataset_name SHALL be
  `oideachais_law_european_nations_fra`

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

## Cross-references

- `oideachais-pipeline` — the parent pipeline; this umbrella spec
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
