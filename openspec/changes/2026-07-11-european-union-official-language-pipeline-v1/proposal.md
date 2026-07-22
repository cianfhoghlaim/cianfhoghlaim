# 2026-07-11-european-union-official-language-pipeline-v1

## Why

The Cianfhoghlaim data plane has so far focused on the British Isles
(Ireland + Scotland + Wales + England + Northern Ireland + Isle of Man
+ Jersey + Guernsey). The
[`2026-07-11-global-region-source-contract-v1`](../2026-07-11-global-region-source-contract-v1/)
change locks the canonical path + source_id + partition contract that
will be reused for the global expansion.

The next region to land is the **European Union institutional layer**:
the EU publishes the same documents (regulations, directives, case law,
medicines register, public-health surveillance, education-information
network, statistics) in **24 official languages**. The outputs are
intended for:

- later alignment (e.g. matching a UK post-Brexit retained-EU-law
  provision against the equivalent EUR-Lex regulation),
- later data creation (BAML extraction of curriculum / legislation /
  medicines / statistics across all 24 languages).

This change ships the EU institutional pipeline end-to-end:

- DLT sources under `dlt/european_union/` for EUR-Lex, Publications
  Office, Eurydice, Cedefop, EMA, ECDC, Eurostat, Council of Europe,
  European Court of Human Rights, and the `europa.eu` portal
- BAML extraction schemas under `baml/european_union/`
- a 24-language registry
- 1 CocoIndex v1 embedding App
- Dagster L1 + L2 + L3 assets for every source
- 1 MotherDuck Dive + 1 daily MotherDuck Flight

## What changes

### 1. New umbrella spec `european-union-official-language-pipeline`

Adds `openspec/specs/european-union-official-language-pipeline/spec.md`
as the canonical spec for the EU institutional pipeline. It declares:

- the 24 EU official languages (with `ga` = Irish added 2022),
- the canonical DLT path contract (`dlt/european_union/<institution>/...`),
- the BAML extraction functions,
- the CocoIndex v1 App + LanceDB table layout,
- the MotherDuck Dive + daily Flight.

### 2. New DLT sources under `dlt/european_union/`

```text
dlt/european_union/
├── _shared/
│   ├── eu_languages.py           # the 24-language registry
│   └── eu_institutions.py        # the institution registry
├── eur_lex/
│   ├── treaties.py
│   ├── regulations.py
│   ├── directives.py
│   ├── decisions.py
│   └── cjeu_case_law.py
├── publications_office/
│   ├── eu_publications.py
│   └── cellar_documents.py
├── education/
│   ├── eurydice.py
│   ├── cedefop.py
│   └── school_education_gateway.py
├── medicine/
│   ├── ema_medicines_register.py
│   ├── ecdc_surveillance.py
│   └── european_health_data_space.py
├── statistics/
│   └── eurostat.py
└── government/
    ├── europa_portal.py
    ├── commission_press.py
    ├── parliament_documents.py
    └── council_documents.py
```

Every DLT source honours `USE_LOCAL_SCRAPES=true` by reading from
`stedding/ingest_queue/eu/<institution>/` and emits rows tagged with
`region="european_union"`, `institution=<institution>`,
`language ∈ {bg, hr, cs, da, nl, en, et, fi, fr, de, el, hu, ga, it,
lv, lt, mt, pl, pt, ro, sk, sl, es, sv}`, and the canonical DuckLake
namespace `cianfhoghlaim.<domain>.european_union.<institution>`.

### 3. New BAML schemas under `baml/european_union/`

```text
baml/european_union/
├── _shared/
│   ├── eu_languages.baml          # the 24-language enum
│   ├── eu_institutions.baml      # the institution enum
│   └── eu_document.baml          # the multilingual-document class
├── eur_lex_extraction.baml       # regulations / directives / case law
├── ema_extraction.baml           # medicines register
├── ecdc_extraction.baml          # surveillance + health alerts
├── eurydice_extraction.baml      # education information network
└── eurostat_extraction.baml      # statistics
```

The canonical extraction function is
`ExtractEUDocument(language: EULanguage, text: string) -> EUDocument`,
mirroring `b.ExtractCurriculumSyllabus` from the BIEP v1 stack.

### 4. New CocoIndex v1 App

`cocoindex/european_union_official_embedding.py` —
embeds every EU document into a single shared LanceDB table
`cianfhoghlaim.eu.official_chunks` using `BAAI/bge-m3` (the canonical 1024-d
multilingual embedder).

### 5. New Dagster L1 assets

```text
orchestration/defs/1_ingestion/european_union/
├── eur_lex/regulations/defs.yaml
├── eur_lex/directives/defs.yaml
├── eur_lex/cjeu_case_law/defs.yaml
├── publications_office/eu_publications/defs.yaml
├── education/eurydice/defs.yaml
├── medicine/ema_medicines_register/defs.yaml
├── medicine/ecdc_surveillance/defs.yaml
└── statistics/eurostat/defs.yaml
```

### 6. New Dagster L3 asset

`orchestration/defs/3_model_lifecycle/cocoindex_v1/european_union_official/defs.yaml`

### 7. New MotherDuck analytics

- 1 Dive: `eu_official_language_coverage` — cross-language coverage
  matrix of EU institutions by topic + language
- 1 daily Flight: `eu_official_daily_sync_flight` — daily BAML
  backfill for the 10 EU institutional sources

## What does NOT change

- The existing British Isles files are NOT renamed (per the Phase 0
  contract — the new contract is forward-only).
- The legacy `cianfhoghlaim.*` namespace pattern is preserved for the EU
  institutional namespace
  (`cianfhoghlaim.<domain>.european_union.<institution>`).
- The 24-language registry does NOT modify the existing
  `language_partitions` in `orchestration/partitions.py` (which lists
  the 6 Celtic languages). A parallel `eu_language_partitions`
  partition definition is added.

## Dependencies

```yaml
Blocked by: 2026-07-11-global-region-source-contract-v1
Blocked by (soft): 2026-07-15-pipeline-architecture-clarity-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-11-european-union-official-language-pipeline-v1 --strict` passes
- `openspec/specs/european-union-official-language-pipeline/spec.md` exists with at least 5 Requirements + 5 Scenarios
- The 14 DLT sources under `dlt/european_union/` exist + AST-parse
- The 6 BAML files under `baml/european_union/` exist + AST-parse
- The CocoIndex v1 App conforms to the R1–R4 contract
  (imports `from ._lifespan import shared_lifespan`)
- `mise run lint:skills` still passes
- Push target: `origin/main`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract that this change obeys
- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the seed instance of the contract
- [`cianfhoghlaim-pipeline`](../../specs/cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- [`cianfhoghlaim-baml-schemas`](../../specs/cianfhoghlaim-baml-schemas/spec.md) —
  the BAML cluster taxonomy
- [`cianfhoghlaim-marimo-dashboards`](../../specs/cianfhoghlaim-marimo-dashboards/spec.md) —
  the downstream marimo surface
- [`motherduck`](../..) — the MotherDuck Dives + Flights surface
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
