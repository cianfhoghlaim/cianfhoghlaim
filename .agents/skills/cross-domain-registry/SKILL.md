---
name: cross-domain-registry
description: KCG's `{nation}.{domain}.{entity}` asset-key contract for every DLT source and Dagster asset. 8 nations (ie/ni/en/sct/wls/iom/jey/ggy) × 5 domains (education/medicine/law/statistics/site_analysis) × 7 kinds. Sole truth: `oideachais/sources.yaml`. Use when adding a new DLT source, registering a new Dagster asset, migrating from legacy asset keys, or resolving a name collision between nations.
---

# Cross-Domain Asset-Key Registry

## When to use this skill

Use when you need to:

- "Add a new DLT source for a new corpus"
- "Register a new Dagster asset"
- "Migrate from legacy asset keys (e.g. `oideachais.curriculum_pages` → `oideachais.education.ie.curriculum.pages`)"
- "Resolve a name collision between nations"
- "Generate the contract validation report for the
  monorepo"

## The contract

Every DLT source and Dagster asset SHALL have an
asset-key of the form `{nation}.{domain}.{entity}`:

| Position | Allowed values | Description |
|:--|:--|:--|
| `nation` | `ie` / `ni` / `en` / `sct` / `wls` / `iom` / `jey` / `ggy` | ISO 3166-1 alpha-2 + Celtic extensions |
| `domain` | `education` / `medicine` / `law` / `statistics` / `site_analysis` | Knowledge domain |
| `entity` | kebab-case slug (e.g. `primary-curriculum`, `ccea-english`, `irish-statute-book`) | The specific corpus or asset |

The canonical registry is `oideachais/sources.yaml`. Every
DLT source registers there with metadata (URL, schedule,
auth, etc.).

## The 8 nations

| Code | Nation | Sample sources |
|:--|:--|:--|
| `ie` | Ireland (Republic) | NCCA, SEC, DES, Irish Statute Book |
| `ni` | Northern Ireland | CCEA, NI Direct, NISRA |
| `en` | England | DfE, Ofqual, UK Statistics |
| `sct` | Scotland | Education Scotland, SQA |
| `wls` | Wales | WJEC, Welsh Government |
| `iom` | Isle of Man | IoM Government |
| `jey` | Jersey | Government of Jersey |
| `ggy` | Guernsey | States of Guernsey |

## The 5 domains

| Domain | Use case |
|:--|:--|
| `education` | NCCA / SEC / CCEA / SQA / WJEC curriculum + exam papers |
| `medicine` | NHS, HSE, Irish health services, WHO |
| `law` | Irish Statute Book, NI legislation, UK laws |
| `statistics` | CSO, NISRA, ONS, NRS |
| `site_analysis` | BAML SiteAnalysis output (page-level fingerprints) |

## The 7 kinds

| Kind | Description |
|:--|:--|
| `pages` | Web pages (HTML) |
| `pdfs` | PDF documents |
| `api` | REST API responses |
| `tables` | Structured tabular data (CSV, Parquet) |
| `entities` | Extracted entities (BAML extraction) |
| `embeddings` | Vector embeddings |
| `kg` | Knowledge graph episodes |

## Naming conventions

| Layer | Convention | Example |
|:--|:--|:--|
| **DuckLake dataset** | `oideachais_{domain}_{nation}_{entity}` | `oideachais_education_ie_primary_curriculum` |
| **DuckLake schema** | `oideachais.{domain}.{nation}` | `oideachais.education.ie` |
| **LanceDB table** | `oideachais.{domain}.{nation}.{entity}` | `oideachais.education.ie.primary_curriculum` |
| **Cognee dataset** | `oideachais_{domain}_{nation}` | `oideachais_education_ie` |
| **Dagster asset key** | `["{nation}", "{domain}", "{entity_slug}"]` | `["ie", "education", "primary_curriculum"]` |
| **Dagster group** | `{domain}_{nation}` | `education_ie` |

## SourceFactory pydantic validator

The contract is enforced at code-load time by
`oideachais/dlt_utils/source_factory.py:SourceFactory`:

```python
from pydantic import BaseModel, Field
from enum import Enum


class Nation(str, Enum):
    IE = "ie"
    NI = "ni"
    EN = "en"
    SCT = "sct"
    WLS = "wls"
    IOM = "iom"
    JEY = "jey"
    GGY = "ggy"


class Domain(str, Enum):
    EDUCATION = "education"
    MEDICINE = "medicine"
    LAW = "law"
    STATISTICS = "statistics"
    SITE_ANALYSIS = "site_analysis"


class SourceSpec(BaseModel):
    """One DLT source, registered in oideachais/sources.yaml."""

    nation: Nation
    domain: Domain
    entity: str = Field(pattern=r"^[a-z][a-z0-9-]*[a-z0-9]$")
    url: str
    schedule: str = "0 */6 * * *"  # cron
    kind: str = "pages"  # pages/pdfs/api/tables/entities/embeddings/kg
```

Any source that fails the contract raises `ValidationError`
at load time, preventing malformed asset keys from entering
the system.

## Coverage report

```bash
uv run --package oideachais python -m oideachais.sources.sources_validation
# OR with --strict to fail on missing nations:
uv run --package oideachais python -m oideachais.sources.sources_validation --strict
```

The report shows:
- Total registered sources
- Per-nation / per-domain / per-kind counts
- Missing combinations (e.g. `iom` × `medicine` is currently empty)
- Backwards-compat aliases still in use

## Backwards-compat aliases

The legacy asset keys (e.g. `oideachais.curriculum_pages`)
are resolved via `oideachais/dagster_defs/definitions.py:BACKWARDS_COMPAT_ASSET_ALIASES`.
The alias table is removed in a follow-on `drop-asset-key-aliases`
change.

| Legacy key | New key |
|:--|:--|
| `oideachais.curriculum_pages` | `oideachais.education.ie.curriculum.pages` |
| `uk.education.northern_ireland.ccea_pages` | `oideachais.education.ni.ccea.pages` |
| `oideachais.site_analysis` | `oideachais.site_analysis.ie.site_analysis` |

## Adding a new source (5-step workflow)

```bash
# 1. Add the source to oideachais/sources.yaml
cat >> oideachais/sources.yaml <<'EOF'
- name: "IoM Government - Education"
  nation: iom
  domain: education
  entity: iom-education
  url: "https://www.gov.im/education"
  schedule: "0 0 * * 0"
  kind: pages
EOF

# 2. Run the contract validator
uv run --package oideachais python -m oideachais.sources.sources_validation

# 3. Implement the DLT source (under oideachais/dlt_sources/)
# File: oideachais/dlt_sources/iom/education.py

# 4. Register the Dagster asset (under oideachais/dagster_defs/assets/)
# File: oideachais/dagster_defs/assets/iom/education.py

# 5. Re-run validation --strict
uv run --package oideachais python -m oideachais.sources.sources_validation --strict
```

## Cross-references

- `oideachais/sources.yaml` — the canonical registry
- `.agents/skills/oideachas-pipeline/SKILL.md` — the
  oideachais pipeline (the source of the contract)
- `.agents/skills/change-detection/SKILL.md` — sitemap
  sensors (per-source change watching)
- `.agents/skills/dlt/SKILL.md` — DLT pipeline patterns
- `.agents/skills/dagster/SKILL.md` — Dagster asset
  patterns
- `.agents/skills/oideachais-storage/SKILL.md` — storage
  mental model
