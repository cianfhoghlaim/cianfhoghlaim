---
name: cross-domain-registry
description: KCG's `{nation}.{domain}.{entity}` asset-key contract for every DLT source and Dagster asset. 8 nations (ie/ni/en/sct/wls/iom/jey/ggy) × 5 domains (education/medicine/law/statistics/site_analysis) × 7 kinds. Sole truth: `sruth/cianfhoghlaim/sources.yaml`. Use when adding a new DLT source, registering a new Dagster asset, migrating from legacy asset keys, or resolving a name collision between nations.
---

# Cross-Domain Asset-Key Registry

## When to use this skill

Use when you need to:

- "Add a new DLT source for a new corpus"
- "Register a new Dagster asset"
- "Migrate from legacy asset keys (e.g. `cianfhoghlaim.curriculum_pages` → `cianfhoghlaim.education.ie.curriculum.pages`)"
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

The canonical registry is `sruth/cianfhoghlaim/sources.yaml`. Every
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
| **DuckLake dataset** | `cianfhoghlaim_{domain}_{nation}_{entity}` | `cianfhoghlaim_education_ie_primary_curriculum` |
| **DuckLake schema** | `cianfhoghlaim.{domain}.{nation}` | `cianfhoghlaim.education.ie` |
| **LanceDB table** | `cianfhoghlaim.{domain}.{nation}.{entity}` | `cianfhoghlaim.education.ie.primary_curriculum` |
| **Cognee dataset** | `cianfhoghlaim_{domain}_{nation}` | `cianfhoghlaim_education_ie` |
| **Dagster asset key** | `["{nation}", "{domain}", "{entity_slug}"]` | `["ie", "education", "primary_curriculum"]` |
| **Dagster group** | `{domain}_{nation}` | `education_ie` |

## SourceFactory pydantic validator

The contract is enforced at code-load time by
`sruth/cianfhoghlaim/dlt_utils/source_factory.py:SourceFactory`:

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
    """One DLT source, registered in sruth/cianfhoghlaim/sources.yaml."""

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
uv run --package oideachais python -m cianfhoghlaim.sources.sources_validation
# OR with --strict to fail on missing nations:
uv run --package oideachais python -m cianfhoghlaim.sources.sources_validation --strict
```

The report shows:
- Total registered sources
- Per-nation / per-domain / per-kind counts
- Missing combinations (e.g. `iom` × `medicine` is currently empty)
- Backwards-compat aliases still in use

## Backwards-compat aliases

The legacy asset keys (e.g. `cianfhoghlaim.curriculum_pages`)
are resolved via `sruth/cianfhoghlaim/dagster_defs/definitions.py:BACKWARDS_COMPAT_ASSET_ALIASES`.
The alias table is removed in a follow-on `drop-asset-key-aliases`
change.

| Legacy key | New key |
|:--|:--|
| `cianfhoghlaim.curriculum_pages` | `cianfhoghlaim.education.ie.curriculum.pages` |
| `uk.education.northern_ireland.ccea_pages` | `cianfhoghlaim.education.ni.ccea.pages` |
| `cianfhoghlaim.site_analysis` | `cianfhoghlaim.site_analysis.ie.site_analysis` |

## Adding a new source (5-step workflow)

```bash
# 1. Add the source to sruth/cianfhoghlaim/sources.yaml
cat >> sruth/cianfhoghlaim/sources.yaml <<'EOF'
- name: "IoM Government - Education"
  nation: iom
  domain: education
  entity: iom-education
  url: "https://www.gov.im/education"
  schedule: "0 0 * * 0"
  kind: pages
EOF

# 2. Run the contract validator
uv run --package oideachais python -m cianfhoghlaim.sources.sources_validation

# 3. Implement the DLT source (under sruth/cianfhoghlaim/dlt_sources/)
# File: sruth/cianfhoghlaim/dlt_sources/iom/education.py

# 4. Register the Dagster asset (under sruth/cianfhoghlaim/dagster_defs/assets/)
# File: sruth/cianfhoghlaim/dagster_defs/assets/iom/education.py

# 5. Re-run validation --strict
uv run --package oideachais python -m cianfhoghlaim.sources.sources_validation --strict
```

## Cross-references

- `sruth/cianfhoghlaim/sources.yaml` — the canonical registry
- `.agents/skills/oideachas-pipeline/SKILL.md` — the
  oideachais pipeline (the source of the contract)
- `.agents/skills/change-detection/SKILL.md` — sitemap
  sensors (per-source change watching)
- `.agents/skills/dlt/SKILL.md` — DLT pipeline patterns
- `.agents/skills/dagster/SKILL.md` — Dagster asset
  patterns
- `.agents/skills/cianfhoghlaim-storage/SKILL.md` — storage
  mental model

## 2024-25 census + fiscal context for the 8 nations

The `{nation}.{domain}.{entity}` contract describes the
**shape** of every asset key. The 2024-25 education
landscape (IFS / NCCA / DES / Welsh Government / Scottish
Government / NISRA / States of Jersey / Isle of Man
Government data) explains **why** certain assets are
sparse, over-funded, or have shifting source URLs.
Carry this context when wiring new sources.

### The demographic crunch (UK-wide, 2025-2035)

IFS forecasts a **7% drop in 0-15 population** in the
UK by 2035 (-800k children), with severe regional
variance:

| Nation | 2025-2035 forecast | 2024-25 status |
|:--|:--|:--|
| `ni` (Northern Ireland) | **-15%** (steepest) | Education budget £2.8B, real-terms cut; CnaG budget -12% real |
| `wls` (Wales) | **-10%** | Schools budget £3.59B (+7.4% cash); Disadvantage Gap Index widened to 3.14 |
| `sct` (Scotland) | -8% | Gaelic Specific Grant ~£940k to Highland; vernacular crisis in Na h-Eileanan Siar |
| `en` (England) | -6% | 9.03M state-funded pupils (-59,600 YoY); EBacc focus; German entries halved since 2002 |
| `ie` (Republic) | rising primary | 153 Gaelscoileanna + 103 Gaeltacht; 8% primary; only 3.8% post-primary; 13 counties with no IME secondary |
| `iom` (Isle of Man) | small, stable | DESC budget £141M (+£18M); Bunscoill Ghaelgagh produces ~170 fluent Manx speakers |
| `jey` (Jersey) | not in IFS sample | Small jurisdiction; curriculum parallels English model with light customisation |
| `ggy` (Guernsey) | not in IFS sample | Small jurisdiction; Education Services managed by States of Guernsey |

Implication: as pupil numbers fall, **per-pupil
spending can rise** if budgets are protected; but
historical precedent (1970s/80s England: -25% pupils,
-14% teachers) suggests resource consolidation is more
likely. Plan sources for **per-school ingestion** rather
than per-LA-level aggregates.

### Language policy divergence (Celtic-language context)

| Nation | Statutory framework | KCG asset-key pattern |
|:--|:--|:--|
| `wls` | **Cymraeg 2050** (statutory 1M speakers by 2050) | `wls.education.cymraeg_2050.*` |
| `sct` | Gaelic Language (Scotland) Act 2005; **demand-led GME** | `sct.education.gme.*` (87% of GME secondary in 3 councils) |
| `ni` | **Identity & Language (NI) Act 2022**; IME statutory | `ni.education.ime.*` (30 standalone + 10 units; 7414 pupils 2024) |
| `ie` | Gaeltacht Act 2012; Policy on Gaeltacht Education 2017 | `ie.education.gaeltacht.*`, `ie.education.gaelscoileanna.*` |
| `iom` | Manx Language Strategy 2022-2032 (5000 speakers target) | `iom.education.bunscoill_ghaelgagh.*` |
| `jey` / `ggy` | no minority language framework | `jey.education.*`, `ggy.education.*` (English-only) |
| `en` | EBacc; Modern Foreign Languages decline | `en.education.ebacc.*` |

### The teacher-pipeline failure (all 4 nations)

A universal theme: Initial Teacher Education (ITE) cannot
produce enough linguistically competent teachers to meet
the statutory targets. KCG data sources are affected:

- **Wales:** ITE recruitment at 62% of secondary target;
  **Welsh-as-subject at 15% of target**. Welsh-medium
  secondary needs ~1,171 additional teachers by 2031.
- **Scotland:** GME secondary subject-specialist shortage
  (87% of GME secondary in 3 councils = brittleness).
- **NI:** >50% of post-primary IME vacancies unfilled
  (only 8 suitably qualified graduates 2023/24).
- **ROI:** 43% of Gaelscoileanna have long-term teacher
  vacancies (vs 10% in English-medium). INTO calls
  this "Government indifference".

When wiring a DLT source that monitors teacher supply
(NCTL/ITE outcomes, GAELSCOIL vacancies), prefer
**per-school sources** over LA-level aggregates so the
asset key captures the supply-constraint signal.

### The "supply-demand paradox"

Across all 5 jurisdictions, demand for Celtic-medium
education is **robust and growing** (parental preference
for the "bilingual advantage"). Supply is artificially
capped by **structural constraints** that differ by
nation:

- `wls` → **workforce-defined** cap (Welsh-speaking teachers)
- `ni` / `ie` → **capital-defined** cap (school buildings;
  16/21 new NI IME primaries are in temporary accommodation)
- `sct` → **geographic / admin** cap (GME present in Glasgow
  + Highlands; absent in 29 of 32 council areas)

KCG implication: when adding sources that monitor
provision, the `{nation}.education.{entity}.capacity`
key is more valuable than the `{nation}.education.{entity}.enrollment`
key — it captures the **bottleneck**, not the demand.

### Where the 2024-25 data lives (parallel data sources)

Cross-nation comparability is hard (different exam
systems: GCSE vs National 5 vs Junior Cert vs H1-H8
grading; different deprivation indices: IMD vs SIMD
vs WIMD vs NIMDM vs Pobal HP). The KCG convention:

- Use **percentile ranks** within each nation (not raw
  grades) for attainment comparison
- Use **decile ranks 1-10** for deprivation (not absolute
  IMD scores)
- Aggregate to **local authority / council level**
  before any cross-border join
- Note **qualification-reform years** in time-series
  (Wales 2019, England 2017+ for 9-1 GCSE, ROI 2017 H1-H8)

The reference table for the per-nation open-data portals,
exam boards, and deprivation indices is the 286-line
parallel-data source map at
[`celtic-asset-generation/references/british-isles-parallel-edu.md`](../celtic-asset-generation/references/british-isles-parallel-edu.md).
See also the 305-line "State of Education and Celtic
Language Revitalisation in the British Isles" report (formerly at
`docs/teanga/British Isles Celtic Language Education Data.md`,
superseded by the round-8 docs → skills migration) for the
full 2024-25 demographic + fiscal deep dive.
