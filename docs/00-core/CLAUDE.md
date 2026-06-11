---
title: 'Cianfhoghlaim - AI Agent Instructions'
domain: 'agents'
status: 'stable'
description: 'Cianfhoghlaim (Irish: \\\\"deep learning\\\\"): Celtic language education platform with AI-powered tools for Irish curriculum. Bilingual focus on English/Irish with pan-Celtic language support (Welsh, Scottish Gaelic, Manx).'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/CLAUDE.md
ccc_query_hints:
  - cianfhoghlaim - ai agent instructions
---

# Cianfhoghlaim - AI Agent Instructions

## PROJECT_IDENTITY
Cianfhoghlaim (Irish: "deep learning"): Celtic language education platform with AI-powered tools for Irish curriculum. Bilingual focus on English/Irish with pan-Celtic language support (Welsh, Scottish Gaelic, Manx).

**Purpose:** Transform Irish educational content (NCCA curriculum, SEC exams, Dept of Education circulars) into searchable, AI-enhanced learning experiences.

**Scope:**
- 63 Claude skills in `.claude/skills/`
- 5 data flows (sruth/) for curriculum processing
- 25+ infrastructure stacks (bonneagar/)
- 70+ ML sources, 20+ models (meaisínfhoghlaim/)
- 2,178+ research documents (taighde_*/)

## CRITICAL_CONSTRAINTS

### Database Safety
- **DuckDB:** SINGLE_THREADED_ONLY (concurrent access = segfault/corruption)
- **LanceDB:** MULTI_PROCESS_SAFE via MVCC
  - Within process: Single-threaded via SerialDatabaseExecutor
  - Between processes: MVCC + automatic conflict resolution
  - Write concurrency: Supported with retry/backoff
- **NEVER:** Concurrent database operations (parsing parallelized, storage single-threaded)

### Embedding Performance
- **Batching:** MANDATORY (100x performance difference)
  - Unbatched 1000 texts: ~100s
  - Batched 1000 texts: ~1s
- **HNSW Index Management:**
  - DROP indexes before bulk inserts >50 rows (20x speedup)
  - RECREATE after batch complete
- **Minimum batch size:** 100 embeddings per API call

### BAML Schema Validation
- SCHEMA_VALIDATION_REQUIRED before LLM calls
- Use type-safe extraction for curriculum documents
- Test schemas in `baml_src/` before production use

### Irish Language Processing
- Irish is <0.1% of web content (~20% model performance gap)
- Use specialized models: UCCIX-Llama2-13B-Instruct, GaBERT, Qwen2.5-Math
- Handle dialects: Connacht, Munster, Ulster, Standard

## DIRECTORY_MAP

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `sruth/` | Data pipelines (5 flows) | `códeolas/`, `gaois/`, `tionscnamh/`, `tuath/`, `oideachas/` |
| `bonneagar/` | Infrastructure stacks | Docker Compose files, deployment configs |
| `agents/` | AI agent frameworks | Agno agents, crew configurations |
| `meaisínfhoghlaim/` | ML sources and models | Training data, fine-tuned models |
| `taighde/patterns/` | **Actionable pattern files** | `PATTERNS_*.md` (agents, pipelines, storage, etc.) |
| `taighde/agents/` | Agent framework references | `google-adk/`, `agno/`, `stagehand/`, `durable/` |
| `taighde/cocoindex/` | CocoIndex flow examples | 20+ canonical embedding/extraction flows |
| `taighde/_archive/` | Superseded research | Historical docs, deprecated examples |
| `taighde_bonneagar/` | Infrastructure research | 100+ docs on tools, patterns |
| `taighde_scoil/` | Education research | Curriculum analysis, indexing strategies |
| `taighde_meaisínfhoghlaim/` | ML research | Model evaluations, training guides |
| `taighde_teanga/` | Language research | Celtic NLP, ASR/TTS resources |
| `taighde_new/` | New research intake | Unsorted research documents |
| `baml_src/` | BAML schemas | Type-safe LLM extraction |
| `.claude/skills/` | 63 Claude skills | Managed skill definitions |

## SRUTH DATA FLOWS

| Flow | Purpose | Status |
|------|---------|--------|
| `códeolas/` | Code analysis and documentation | Active |
| `gaois/` | Irish language processing | Active |
| `tionscnamh/` | Project management | Active |
| `tuath/` | Community content | Active |
| `oideachas/` | Education curriculum processing | Primary focus |

## SKILLS_REFERENCE

**ALWAYS check `.claude/skills/` before implementing.** 63 skills available:

**Celtic Language & Education (4):**
- `celtic-language-ai` - Irish, Welsh, Scottish Gaelic, Manx NLP models
- `irish-edtech` - Irish curriculum and bilingual education platform
- `oideachas-pipeline` - Celtic education curriculum processing with DLT/CocoIndex/Dagster
- `graphiti` - Bi-temporal knowledge graphs for curriculum versioning

**Document Processing (6):**
- `document-intelligence` - VLM, OCR, PDF extraction, table parsing
- `baml` - Type-safe LLM outputs with schema validation
- `pdf`, `xlsx`, `docx`, `pptx` - Office document format handling

**Data Infrastructure (12):**
- `duckdb`, `lancedb`, `memgraph`, `falkordb` - Databases (SQL, vector, graph)
- `dlt`, `dagster`, `cocoindex` - ETL/pipeline orchestration
- `risingwave` - Streaming SQL for real-time analytics
- `ducklake`, `olake` - Data lakehouse solutions
- `ibis` - Portable dataframe library (multi-backend)
- `convex` - Real-time serverless backend

**ML/AI Operations (10):**
- `huggingface` - Transformers, model hub, datasets
- `hf-llm-trainer`, `hf-paper-publisher`, `hf-dataset-creator`, `hf-model-evaluation` - HuggingFace workflows
- `litellm`, `mlflow` - LLM routing and experiment tracking
- `unsloth` - Efficient LLM fine-tuning (70% VRAM reduction)
- `cognee` - AI memory and knowledge graph systems
- `pydantic` - Data validation and settings management

**Data Collection (4):**
- `crawl4ai`, `firecrawl` - Web scraping and extraction
- `chunkhound` - Semantic code search with MVCC
- `beads` - Distributed issue tracking for AI agents

**Frontend & Design (10):**
- `tanstack-start`, `hono`, `cloudflare` - Edge-native web frameworks
- `marimo`, `evidence` - Notebooks and BI dashboards
- `canvas-design`, `theme-factory`, `frontend-design` - UI/UX design systems
- `brand-guidelines` - Brand identity management
- `web-artifacts-builder` - Interactive web component creation

**Infrastructure & DevOps (9):**
- `dagger` - CI/CD pipelines with TypeScript SDK
- `docker-compose` - Container orchestration
- `komodo`, `pangolin` - Deployment and network management
- `pulumi` - Infrastructure as Code
- `agno` - Multi-agent orchestration
- `effect-ts`, `orpc` - Type-safe APIs and RPC
- `feast` - Feature store for ML

**Developer Tools (8):**
- `skill-creator`, `mcp-builder` - Claude extension development
- `oh-my-opencode` - Developer environment toolkit
- `webapp-testing` - Automated web testing
- `algorithmic-art` - Generative art creation
- `doc-coauthoring`, `internal-comms`, `slack-gif-creator` - Collaboration tools

## KEY_COMMANDS

```bash
# Development
uv sync                            # Install dependencies
uv run pytest tests/               # Run tests

# Data pipelines
dagster dev -m sruth.oideachas     # Start Dagster UI
marimo edit notebook.py            # Edit Marimo notebook

# Infrastructure
docker-compose -f bonneagar/<stack>/docker-compose.yml up -d

# Skills
ls .claude/skills/                  # List available skills
cat .claude/skills/<skill>/SKILL.md # Read skill documentation
```

## MODIFICATION_RULES

- **NEVER:** Remove SerialDatabaseProvider wrapper from database code
- **NEVER:** Add concurrent database operations
- **NEVER:** Skip BAML schema validation for LLM extractions
- **NEVER:** Process embeddings without batching
- **ALWAYS:** Check existing skills before implementing features
- **ALWAYS:** Use uv for all Python operations
- **ALWAYS:** Batch embeddings (min: 100, max: provider_limit)
- **ALWAYS:** Drop HNSW indexes for bulk inserts >50 rows

## PATTERNS_REFERENCE

**Consolidated pattern files in `taighde/patterns/`:**

| Pattern File | Focus | Key Patterns |
|--------------|-------|--------------|
| `PATTERNS_AGENTS.md` | Agent design | ADK routing, SequentialAgent, Agno teams, Stagehand browser |
| `PATTERNS_DATA_PIPELINE.md` | ETL flows | DLT REST API, Dagster assets, CocoIndex transforms |
| `PATTERNS_STORAGE.md` | Databases | SerialDatabaseExecutor, HNSW management, DuckLake CDC |
| `PATTERNS_EMBEDDINGS.md` | Vector ops | Batching (min 100), model selection, chunking strategies |
| `PATTERNS_BAML.md` | LLM extraction | Type-safe schemas, multimodal, curriculum entities |
| `PATTERNS_WEB.md` | Frontend | TanStack Start, AG-UI protocol, SSE streaming |
| `PATTERNS_OBSERVABILITY.md` | Monitoring | Datadog LLMObs, MLflow, Langfuse, Ragas |

**Always check pattern files before implementing new features.**

## TECHNOLOGY_STACK

| Layer | Technology | Purpose |
|-------|------------|---------|
| Document Ingestion | ColPali, DeepSeek-OCR, Granite-Docling | Multi-modal extraction |
| Knowledge Base | FalkorDB + Qdrant | Hybrid vector/graph |
| Temporal Reasoning | Graphiti | Bi-temporal data model |
| ETL Orchestration | CocoIndex, Dagster, DLT | High-velocity pipelines |
| Structured Extraction | BAML | Type-safe LLM outputs |
| RAG Retrieval | BGE-M3 + ColPali | Dense + sparse + visual |
| Generation | Qwen2.5-Math-7B, UCCIX | Bilingual math/Irish |
| Frontend | TanStack Start + Cloudflare | Edge-native rendering |
| Agent Protocols | AG-UI, MCP-UI | Agent-frontend communication |
| Durable Execution | Restate, DBOS | Crash-resistant agent workflows |
| Interactive Compute | Marimo WASM | Browser-based Python |
| BI Semantic Layer | Cube, Rill | Metric definitions, dashboards |

## COMMON_ERRORS_AND_SOLUTIONS

| Error | Cause | Solution |
|-------|-------|----------|
| Database locked | Concurrent access attempted | Use SerialDatabaseProvider |
| Segmentation fault | DuckDB multi-threading | Single-threaded access only |
| Slow embeddings | Unbatched API calls | Batch minimum 100 texts |
| HNSW timeout | Large bulk insert | Drop index before, recreate after |
| Irish OCR failures | Model not trained on Irish | Use UCCIX or GaBERT |
| BAML validation error | Schema mismatch | Update BAML schema first |
| AG-UI event dropped | Missing event handler | Implement all 17 AG-UI event types |
| Stagehand timeout | Selector not found | Use observe() before act() |
| DLT pagination fails | Wrong paginator type | Check API docs for cursor vs link header |
| CocoIndex flow stalls | Blocking I/O in transform | Use async generators |
| DuckLake query slow | Missing partition pruning | Add partition columns to WHERE |

## RESEARCH_ORGANIZATION

| Directory | Count | Focus |
|-----------|-------|-------|
| `taighde_bonneagar/` | 500+ | Infrastructure patterns |
| `taighde_scoil/` | 300+ | Education/curriculum |
| `taighde_meaisínfhoghlaim/` | 400+ | ML/AI techniques |
| `taighde_teanga/` | 200+ | Celtic language NLP |
| `taighde_new/` | Variable | New research intake |

## PROJECT_CONVENTIONS

### Naming
- Irish names for core concepts (sruth=flow, bonneagar=infrastructure)
- English for technical implementation
- Bilingual support in all user-facing content

### File Organization
- Research in `taighde_*/` directories
- Skills in `.claude/skills/<name>/SKILL.md`
- Infrastructure in `bonneagar/<stack>/`
- Pipelines in `sruth/<flow>/`

### Data Flow Pattern
```
Sources → DLT Ingestion → CocoIndex Transform → Vector/Graph Store → RAG Retrieval → BAML Extraction
```

## RESOURCES

- **NCCA Curriculum:** https://curriculumonline.ie
- **SEC Exams:** https://examinations.ie
- **UCCIX Demo:** https://aine.chat
- **GaBERT:** https://huggingface.co/DCU-NLP/bert-base-irish-cased-v1
- **TanStack Start:** https://tanstack.com/start
- **Marimo:** https://marimo.io
