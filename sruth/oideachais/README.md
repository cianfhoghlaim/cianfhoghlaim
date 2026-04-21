# Oideachais — Celtic Education Platform

Oideachais is a pan-Celtic curriculum search, content management, and learning outcomes platform. It leverages AI to bridge the gap between official curriculum documents and interactive learning experiences.

## Architecture

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    Celtic Education Platform                  │
                    └─────────────────────────────────────────────────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         │                                    │                                    │
         ▼                                    ▼                                    ▼
┌─────────────────┐              ┌─────────────────────┐              ┌─────────────────┐
│   DLT Sources   │              │   Dagster Assets    │              │   ADK Agents    │
│                 │              │                     │              │                 │
│ • Ireland (8)   │──────────────│ • ireland_education │──────────────│ • RootAgent     │
│ • UK (12)       │              │ • uk_education      │              │ • Curriculum    │
│ • Celtic (6)    │              │ • celtic_language   │              │ • Geospatial    │
│ • Geospatial(4) │              │ • geospatial        │              │ • Translation   │
└─────────────────┘              │ • embeddings        │              │ • Corpus        │
                                 │ • evaluation        │              │ • Statistics    │
                                 └─────────────────────┘              └─────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         │                                    │                                    │
         ▼                                    ▼                                    ▼
┌─────────────────┐              ┌─────────────────────┐              ┌─────────────────┐
│    Storage      │              │   CocoIndex Flows   │              │  Observability  │
│                 │              │                     │              │                 │
│ • DuckDB        │◄─────────────│ • curriculum_embed  │─────────────►│ • Datadog APM   │
│ • LanceDB       │              │ • translation       │              │ • Datadog LLMObs│
│ • Memgraph      │              │ • geospatial_index  │              │ • MLflow        │
└─────────────────┘              └─────────────────────┘              │ • Langfuse      │
                                                                      │ • Ragas         │
                                                                      │ • Kafka         │
                                                                      └─────────────────┘
```

## 🛠 Deployment Configuration

- **Development**: Managed via `compose.dev.yaml` for local hot-reloading.
- **Production**: Deployed as a **Komodo Stack** on the **MacBook M4 Max**.
- **Secrets**: Injected via **Locket** sidecar, pulling from 1Password.
- **Routing**: Securely exposed via **Pangolin** at `oideachais.cianfhoghlaim.ie`.

---

## 🇮🇪 Ireland Education Pipelines

The `dlt_sources/ireland/` directory is the primary data ingestion layer for the Republic of Ireland's education system. It provides a comprehensive suite of DLT (Data Load Tool) sources that crawl, extract, normalise, and deduplicate curriculum data from every major Irish education body.

### Data Sources

The pipelines ingest data from five principal Irish education organisations, each serving a distinct role in the national education infrastructure:

| Source | Organisation | URL | Description |
| :--- | :--- | :--- | :--- |
| **Curriculum Online** | NCCA | `curriculumonline.ie` | The official portal for all Irish curriculum documentation — from Aistear (Early Childhood, ages 1–6) through Primary (5–12), Junior Cycle (12–15), and Senior Cycle (16–18). Bilingual (English/Irish). |
| **NCCA** | National Council for Curriculum and Assessment | `ncca.ie` | The statutory body responsible for curriculum development and assessment policy. Publishes specifications, guidelines, and consultation documents. |
| **SEC** | State Examinations Commission | `examinations.ie` | Administers the Junior Certificate and Leaving Certificate examinations. Provides chief examiner reports, marking schemes, exam material archives, and statistics. |
| **Oide** | Education Support Services | `oide.ie` | Delivers continuing professional development (CPD) for teachers. Contains subject-specific support materials and pedagogical resources. |
| **Department of Education** | Gov.ie | `gov.ie/en/organisation/department-of-education/` | Government education policy, circulars, and official guidance documents. |

### Pipeline Modules

#### Core Curriculum Ingestion

- **[`curriculum_source.py`](dlt_sources/ireland/curriculum_source.py)** — The unified entry point. Merges content from curriculumonline.ie, ncca.ie, and examinations.ie into a single, deduplicated data source organised by `(cycle, subject, language)`. Supports subject-centric crawling with cross-source content hashing and provenance tracking.

- **[`curriculum_registry.py`](dlt_sources/ireland/curriculum_registry.py)** — Subject taxonomy and URL resolution engine. Reads from `curriculum_index.json` to provide a centralised registry of all Irish curriculum subjects, their associated cycles (Junior Cycle, Senior Cycle), levels (Foundation, Ordinary, Higher), and source-specific URL patterns. Generates crawl configurations for each subject.

- **[`curriculum_document.py`](dlt_sources/ireland/curriculum_document.py)** — Unified Pydantic model for all Irish curriculum documents. Defines the core data schema including `LearningOutcome`, `AssessmentInfo`, `ContentQuality`, `EducationLevel`, and `Language` (en/ga/bilingual) enums. Handles NCCA specifications, SEC exam papers, Department circulars, and textbook content.

#### Per-Subject Sources (`subjects/`)

- **[`subjects/base.py`](dlt_sources/ireland/subjects/base.py)** — Foundation for per-subject DLT resources. Handles subject-specific URL resolution, Firecrawl crawling with rate limiting, PDF URL extraction from pages, bilingual support (EN/GA), and content hashing for deduplication.

- **[`subjects/junior_cycle.py`](dlt_sources/ireland/subjects/junior_cycle.py)** — Per-subject DLT resources for all 18 Junior Cycle subjects (Applied Technology, Business Studies, Classics, Engineering, English, Gaeilge, Geography, Graphics, History, Home Economics, Mathematics, MFL, Music, Religious Education, Science, Visual Art, Wood Technology). Each subject yields pages and PDF URLs from curriculumonline.ie.

- **[`subjects/senior_cycle.py`](dlt_sources/ireland/subjects/senior_cycle.py)** — Per-subject DLT resources for all 34 Leaving Certificate subjects (Accounting through Technology). Each subject yields pages and PDF URLs from curriculumonline.ie and ncca.ie.

#### Source Adapters & Normalisation

- **[`source_adapters.py`](dlt_sources/ireland/source_adapters.py)** — Normalises output from different curriculum sources into a consistent `NormalizedPage` format. Implements the `SourceAdapter` protocol with concrete adapters for CurriculumOnline, NCCA, and Examinations.ie. Handles source-specific URL patterns, bilingual content (English/Irish), and metadata extraction (cycle, subject) from URLs.

- **[`content_deduplication.py`](dlt_sources/ireland/content_deduplication.py)** — Cross-source content deduplication via content hashing. Tracks source provenance (which source provided which content), resolves canonical URLs, and manages incremental state to avoid re-processing unchanged pages.

- **[`education_sources.py`](dlt_sources/ireland/education_sources.py)** — Configuration registry for all Irish education websites, including their URLs, supported languages, education stages, and descriptions.

#### Examination Data

- **[`exam_source.py`](dlt_sources/ireland/exam_source.py)** — DLT source for examinations.ie. Crawls and extracts chief examiner reports (200+ PDFs), exam material archives, marking schemes, statistics, and circulars. Uses Firecrawl for web crawling with configurable content type filtering.

- **[`sec_aural_transcripts.py`](dlt_sources/ireland/sec_aural_transcripts.py)** — Parses structured transcript data from SEC aural exam scripts. Supports Irish Leaving Certificate aural transcripts with dialect tags (Connacht, Munster, Ulster), French/German/Spanish listening comprehension, and Junior Cycle aural components. Aligns with Canuint word-level alignments for unified training. Uses PyMuPDF4LLM for PDF extraction and BAML for structured entity extraction.

- **[`edcolearning.py`](dlt_sources/ireland/edcolearning.py)** — Extracts Leaving Certificate exam audio resources from EdcoLearning.ie. Handles session-based authentication, Azure Blob storage access, and audio metadata extraction (year, level, language, paper type) for Irish, French, German, and Spanish exams.

#### Intelligent Discovery

- **[`agentic_discovery.py`](dlt_sources/ireland/agentic_discovery.py)** — Uses the Firecrawl agent for autonomous URL discovery and structured data extraction across Irish educational websites. Supports natural language discovery prompts (e.g., "Find all 2024 exam papers for Irish"), schema-driven extraction, multi-site coordination, and PDF/document discovery.

- **[`json_seed.py`](dlt_sources/ireland/json_seed.py)** — Loads pre-existing scraped JSON data (from ncca.ie, curriculumonline.ie, examinations.ie) as seed data for pipeline bootstrapping. Normalises disparate JSON structures into a consistent schema for augmentation via Firecrawl.

#### Statistical & Geospatial Data (`statistics/`)

The `statistics/` subdirectory provides DLT sources for Irish national statistics that contextualise education data:

- **[`statistics/cso_small_areas.py`](dlt_sources/ireland/statistics/cso_small_areas.py)** — Fetches Small Area statistics from the CSO (Central Statistics Office) PxStat API. Ireland's 18,641 Small Areas are the most granular geographic unit for census data. Covers population, age groups, educational attainment, housing, employment, and Irish language speakers (Census 2022 tables).

- **[`statistics/geohive.py`](dlt_sources/ireland/statistics/geohive.py)** — Fetches geospatial boundaries from GeoHive.ie (ArcGIS FeatureServer). Provides Small Area boundaries, county boundaries, and Electoral Division boundaries for spatial joins with census and education data.

- **[`statistics/met_office.py`](dlt_sources/ireland/statistics/met_office.py)** — UK Met Office DataHub integration for weather observations and climate data, supporting cross-border environmental context for education research.

### Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Irish Education Data Sources                   │
├──────────────┬──────────────┬──────────────┬─────────────────────┤
│ curriculum   │ examinations │    ncca.ie   │    oide.ie          │
│ online.ie    │     .ie      │              │                     │
└──────┬───────┴──────┬───────┴──────┬───────┴──────────┬──────────┘
       │              │              │                  │
       ▼              ▼              ▼                  ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Source Adapters (Normalisation)                │
│  CurriculumOnlineAdapter │ NCCAAdapter │ ExaminationsAdapter     │
└──────────────────────┬───────────────────────────────────────────┘
                       │  NormalizedPage
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│              Content Deduplication & Provenance                   │
│         (content hashing, canonical URL resolution)              │
└──────────────────────┬───────────────────────────────────────────┘
                       │  Deduplicated pages
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│              Curriculum Registry (Subject Taxonomy)               │
│    (cycle → subject → language → source URL resolution)          │
└──────────────────────┬───────────────────────────────────────────┘
                       │  Structured curriculum data
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                    DLT Pipeline → DuckDB / LanceDB                │
│              (persisted to Cloudflare R2 via DuckLake)            │
└──────────────────────────────────────────────────────────────────┘
```

### Education Levels Covered

The Ireland pipelines cover the full spectrum of the Irish education system:

| Level | Ages | Qualifications |
| :--- | :--- | :--- |
| **Aistear** (Early Childhood) | 1–6 | Early Childhood Curriculum Framework |
| **Primary** | 5–12 | Primary School Curriculum (incl. redeveloped 2025 curriculum) |
| **Junior Cycle** | 12–15 | Junior Certificate / Junior Cycle (Level 1 & 2 LPs, Short Courses) |
| **Senior Cycle** | 16–18 | Leaving Certificate (Established, LCA, LCVP) |
| **Further Education** | 18+ | FETAC / QQI levels |

### Bilingual Support

All pipeline modules support **bilingual content extraction** (English and Irish/Gaeilge). The `curriculumonline.ie` and `ncca.ie` sources maintain parallel content trees accessible via language prefixes (e.g., `/ga-ie/`). Source adapters handle language-specific URL routing and normalise both language variants into the unified schema.

### Quick Start

```python
import dlt
from sruth.oideachais.dlt_sources.ireland import curriculum_source

# Crawl Junior Cycle Mathematics (English)
pipeline = dlt.pipeline(
    pipeline_name="ireland_curriculum",
    destination="duckdb",
    dataset_name="ireland_education",
)

# Ingest all Junior Cycle subjects from all sources
pipeline.run(curriculum_source(
    cycle="junior_cycle",
    language="en",
))

# Or target a specific subject
pipeline.run(curriculum_source(
    cycle="senior_cycle",
    subject="mathematics",
    language="en",
))

# Per-subject sources for fine-grained control
from sruth.oideachais.dlt_sources.ireland.subjects import (
    senior_cycle_source,
    junior_cycle_source,
)

# All 34 Senior Cycle subjects
pipeline.run(senior_cycle_source(language="en"))

# All 18 Junior Cycle subjects
pipeline.run(junior_cycle_source(language="ga"))
```

---

## 📂 Pipeline Directory Structure

```
dlt_sources/
├── ireland/                        # 🇮🇪 Republic of Ireland
│   ├── curriculum_source.py        # Unified curriculum DLT source
│   ├── curriculum_registry.py      # Subject taxonomy & URL resolution
│   ├── curriculum_document.py      # Pydantic document models
│   ├── source_adapters.py          # Source normalisation adapters
│   ├── content_deduplication.py    # Cross-source deduplication
│   ├── education_sources.py        # Source site configurations
│   ├── exam_source.py              # SEC examinations source
│   ├── sec_aural_transcripts.py    # Aural transcript parsing
│   ├── edcolearning.py             # EdcoLearning audio resources
│   ├── agentic_discovery.py        # Firecrawl agent discovery
│   ├── json_seed.py                # Seed data loader
│   ├── subjects/                   # Per-subject DLT sources
│   │   ├── base.py                 # Subject source foundation
│   │   ├── junior_cycle.py         # 18 Junior Cycle subjects
│   │   └── senior_cycle.py         # 34 Leaving Certificate subjects
│   └── statistics/                 # Statistical & geospatial sources
│       ├── cso_small_areas.py      # CSO census data
│       ├── geohive.py              # GeoHive boundaries
│       └── met_office.py           # Weather/climate data
├── northern_ireland/               # Northern Ireland (UK)
│   ├── ccea_curriculum.py          # CCEA curriculum
│   ├── education_ni.py             # Education NI
│   ├── etini.py                    # ETI NI inspections
│   └── nisra.py                    # NISRA statistics
├── great_britain/                  # England, Scotland, Wales
│   ├── england/                    # National Curriculum, DfE, Ofsted
│   ├── scotland/                   # CfE, SIMD, Insight
│   └── wales/                      # Curriculum for Wales, Estyn
└── crown_dependencies/             # Channel Islands, Isle of Man
```
