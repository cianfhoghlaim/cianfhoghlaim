# Sruth Pipeline Architecture

Comprehensive documentation of all data flows (sruth), BAML schemas, and DLT sources in the Cianfhoghlaim Celtic education platform.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Sruth Flows Overview](#sruth-flows-overview)
3. [Flow Details](#flow-details)
   - [Oideachais (Education)](#oideachais-education)
   - [Codeolas (Code Analysis)](#codeolas-code-analysis)
   - [Crypteolas (DeFi Research)](#crypteolas-defi-research)
   - [Tuath (Celtic MMO)](#tuath-celtic-mmo)
   - [Aleyum (Portfolio)](#aleyum-portfolio)
   - [Browser (Automation)](#browser-automation)
   - [Taighde (Research)](#taighde-research)
   - [Shared (Utilities)](#shared-utilities)
4. [BAML Schemas](#baml-schemas)
5. [DLT Sources](#dlt-sources)
6. [Cross-Cutting Patterns](#cross-cutting-patterns)
7. [Architecture Diagrams](#architecture-diagrams)
8. [Quick Reference](#quick-reference)

---

## Executive Summary

### Project Scope

| Metric | Count |
|--------|-------|
| Data Flows (sruth) | 8 |
| BAML Schema Files | 11 |
| DLT Sources | 50+ |
| Dagster Assets | 37+ |
| Kafka Topics | 25+ |
| Agent Tools | 15+ |

### Core Architecture Pattern

```
Sources (DLT) -> Storage (DuckDB) -> Embeddings (CocoIndex)
  -> Vector DB (LanceDB) -> Graph DB (Memgraph/FalkorDB)
  -> RAG Retrieval -> BAML Extraction -> Agents (ADK/Agno)
  -> API (FastAPI) -> UI (TanStack Start)
```

### Critical Constraints

| Constraint | Rule | Impact |
|------------|------|--------|
| **DuckDB** | SINGLE-THREADED ONLY | Use SerialDatabaseExecutor |
| **Embeddings** | BATCH MINIMUM 100 | 100x performance difference |
| **HNSW Index** | DROP before bulk >50 rows | 20x speedup |
| **LanceDB** | MVCC safe multi-process | Retry with backoff for writes |

---

## Sruth Flows Overview

"Sruth" (Irish: "flow") represents the data pipeline architecture. Each sruth is a self-contained data flow with its own DLT sources, Dagster assets, CocoIndex flows, and API endpoints.

| Flow | Purpose | Status | Primary DB |
|------|---------|--------|------------|
| **oideachais** | Celtic education platform | Production | DuckDB + LanceDB + Memgraph |
| **codeolas** | Code analysis & semantic search | Active (PyPI) | LanceDB + Memgraph |
| **crypteolas** | Crypto/DeFi research | Production | DuckDB + FalkorDB + Graphiti |
| **tuath** | Celtic educational MMO | Development | SpacetimeDB + Graphiti |
| **aleyum** | Music/developer portfolio | Development | DuckDB + LanceDB |
| **browser** | Browser automation | Active | Redis |
| **taighde** | Research document ingestion | Active | DuckDB |
| **shared** | Cross-project utilities | Core | N/A |

---

## Flow Details

### Oideachais (Education)

The primary Celtic education platform processing curriculum from Ireland, UK, and pan-Celtic nations.

**Directory Structure:**

```
sruth/oideachais/
├── api/                  # FastAPI with Datadog APM
│   ├── main.py          # App with observability lifespan
│   └── routes/          # API endpoints (curriculum, search, TTS)
├── agents/               # ADK-based AI agents
│   ├── adk/
│   │   ├── root_agent.py          # Orchestrator with query routing
│   │   ├── curriculum_agent.py    # Curriculum search
│   │   ├── geospatial_agent.py    # Map queries, boundaries
│   │   ├── translation_agent.py   # Celtic language translation
│   │   ├── corpus_agent.py        # Folklore, cultural content
│   │   └── statistics_agent.py    # Education statistics
│   └── tools/            # 15+ agent tools
├── cocoindex_flows/      # Vector embedding pipelines
│   ├── curriculum_embedding.py    # Batch embedding (100+ min)
│   ├── curriculum_translation.py  # Bilingual alignment
│   └── geospatial_indexing.py     # Spatial indexing
├── dagster_defs/         # Dagster asset orchestration (6.2K LOC)
│   ├── assets/
│   │   ├── ie_education_assets.py
│   │   ├── uk_education_assets.py
│   │   ├── celtic_language_assets.py
│   │   ├── geospatial_assets.py
│   │   └── embedding_assets.py
│   ├── factories.py      # Asset factory patterns
│   ├── resources.py      # Tenant-aware resources
│   └── schedules.py
├── dlt_sources/          # 50+ data ingestion sources
│   ├── ireland/          # NCCA, SEC, curriculumonline
│   ├── uk/               # England, Scotland, Wales, NI
│   ├── celtic/           # Language resources (Duchas, Tearma)
│   └── geospatial/       # Boundaries and locations
├── kafka/                # Event streaming
│   ├── producer.py       # Confluent Kafka producer
│   ├── consumer.py       # Consumer with observability
│   └── topics.py         # 25+ topic configurations
├── observability/        # Unified observability stack
│   ├── agent_tracing.py  # Datadog LLMObs decorators
│   ├── mlflow_config.py  # MLflow experiments
│   ├── langfuse_config.py # LLM cost tracking
│   └── ragas_evaluator.py # RAG quality evaluation
└── storage/              # Database configurations
    ├── duckdb.py         # Single-threaded executor
    └── lancedb.py        # Vector store
```

**Key Statistics:**
- 37+ Dagster assets across 4 domains (Ireland, UK, Celtic, Geospatial)
- 30+ DLT sources for curriculum, statistics, and language data
- DuckDB Spatial with 60k+ statistical area boundaries
- 5 domain-specific ADK agents

**Agent Query Routing:**

```python
# Keyword routing (fast)
"curriculum" -> CurriculumAgent
"map", "location" -> GeospatialAgent
"translate" -> TranslationAgent
"folklore", "story" -> CorpusAgent
"statistics", "compare" -> StatisticsAgent

# LLM routing (fallback for ambiguous queries)
Gemini 2.0 Flash classifies intent
```

**Kafka Topics:**

| Topic | Purpose | Key |
|-------|---------|-----|
| `edu.curriculum.pages` | Curriculum page events | document_id |
| `edu.curriculum.updates` | Curriculum update notifications | source |
| `edu.exams.papers` | Exam paper events | exam_id |
| `celtic.language.translations` | Translation events | source_lang |
| `celtic.folklore.documents` | Folklore document events | collection |
| `ai.agent.queries` | Agent query events | session_id |
| `ai.agent.responses` | Agent response events | session_id |
| `eval.rag.scores` | RAG evaluation scores | evaluation_id |

---

### Codeolas (Code Analysis)

Semantic code search and knowledge graph construction for repository intelligence.

**Package:** Available on PyPI as `codeolas`

**Directory Structure:**

```
sruth/codeolas/
├── core/                 # Core functionality
│   ├── analyzer.py       # Main CodebaseAnalyzer API
│   ├── chunking.py       # cAST algorithm (29 languages)
│   ├── embeddings.py     # BGE-M3 embeddings
│   ├── entities.py       # Entity deduplication
│   └── types.py          # 40+ relationship types
├── search/               # Search capabilities
│   ├── multihop.py       # Multi-hop research with convergence
│   └── reranker.py       # Jina/Cohere/Aliyun reranking
├── graph/                # Knowledge graph
│   ├── builder.py        # Graph construction
│   └── queries.py        # Cypher queries
├── generators/           # Documentation
│   ├── arch.py           # .arch.md generation
│   └── changelog.py      # Changelog generation
├── storage/              # Storage backends
│   ├── lance.py          # LanceDB integration
│   └── serial_executor.py # Single-threaded safety
└── mcp/                  # MCP server
    ├── server.py         # JSON-RPC server
    └── tools.py          # Tool definitions
```

**Key Features:**
- **cAST Chunking**: Syntax-aware code splitting (29 languages via Tree-sitter)
- **Semantic Search**: LanceDB vector search with BGE-M3 embeddings
- **Multi-hop Research**: Iterative search with convergence detection
- **Reranking**: Jina/Cohere/Aliyun API integration (15-20% precision boost)
- **Knowledge Graph**: 40+ relationship types for code analysis
- **MCP Server**: Claude Code integration via JSON-RPC

**CLI Usage:**

```bash
# Index a repository
codeolas index --repo /path/to/repo

# Search for code
codeolas search "database connection" --limit 10

# Deep research
codeolas research "How does authentication work?"

# Generate architecture docs
codeolas arch --output ARCHITECTURE.md

# Start MCP server
codeolas mcp
```

---

### Crypteolas (DeFi Research)

Crypto/DeFi research platform with GitHub intelligence and temporal knowledge graphs.

**Directory Structure:**

```
sruth/crypteolas/
├── dlt_sources/          # GitHub, DeFi, documentation sources
│   ├── github/           # Repository intelligence
│   ├── defi/             # DeFi protocol analytics
│   └── documentation/    # Protocol docs
├── cocoindex_flows/      # Code + document embeddings
│   └── transforms/       # Custom transformations
├── dagster_assets/       # Pipeline orchestration
├── agents/               # ADK + HITL RAG agents
│   ├── adk/              # ADK agents
│   └── tools/            # Agent tools
├── knowledge_graph/      # Temporal knowledge graphs
│   ├── graphiti/         # Bi-temporal data model
│   └── cognee/           # AI memory integration
├── api/                  # FastAPI with SIWE + x402
│   └── routes/           # API routes
└── ui/                   # TanStack Start HITL interface
```

**Key Features:**
- GitHub repository intelligence and code analysis
- DeFi protocol analytics with temporal reasoning
- Graphiti bi-temporal knowledge graphs
- SIWE (Sign-In with Ethereum) authentication
- x402 payment protocol integration
- Human-in-the-loop (HITL) agent interface

---

### Tuath (Celtic MMO)

Celtic educational MMO with mythology-driven content and SpacetimeDB integration.

**Directory Structure:**

```
sruth/tuath/
├── dlt_sources/          # Mythology, geospatial sources
│   ├── celtic_education/ # Pan-Celtic curriculum
│   ├── crypto/           # Game token economics
│   └── geospatial/       # Game world geography
├── cocoindex_flows/      # Mythology embeddings
│   └── transforms/       # Custom transformations
├── dagster_assets/       # Content orchestration
├── agents/               # ADK game agents
│   ├── adk/              # Game AI agents
│   └── tools/            # Agent tools
│   └── mcp_server/       # MCP integration
├── knowledge_graph/      # Graphiti hybrid search
├── game/                 # SpacetimeDB integration
│   └── modules/          # Game modules
├── api/                  # FastAPI game API
│   └── routes/           # API routes
└── ui/                   # TanStack Start game UI
```

**Key Features:**
- Celtic mythology content integration
- SpacetimeDB for real-time multiplayer
- Graphiti for mythology knowledge graphs
- ADK agents for NPC AI and quest generation
- Pan-Celtic educational content

---

### Aleyum (Portfolio)

Personal portfolio and developer dashboard combining data engineering with modern web technologies.

**Directory Structure:**

```
sruth/aleyum/
├── pipelines/            # Data pipelines
│   ├── spotify/          # Spotify API pipeline
│   │   ├── source.py     # DLT source definition
│   │   └── resources.py  # API endpoint configs
│   ├── soundcloud/       # SoundCloud scraper
│   │   ├── scraper.py    # Crawl4AI scraper
│   │   └── downloader.py # Audio downloader to R2
│   └── github/           # GitHub repos pipeline
├── notebooks/            # Marimo analytics notebooks
│   ├── music_analytics.py     # Music data exploration
│   └── github_insights.py     # GitHub project insights
├── web/                  # TanStack Start application
│   ├── src/routes/       # File-based routing
│   │   ├── index.tsx     # Home page
│   │   ├── music.tsx     # Music portfolio
│   │   ├── code.tsx      # Code projects
│   │   └── about.tsx     # About/Resume
│   └── components/
│       ├── music/AudioCard.tsx    # Track analytics
│       └── code/ProjectCard.tsx   # Repository card
└── cocoindex_flows/      # Artwork embeddings
```

**Key Features:**
- Spotify and SoundCloud data pipelines
- GitHub repository analytics
- Cloudflare R2 for media storage
- TanStack Start with React 19 + Tailwind CSS 4
- Marimo interactive analytics notebooks

---

### Browser (Automation)

Browser automation with multi-backend support and circuit breakers.

**Directory Structure:**

```
sruth/browser/
├── backends/             # Browser backends
│   ├── stagehand.py      # Stagehand browser
│   ├── browserbase.py    # Browserbase cloud
│   └── local.py          # Local Playwright
├── router.py             # Backend routing
├── circuit_breaker.py    # Fault tolerance
└── __init__.py
```

**Key Features:**
- Multi-backend support (Stagehand, Browserbase, local Playwright)
- Circuit breaker pattern for fault tolerance
- Lazy loading to avoid heavy dependencies
- Integration with ADK and Agno agents

---

### Taighde (Research)

Research document ingestion and processing.

**Directory Structure:**

```
sruth/taighde/
├── dlt_sources/          # Document sources
├── processors/           # Document processors
└── __init__.py
```

---

### Shared (Utilities)

Cross-project utilities used by all sruth pipelines.

**Modules:**

| Module | Purpose | Key Exports |
|--------|---------|-------------|
| `storage` | Database access | `SerialDatabaseExecutor`, `DuckDBClient`, `LanceDBClient`, `HNSW_DROP_THRESHOLD` |
| `utils` | Common utilities | `CircuitBreaker`, `RateLimiter`, `retry_with_backoff` |
| `http` | HTTP client factory | `HttpClientFactory`, `AuthStrategy`, `BearerTokenAuth`, `ApiKeyAuth` |
| `observability` | Unified tracing | `UnifiedTracer`, `DatadogBackend`, `LangfuseBackend`, `LogfireBackend` |
| `graph` | Graph DB clients | `MemgraphClient`, `FalkorDBClient`, `Neo4jClient` |
| `embeddings` | Batched embeddings | `EmbeddingBatcher`, `MIN_BATCH_SIZE`, `EmbeddingService` |
| `config` | Base settings | `FlowSettings`, `get_flow_settings` |
| `dlt` | DLT source mixins | `PaginatedSourceMixin`, `RateLimitedSourceMixin`, `CachedSourceMixin` |
| `browser` | Browser automation | `BackendRouter` (lazy import) |
| `codeolas` | Code intelligence | TreeSitter chunking, language detection |

**SerialDatabaseExecutor Pattern:**

```python
# MANDATORY for DuckDB operations (prevents segfaults)
from sruth.shared import SerialDatabaseExecutor, run_serial

executor = SerialDatabaseExecutor()
result = await executor.execute(query)

# Or use the convenience function
result = run_serial(lambda conn: conn.execute("SELECT * FROM table"))
```

---

## BAML Schemas

BAML (Basically A Made-up Language) provides type-safe LLM extraction with schema validation.

### Schema Files Overview

| Schema | Domain | Key Types | Functions |
|--------|--------|-----------|-----------|
| `generators.baml` | LLM configuration | Client configs | Retry policies |
| `celtic_sources.baml` | Core enums | `CelticLanguage`, `FolkloreSource`, `MediaType` | Base types |
| `isles_education.baml` | Pan-Celtic education | `BilingualText`, `CurriculumSpecification`, `ExamPaper` | 6 extraction functions |
| `multi_nation_curriculum.baml` | Cross-nation alignment | `CrossNationLearningOutcome`, `OutcomeAlignment` | 6 comparison functions |
| `oideachas.baml` | Irish education | `SyllabusExtraction`, `ExamPaperExtraction`, `CurriculumGraph` | 5 functions |
| `folklore_extraction.baml` | Duchas.ie Schools Collection | `DuchasXMLRecord`, `HandwritingExtraction`, `StoryExtraction` | 3 functions |
| `ocr_extraction.baml` | Hidden Heritages HTR | `HiddenHeritagesTale`, `HHTTranscription`, `TaleType` | 2 functions |
| `audio_extraction.baml` | Canuint.ie dialects | Audio metadata | 3 functions |
| `ocr_validation.baml` | OCR quality | Validation types | 4 functions |
| `portfolio_extraction.baml` | CV/profile extraction | `HybridProfile`, `MusicProfile`, `GameProject` | 6 functions |
| `clients.baml` | Gemini clients | Direct Gemini configs | - |

### LiteLLM Client Configuration

All BAML clients route through LiteLLM gateway for unified model access:

```baml
// generators.baml - LiteLLM routing with fallback chains

// Primary extraction client
// Fallback chain: gemini-2.5-pro -> glm-4.6v -> gemini-2.5-flash
client<llm> Extractor {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "extract"
  }
}

// OCR extraction - Local OLMoCR MLX with fallback
// Fallback chain: olmocr2-7b -> granite-docling
client<llm> OCRExtractor {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "ocr"
  }
}

// Vision/multimodal
// Fallback chain: qwen3-vl-30b -> glm-4.6v -> gemma-27b-vision
client<llm> VisionExtractor {
  provider openai
  options {
    base_url env.LITELLM_API_BASE
    api_key env.LITELLM_API_KEY
    model "vision"
  }
}
```

### Core Celtic Types

```baml
// celtic_sources.baml - Core enums

enum CelticLanguage {
  GA @alias("Irish (Gaeilge)")
  GD @alias("Scottish Gaelic (Gaidhlig)")
  CY @alias("Welsh (Cymraeg)")
  GV @alias("Manx (Gaelg)")
  KW @alias("Cornish (Kernewek)")
  EN @alias("English")
  SCO @alias("Scots")
  ULS @alias("Ulster Scots")
}

enum FolkloreSource {
  DUCHAS @alias("Duchas.ie - Schools Collection")
  CANUINT @alias("Canuint.ie - Repository of Irish Dialects")
  HIDDEN_HERITAGES @alias("Decoding Hidden Heritages")
  NFC @alias("National Folklore Collection, UCD")
  SSS @alias("School of Scottish Studies Archives")
}

enum IrishDialect {
  MUNSTER @alias("Gaeilge na Mumhan - Kerry, Cork, Waterford")
  CONNACHT @alias("Gaeilge Chonnacht - Galway, Mayo, Roscommon")
  ULSTER @alias("Gaeilge Uladh - Donegal")
  STANDARD @alias("An Caighdean Oifigiuil - Official Standard")
}
```

### Education Level Mapping

```baml
// multi_nation_curriculum.baml - Cross-nation education levels

enum NationEducationLevel {
  // Ireland
  IE_EARLY_CHILDHOOD   // Aistear framework, ages 0-6
  IE_PRIMARY           // Primary school, classes 1-6
  IE_JUNIOR_CYCLE      // Junior Certificate, years 1-3
  IE_TRANSITION_YEAR   // Optional TY, year 4
  IE_SENIOR_CYCLE      // Leaving Certificate, years 5-6

  // England
  EN_EARLY_YEARS       // EYFS, ages 0-5
  EN_KEY_STAGE_1       // Years 1-2, ages 5-7
  EN_KEY_STAGE_2       // Years 3-6, ages 7-11
  EN_KEY_STAGE_3       // Years 7-9, ages 11-14
  EN_KEY_STAGE_4       // Years 10-11, GCSE, ages 14-16
  EN_KEY_STAGE_5       // Years 12-13, A-Level, ages 16-18

  // Scotland
  SC_EARLY_LEVEL       // Pre-school to P1
  SC_FIRST_LEVEL       // P2-P4
  SC_SECOND_LEVEL      // P5-P7
  SC_THIRD_LEVEL       // S1-S3
  SC_FOURTH_LEVEL      // S4-S6 with National Qualifications
  SC_NATIONAL_5        // SQA National 5
  SC_HIGHER            // SQA Higher
  SC_ADVANCED_HIGHER   // SQA Advanced Higher

  // Wales
  WA_FOUNDATION_PHASE  // Ages 3-7
  WA_PROGRESSION_STEP_2 // Ages 7-11
  WA_PROGRESSION_STEP_3 // Ages 11-14
  WA_PROGRESSION_STEP_4 // Ages 14-16, GCSE

  // Northern Ireland
  NI_FOUNDATION        // Years 1-2, ages 4-6
  NI_KEY_STAGE_1       // Years 3-4, ages 6-8
  NI_KEY_STAGE_2       // Years 5-7, ages 8-11
  NI_KEY_STAGE_3       // Years 8-10, ages 11-14
  NI_KEY_STAGE_4       // Years 11-12, GCSE, ages 14-16
}
```

### Key Extraction Functions

```baml
// Curriculum extraction
function ExtractCurriculumSpec(document: string) -> CurriculumSpecification
function ExtractExamPaper(document: string) -> ExamPaper
function ExtractTerminology(document: string) -> TermEntry[]

// Folklore extraction
function ParseDuchasXML(xml_content: string) -> DuchasXMLRecord
function ExtractHandwriting(page_image: image, context: DuchasXMLRecord?) -> HandwritingExtraction
function ExtractStory(page_images: image[], metadata: DuchasXMLRecord) -> StoryExtraction

// Cross-nation comparison
function AlignOutcomes(source: CrossNationLearningOutcome[], target: CrossNationLearningOutcome[]) -> OutcomeAlignment[]
function CompareCurricula(specs: CrossNationCurriculumSpec[], subject: string) -> CrossNationComparison

// Portfolio extraction
function ExtractProfileFromCV(document: string) -> HybridProfile
function ExtractMusicProfile(platformData: string, platform: PlatformType) -> MusicProfile
function MergeProfiles(profiles: HybridProfile[]) -> HybridProfile
```

---

## DLT Sources

Data Load Tool (DLT) sources for ingesting data from various APIs and websites.

### Sources by Region

#### Ireland Education (8 sources)

| Source | Module | Description | Pagination |
|--------|--------|-------------|------------|
| NCCA | `ireland/ncca.py` | Curriculum specifications | JSON link |
| Curriculum Online | `ireland/curriculum_online.py` | Subject specifications | Page number |
| SEC | `ireland/examinations.py` | State Examinations Commission | Offset |
| Oide.ie | `ireland/oide.py` | Teacher professional development | Cursor |
| Parallel Corpus | `ireland/parallel_corpus.py` | EN-GA translations | Offset |
| Local Documents | `ireland/local_documents.py` | Local PDF/DOCX | Filesystem |
| JSON Seed | `ireland/json_seed.py` | Manual seed data | None |
| Agentic Discovery | `ireland/agentic_discovery.py` | AI-driven discovery | None |

#### UK Education (12 sources)

| Source | Module | Description | Pagination |
|--------|--------|-------------|------------|
| National Curriculum | `uk/england/national_curriculum.py` | DfE National Curriculum | Page number |
| DfE Statistics | `uk/england/dfe_explore_statistics.py` | Education statistics | Offset |
| School Info | `uk/england/school_info.py` | School database | Cursor |
| Ofsted | `uk/england/ofsted.py` | Inspection reports | Header link |
| Curriculum for Excellence | `uk/scotland/curriculum_for_excellence.py` | Scottish curriculum | JSON link |
| Gov.scot Statistics | `uk/scotland/gov_scot_statistics.py` | Scottish statistics | Offset |
| Insight Benchmarking | `uk/scotland/insight_benchmarking.py` | School benchmarking | Page number |
| SIMD | `uk/scotland/simd.py` | Deprivation index | None |
| Curriculum for Wales | `uk/wales/curriculum_for_wales.py` | Welsh curriculum | JSON link |
| StatsWales | `uk/wales/statswales.py` | Welsh statistics | OData |
| Estyn | `uk/wales/estyn.py` | Welsh inspections | Header link |
| CCEA Curriculum | `uk/northern_ireland/ccea_curriculum.py` | NI curriculum | Page number |
| Education NI | `uk/northern_ireland/education_ni.py` | NI education data | Offset |
| ETINI | `uk/northern_ireland/etini.py` | NI inspections | Header link |
| NISRA | `uk/northern_ireland/nisra.py` | NI statistics | Offset |

#### Celtic Language (6 sources)

| Source | Module | Description | Pagination |
|--------|--------|-------------|------------|
| Duchas | `celtic/duchas.py` | Schools Collection XML | Cursor |
| Duchas Images | `celtic/duchas_images.py` | Handwriting images | None |
| Canuint | `celtic/canuint.py` | Irish dialects audio | Page number |
| Gaois | `celtic/gaois.py` | Logainm, Ainm, Focal | JSON link |
| Tearma | `tearma.py` | Irish terminology | Offset |
| Universal Dependencies | `celtic/universal_dependencies.py` | Treebanks | None |

#### Geospatial (4 sources)

| Source | Module | Description | Pagination |
|--------|--------|-------------|------------|
| CSO Small Areas | `geospatial/cso_small_areas.py` | Irish census boundaries | None |
| GeoHive | `geospatial/geohive.py` | Irish spatial data | WFS |
| Met Office | `geospatial/met_office.py` | UK weather data | Cursor |

#### Crown Dependencies (2 sources)

| Source | Module | Description |
|--------|--------|-------------|
| Isle of Man | `crown_dependencies/isle_of_man.py` | IoM education |
| Channel Islands | `crown_dependencies/channel_islands.py` | Jersey/Guernsey |

### Pagination Strategies

Five pagination strategies are implemented in `pagination.py`:

```python
# 1. Cursor-based (Slack, Stripe, GitHub)
paginator = CursorPagination(
    cursor_path="meta.next_cursor",
    cursor_param="cursor",
)

# 2. Offset-based (SQL-backed APIs)
paginator = OffsetPagination(
    limit=100,
    offset_param="offset",
    limit_param="limit",
)

# 3. Page number (traditional web APIs)
paginator = PageNumberPagination(
    per_page=50,
    page_param="page",
    per_page_param="per_page",
)

# 4. Header link (RFC 5988 - GitHub API)
paginator = HeaderLinkPagination()
# Parses: Link: <https://api.example.com/items?page=2>; rel="next"

# 5. JSON link (next URL in response body)
paginator = JSONLinkPagination(next_url_path="links.next")
```

### DLT Source Mixins

```python
from sruth.shared.dlt import (
    PaginatedSourceMixin,    # Handles pagination strategies
    RateLimitedSourceMixin,  # Rate limiting with backoff
    CachedSourceMixin,       # Response caching
    AuthenticatedSourceMixin, # Auth strategies
    IncrementalSourceMixin,  # Incremental loading
)
```

---

## Cross-Cutting Patterns

### Database Safety

**DuckDB Single-Threaded Access:**

```python
from sruth.shared import SerialDatabaseExecutor, run_serial, HNSW_DROP_THRESHOLD

# Use SerialDatabaseExecutor for all DuckDB operations
executor = SerialDatabaseExecutor()
result = await executor.execute(query)

# Convenience function
result = run_serial(lambda conn: conn.execute("SELECT * FROM table"))
```

**LanceDB MVCC:**

```python
# LanceDB is multi-process safe via MVCC
# Within process: Single-threaded via SerialDatabaseExecutor
# Between processes: MVCC + automatic conflict resolution
# Write concurrency: Supported with retry/backoff
```

### Embedding Batching

```python
from sruth.shared import EmbeddingBatcher, MIN_BATCH_SIZE, batch_embed

# MANDATORY: Batch minimum 100 (100x performance difference)
# Unbatched 1000 texts: ~100s
# Batched 1000 texts: ~1s

batcher = EmbeddingBatcher(batch_size=100)  # MANDATORY minimum
embeddings = await batcher.embed(texts)
```

### HNSW Index Management

```python
from sruth.shared import HNSW_DROP_THRESHOLD  # 50

if row_count > HNSW_DROP_THRESHOLD:
    # Drop index before insert (20x speedup)
    table.drop_index("vector_idx")

    # Bulk insert
    table.add(embeddings)

    # Recreate index
    table.create_index("vector_idx", index_type="IVF_HNSW")
```

### HTTP Client Factory

```python
from sruth.shared import HttpClientFactory, BearerTokenAuth, ApiKeyAuth

# Create resilient HTTP client
client = HttpClientFactory.create(
    base_url="https://api.example.com",
    auth=BearerTokenAuth(token="..."),
    timeout=30.0,
    retry_count=3,
    circuit_breaker=True,
)
```

### Observability

```python
from sruth.shared import (
    UnifiedTracer,
    DatadogBackend,
    LangfuseBackend,
    trace_agent_run,
    trace_tool_call,
)

# Configure unified tracing
tracer = UnifiedTracer(backends=[
    DatadogBackend(),
    LangfuseBackend(),
])

# Trace agent runs
@trace_agent_run("curriculum_search")
async def search_curriculum(query: str):
    pass

# Trace tool calls
@trace_tool_call("vector_search")
async def vector_search(query: str):
    pass
```

---

## Architecture Diagrams

### Overall Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SRUTH DATA ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │   Ireland   │     │     UK      │     │   Celtic    │     │  Geospatial │
   │  Education  │     │  Education  │     │  Language   │     │    Data     │
   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
          │                   │                   │                   │
          │    DLT Sources    │                   │                   │
          └───────────────────┼───────────────────┼───────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Dagster       │
                    │   Orchestration │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   DuckDB    │    │  CocoIndex  │    │   Kafka     │
   │  (Spatial)  │    │  Embeddings │    │  Streaming  │
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │
          │                  ▼                  │
          │           ┌─────────────┐           │
          │           │   LanceDB   │           │
          │           │  (Vectors)  │           │
          │           └──────┬──────┘           │
          │                  │                  │
          └────────┬─────────┼─────────┬────────┘
                   │         │         │
                   ▼         ▼         ▼
            ┌─────────────────────────────┐
            │      Graph Databases        │
            │  Memgraph | FalkorDB | Neo4j│
            └─────────────┬───────────────┘
                          │
                          ▼
            ┌─────────────────────────────┐
            │       BAML Extraction       │
            │   Type-Safe LLM Outputs     │
            └─────────────┬───────────────┘
                          │
                          ▼
            ┌─────────────────────────────┐
            │        ADK Agents           │
            │  Root | Curriculum | Geo    │
            │  Translation | Corpus       │
            └─────────────┬───────────────┘
                          │
                          ▼
            ┌─────────────────────────────┐
            │        FastAPI             │
            │  + Datadog APM + LLMObs    │
            └─────────────┬───────────────┘
                          │
                          ▼
            ┌─────────────────────────────┐
            │      TanStack Start UI      │
            │   Cloudflare Edge Deploy    │
            └─────────────────────────────┘
```

### Observability Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      OBSERVABILITY STACK                        │
└─────────────────────────────────────────────────────────────────┘

   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
   │   Datadog     │    │    MLflow     │    │   Langfuse    │
   │  APM + LLMObs │    │  Experiments  │    │  LLM Costs    │
   └───────┬───────┘    └───────┬───────┘    └───────┬───────┘
           │                    │                    │
           └────────────────────┼────────────────────┘
                                │
                                ▼
                    ┌───────────────────┐
                    │  UnifiedTracer    │
                    │  (sruth.shared)   │
                    └─────────┬─────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │  Agent      │    │   Pipeline  │    │    RAG      │
    │  Tracing    │    │   Metrics   │    │ Evaluation  │
    └─────────────┘    └─────────────┘    └─────────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │      Ragas        │
                    │  Quality Scores   │
                    └───────────────────┘
```

---

## Quick Reference

### Environment Variables

```bash
# Database
DUCKDB_PATH=./storage/data/main.duckdb
LANCEDB_PATH=./storage/data/lancedb

# LiteLLM Gateway
LITELLM_API_BASE=https://llm.cianfhoghlaim.ie
LITELLM_API_KEY=your-key

# Observability
DD_API_KEY=your-datadog-key
DD_SITE=datadoghq.eu
DD_SERVICE=oideachais
DD_LLMOBS_ENABLED=1

MLFLOW_TRACKING_URI=http://localhost:5000
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...

# Kafka
CONFLUENT_BOOTSTRAP_SERVERS=pkc-xxx.region.cloud:9092
CONFLUENT_API_KEY=your-key
CONFLUENT_API_SECRET=your-secret
```

### Commands

```bash
# Start Dagster for any flow
dagster dev -m sruth.oideachais.dagster_defs

# Start FastAPI
uvicorn sruth.oideachais.api.main:app --reload

# Run Marimo notebook
marimo run notebooks/analytics.py

# Start UI
cd sruth/oideachais/apps/web && pnpm dev

# Index with codeolas
codeolas index --repo /path/to/repo
codeolas search "database connection"
```

### Performance Guidelines

| Operation | Guideline |
|-----------|-----------|
| DuckDB access | Always use `SerialDatabaseExecutor` |
| Embedding batch size | Minimum 100 texts per batch |
| HNSW bulk insert | Drop index when inserting >50 rows |
| HTTP requests | Use `HttpClientFactory` with circuit breaker |
| LLM calls | Route through LiteLLM with fallbacks |

### Database Connections

| Database | Client | Notes |
|----------|--------|-------|
| DuckDB | `DuckDBClient` via `SerialDatabaseExecutor` | Single-threaded only |
| LanceDB | `LanceDBClient` | MVCC safe, batch embeddings |
| Memgraph | `MemgraphClient` | Bolt protocol |
| FalkorDB | `FalkorDBClient` | Redis protocol |
| Neo4j | `Neo4jClient` | Bolt protocol |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-12 | Initial architecture documentation |

---

*Generated from codebase analysis - December 2024*
