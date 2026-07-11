# 2026-07-12-canada-provinces-quebec-montreal-pipeline-v1

## Why

The
[`2026-07-11-commonwealth-pipeline-v1`](../2026-07-11-commonwealth-pipeline-v1/)
change ships the Commonwealth of Nations pipeline with 5 pilot
countries. Canada is in the pilot list, but only at the **federal**
level (CMEC + federal_laws + Health Canada + StatCan + canada.ca).
The 10 provinces + 3 territories are not yet covered, and Quebec +
Montreal education is the user's explicit focus ("**for now focus on
english and french official resources especially education in quebec
and montreal**").

This change adds:

- 10 Canadian provinces + 3 territories, each with a per-domain
  DLT scaffold (Ontario / Quebec / BC / Alberta / Saskatchewan /
  Manitoba / Nova Scotia / New Brunswick / PEI / NL + NT / NU / YT)
- A **deep Quebec + Montreal education cluster** with 6 dedicated
  DLT sources:
  - `mees` — Ministère de l'Éducation et de l'Enseignement
    supérieur
  - `cssdm` — Centre de services scolaire de Montréal (French-language
    Montreal school board)
  - `emsb` — English Montreal School Board
  - `lbpsb` — Lester B. Pearson School Board (English Montreal)
  - `mcgill_universities` — McGill + UdeM + UQAM + Concordia
    (Montreal university cluster)
- A bilingual language partition for Quebec (`fr` default + `en`
  secondary) — mirroring the existing British Isles bilingual
  pattern (Ireland `en` + `ga` with `en` default).
- 3 new BAML schemas (`ExtractQuebecEducationDocument`,
  `ExtractCanadianProvinceDocument`,
  `ExtractCanadianProvinceLawDocument`).
- 1 CocoIndex v1 App `quebec_montreal_education_embedding.py` + the
  per-province Apps.
- 1 MotherDuck Dive `quebec_montreal_curriculum_matrix` + per-province
  Dives.
- 1 daily MotherDuck Flight `canada_daily_sync_flight`.

## What changes

### 1. Per-province DLT scaffolds (13 provinces/territories)

For each of Ontario (`on`), Quebec (`qc`), British Columbia (`bc`),
Alberta (`ab`), Saskatchewan (`sk`), Manitoba (`mb`), Nova Scotia
(`ns`), New Brunswick (`nb`), PEI (`pe`), Newfoundland & Labrador
(`nl`), Northwest Territories (`nt`), Nunavut (`nu`), Yukon (`yt`):

- `dlt/commonwealth/can/<prov>/education/<ministry>.py` (1 file per
  province)
- `dlt/commonwealth/can/<prov>/law/<legislation>.py`
- `dlt/commonwealth/can/<prov>/medicine/<health_authority>.py`
- `dlt/commonwealth/can/<prov>/statistics/<stats_office>.py`
- `dlt/commonwealth/can/<prov>/government/<gov_portal>.py`

Provinces use the canonical `NationSource` subclass pattern (matching
the existing scaffolded Australian + Indian + South African +
New Zealand pipelines). Quebec + Ontario + BC + Alberta + SK are
the deep-dive provinces; the other 8 are thin scaffolds (1 source per
domain).

### 2. Quebec + Montreal deep education cluster

- `dlt/commonwealth/can/qc/education/mees.py` — Ministère de
  l'Éducation et de l'Enseignement supérieur
- `dlt/commonwealth/can/qc/education/cssdm.py` — Centre de services
  scolaire de Montréal (French-language Montreal)
- `dlt/commonwealth/can/qc/education/emsb.py` — English Montreal
  School Board
- `dlt/commonwealth/can/qc/education/lbpsb.py` — Lester B. Pearson
  School Board (English Montreal)
- `dlt/commonwealth/can/qc/education/mcgill_universities.py` —
  McGill + UdeM + UQAM + Concordia university cluster

### 3. BAML extensions

- `baml/commonwealth/can/quebec/education.baml` — defines
  `QuebecEducationBilingualRecord` with `BilingualTextQuebec`
  pattern (FR + EN).
- `baml/commonwealth/can/quebec/montreal_education.baml` — defines
  `MontrealSchoolBoardRecord` for the 3 Montreal school boards.
- `baml/commonwealth/can/_shared/province.baml` — generic
  `ExtractCanadianProvinceDocument(province, language, text)`.

### 4. CocoIndex v1 Apps

- `dlt/commonwealth/can/qc/education/embedding.py` — embeds the 5
  Quebec education sources + 4 Montreal universities into the
  shared LanceDB table `oideachais.commonwealth.can.qc.education_chunks`,
  partitioned by `language ∈ ("fr", "en")`.
- Per-province CocoIndex v1 Apps (one per deep-dive province).

### 5. MotherDuck Dive + Flight

- `quebec_montreal_curriculum_matrix` — cross-language matrix
  (FR-default) showing the bilingual curriculum coverage.
- `canada_daily_sync_flight` — daily BAML backfill.

### 6. Dagster defs

- 13 provincial `1_ingestion/commonwealth/can/<prov>/<domain>/defs.yaml`
  files (1 per province × 5 domains = 65 L1 defs)
- 1 L3 defs for the Quebec CocoIndex v1 App
- 5 provincial Dagster defs

## Dependencies

```yaml
Blocked by: 2026-07-11-global-region-source-contract-v1
Blocked by (soft):
  - 2026-07-11-commonwealth-pipeline-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-12-canada-provinces-quebec-montreal-pipeline-v1 --strict` passes
- 65 provincial DLT sources exist + AST-parse
- 6 Quebec + Montreal DLT sources exist + AST-parse
- 3 BAML files exist + AST-parse
- 2+ CocoIndex v1 Apps conform to R1–R4
- 1 MotherDuck Dive + 1 daily Flight exist + YAML-parse
- 65+ Dagster L1 defs.yaml files YAML-parse
- `dg check yaml` passes
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`commonwealth-pipeline`](../commonwealth-pipeline/spec.md) —
  the parent pipeline
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the bilingual reference (Ireland `en` + `ga`)
- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) —
  the parent pipeline
- `docs/agents/british_isles_endpoint_health_audit.md` —
  the Phase 1 endpoint snapshot
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
