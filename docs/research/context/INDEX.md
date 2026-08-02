# Cianfhoghlaim Context Library

Consolidated documentation for NotebookLM and LLM context research.
Curated from ~50,000 files across 16+ source directories.

**Generated:** 2025-12-30

---

## Quick Start

1. **Upload priority order for NotebookLM:**
   - `01-patterns/` - Proven implementation patterns (~3,800 lines)
   - `02-architecture/` - System architecture docs
   - `00-core/CLAUDE.md` - Project identity and constraints

2. **Total files:** 66 files across 9 categories

---

## Directory Contents

### 00-core/ (3 files)
Project identity, constraints, and specifications.

| File | Description |
|------|-------------|
| `CLAUDE.md` | Complete project identity, directory map, modification rules |
| `CONSTRAINTS.md` | Critical database safety, embedding batching, BAML validation |
| `PROJECT_SPEC.md` | Capability areas and naming conventions |

### 01-patterns/ (7 files)
Consolidated implementation patterns - **highest value for context**.

| File | Lines | Focus |
|------|-------|-------|
| `DATA_PIPELINE.md` | 510 | DLT REST API, Dagster assets, CocoIndex transforms |
| `AGENTS.md` | 282 | ADK routing, SequentialAgent, Agno teams, Stagehand |
| `STORAGE.md` | 587 | SerialDatabaseExecutor, HNSW management, DuckLake CDC |
| `EMBEDDINGS.md` | 637 | Batching strategies, model selection, chunking |
| `BAML.md` | 570 | Type-safe extraction, multimodal, curriculum entities |
| `WEB.md` | 621 | TanStack Start, AG-UI protocol, SSE streaming |
| `OBSERVABILITY.md` | 584 | Datadog LLMObs, MLflow, Langfuse, Ragas |

### 02-architecture/ (10 files)
System architecture documentation.

| File | Description |
|------|-------------|
| `OIDEACHAIS_PIPELINE.md` | Celtic education pipeline (37+ Dagster assets, 30+ DLT sources) |
| `ALEYUM_PORTFOLIO.md` | Portfolio pipeline (Spotify → SoundCloud → GitHub → Web) |
| `TUATH_MMO.md` | Celtic MMO with gamified education and AI tutoring |
| `SRUTH_OVERVIEW.md` | Overview of all four sruth data pipelines |
| `ML_SYSTEMS.md` | Comprehensive ML/AI systems architecture |
| `MULTI_AGENT_PRODUCTION.md` | Production multi-agent system patterns |
| `DOCUMENT_PROCESSING.md` | Document processing, OCR, multimodal extraction |
| `EDUCATION_ARCHITECTURE.md` | Complete education platform architecture |
| `AGENT_IMPLEMENTATIONS.md` | Summary of agent implementations |
| `IRISH_EDTECH.md` | Irish EdTech platform overview |

### 03-pipelines/ (8 files)
Data pipeline implementation examples.

| File | Type | Description |
|------|------|-------------|
| `dagster_definitions.py` | Python | Unified Dagster configuration |
| `dagster_factories.py` | Python | Asset factory patterns |
| `curriculum_embedding.py` | Python | CocoIndex embedding pipeline |
| `api_main.py` | Python | FastAPI with observability |
| `ag_ui_protocol.py` | Python | AG-UI 17-event protocol |
| `storage_init.py` | Python | Multi-database storage layer |
| `observability_init.py` | Python | Unified observability integration |
| `AI_ML_PIPELINE.md` | Markdown | AI/ML pipeline architecture |

### 04-agents/ (6 files)
Agent framework documentation and examples.

| File | Description |
|------|-------------|
| `browser_orchestrator.py` | Google ADK multi-agent pipeline |
| `durable_orchestrator.py` | Restate durable execution with agents |
| `browser_session.py` | Multi-backend browser session management |
| `MCP_RESEARCH.md` | Model Context Protocol research |
| `TECH_STACK.md` | Educational website technology stack |
| `TUATH_QUICKSTART.md` | Celtic MMO quick start guide |

### 05-celtic-language/ (6 files)
Celtic NLP and language resources.

| File | Description |
|------|-------------|
| `CELTIC_AI_RESOURCES.md` | Comprehensive Celtic language AI catalog |
| `LANGUAGE_ARCHITECTURE.md` | Language processing architecture |
| `BILINGUAL_EDTECH.md` | Bilingual platform architecture |
| `IRISH_HUGGINGFACE.md` | Irish language HuggingFace resources |
| `MODEL_TRAINING.md` | Model training strategies for Celtic languages |
| `IRISH_ENGLISH_EDUCATION.md` | Bilingual Irish-English education |

### 06-infrastructure/ (6 files)
Deployment and infrastructure configuration.

| File | Description |
|------|-------------|
| `BONNEAGAR_OVERVIEW.md` | 19 storage stacks, Pangolin routing, Locket secrets |
| `auto-deploy-stacks.toml` | 70+ infrastructure stacks with server assignments |
| `ML_MODELS_REGISTRY.md` | 70+ ML models registry |
| `ML_STACK.md` | Resource allocation across cloud providers |
| `models_registry.yaml` | Central model configuration |
| `celtic_ml_models.yaml` | Celtic language models catalog |

### 07-skills/ (12 files)
Claude skill definitions for key technologies.

| Skill | Focus |
|-------|-------|
| `oideachas-pipeline.md` | Celtic education curriculum pipeline |
| `celtic-language-ai.md` | Irish, Welsh, Scottish Gaelic, Manx NLP |
| `baml.md` | Type-safe LLM extraction |
| `cocoindex.md` | ETL flows for embeddings |
| `dlt.md` | Data ingestion pipelines |
| `dagster.md` | Orchestration and asset management |
| `lancedb.md` | Vector database with MVCC |
| `duckdb.md` | Single-threaded SQL database |
| `memgraph.md` | Graph database |
| `graphiti.md` | Bi-temporal knowledge graphs |
| `agno.md` | Multi-agent orchestration |
| `tanstack-start.md` | Edge-native web framework |

### 08-examples/ (8 files)
Canonical implementation examples.

| File | Description |
|------|-------------|
| `DATA_ARCHITECTURE.md` | Data model and schema design |
| `FRONTEND_STACK.md` | Frontend technologies and UI/UX |
| `SUBJECT_IMPLEMENTATIONS.md` | Subject-specific curriculum mapping |
| `MODEL_FINETUNING.md` | Model fine-tuning strategies |
| `IMPLEMENTATION_GUIDE.md` | Step-by-step implementation guide |
| `OPENSPEC_AGENTS.md` | OpenSpec workflow and validation |
| `OIDEACHAIS_SPEC.md` | Curriculum processing requirements |
| `BEADS_TRACKER.md` | Distributed issue tracking setup |

---

## Critical Constraints

From `00-core/CONSTRAINTS.md`:

| Constraint | Rule |
|------------|------|
| **DuckDB** | SINGLE_THREADED_ONLY (concurrent access = segfault) |
| **Embeddings** | Batch minimum 100 (100x performance difference) |
| **HNSW Index** | DROP before bulk >50 rows, RECREATE after |
| **Irish Language** | Use specialized models (UCCIX, GaBERT, Qwen2.5-Math) |
| **BAML** | Schema validation REQUIRED before LLM calls |

---

## Source Directories (Excluded)

| Directory | Files | Reason Excluded |
|-----------|-------|-----------------|
| taighde_crypteolas_tuath | 35,475 | Library clones, low relevance |
| taighde_old | 362 | Superseded by newer docs |
| Most of taighde_scoil | 12,000+ | Bulk curriculum data |
| Most of taighde_meaisínfhoghlaim | 600+ | Raw training references |
