# Cianfhoghlaim Project Analysis

## Overview

This is a comprehensive research and development ecosystem for building **Anam** - a learn-to-earn cryptocurrency platform for Celtic language education through an educational MMO centered on British Isles mythology.

---

## Root Directory Summaries

### 1. BONNEAGAR (Infrastructure)
**Path:** `/Users/cliste/dev/cianfhoghlaim/bonneagar`

The production infrastructure layer containing deployment configurations, CI/CD pipelines, and operational tooling.

| Subdirectory | Purpose |
|--------------|---------|
| `SpacetimeDB/` | Distributed real-time database (Rust-based) for multiplayer game state |
| `beads/` | AI agent issue tracking and coordination system (Go-based) |
| `dagger_docs/` | Dagger CI/CD documentation and pipeline examples |
| `gdext/` | Godot Engine extension framework (multi-language: C++, Swift, Rust, Zig) |
| `greetings-api/` | Demo API project with Dagger pipelines |
| `hf-model-ops/` | Hugging Face model operations and CI/CD |
| `hophacks-spacetimedb-workshop/` | SpacetimeDB learning workshop |
| `komodo/` | Server orchestration and container management |
| `locket/` | Secrets injection from 1Password/Bitwarden |
| `mlflow_kafka_ducklake/` | ML ops + data streaming (MLFlow + Kafka + DuckDB) |
| `orchestration/` | Workflow orchestration tools |
| `pangolin/` | VPN, reverse proxy, tunneling infrastructure |
| `pixi_sqlmesh_ducklake/` | Data stack with SQLMesh + DuckDB + Dagster |
| `rawkode-academy/` | Educational platform reference (Bun monorepo) |
| `spacetimedb-cookbook/` | SpacetimeDB examples and patterns |
| `spacetimedb-typescript-sdk/` | TypeScript SDK for SpacetimeDB |
| `uv-dagger-dream/` | Python + Dagger integration |

**Key Technologies:** Dagger, Komodo, Ansible, 1Password, Docker, SpacetimeDB, Pangolin

---

### 2. MEAISÍNFHOGHLAIM (Machine Learning)
**Path:** `/Users/cliste/dev/cianfhoghlaim/meaisínfhoghlaim`

Machine learning research and model fine-tuning for Celtic language processing.

| Component | Purpose |
|-----------|---------|
| `OCR_ANALYSIS/` | Vision-language model research (Chandra, OlmOCR-2, DeepSeek-OCR, Qwen3-VL) |
| `on_device/` | iOS/Apple Silicon ML (MLX-VLM, Swift Transformers, AnyLanguageModel) |
| `federated/` | Flower framework for privacy-preserving distributed learning |
| `fine_tuning/` | Unsloth, LoRA hyperparameters, GGUF conversion workflows |
| `gpu_experiments/` | GPU optimization guides |

**Focus Areas:**
- OCR for Celtic language handwriting (Irish, Welsh, Scottish Gaelic)
- Edge AI deployment (local Mac, iOS)
- Efficient fine-tuning on consumer hardware
- Federated learning for educational data privacy

**Key Technologies:** MLX, Unsloth, Flower, vLLM, Transformers, GGUF/llama.cpp

---

### 3. SRUTH (Flows/Data Pipelines)
**Path:** `/Users/cliste/dev/cianfhoghlaim/sruth`

Data transformation pipelines using CocoIndex flows for knowledge extraction.

| Subdirectory | Purpose |
|--------------|---------|
| `códeolas/` | GitHub data intelligence (DLT + CocoIndex + Cognee → code analytics) |
| `gaois/` | Irish education curriculum indexing (exam papers, syllabi, bilingual content) |
| `scoil/` | Agent orchestration (placeholder) |
| `tionscnamh/` | Portfolio/music analytics (Spotify, SoundCloud → TanStack web app) |
| `tuath/` | DeFi/cryptocurrency analytics (CoinGecko, DeFiLlama, protocol docs) |

**códeolas/ subdirectories:**
- `pipelines/github_api/` - DLT source for GitHub REST API
- `cocoindex/` - Semantic code indexing with tree-sitter
- `cognee/` - Knowledge graph extraction
- `sqlmesh-ibis/` - Semantic layer for BI with agents
- `rill-github-analytics/` - Real-time GitHub dashboards
- `dagster/` - Orchestration integrations
- `ducklake/` - DuckDB + Iceberg lakehouse

**gaois/ subdirectories:**
- `sources/` - examinations.ie, curriculumonline.ie, ncca.ie scrapers
- `processing/` - VLM-based PDF/exam paper processing
- `indexers/` - Bilingual curriculum indexing

**tionscnamh/ subdirectories:**
- `pipelines/spotify/` - Spotify API integration
- `pipelines/soundcloud/` - Crawl4AI + R2 audio uploads
- `notebooks/` - Marimo analytics
- `web/` - TanStack Start portfolio app

**tuath/ subdirectories:**
- `sources/` - CoinGecko, DeFiLlama, Binance, Aave subgraphs
- `transformations/` - Ibis-based crypto analytics
- `indexers/` - Protocol documentation indexing
- `knowledge/` - Crypto domain ontology

**Key Technologies:** CocoIndex, DLT, LanceDB, Memgraph, DuckDB, Marimo, Firecrawl

---

### 4. TAIGHDE (Research)
**Path:** `/Users/cliste/dev/cianfhoghlaim/taighde`

The comprehensive research repository with ~95,000 files across 7 categories.

| Category | Path | Files | Purpose |
|----------|------|-------|---------|
| **BASE** | `base/` | 123 | Infrastructure & AI foundation research |
| **BONNEAGAR** | `bonneagar/` | 24,028 | Game engine & systems architecture research |
| **DATA** | `data/` | 2,331 | AI data pipelines & agent frameworks |
| **GAEILGE** | `gaeilge/` | 10,142 | Irish language resources & datasets |
| **MEAISÍNFHOGHLAIM** | `meaisínfhoghlaim/` | 477 | ML & model fine-tuning research |
| **TUATH** | `tuath/` | 2,913 | Complete Anam project architecture |
| **WEB** | `web/` | 55,184 | Frontend & UI framework research |

#### base/ subdirectories (18 numbered categories):
- `00-infra-overview/`, `00-ml-overview/`
- `01-celtic-language-ai-resources/`, `01-irish-edtech-platform/`, `01-selfhosting/`
- `02-celtic-data-acquisition/`, `02-cicd/`, `02-multimodal-document-intelligence/`
- `03-ai-native-data-pipelines/`, `03-bilingual-dataset-creation/`, `03-cloud-services/`
- `04-geospatial-linguistics/`, `04-web-automation-archival/`
- `05-education-policy-context/`, `05-knowledge-graph-infrastructure/`
- `06-document-processing/`, `06-platform-engineering/`
- `07-technical-implementation/`

#### data/ subdirectories:
- `agno/` - Agent framework
- `baml/` - Type-safe LLM outputs
- `cocoindex/` - Semantic chunking
- `dlt/`, `dspy/`, `marimo/`, `pydantic_ai/`

#### gaeilge/ subdirectories:
- `An-Scealai/` - Online Irish learning platform (TCD research)
- `IRLBench/` - Multi-modal Irish-English LLM benchmark
- `gaois/` - Irish language data aggregation
- `kscanne/` - Kevin P. Scannell's language tools
- `datasets/` - British Isles parallel corpora

#### tuath/ subdirectories (13 functional areas):
- `game-design/` - Celtic mythology (Tuatha Dé Danann, Cúchulainn)
- `frontend/` - TanStack Start + MCP-UI
- `data-pipeline/` - Dagster workflows
- `ml-models/` - Whisper, OCR, Qwen-VL
- `smart-contracts/` - ERC20, ERC721, staking
- `tokenomics/` - L2E model, x402 payments
- `infrastructure/` - Scaffold-ETH, Arbitrum/Base
- `buntaighde/` - Research consolidation
- `consolidated/` - Integrated documentation

#### web/ subdirectories (25 framework projects):
- `tanstack/` - TanStack Start, Router, Query
- `CopilotKit/` - AI chat interface SDK
- `baml/` - Type-safe LLM outputs
- `ag-ui/` - AI-native UI components
- `duckdb/`, `cloudflare/`, `hono/`, `orpc/`
- `convex/`, `restate/` - Real-time backends

---

## Vertical Integration

```
┌─────────────────────────────────────────────────────────────────┐
│                        TAIGHDE (Research)                       │
├─────────────────────────────────────────────────────────────────┤
│  GAEILGE → MEAISÍNFHOGHLAIM → DATA → BASE → BONNEAGAR → TUATH  │
│  (Language)   (ML Models)    (Pipelines) (Infra) (Engine) (Game)│
│                              ↓                                  │
│                            WEB (Frontend)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   PRODUCTION DIRECTORIES                         │
├─────────────────────────────────────────────────────────────────┤
│  bonneagar/     meaisínfhoghlaim/     sruth/                    │
│  (Infra)        (ML)                   (Data Flows)             │
└─────────────────────────────────────────────────────────────────┘
```

## Cross-Cutting Technologies

| Layer | Technologies |
|-------|-------------|
| **AI/ML** | Claude, Qwen-VL, Whisper, LLaMA, MLX, Unsloth |
| **Data** | DLT, Dagster, DuckDB, LanceDB, Cognee, CocoIndex |
| **Infrastructure** | Komodo, Pangolin, Cloudflare, Ansible, Dagger |
| **Blockchain** | x402 payments, ERC20/ERC721, SpacetimeDB |
| **Frontend** | TanStack Start, React, CopilotKit |
| **Game Engine** | Godot (GDExt), Babylon.js, SpacetimeDB |

---

## Rust & Package Inventory

### TAIGHDE Rust Packages

#### 1. x402-rs (HTTP 402 Payment Protocol)
**Location:** `taighde/tuath/x402-rs/`
**Version:** 0.10.0
**Purpose:** Rust implementation of x402 protocol for blockchain-based HTTP payments

| Crate | Version | Purpose |
|-------|---------|---------|
| `x402-rs` | 0.10.0 | Core protocol types, facilitator traits, on-chain verification |
| `x402-axum` | 0.6.3 | Axum middleware for enforcing x402 payments |
| `x402-reqwest` | 0.4.1 | Reqwest wrapper for transparent x402 client payments |

**Key Dependencies:** Axum 0.8.4, Tokio 1.45, Alloy 1.0.7 (EVM), Solana SDK 2.3.1, OpenTelemetry 0.30

---

#### 2. AG-UI Rust SDK
**Location:** `taighde/web/ag-ui/sdks/community/rust/`
**Version:** 0.1.0
**Purpose:** Client library for the AG-UI agent protocol

| Crate | Purpose |
|-------|---------|
| `ag-ui-core` | Core type library (minimal deps) |
| `ag-ui-client` | HTTP Agent pattern for agent communication |

---

#### 3. SpacetimeDB (Distributed Database)
**Location:** `taighde/bonneagar/SpacetimeDB/`
**Version:** 1.11.1
**Purpose:** Distributed database for real-time multiplayer applications
**Crates:** 40+ internal workspace crates

| Category | Crates |
|----------|--------|
| **Core** | spacetimedb-cli, spacetimedb-core, spacetimedb-lib, spacetimedb-sdk |
| **Data** | datastore, data-structures, table, snapshot, durability, commitlog |
| **Query** | query, expression, physical-plan, execution, sql-parser |
| **Module** | bindings, bindings-macro, bindings-sys, codegen |

**Key Dependencies:** Tokio 1.37, Axum 0.7, Wasmtime 39, V8 140.2, PostgreSQL support

---

#### 4. GDExt/Rustshipper (Godot Bindings)
**Location:** `taighde/bonneagar/gdext/rust/`
**Version:** 0.1.0
**Purpose:** Rust bindings for Godot game engine using GDExt

---

### TAIGHDE Python Packages

#### 1. Pydantic AI Demo
**Location:** `taighde/data/pydantic_ai/`
**Python:** >= 3.12
**Key Deps:** pydantic-ai 1.20, FastAPI, MCP 1.15, Tavily, DBOS 2

#### 2. Bindu (Agent-to-Agent Protocol)
**Location:** `taighde/tuath/Bindu/`
**Python:** >= 3.12
**Purpose:** Secure agent-to-agent communication with cryptography and observability
**Key Deps:** FastAPI, cryptography 44.0, OpenTelemetry 1.35

#### 3. AP2 (Agent Payments Protocol)
**Location:** `taighde/tuath/AP2/`
**Python:** >= 3.10
**Purpose:** Payment protocol for agent-to-agent transactions

#### 4. MLFlow Kafka DuckLake
**Location:** `taighde/bonneagar/mlflow_kafka_ducklake/`
**Version:** 1.1.0 | **Python:** >= 3.13
**Purpose:** Data lab combining Kafka streaming, DuckDB analytics, dbt transforms
**Key Deps:** aiokafka, duckdb 1.4.1, dbt-core 1.9.6, FastAPI, JupyterLab

---

### MEAISÍNFHOGHLAIM Packages

#### Rust ML Frameworks

| Package | Location | Version | Purpose |
|---------|----------|---------|---------|
| **Burn** | `cleachtadh/burn/` | 0.20.0-pre.6 | Deep learning framework with multi-backend support (CUDA, ROCm, Metal, WebGPU) |
| **Candle** | `cleachtadh/candle/` | 0.9.2-alpha.2 | Minimalist ML framework with GPU support |
| **Mistral.rs** | `cleachtadh/mistral.rs/` | 0.7.0 | Fast LLM serving with MCP support |
| **Uzu** | `cleachtadh/uzu/` | 0.1.7 | High-performance inference for Apple Metal |
| **WGPU** | `cleachtadh/wgpu/` | - | WebGPU implementation (27+ crates) |

**Burn Sub-crates (45+):** burn-core, burn-tensor, burn-nn, burn-train, burn-autodiff, burn-cuda, burn-rocm, burn-wgpu, burn-vision, burn-import (ONNX/PyTorch)

**Candle Sub-crates:** candle-core, candle-nn, candle-transformers, candle-pyo3, candle-onnx, candle-flash-attn, WASM examples (Whisper, LLaMA2, T5, BERT, BLIP)

**Mistral.rs Sub-crates:** mistralrs-core, mistralrs-server, mistralrs-pyo3, mistralrs-vision, mistralrs-audio, mistralrs-mcp

---

#### Python ML Packages

| Package | Location | Purpose |
|---------|----------|---------|
| **Unstract** | `foinse/models/eile/unstract/` | Enterprise ETL platform for unstructured data |
| **OLMo** | `cleachtadh/OLMo/` | Open Language Model (pre-trained LLM) |
| **Open-Instruct** | `cleachtadh/open-instruct/` | Instruction-following model training |
| **GLM-V** | `cleachtadh/GLM-V/` | Multimodal vision-language model |
| **ColPali** | `cleachtadh/colpali/` | Vision document retrieval embeddings |
| **Sam-Audio** | `cleachtadh/sam-audio/` | Segment Anything for audio |
| **SAM 3D API** | `cleachtadh/sam3d-api/` | SAM 2 with 3D Gaussian splat generation |
| **FIBO** | `cleachtadh/FIBO/` | Fine-grained image generation control |
| **Gemma Cookbook** | `cleachtadh/gemma-cookbook/` | Demo apps (web, code assistant) |

**Unstract Components:**
- `unstract-backend` - Django REST API with Celery
- `unstract-workers` - Celery background workers
- `unstract-sdk1` - SDK with LiteLLM, Llama-Index, vector DB adapters
- `unstract-frontend` - React 18 + Ant Design UI

---

## Technology Stack Summary

### Language Breakdown
| Language | Crates/Packages | Focus |
|----------|-----------------|-------|
| **Rust** | 120+ crates | ML inference, databases, game engine, payments |
| **Python** | 40+ packages | LLMs, vision, audio, ETL, training |
| **TypeScript** | 25+ projects | Web frontends, SDKs, APIs |

### GPU/Compute Backends
- **NVIDIA:** CUDA (Burn, Candle, Mistral.rs)
- **AMD:** ROCm (Burn)
- **Apple:** Metal (Burn, Uzu, Candle), MLX
- **Cross-platform:** Vulkan, WebGPU (WGPU, Burn)
- **Intel:** MKL (Candle)

### Observability
OpenTelemetry integrated across x402-rs, SpacetimeDB, Bindu, Unstract

---

## Summary

This project is building a **Web3-enabled educational MMO** for Celtic language preservation through:
1. **Blockchain-based incentives** (learn-to-earn, x402 micropayments)
2. **AI-powered learning** (OCR for handwriting, speech synthesis, grammar checking)
3. **Celtic mythology** as game narrative (Tuatha Dé Danann, Cúchulainn, Brigid)
4. **Federated learning** for privacy-preserving educational data
5. **Sophisticated data pipelines** for curriculum, crypto, and code intelligence
6. **Rust ML stack** (Burn, Candle, Mistral.rs) for high-performance inference
7. **Multi-backend GPU support** (CUDA, ROCm, Metal, WebGPU) for cross-platform deployment
