# Oideachais (Kings' College Galway) by Cianfhoghlaim - Unified Celtic Education Platform

*v0.5 A unified data platform and research repository for education and cultural preservation.*

> ⚠️ **Project Status & Disclaimer**
> 
> This repository is a **work in progress**. It is being actively set up to automatically update as syllabus and exam papers change over time. The goal is to have a working prototype prior to this year's secondary school Leaving Certificate Computer Science exam, though this is not guaranteed.
> 
> Please note that folder structures, README files, packages used, and architectural decisions are all subject to change. Many aspects of the project were designed in line with previous hackathons; the use of specific software or packages is not an endorsement, and the rationale for these choices will be explained later.
> 
> This project is being developed publicly as an attempt to demonstrate how to coalesce various open-source repositories and documentation (as found in our `docs/` folder) into a workable, large-scale project.
> 
> This is made possible thanks to massive improvements in the development process brought about by breakthroughs in large language coding models assisting a lone developer. The primary AI agent toolchain driving this project includes **Gemini CLI**, **Roo Code**, **GitHub Copilot**, assorted **MCP (Model Context Protocol) servers**, and open-source **HuggingFace models**.

Oideachais is an advanced, AI-driven educational data platform designed to standardize curriculums across the British Isles. Beginning with a focus on English-language curriculums (GCSE, A-Level, Junior Cycle, Leaving Certificate), the platform's ultimate mission is to evolve into a comprehensive digital sanctuary for Celtic language educational nations (Ireland, Scotland, Wales, Isle of Man, Cornwall, Brittany).

## 🏗️ Core Architecture: Sruthanna

The project is organized into domain-specific 'streams' (**sruthanna**) within the `sruth/` directory. This architecture utilizes a **Hybrid Strategy** that balances local high-performance compute with cloud-based orchestration.

### 🌊 The Streams (Sruthanna)

| Stream | Domain | Key Technologies & Architecture |
| :--- | :--- | :--- |
| `sruth/bonneagar/` | **Infrastructure (Taisce)** | **Multi-Cloud Zero-Trust Platform:** Pulumi IaC (Hetzner ARM + OCI ARM + Cloudflare WAF), Komodo GitOps orchestration (50+ services, 60+ procedures), Pangolin WireGuard networking (SSO, CrowdSec WAF, multi-tenant Traefik routing), Browser Automation (Hunter-Gatherer-Operator pattern), and ~45 modular Docker stacks. Secrets via 1Password Connect + Locket sidecars. |
| `sruth/oideachais/` | **Education Platform** | **Full-Stack AI Education:** TanStack Start (Frontend), FastAPI (API), Dagster v1.13 (Orchestration), and DuckLake/LanceDB (Storage). Transforms curriculums into interactive learning outcomes via Gemini 2.0/Claude 3.7. |
| `sruth/meaisínfhoghlaim/` | **Intelligence** | Opensource Huggingface.co model finetuning and educational asset generation in English and minority languages. |
| `sruth/códeolas/` | **Code Intel** | **Beads & Chunkhound:** Deep codebase analysis and indexing via MCP (Model Context Protocol) servers. |
| `sruth/crypteolas/` | **Finance Intel** | Agent OS, Federated Learning, DLT, Crypto-payments |
| `sruth/tuatha/` | **Educational MMO** | Pocket-ID, Forgejo (Community & Sovereignty) |
| `sruth/web/` | **Frontend UI** | Real-time, type-safe user interfaces and AI chat dashboards |
| `sruth/hmgcc/` | **Security Standards** | **HMGCC Compliance:** Implementation of government-grade security standards (Bailo, CyberChef, Gaffer, Stroom). |

### 📦 Tech Stack Analysis by Directory

Based on comprehensive package research across the three primary streams, here's the detailed tech stack breakdown:

#### **sruth/bonneagar** — Browser Automation & Infrastructure

| Category | Packages | Latest Versions & Key Features |
| :--- | :--- | :--- |
| **Core Backend** | httpx, aiohttp, fastapi, uvicorn, pydantic | FastAPI async backend with Pydantic v2 validation |
| **Agent Frameworks** | google-adk, agno, mcp, baml-py | google-adk (>=0.1.0) multi-agent coordination; agno (>=2.0.0) knowledge graphs |
| **Observability** | langfuse, logfire, mlflow, ragas, datadog | langfuse (>=2.0.0) prompt management & A/B testing; ragas (>=0.1.10) trace-based metrics |
| **Infrastructure** | @pulumi/hcloud, @pulumi/oci, @1password/connect | Multi-cloud IaC with Hetzner & Oracle Cloud |
| **Browser Automation** | @browserbasehq/stagehand, patchright, crawl4ai, skyvern | Stagehand (latest) AI-powered precision interactions; Patchright stealth Chromium |

#### **sruth/meaisínfhoghlaim** — AI Agents & Data Engineering

| Category | Packages | Latest Versions & Key Features |
| :--- | :--- | :--- |
| **Data Orchestration** | dagster, dlt, duckdb, lancedb, neo4j | dagster (>=1.9.0) asset-based pipelines; dlt (>=1.4.0) streaming support; lancedb (>=0.15.0) HNSW indexing & MVCC safety |
| **ML/AI Core** | sentence-transformers, transformers, torch, accelerate | HuggingFace transformers with PyTorch backend |
| **Agent Frameworks** | google-adk, agno, litellm, cocoindex | google-adk (>=0.1.0) multi-agent coordination; agno (>=2.0.0) knowledge graphs |
| **Memory Systems** | cognee, graphiti-core | graphiti-core (>=0.5.0) temporal knowledge graphs; cognee (>=0.1.0) graph traversal & temporal tracking |
| **Model Training** | unsloth, trl, datasets, mlflow, wandb | unsloth (>=2024.12) multilingual support & flash attention (2x faster) |
| **Observability** | langfuse, ragas, ddtrace, opentelemetry | langfuse (>=2.0.0) prompt management; ragas (>=0.1.10) trace-based metrics |

#### **sruth/oideachais** — Education Pipeline & Frontend

| Category | Packages | Latest Versions & Key Features |
| :--- | :--- | :--- |
| **Data Orchestration** | dagster, dlt, duckdb, lancedb, neo4j | dagster (>=1.9.0) asset-based pipelines; dlt (>=1.4.0) streaming support; lancedb (>=0.15.0) HNSW indexing |
| **ML/AI Core** | sentence-transformers, transformers, torch, unsloth | sentence-transformers for curriculum embeddings; unsloth (>=2024.12) multilingual support |
| **Frontend Stack** | React, TypeScript, Vite, TanStack Router, CopilotKit, Vinxi | tanstack-start (^1.94.0) React Server Components; vinxi (^0.5.1) full-stack framework; copilotkit (>=0.1.0) AI agent UI |
| **Agent Frameworks** | google-adk, agno, cocoindex, litellm | google-adk (>=0.1.0) multi-agent coordination; agno (>=2.0.0) knowledge graphs |
| **Memory Systems** | cognee, graphiti-core | graphiti-core (>=0.5.0) temporal knowledge graphs; cognee (>=0.1.0) graph traversal |
| **Data Transformation** | sqlmesh | sqlmesh (>=0.228.1) DuckDB integration & virtual data warehouse |
| **Observability** | langfuse, ragas, ddtrace | langfuse (>=2.0.0) prompt management; ragas (>=0.1.10) trace-based metrics |

### 🔑 Latest Package Updates & Key Features

| Package | Version | Key Features |
| :--- | :--- | :--- |
| **google-adk** | >=0.1.0 | Multi-agent coordination with Google AI integration |
| **agno** | >=2.0.0 | Knowledge graphs feature for complex relationship tracking |
| **dagster** | >=1.9.0 | Asset-based pipelines with observability and partitioning |
| **dlt** | >=1.4.0 | Streaming support for real-time data pipelines |
| **lancedb** | >=0.15.0 | HNSW indexing, MVCC safety, hybrid search capabilities |
| **langfuse** | >=2.0.0 | Prompt management, A/B testing, trace-based analytics |
| **ragas** | >=0.1.10 | Trace-based metrics for RAG evaluation |
| **unsloth** | >=2024.12 | Multilingual support, flash attention, 2x faster training |
| **tanstack-start** | ^1.94.0 | React Server Components, edge runtime, streaming suspense |
| **vinxi** | ^0.5.1 | Full-stack framework with Vite-based architecture |
| **copilotkit** | >=0.1.0 | AI agent UI framework with React components |
| **graphiti-core** | >=0.5.0 | Temporal knowledge graphs with bi-temporal model |
| **cognee** | >=0.1.0 | Graph traversal, temporal tracking, multi-modal support |
| **sqlmesh** | >=0.228.1 | DuckDB integration, virtual data warehouse, CI/CD |
| **@browserbasehq/stagehand** | Latest | AI-powered precision browser interactions |
| **patchright** | Latest | Stealth Chromium browser with anti-detection |

### 🚀 Key Platform Capabilities

**Multi-Agent Orchestration:**
- **Google-ADK** enables coordinated multi-agent workflows with Google AI integration
- **Agno** provides knowledge graph-based agent memory and reasoning
- **MCP (Model Context Protocol)** for tool discovery and execution across agents

**Advanced Data Pipelines:**
- **Dagster** asset-based orchestration with partitioned asset checks
- **DLT** streaming support for real-time data ingestion
- **SQLMesh** virtual data warehouse with DuckDB integration

**Memory & Knowledge Systems:**
- **Graphiti-Core** temporal knowledge graphs with bi-temporal model for tracking curriculum changes over time
- **Cognee** graph traversal with temporal tracking and multi-modal support
- **LanceDB** HNSW indexing and MVCC safety for concurrent vector operations

**Observability & Evaluation:**
- **Langfuse** prompt management with A/B testing capabilities
- **Ragas** trace-based metrics for RAG evaluation
- **DDTrace** and OpenTelemetry for distributed tracing

**Frontend Innovation:**
- **TanStack Start** with React Server Components and edge runtime
- **Vinxi** full-stack framework with Vite-based architecture
- **CopilotKit** AI agent UI components for seamless AI integration

**Browser Automation:**
- **Stagehand** AI-powered precision browser interactions
- **Patchright** stealth Chromium with anti-detection
- **Hunter-Gatherer-Operator** pattern for scalable web scraping

**Model Training:**
- **Unsloth** multilingual support with flash attention (2x faster training)
- **TRL** and datasets for efficient model fine-tuning
- **MLflow** and WandB for experiment tracking

---

## 📚 Oideachais — Education Platform Details

> Full source: [`sruth/oideachais/README.md`](sruth/oideachais/README.md)

Oideachais is a pan-Celtic curriculum search, content management, and learning outcomes platform. It leverages AI to bridge the gap between official curriculum documents and interactive learning experiences.

### 🏗 Platform Architecture

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | TanStack Start | Type-safe, full-stack React application with high-performance streaming. Primary interface for students and educators. |
| **API** | FastAPI | High-concurrency, asynchronous Python backend. Handles LLM orchestration, vector search queries, and real-time streaming via Gemini 2.0 and Claude 3.7. |
| **Pipeline** | Dagster v1.13 ("Octopus's Garden") | Asset-based data orchestration. Manages data flow from raw PDF/HTML ingestion to final vector embeddings. Leverages AI skills, Partitioned Asset Checks, and Python 3.14 support. |
| **Storage** | DuckDB (DuckLake v1.0) & LanceDB (v0.31.0) | DuckDB for fast local analytical processing; LanceDB for multi-modal vector storage with namespace-backed federated database support. Data persisted to Cloudflare R2 for durability. |

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

### 🛠 Deployment Configuration

- **Development**: Managed via `compose.dev.yaml` for local hot-reloading.
- **Production**: Deployed as a **Komodo Stack** on the **MacBook M4 Max**.
- **Secrets**: Injected via **Locket** sidecar, pulling from 1Password.
- **Routing**: Securely exposed via **Pangolin** at `oideachais.cianfhoghlaim.ie`.

### 🇮🇪 Ireland Education Pipelines

The `sruth/oideachais/dlt_sources/ireland/` directory is the primary data ingestion layer for the Republic of Ireland's education system. It provides a comprehensive suite of DLT (Data Load Tool) sources that crawl, extract, normalise, and deduplicate curriculum data from every major Irish education body.

#### Data Sources

| Source | Organisation | URL | Description |
| :--- | :--- | :--- | :--- |
| **Curriculum Online** | NCCA | `curriculumonline.ie` | Official portal for all Irish curriculum documentation — Aistear (ages 1–6) through Senior Cycle (16–18). Bilingual (English/Irish). |
| **NCCA** | National Council for Curriculum and Assessment | `ncca.ie` | Statutory body for curriculum development and assessment policy. Publishes specifications, guidelines, and consultation documents. |
| **SEC** | State Examinations Commission | `examinations.ie` | Administers Junior Certificate and Leaving Certificate examinations. Chief examiner reports, marking schemes, exam archives, and statistics. |
| **Oide** | Education Support Services | `oide.ie` | Continuing professional development (CPD) for teachers. Subject-specific support materials and pedagogical resources. |
| **Department of Education** | Gov.ie | `gov.ie/en/organisation/department-of-education/` | Government education policy, circulars, and official guidance documents. |

#### Pipeline Modules

**Core Curriculum Ingestion:**

- **[`curriculum_source.py`](sruth/oideachais/dlt_sources/ireland/curriculum_source.py)** — Unified entry point. Merges content from curriculumonline.ie, ncca.ie, and examinations.ie into a single, deduplicated data source organised by `(cycle, subject, language)`.
- **[`curriculum_registry.py`](sruth/oideachais/dlt_sources/ireland/curriculum_registry.py)** — Subject taxonomy and URL resolution engine. Centralised registry of all Irish curriculum subjects, cycles, levels, and source-specific URL patterns.
- **[`curriculum_document.py`](sruth/oideachais/dlt_sources/ireland/curriculum_document.py)** — Unified Pydantic model for all Irish curriculum documents. Defines `LearningOutcome`, `AssessmentInfo`, `ContentQuality`, `EducationLevel`, and `Language` enums.

**Per-Subject Sources (`subjects/`):**

- **[`subjects/base.py`](sruth/oideachais/dlt_sources/ireland/subjects/base.py)** — Foundation for per-subject DLT resources. Handles URL resolution, Firecrawl crawling with rate limiting, PDF extraction, bilingual support, and content hashing.
- **[`subjects/junior_cycle.py`](sruth/oideachais/dlt_sources/ireland/subjects/junior_cycle.py)** — Per-subject DLT resources for all 18 Junior Cycle subjects.
- **[`subjects/senior_cycle.py`](sruth/oideachais/dlt_sources/ireland/subjects/senior_cycle.py)** — Per-subject DLT resources for all 34 Leaving Certificate subjects.

**Source Adapters & Normalisation:**

- **[`source_adapters.py`](sruth/oideachais/dlt_sources/ireland/source_adapters.py)** — Normalises output from different curriculum sources into a consistent `NormalizedPage` format. Implements adapters for CurriculumOnline, NCCA, and Examinations.ie.
- **[`content_deduplication.py`](sruth/oideachais/dlt_sources/ireland/content_deduplication.py)** — Cross-source content deduplication via content hashing with source provenance tracking and canonical URL resolution.
- **[`education_sources.py`](sruth/oideachais/dlt_sources/ireland/education_sources.py)** — Configuration registry for all Irish education websites.

**Examination Data:**

- **[`exam_source.py`](sruth/oideachais/dlt_sources/ireland/exam_source.py)** — DLT source for examinations.ie. Crawls chief examiner reports (200+ PDFs), exam archives, marking schemes, and statistics.
- **[`sec_aural_transcripts.py`](sruth/oideachais/dlt_sources/ireland/sec_aural_transcripts.py)** — Parses structured transcript data from SEC aural exam scripts with dialect tags (Connacht, Munster, Ulster).
- **[`edcolearning.py`](sruth/oideachais/dlt_sources/ireland/edcolearning.py)** — Extracts Leaving Certificate exam audio resources from EdcoLearning.ie.

**Intelligent Discovery:**

- **[`agentic_discovery.py`](sruth/oideachais/dlt_sources/ireland/agentic_discovery.py)** — Uses Firecrawl agent for autonomous URL discovery and structured data extraction across Irish educational websites.
- **[`json_seed.py`](sruth/oideachais/dlt_sources/ireland/json_seed.py)** — Loads pre-existing scraped JSON data as seed data for pipeline bootstrapping.

**Statistical & Geospatial Data (`statistics/`):**

- **[`statistics/cso_small_areas.py`](sruth/oideachais/dlt_sources/ireland/statistics/cso_small_areas.py)** — Small Area statistics from CSO PxStat API (18,641 areas, Census 2022).
- **[`statistics/geohive.py`](sruth/oideachais/dlt_sources/ireland/statistics/geohive.py)** — Geospatial boundaries from GeoHive.ie (ArcGIS FeatureServer).
- **[`statistics/met_office.py`](sruth/oideachais/dlt_sources/ireland/statistics/met_office.py)** — UK Met Office DataHub integration for weather observations and climate data, supporting cross-border environmental context.

#### Data Flow Architecture

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

#### Education Levels Covered

| Level | Ages | Qualifications |
| :--- | :--- | :--- |
| **Aistear** (Early Childhood) | 1–6 | Early Childhood Curriculum Framework |
| **Primary** | 5–12 | Primary School Curriculum (incl. redeveloped 2025 curriculum) |
| **Junior Cycle** | 12–15 | Junior Certificate / Junior Cycle (Level 1 & 2 LPs, Short Courses) |
| **Senior Cycle** | 16–18 | Leaving Certificate (Established, LCA, LCVP) |
| **Further Education** | 18+ | FETAC / QQI levels |

#### Bilingual Support

All pipeline modules support **bilingual content extraction** (English and Irish/Gaeilge). The `curriculumonline.ie` and `ncca.ie` sources maintain parallel content trees accessible via language prefixes (e.g., `/ga-ie/`). Source adapters handle language-specific URL routing and normalise both language variants into the unified schema.

#### Quick Start

```python
import dlt
from sruth.oideachais.dlt_sources.ireland import curriculum_source

# Crawl Junior Cycle Mathematics (English)
# DLT (>=1.4.0) provides streaming support for real-time data pipelines
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

**Package Versions Used:**
- **dlt** (>=1.4.0) — Streaming support for real-time data pipelines
- **Dagster** (>=1.9.0) — Asset-based pipelines with observability
- **DuckDB** — Fast local analytical processing
- **LanceDB** (>=0.15.0) — Multi-modal vector storage with HNSW indexing

**For detailed implementation guides:**
- See [`.skills/dlt/SKILL.md`](.skills/dlt/SKILL.md) for DLT pipeline patterns
- See [`.skills/dagster/SKILL.md`](.skills/dagster/SKILL.md) for Dagster orchestration
- See [`.skills/lancedb/SKILL.md`](.skills/lancedb/SKILL.md) for vector database integration

#### Pipeline Directory Structure

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

---

## 🏗️ Bonneagar — Infrastructure & Platform Details

> Full source: [`sruth/bonneagar/README.md`](sruth/bonneagar/README.md)

Bonneagar (Irish: "infrastructure") is the backbone of the Cianfhoghlaim platform — a **multi-cloud, zero-trust infrastructure** that provisions, orchestrates, and secures 50+ containerised services across Oracle Cloud, Hetzner, and local ARM hardware. It combines declarative IaC (Pulumi), GitOps orchestration (Komodo), WireGuard tunneling (Pangolin), and a self-hosted browser automation stack to provide the foundation for all other sruthanna.

### 🏗 Platform Architecture

| Component | Technology | Role |
| :--- | :--- | :--- |
| **IaC** | Pulumi (TypeScript), @pulumi/hcloud, @pulumi/oci | Provisions ARM servers on Hetzner Cloud and Oracle Cloud, Cloudflare DNS/WAF, and firewall rules. Includes Automation API for CI/CD deployment pipelines. |
| **Orchestration** | Komodo | GitOps-managed container orchestration across 3 servers. 60+ declarative TOML procedures for multi-cloud deployments, canary rollouts, and automated rollbacks. |
| **Zero-Trust Networking** | Pangolin + WireGuard | Identity-aware tunneled reverse proxy with SSO (Pocket ID + TinyAuth), CrowdSec WAF, Traefik v3 reverse proxy, and multi-tenant routing for `cianfhoghlaim.ie` and `aleyum.com`. |
| **Browser Automation** | @browserbasehq/stagehand (latest), Patchright, Crawl4AI, Skyvern | Hunter-Gatherer-Operator pattern: Skyvern (vision-based Hunter), Crawl4AI (bulk Gatherer), Stagehand (AI-powered precision Operator), all sharing a stealth Chromium grid. Exposes MCP, AG-UI, and TanStack AI protocols. |
| **Secrets** | 1Password Connect + Locket | Zero-disk-secret deployment via Locket sidecar containers injecting tmpfs-backed secrets from 1Password Connect. |
| **Observability** | Datadog APM + MLflow + Langfuse (>=2.0.0) + Logfire + Ragas (>=0.1.10) | Three-tier: Datadog (full APM/metrics/logs), MLflow/Langfuse (ML/LLM-specific with prompt management & A/B testing), Logfire (Python app tracing), Ragas (trace-based metrics). |
| **Agent Frameworks** | Google-ADK (>=0.1.0), Agno (>=2.0.0), MCP, BAML-py | Multi-agent coordination with Google AI integration; knowledge graphs for complex relationship tracking; Model Context Protocol for tool discovery. |

```
                          ┌─────────────────────────────────────────────────────────────────┐
                          │                    Bonneagar Infrastructure                      │
                          └─────────────────────────────────────────────────────────────────┘
                                                        │
               ┌────────────────────────────────────────┼──────────────────────────────────────────┐
               │                                        │                                          │
               ▼                                        ▼                                          ▼
 ┌─────────────────────────┐             ┌──────────────────────────┐              ┌──────────────────────────┐
 │   Pulumi IaC            │             │   Komodo Orchestration   │              │   Pangolin Networking    │
 │                         │             │                          │              │                          │
 │ • Cloudflare WAF (31 🌍)│             │ • Core (OCI)             │              │ • WireGuard Tunnels      │
 │ • Hetzner CAX41 (ARM)   │─────────────│ • Periphery (3 servers)  │──────────────│ • Traefik v3 Reverse Proxy│
 │ • OCI Ampere A1 (ARM)   │             │ • 25 Stacks / 60+ Procs  │              │ • Pocket ID SSO          │
 │ • Automation API deploy │             │ • Canary Deployments     │              │ • CrowdSec WAF           │
 └─────────────────────────┘             │ • Staged Rollouts        │              │ • Multi-Tenant Routing   │
                                         └──────────────────────────┘              │ • TinyAuth Forward Auth  │
                                                                                    └──────────────────────────┘
                                                        │
               ┌────────────────────────────────────────┼──────────────────────────────────────────┐
               │                                        │                                          │
               ▼                                        ▼                                          ▼
 ┌─────────────────────────┐             ┌──────────────────────────┐              ┌──────────────────────────┐
 │   Browser Automation    │             │   ~45 Docker Stacks      │              │   Secrets & Observability│
 │                         │             │                          │              │                          │
 │ • Patchright Stealth    │             │ • Engineering (7)        │              │ • 1Password Connect      │
 │ • Stagehand (Operator)  │─────────────│ • Infrastructure (3)     │──────────────│ • Locket Sidecars        │
 │ • Crawl4AI (Gatherer)   │             │ • Machine Learning (5)   │              │ • Datadog APM + LLMObs   │
 │ • Skyvern (Hunter)      │             │ • Storage (18)           │              │ • MLflow + Langfuse      │
 │ • MCP / AG-UI / SSE     │             │ • Tools (9)              │              │ • Logfire + Ragas        │
 └─────────────────────────┘             └──────────────────────────┘              └──────────────────────────┘
```

### 🖥️ Multi-Cloud Server Fleet

| Server | Hardware | Location | Role | Key Services |
| :--- | :--- | :--- | :--- | :--- |
| **arm1-oci** | 4 ARM OCPUs, 24 GB RAM, 200 GB | Oracle Cloud London | Control Plane | Pangolin Core, Komodo Core, 1Password Connect, Garage S3, Forgejo, Qdrant |
| **cax41-hetzner** | CAX41 ARM, 16 vCPU, 32 GB RAM | Hetzner Nuremberg | Primary Workloads | Memgraph, FalkorDB, MLflow, Langfuse, LanceDB, Cognee, Graphiti, Dagster, Browser Grid |
| **bunchloch** | MacBook M4 Max, ~14 cores, 48 GB RAM | Local | Dev & Analytics | LakeFS, Lakekeeper, Convex, Crawl4AI, Media servers, Aleyum portal |

### 🌐 Browser Automation (`browser/`)

A self-hosted, multi-backend browser automation stack following the **Hunter-Gatherer-Operator** pattern:

| Backend | Role | Cost |
| :--- | :--- | :--- |
| **Patchright** (stealth Chromium) | Shared browser grid with anti-detection | Free (self-hosted) |
| **Crawl4AI** | High-throughput bulk extraction (Gatherer) | Free (self-hosted) |
| **Skyvern** | Vision-based semantic navigation (Hunter) | Free (self-hosted) |
| **Stagehand** | AI-powered precision interactions (Operator) | Free (self-hosted) |
| **Browserbase** | Cloud browser fallback for anti-bot | Paid |
| **Firecrawl** | Web scraping API with autonomous research | Paid |

**Domain-Specific Scrapers:**

| Scraper | Target | Extracts |
| :--- | :--- | :--- |
| [`duchas_scraper.py`](sruth/bonneagar/browser/sruth_browser/tools/duchas_scraper.py) | [duchas.ie](https://www.duchas.ie) | National Folklore Collection — 740K+ manuscript pages, images, transcriptions, metadata |
| [`canuint_scraper.py`](sruth/bonneagar/browser/sruth_browser/tools/canuint_scraper.py) | [canuint.ie](https://www.canuint.ie) | Irish dialect audio recordings — Connacht, Munster, Ulster; TTS dataset export (LJSpeech format) |
| [`examinations_scraper.py`](sruth/bonneagar/browser/sruth_browser/tools/examinations_scraper.py) | [examinations.ie](https://www.examinations.ie) | State Examination Commission — past papers (1999–2024), marking schemes, Chief Examiner Reports |

**Multi-Protocol Server:** A single FastAPI server exposes three protocols simultaneously:
- **MCP** (JSON-RPC) — Tool discovery/execution for AI agents
- **AG-UI** (17-event SSE) — CopilotKit integration
- **TanStack AI** (SSE) — Chat-based browser control

### 🔄 Komodo Orchestration (`komodo/`)

Declarative GitOps orchestration managing 25 stack definitions and 60+ automation procedures:

**Key Procedures:**

| Procedure | Purpose |
| :--- | :--- |
| [`deploy-cianfhoghlaim`](sruth/bonneagar/komodo/procedures/deploy-cianfhoghlaim.toml) | 6-stage full platform deployment across all servers |
| [`deploy-multi-cloud`](sruth/bonneagar/komodo/procedures/deploy-multi-cloud.toml) | Dependency-ordered deployment: OCI → Hetzner → Local |
| [`staged-rollout`](sruth/bonneagar/komodo/procedures/staged-rollout.toml) | Canary deployment with configurable % and auto-rollback |
| [`rollback`](sruth/bonneagar/komodo/procedures/rollback.toml) | Safe rollback with pre-flight checks and optional snapshots |
| [`health-check`](sruth/bonneagar/komodo/procedures/health-check.toml) | Aggregate health across all stacks with alerting |
| [`init-site`](sruth/bonneagar/komodo/procedures/init-site.toml) | 5-stage new site bootstrap: validate → DNS → Pangolin → Ansible → verify |

**Komodo-Managed Stacks:**

| Stack Group | Services |
| :--- | :--- |
| **Sruth Pipelines** | Oideachais, Crypteolas, Tuath, Codeolas, Browser, Taighde |
| **Dagster Unified** | Production Dagster (Hetzner) + Dev Dagster (MacBook) |
| **Hetzner Databases** | Memgraph, FalkorDB, LanceDB, Cognee, Graphiti, MLflow, Langfuse, Kafka, Nimtable |
| **OCI Control Plane** | Garage S3, Beszel, Dozzle, Qdrant, Forgejo + Runner |
| **MacBook Analytics** | LakeFS, Lakekeeper, OLake-UI, Convex, Scraping stack |
| **Pangolin Tunnels** | Newt (Hetzner), OLM (Oracle), OLM (Hetzner) |
| **Observability** | Datadog APM + LLM Observability on all 3 servers |

### 🛡️ Pangolin Zero-Trust Networking (`pangolin/`)

An identity-aware tunneled reverse proxy providing zero-trust network access:

```
Internet → Cloudflare (DNS) → Gerbil (WireGuard, 132.145.27.89) → Traefik v3 → Services
                                                                      ↓
                                                            Pangolin API → Newt/OLM tunnel agents → Remote hosts
```

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Pangolin Core** | `fosrl/pangolin` | Identity-aware proxy with session management (30-day sessions) |
| **Gerbil** | `fosrl/gerbil` | WireGuard tunnel controller (UDP 51820, TCP 80/443/8443) |
| **Traefik v3** | `traefik:v3.4.0` | Reverse proxy with dynamic config, Let's Encrypt wildcard certs via Cloudflare DNS-01 |
| **Pocket ID** | Passkey-based OIDC | SSO provider at `auth.cianfhoghlaim.ie` |
| **TinyAuth v4** | Forward auth | OAuth integration with Pocket ID for resource protection |
| **CrowdSec** | WAF + AppSec | Intrusion detection with virtual patching on port 7422 |
| **Middleware Manager** | Traefik middleware UI | Predefined templates for auth, rate limiting, CORS, circuit breakers |

**Multi-Tenant Routing:**

| Tenant | Domain | Theme | Type |
| :--- | :--- | :--- | :--- |
| **Cianfhoghlaim** | `*.cianfhoghlaim.ie` | Celtic blue/green/gold, Inter + Playfair Display | Education Platform |
| **Aleyum** | `*.aleyum.com` | Purple/amber/pink, Space Grotesk + Orbitron | Music & Game Dev Portfolio |

**Agent-to-Agent (A2A) Resources:** Four AgentOS instances (Oideachais, Crypteolas, Browser, Aleyum) exposed via Pangolin with SSO protection, plus an internal A2A gateway for service mesh communication.

### ⚡ Pulumi Infrastructure-as-Code (`pulumi/`)

Three Pulumi projects (TypeScript) provisioning multi-cloud infrastructure:

| Project | Cloud | Resources |
| :--- | :--- | :--- |
| [`cloudflare/`](sruth/bonneagar/pulumi/cloudflare/index.ts) | Cloudflare | WAF ruleset with geo-restriction (31 allowed countries) for 4 domains |
| [`hetzner/`](sruth/bonneagar/pulumi/hetzner/index.ts) | Hetzner Cloud | CAX41 ARM server (16 vCPU, 32 GB, Nuremberg), SSH key, firewall (6 rules), Cloudflare DNS, cloud-init with Docker + sysctl tuning |
| [`oci/`](sruth/bonneagar/pulumi/oci/index.ts) | Oracle Cloud | Ampere A1 ARM (4 OCPU, 24 GB, London), VCN/subnet/IGW/security lists, wildcard DNS, Automation API deploy pipeline |

**Automation API ([`oci/deploy.ts`](sruth/bonneagar/pulumi/oci/deploy.ts)):** A 5-step CI/CD pipeline — `pulumi up` → wait for SSH → flush Oracle iptables → regenerate Ansible inventory → run Ansible playbook.

### 📦 Infrastructure Stacks (`stacks/`)

~45 modular Docker Compose stacks organised into 5 categories, each following the **Gold Standard** 5-file convention:

```
stacks/<category>/<stack>/
├── compose.yaml      # Application services (healthchecks, named volumes, bridge networks)
├── sidecar.yaml      # Locket sidecar for 1Password Connect secret injection (tmpfs, non-root)
├── secrets.env       # Locket template with {{ op://dev-baile/... }} references
├── pangolin.yaml     # Docker labels for Pangolin auto-discovery
└── blueprint.yaml    # Pangolin routing rule (domain → site → hostname → port)
```

| Category | Count | Key Stacks |
| :--- | :--- | :--- |
| **Engineering** | 7 | Coder (VS Code), Crawl4AI (scraping), LiteLLM (AI gateway), MCPJungle (MCP management), Windmill (low-code pipelines) |
| **Infrastructure** | 3 | Technitium DNS, Dozzle (log viewer), Pocket-ID (OIDC) |
| **Machine Learning** | 5 | Cognee (GraphRAG), Graphiti (knowledge graphs), Langfuse v3 (LLM tracing), LMNR (LLM observability), OLake (DB→Iceberg replication) |
| **Storage** | 18 | Garage (S3), Lakekeeper (Iceberg REST), LanceDB (vectors), Memgraph/FalkorDB (graphs), Qdrant (vector search), Kafka (streaming), Forgejo (Git/CI) |
| **Tools** | 9 | Actual (finance), Blinko (notes), Linkwarden (bookmarks), Perplexica (AI search), Romm (game library) |

### 🛠 Deployment Configuration

- **Development**: Managed via `compose.dev.yaml` for local hot-reloading on MacBook M4 Max.
- **Production**: Deployed as **Komodo Stacks** across OCI (control plane) and Hetzner (workloads).
- **Secrets**: Injected via **Locket** sidecar, pulling from 1Password Connect at `arm1-oci:8080`.
- **Routing**: Securely exposed via **Pangolin** at `*.cianfhoghlaim.ie` with CrowdSec WAF and TinyAuth SSO.
- **DNS**: Cloudflare DNS with Let's Encrypt wildcard certificates via DNS-01 challenge.
- **Monitoring**: Datadog APM agents on all servers; MLflow/Langfuse for ML/LLM observability.

---

## ️ Knowledge & Research Vaults

Beyond the active code streams, this repository serves as a massive knowledge base for British Isles cultural and political research.

### 📚 Documentation Index (`docs/`)

The `docs/` folder contains comprehensive research and specifications across multiple domains:
*   **`docs/agents/`:** Analysis of agentic frameworks (Agno, PydanticAI, Smolagents) and MCP server implementations.
*   **`docs/teanga/`:** Resources for Irish language preservation, historical document analysis (Escriptorium), and TTS dataset generation.
*   **`docs/hmgcc/`:** Security configurations and guidance for government-grade system deployments.
*   **`docs/data_engineering/`:** Strategies for Lakehouse architectures using DuckDB, Iceberg, and LakeFS.
*   **`docs/meaisínfhoghlaim/`:** Machine learning workflows, model evaluation, and fine-tuning patterns.

### 🛠️ Skills Documentation (`.skills/`)

The [`.skills/`](.skills/) folder contains detailed skill documentation for key technologies and frameworks used across the platform. Each skill provides comprehensive guides, best practices, and implementation patterns:

**Agent Frameworks:**
*   [**agno**](.skills/agno/SKILL.md) — Multi-agent orchestration with tool calling and knowledge graphs (v2.0+)
*   [**google-adk**](.skills/google-adk/SKILL.md) — Google's Agent Development Kit for multi-agent coordination

**Knowledge & Memory Systems:**
*   [**graphiti-core**](.skills/graphiti-core/SKILL.md) — Temporal knowledge graph memory with bi-temporal model
*   [**graphiti**](.skills/graphiti/SKILL.md) — Knowledge graph for agents with HNSW indexing (v0.5+)
*   [**cognee**](.skills/cognee/SKILL.md) — Graph-based knowledge management with temporal tracking (v0.1+)
*   [**lancedb**](.skills/lancedb/SKILL.md) — Vector database for RAG with HNSW indexing (v0.15+)

**Data Pipelines & Orchestration:**
*   [**dagster**](.skills/dagster/SKILL.md) — Data orchestration platform with asset-based pipelines (v1.9+)
*   [**dlt**](.skills/dlt/SKILL.md) — Data load tool for pipelines with streaming support (v1.4+)
*   [**sqlmesh**](.skills/sqlmesh/SKILL.md) — Data transformation framework with DuckDB integration

**Observability & Evaluation:**
*   [**langfuse**](.skills/langfuse/SKILL.md) — LLM observability platform with prompt management (v2.0+)
*   [**ragas**](.skills/ragas/SKILL.md) — RAG evaluation framework with trace-based metrics (v0.1.10+)

**UI & Agent Interaction:**
*   [**copilotkit**](.skills/copilotkit/SKILL.md) — AI agent UI framework with React components
*   [**vinxi**](.skills/vinxi/SKILL.md) — Full-stack framework (Poimandres) with Vite-based architecture
*   [**tanstack-start**](.skills/tanstack-start/SKILL.md) — React framework with React Server Components (v1.94+)

**Model Training & Fine-tuning:**
*   [**unsloth**](.skills/unsloth/SKILL.md) — LLM fine-tuning with multilingual support (v2024.12+)

For detailed implementation guides and best practices, refer to individual skill files in the [`.skills/`](.skills/) directory.

### 🏛️ Political & Social Research (`bunchloch/gemini/`)
A massive collection of over 140 deep-dive research documents (PDFs) generated during the project's development. This "Gemini Vault" is organized into thematic subdirectories for clarity.

**Note on Methodology**: These reports were generated using **Gemini Deep Research** with expert prompting. For detailed information on the generation process and official documentation links, see the [**Gemini Vault README**](./bunchloch/gemini/README.md).

*   **`technology/`**: AI company analysis, Gemini/Google AI goals, Big Tech regulation, and cybersecurity job cycles.
*   **`politics/`**: Brexit impact, Sinn Féin/Fine Gael coalition strategy, election research, and Irish economic future planning.
*   **`law/`**: Dual citizenship jurisprudence, court forms/procedures, medical malpractice strategies, and data access inquiries.
*   **`medical/`**: TBI/C-PTSD recovery protocols, medical cannabis access, disability allowance assistance, and neuro-scientific trauma research.
*   **`culture/`**: Celtic language revitalization, Deacy family genealogy, Irish kingship claims, and Royal family research.
*   **`other/`**: Public service connectivity (Irish Rail), London borough cleanliness, and radicalization prevention strategies.

### 📥 Downloading Specific Research Data (Sparse Checkout)

This repository contains massive amounts of data, models, and PDFs. If you only want to download a specific directory, such as the University of Galway research archives, you can use Git's sparse-checkout feature to save time and disk space:

```bash
# 1. Clone the repository without downloading the files
git clone --no-checkout https://github.com/cianfhoghlaim/kings_college_galway.git
cd kings_college_galway

# 2. Initialize sparse-checkout
git sparse-checkout init --cone

# 3. Specify the directory you want to download
git sparse-checkout set bunchloch/university_of_galway

# 4. Checkout the files
git checkout main
```

---

## 🎓 Cian CV: Academic, Professional & Civic Credentials

To ensure transparency and verify the author's background, high-resolution scans of key credentials and professional references are provided below:

### 📜 Academic & Professional Records
*   **[University Degree Transcript (BA & HDip)](./cian_cv/ba_and_hdip_transcript.pdf)** | **[Transcript of Results (Bilingual)](./cian_cv/tras_scribhinn_torthai_transcript_of_results.pdf)**
*   **[Academic Parchment 1](./cian_cv/parcment_1.jpeg)** | **[Academic Parchment 2](./cian_cv/parchment_2.jpeg)**
*   **[Leaving Certificate](./cian_cv/leaving_certificate.pdf)** | **[Junior Certificate](./cian_cv/junior_certificate.pdf)**
*   **[Torthaí Ghaeilge (Irish Results)](./cian_cv/torthai_ghaeilge.pdf)**
*   **[Coláiste na Coiribe](./cian_cv/colaiste_na_coiribe.pdf)** | **[Scoil Iognáid](./cian_cv/scoil_iognaid.pdf)**
*   **[Teaching Placement Reference](./cian_cv/placement_reference.pdf)** | **[Placement Feedback](./cian_cv/teaching_placement_feedback.pdf)**
*   **[Part-Time Teaching Reference](./cian_cv/part_time_teaching_reference.pdf)** | **[BME Reference](./cian_cv/bme_reference.pdf)**
*   **[Apple Award](./cian_cv/apple_award.pdf)** | **[Teaching Council Registration](./cian_cv/teaching_registration.pdf)**

### 🛡️ Cybersecurity & Trust
*   **[Cybersecurity Professional Reference](./cian_cv/cybersecurity_reference.pdf)**
*   **[University of Galway Complaint (Covered Up)](./cian_cv/university_galway_complaint_covered_up.pdf)**
*   **[Threat Message Documentation (Evidence)](./cian_cv/threat_message.jpeg)**
*   **[Verified Lack of Criminality (Garda Vetting ROI)](./cian_cv/garda_vetting_roi.pdf)**
*   **[Children First Certificate (Safeguarding)](./cian_cv/children_first_certificate.pdf)**
*   **[Enhanced Disclosure (Northern Ireland)](./cian_cv/enhanced_cert_ni.pdf)** | **[Enhanced Disclosure (UCL/England)](./cian_cv/enhanced_cert_ucl.pdf)**

### 🏥 Medical & Trauma Verification
*   **[C-PTSD Diagnosis (Chronic & Complex)](./cian_cv/chronic_complex_ptsd_diagnosis.pdf)**
*   **[Generalized Anxiety Disorder (GAD) Diagnosis](./cian_cv/anxiety_disorder_diagnosis.pdf)**
*   **[Head of Counselling Reference](./cian_cv/head_of_counselling_reference.pdf)**

### 🏛️ Civic, Political & Family Heritage
*   **[Fine Gael Party Membership](./cian_cv/fine_gael_member.pdf)**
*   **[Liberal Democrats Membership](./cian_cv/libdems_membership.png)**
*   **[Alliance Party Membership](./cian_cv/alliance_membership.pdf)**
*   **[Eamon Deacy Memorial & Family Heritage](./cian_cv/uncle_eamonn_memorial_combined.pdf)**
*   **[Royal Communication (Buckingham Palace)](./cian_cv/buckingham_letter.pdf)**
*   **[Dual Citizenship Verification (ROI & UK)](./cian_cv/old_passports_dual_citizen_verification_roi_uk.pdf)**

---

## 🛰️ Pangolin (Hybrid Strategy)

> **See [Bonneagar — Infrastructure & Platform Details](#️-bonneagar--infrastructure--platform-details) for the full architecture.** The platform uses a two-tier Pangolin Convergence strategy: OCI (Control Plane) for availability, routing, and identity; and local MacBook M4 Max (Bunchloch) for high-performance compute, vector/graph databases, and heavy data analytics. All connectivity is secured via WireGuard tunnels with zero-trust authentication.

---

## 📂 Directory Description: `/Users/cliste/dev/cianfhoghlaim/cian_cv`

The `/Users/cliste/dev/cianfhoghlaim/cian_cv` directory contains the digital artifacts and verifiable proof of the author's academic and professional journey. It acts as a dedicated proof-of-paternity vault within the repository, housing high-resolution scans of degree parchments, civic memberships, and security clearances. This ensures that the project's lead developer is identifiable and their qualifications are transparently available to collaborators and stakeholders.

---

## 🗣️ A Note on the Name & Author

**Cianfhoghlaim & Celtic Linguistic Roots:**
The domain `cianfhoghlaim.ie` || `cian.lyons.co.uk` is a deliberate linguistic play on words that highlights the mechanics of the Irish language while pointing to the broader Celtic linguistic traditions this repository aims to protect:
*   **Cian:** The author's name, which also serves as the Irish prefix for "distance," "remote," or "long-enduring."
*   **Foghlaim:** The Irish word for "learning."

This digital sanctuary will ensure the inter-generational transmission of Goidelic and Brythonic languages and protect our shared cultural heritage against monolingual algorithmic manipulations.

**Author Identity:**
This platform is developed entirely by **Cian Lyons-Deacy** (Irish Passport Name: **Cian Mac Liatháin Uí Dhéisigh**).

---

## ⚖️ Paternity & Usage Policy

**Moral Rights & Paternity:**
The author explicitly asserts their moral right of paternity under the Copyright and Related Rights Act 2000 (Ireland) and the Copyright, Designs and Patents Act 1988 (UK) to be permanently identified as the creator of this work.

**Institutional Nomenclature Disclaimer:**
While this platform embraces the structural and historical reference of "Kings' College Galway" to reflect its academic rigor, "Kings' College Galway" operates exclusively as an artistic and thematic project identifier. It does not represent an accredited, regulated, or statutorily recognized degree-awarding higher education institution in any jurisdiction.

**Usage Policies & Licensing:**
This repository operates under a highly restrictive **Business Source License (BSL) 1.1**. 

By downloading, copying, or utilizing this codebase, you agree to the following core tenets (see `LICENSE.md` for full legal terms):
1.  **Geographic Restrictions:** Production deployment is legally restricted to Ireland, Northern Ireland, the Republic of Ireland, the United Kingdom of Great Britain and Northern Ireland, Ukraine, the European Union, the British Isles, The Commonwealth of Nations, The Crown, and those in the United States of America aligned with Apple and the Duke and Duchess of Sussex, Taiwan, Tibet, Nepal, South Korea, Japan, China.
2.  **Non-Commercial Use Only:** The software is provided exclusively for non-profit, cultural preservation, and academic research. Commercial monetization—including for-profit AI training, DeFi analytics, and ed-tech SaaS platforms—is strictly prohibited.
3.  **Acceptable Use:** Usage by entities affiliated with sanctioned organizations, paramilitary groups, or those in violation of international human rights conventions is fundamentally banned and will result in immediate technological and legal revocation of access.
