# 2026-07-11-european-nations-ukraine-pipeline-v1

## Why

The
[`2026-07-11-european-union-official-language-pipeline-v1`](../2026-07-11-european-union-official-language-pipeline-v1/)
change ships the EU institutional layer (EUR-Lex + EMA + ECDC +
Eurydice + Eurostat + Publications Office + Council + Parliament +
Commission + `europa.eu`). This change ships the complementary
**national layer**: one DLT subtree per EU member state + Ukraine.

The pilot countries are:

- `ukr` Ukraine (EU candidate since 2022 — humanitarian + EU-candidate
  priority)
- `fra` France
- `deu` Germany
- `pol` Poland
- `esp` Spain
- `ita` Italy

These 6 countries cover the 4 largest EU member states by population
(DE, FR, ES, IT) plus Poland + Ukraine, giving representative
coverage of continental European + Eastern European + Mediterranean
data surfaces.

The change obeys the canonical
[`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md)
contract (the Phase 0 lockdown).

## What changes

### 1. New umbrella spec `european-nations-ukraine-pipeline`

Adds `openspec/specs/european-nations-ukraine-pipeline/spec.md` as
the canonical spec for the EU nations + Ukraine pipeline. It
declares:

- the 27 EU member states + Ukraine (`ukr`) + the EU candidate /
  EEA / EFTA countries (`tur`, `mda`, `srb`, `mkd`, `alb`, `mne`,
  `bih`, `xkx`, `nor`, `che`, `isl`)
- the canonical DLT path contract (`dlt/european_nations/<iso3>/<domain>/<source>.py`)
- the BAML extraction schemas
- the CocoIndex v1 Apps + LanceDB tables
- the MotherDuck Dives + daily Flights

### 2. New DLT sources under `dlt/european_nations/<iso3>/`

For each of the 6 pilot countries, ship 5 DLT sources (one per
canonical domain):

```text
dlt/european_nations/<iso3>/
├── education/
│   └── ministry_education_science.py
├── law/
│   └── <statute_book>.py
├── medicine/
│   └── <health_authority>.py
├── statistics/
│   └── <stats_office>.py
└── government/
    └── <gov_portal>.py
```

The pilot country → DLT-source mapping:

| Country | Education source | Law source | Medicine source | Statistics source | Government source |
|:--|:--|:--|:--|:--|:--|
| `ukr` | `ministry_education_science.py` (Ministry of Education and Science of Ukraine) | `zakon_rada.py` (Verkhovna Rada / Legislation of Ukraine) | `ministry_health.py` (Ministry of Health of Ukraine) | `ukrstat.py` (State Statistics Service of Ukraine) | `kmu_portal.py` (Cabinet of Ministers of Ukraine portal) |
| `fra` | `ministere_education_nationale.py` | `legifrance.py` (Légifrance — French statute book) | `has_sante.py` (Haute Autorité de Santé) | `insee.py` (Institut national de la statistique et des études économiques) | `service_public.py` (Service-Public.fr portal) |
| `deu` | `kmk.py` (Kultusministerkonferenz) | `gesetze_im_internet.py` (Bundesministerium der Justiz) | `rki.py` (Robert Koch Institute) | `destatis.py` (Statistisches Bundesamt) | `bundesregierung.py` (Bundesregierung portal) |
| `pol` | `men.py` (Ministerstwo Edukacji Narodowej) | `sejm.py` (Sejm + Senat) | `nfz.py` (Narodowy Fundusz Zdrowia) | `gus.py` (Główny Urząd Statystyczny) | `gov_pl.py` (gov.pl portal) |
| `esp` | `mecd.py` (Ministerio de Educación, Formación Profesional y Deportes) | `boe.py` (Boletín Oficial del Estado) | `mscbs.py` (Ministerio de Sanidad) | `ine.py` (Instituto Nacional de Estadística) | `la_moncloa.py` (La Moncloa portal) |
| `ita` | `miur.py` (Ministero dell'Istruzione e del Merito) | `gazzetta_ufficiale.py` (Gazzetta Ufficiale della Repubblica Italiana) | `aifa.py` (Agenzia Italiana del Farmaco) | `istat.py` (Istituto Nazionale di Statistica) | `governo_it.py` (governo.it portal) |

### 3. New BAML extraction schemas under `baml/european_nations/`

For each of the 6 pilot countries, ship 3 BAML extraction functions
(education + law + medicine — the same canonical 3-fn trio as the
British Isles per-nation templates):

```text
baml/european_nations/
├── _shared/
│   └── jurisdiction.baml
├── ukr/
│   ├── education.baml
│   ├── law.baml
│   └── medicine.baml
├── fra/
│   ├── education.baml
│   ├── law.baml
│   └── medicine.baml
├── deu/...
├── pol/...
├── esp/...
└── ita/...
```

The canonical extraction function is
`ExtractNationCurriculumSpec(country_code, language, text) -> NationCurriculumSpec`
(mirroring `b.ExtractLC6Syllabus`).

### 4. New CocoIndex v1 Apps

```text
cocoindex/european_nations_education_embedding.py
cocoindex/european_nations_law_embedding.py
cocoindex/european_nations_medicine_embedding.py
```

Each App embeds its domain's rows for the 6 pilot countries into a
shared LanceDB table using `BAAI/bge-m3`.

### 5. New Dagster L1 + L3 assets

```text
orchestration/defs/1_ingestion/european_nations/<iso3>/<domain>/defs.yaml
orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_<domain>/defs.yaml
```

### 6. New MotherDuck analytics

- 1 Dive: `eu_nation_curriculum_matrix` — cross-nation coverage matrix
  of the 6 pilot countries' education systems
- 1 daily Flight: `eu_nation_daily_sync_flight` — daily BAML backfill

## What does NOT change

- The existing British Isles files are NOT renamed.
- The existing EU institutional pipeline from
  `2026-07-11-european-union-official-language-pipeline-v1` is NOT
  modified.

## Dependencies

```yaml
Blocked by: 2026-07-11-global-region-source-contract-v1
Blocked by (soft):
  - 2026-07-11-european-union-official-language-pipeline-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-11-european-nations-ukraine-pipeline-v1 --strict` passes
- `openspec/specs/european-nations-ukraine-pipeline/spec.md` exists with at least 5 Requirements + 5 Scenarios
- The 30 DLT sources (6 countries × 5 domains) exist + AST-parse
- The 18 BAML files (6 countries × 3 domains) exist + AST-parse
- The 3 CocoIndex v1 Apps conform to R1–R4
- `dg check yaml` passes on the new defs.yaml
- `mise run lint:skills` still passes
- Push target: `origin/main`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../../specs/european-union-official-language-pipeline/spec.md) —
  the institutional counterpart
- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the seed instance (per-nation pattern template)
- [`cianfhoghlaim-pipeline`](../../specs/cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
