---
title: 'Cross-Domain Asset-Key Registry'
domain: 'data_platform'
status: 'stable'
description: 'The {nation}.{domain}.{entity} contract for every DLT source and Dagster asset. Authoritative reference: oideachais/sources.yaml.'
read_when:
  - adding a new DLT source
  - registering a new Dagster asset
  - migrating from legacy asset keys
truth: sole
updated: '2026-06-13'
ccc_query_hints:
  - cross domain registry asset key nation domain entity
  - sources.yaml canonical
---

# Cross-Domain Asset-Key Registry

> **One line:**
> Every DLT source / Dagster asset in the platform is identified by
> `["{nation}", "{domain}", ...]` where `nation ∈ {ie, ni, en, sct, wls, iom, jey, ggy}`
> and `domain ∈ {education, medicine, law, statistics, site_analysis}`.
> The canonical source of truth is [`oideachais/sources.yaml`](../../oideachais/sources.yaml).

## The contract

| Position | Value | Notes |
|---|---|---|
| 0 | nation | `ie \| ni \| en \| sct \| wls \| iom \| jey \| ggy` |
| 1 | domain | `education \| medicine \| law \| statistics \| site_analysis` |
| 2 | entity_slug | the YAML `id` suffix, e.g. `ncca`, `irish_statute_book` |
| 3+ | (optional) | the specific resource/table, e.g. `pages`, `acts`, `guidelines_pages` |

The YAML `id` is `{nation}.{domain}.{entity}` and **must always** match
the first three positions of `asset_key`. The `SourceFactory`
([`oideachais/dlt_utils/source_factory.py`](../../oideachais/dlt_utils/source_factory.py))
enforces this with a pydantic validator.

## Nations (8)

| Code | Name | Jurisdiction |
|---|---|---|
| `ie` | Ireland | EU (euro) |
| `ni` | Northern Ireland | UK |
| `en` | England | UK |
| `sct` | Scotland | UK |
| `wls` | Wales | UK |
| `iom` | Isle of Man | Crown dependency |
| `jey` | Jersey | Crown dependency |
| `ggy` | Guernsey | Crown dependency |

## Domains (5)

| Domain | Notes | Status |
|---|---|---|
| `education` | Curriculum, exam boards, inspection reports | **active** — 24 sources across 8 nations |
| `medicine` | Health service + medical register pages | **active** — 8 sources (IE + 4 UK) |
| `law` | **Statutory only** (no case law yet) | **active** — 8 sources (IE + 4 UK) |
| `statistics` | Census / open data | scaffold (reserved) |
| `site_analysis` | firecrawl + browserbase MCP page fingerprints | **active** — 1 source (1 row per public source) |

## Kinds (7)

`firecrawl_pages`, `stagehand_papers`, `browserbase_extract`,
`api_table`, `api_xml`, `filesystem_csv`, `filesystem_parquet`.

## Sample entries (43 total in `oideachais/sources.yaml`)

| id | nation | domain | kind | asset_key |
|---|---|---|---|---|
| `ie.education.ncca` | ie | education | firecrawl_pages | `[ie, education, ncca, pages]` |
| `ni.education.ccea` | ni | education | firecrawl_pages | `[ni, education, ccea, pages]` |
| `en.education.dfe` | en | education | api_table | `[en, education, dfe, statistics]` |
| `wls.education.cfw` | wls | education | firecrawl_pages | `[wls, education, cfw, pages]` |
| `iom.education.desc` | iom | education | firecrawl_pages | `[iom, education, desc, pages]` |
| `ie.medicine.hse` | ie | medicine | firecrawl_pages | `[ie, medicine, hse, pages]` |
| `en.medicine.gmc` | en | medicine | api_table | `[en, medicine, gmc, register]` |
| `ie.law.irish_statute_book` | ie | law | api_xml | `[ie, law, irish_statute_book, acts]` |
| `en.law.legislation` | en | law | api_xml | `[en, law, legislation, uk]` |
| `site_analysis` (singleton) | — | site_analysis | (composite) | `[oideachais, site_analysis, extract/embed/cognify]` |

The full list is in `oideachais/sources.yaml`. A coverage report
emits which sources are missing DLT / Lance / Cognee / marimo / pytest
artefacts:

```bash
uv run --package oideachais python -m oideachais.sources.sources_validation
uv run --package oideachais python -m oideachais.sources.sources_validation --strict
```

## DuckLake schema convention

Every DLT `dataset_name` is `oideachais_{domain}_{nation}_{entity}` (e.g.
`oideachais_education_ie_ncca`) so per-source state files stay small.
The underlying DuckLake **schema** is `oideachais.{domain}.{nation}`.
Tables within the schema are the per-source resource names
(`pages`, `acts`, `register`, etc.).

## LanceDB / Cognee naming

- **LanceDB** table: `oideachais.{domain}.{nation}.{entity}` (matches
  the DuckLake schema). Override per-source via the `embedding.table`
  field in `sources.yaml`.
- **Cognee** dataset: `oideachais_{domain}_{nation}` (one per source).
  Override per-source via the `kg.dataset` field in `sources.yaml`.
  Cross-domain edges live in a single `oideachais_cross_nation` dataset.

## Backwards-compat

Legacy asset keys (`["ireland", "curriculum", …]` /
`["uk", "education", "northern_ireland", …]`) remain resolvable via a
one-shot alias table in
`oideachais/dagster_defs/definitions.py:BACKWARDS_COMPAT_ASSET_ALIASES`.
The alias is removed in a follow-on `drop-asset-key-aliases` change.

## See also

- [`oideachais/sources.yaml`](../../oideachais/sources.yaml) — the canonical source registry
- [`oideachais/dlt_utils/source_factory.py`](../../oideachais/dlt_utils/source_factory.py) — the 7-method factory
- [`oideachais/tests/sources/test_sources_yaml_schema.py`](../../oideachais/tests/sources/test_sources_yaml_schema.py) — schema validation tests
- [`oideachais/dagster_defs/definitions.py`](../../oideachais/dagster_defs/definitions.py) — the alias table
