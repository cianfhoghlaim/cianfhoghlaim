## ADDED Requirements

### Requirement: 30 EU nations reach Ireland-level depth

The system MUST bring the 6 EU pilot countries (UKR / FRA / DEU /
POL / ESP / ITA) + the 21 remaining EU member states + 3 EEA/EFTA
members + 9 EU candidate / neighbour states (total 39 jurisdictions,
of which 30 are in scope for this change) to the British Isles
parity depth.

Per-country depth requires:

- ≥6 per-subject DLT sources (mathematics / chemistry / biology /
  physics / language / computing_science) at
  `dlt/european_nations/<iso3>/education/subjects/<subject>.py`
- 5 baseline DLT sources (1 per canonical domain) at
  `dlt/european_nations/<iso3>/{law,medicine,statistics,government}/`
- 3 BAML files at
  `baml/european_nations/<iso3>/{education,law,medicine}.baml`
  with per-country extraction functions
- 1 CocoIndex v1 App per nation (R1–R4 conformance)
- 6 L1 + 1 L3 Dagster defs

#### Scenario: Germany ships 6 per-subject DLT sources

- **WHEN** the EU full-depth expansion is materialised
- **THEN** the system MUST provide 6 per-subject DLT sources under
  `dlt/european_nations/deu/education/subjects/` (mathematics,
  chemistry, biology, physics, language, computing_science)
- **AND** each source MUST partition on `language ∈ ("de", "en")`
  (German + English)
- **AND** the `european_nations_deu_education_embedding` CocoIndex v1
  App MUST embed every per-subject row into the shared LanceDB
  table `oideachais.lc.european_nations.deu.education_chunks`
- **AND** the 3 BAML files at
  `baml/european_nations/deu/{education,law,medicine}.baml` MUST
  define `ExtractDEU<Domain>Document(germany, language, text)`
  functions

### Requirement: Official-language focus

The system MUST prioritise each country's official language(s) for
the `language` partition. For multilingual countries the partition
MUST list all official languages with the primary language
appearing first.

#### Scenario: Belgium supports 3 official languages

- **WHEN** the Belgium EU nation DLT source materialises
- **THEN** the `language` partition MUST list
  `["nl", "fr", "de"]` (Dutch primary + French + German)
- **AND** the per-subject sources MUST honour all 3 languages
- **AND** the BAML extraction functions MUST carry the same
  3-language partition

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-nations-ukraine-pipeline`](../european-nations-ukraine-pipeline/spec.md) —
  the existing EU nations scaffold
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the Ireland-level template
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
