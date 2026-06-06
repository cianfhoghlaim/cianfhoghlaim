# Meaisínfhoghlaim (Machine Learning)

> Irish: *machine learning*. The AI/ML quadrant of the Cianfhoghlaim stack —
> specialised agents, OCR, Celtic-language data, and ML pipelines that feed
> the curriculum knowledge graph consumed by `oideachais/`, the dashboards in
> `croilar/apps/portal/`, and the public-facing Marimo notebooks in
> `croilar/notebooks/`.

Meaisínfhoghlaim is the **AI services layer** of the monorepo. Where
`oideachais/` is the lakehouse and `croilar/` is the multi-persona platform,
Meaisínfhoghlaim is what populates the lakehouse with structured data and
serves the live inference surface.

---

## 1. What lives here

Eight tightly integrated components, ~15,000+ lines of Python:

| Component | Purpose | Entry point | Status |
|:--|:--|:--|:--|
| **AI Agents** | 12 specialised agents (curriculum, translation, corpus, research, geospatial, voice, ADK research) with root-router | `agents/` | Functional |
| **OCR / HTR** | 10 OCR models across 6 backends with Irish-specific metrics (fadas, tironian, punctum delens) | `ocr/` | Functional |
| **Celtic Language Data** | DLT sources for Dúchas, Canúint, Téarma, Gaois + 6-language cognate DB | `language/` | Functional |
| **ML Pipelines** | Irish document scanner, dialect classifier, transcript aligner, LLM router | `pipelines/` | Functional |
| **Text Alignment** | Sentence-level Irish↔English aligner, ColPali visual aligner, G2P, dataset export | `alignment/` | Functional |
| **RAG Evaluation** | RAGAS evaluation: baseline 65.2% → agentic 87.9% (+22.7%) | `evaluation/` | Functional |
| **Content Quality** | Curriculum document quality + completeness + audio validation | `quality/` | Functional |
| **Model & Data Catalog** | 13 models (text/embeddings/speech/vision) + 16 data sources + 3 training mixes | `catalog/` | Functional |

Plus **services** (FastAPI wrappers for agents + pipelines as standalone
microservices) and **scripts** (HF model download, GGUF conversion).

---

## 2. Architecture

```
                         ┌──────────────────────────────────────┐
                         │       Meaisínfhoghlaim (uv: ml)      │
                         └────────────────┬────────────────────┘
                                          │
        ┌─────────────┬──────────────────┼──────────────────┬──────────────┐
        ▼             ▼                  ▼                  ▼              ▼
   ┌─────────┐  ┌──────────┐  ┌─────────────────┐  ┌─────────┐  ┌──────────┐
   │ AGENTS  │  │   OCR   │  │ LANGUAGE DATA   │  │PIPELINES│  │ALIGNMENT │
   │  (12)   │  │  (10    │  │  (6 languages,  │  │(4 full  │  │(en↔ga,  │
   │  5K LOC │  │ models) │  │  4 DLT sources) │  │ suites) │  │ ColPali) │
   └────┬────┘  └────┬────┘  └────────┬────────┘  └────┬────┘  └────┬─────┘
        │            │                │                │             │
        └────────────┴────────┬───────┴────────────────┴─────────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  EVALUATION (RAGAS)  │  baseline 65.2% → agentic 87.9%
                  │  QUALITY (content +  │  +22.7pp improvement
                  │  audio validation)   │
                  └─────────┬───────────┘
                            │
        ┌───────────────────┬──┴────┬──────────┬─────────────┐
        ▼                   ▼       ▼          ▼             ▼
   ┌─────────┐      ┌──────────┐ ┌─────┐  ┌────────┐  ┌──────────────┐
   │oideachais│      │ croilar  │ │FastAPI│ │LanceDB│  │LiteLLM Gateway│
   │lakehouse │      │ portal + │ │(8000)│ │ vectors│  │(all LLM calls)│
   │Dagster + │      │ notebooks│ └──────┘ └────────┘  └──────────────┘
   │CocoIndex│      │          │
   └─────────┘      └──────────┘
```

Every LLM call in this quadrant routes through the **LiteLLM gateway** at
`http://localhost:4000` (or `litellm.cianfhoghlaim.ie` in prod), with full
Langfuse + MLflow + Logfire observability.

---

## 3. Quick start

### 3.1 Bring up the inference server

```bash
# from the monorepo root
mise install                          # installs the toolchain (bun, uv, python3.12)

# llama-swap serves all 11 models (text / vision / image profiles)
docker compose -f meaisínfhoghlaim/compose.yaml up -d

# health check
curl http://localhost:10240/v1/models
```

### 3.2 Run a DLT source (offline / cached)

```bash
cd meaisínfhoghlaim
USE_LOCAL_SCRAPES=true \
  uv run python -c "from language.gaeilge.duchas import duchassource; print(duchassource())"
```

`USE_LOCAL_SCRAPES=true` routes every DLT source to the curated
`stedding/dev/eile/ingest_queue/` cache, never to the live network. The
meaisínfhoghlaim's three core DLT sources (Dúchas, Canúint, Téarma) all
respect this flag.

### 3.3 Start the FastAPI agent server

```bash
cd meaisínfhoghlaim
uv run python -m agents.api.main
# → http://localhost:8000
# → /docs (auto-generated OpenAPI)
# → /agent (AG-UI streaming endpoint)
```

### 3.4 Run the RAGAS evaluation

```bash
cd meaisínfhoghlaim
uv run python -m evaluation.run_evaluation \
  --language ga \
  --baseline     # or --agentic for the +22.7pp run
```

---

## 4. Components in depth

### 4.1 AI Agents (12 agents, ~5,000 LOC)

The agent surface is the user-facing inference layer. Every agent speaks
both a sync JSON API and the CopilotKit AG-UI streaming protocol.

| Agent | Framework | Domain |
|:--|:--|:--|
| `root_agent` | Custom + LiteLLM | Query routing (keyword + LLM), 5 domains, RisingWave streaming, Langfuse/Letta |
| `enhanced_orchestrator` | Custom + ADK | AG-UI protocol events, task lifecycle, Cognee/LanceDB memory |
| `curriculum_agent` | Custom | LanceDB semantic search + DuckDB LO queries, nation/level/subject filtering |
| `translation_agent` | Custom | 6 Celtic languages, 3 model backends (opus-mt, m2m100, NLLB) |
| `corpus_agent` | Custom | Dúchas.ie folklore search, dictionary lookup |
| `research_agent` | ADK | Iterative search → evaluate → compose with citations |
| `education_research_agent` | ADK (LoopAgent) | Cross-nation (IE/UK) education policy research |
| `bunchloch_research_agent` | ADK (SequentialAgent) | Local academic document research |
| `geospatial_agent` | ADK | LSOA/Data Zone spatial analysis, school accessibility |
| `statistics_agent` | ADK | Education metrics, trend analysis, benchmarking |
| `curriculum_comparison_agent` | ADK | Cross-nation curriculum mapping, LO comparison |
| `mcp_curriculum_agent` | Custom MCP | Orchestrates chunkhound, zai-mcp, Cognee, Firecrawl, LanceDB |
| `voice_agent` | Pipecat | Real-time ASR → Agent → TTS (Whisper/wav2vec2 → LLM → ABAIR/Chatterbox) |

**Entry point**: `agents/api/main.py` (FastAPI, 295 lines, Datadog APM +
Langfuse + MLflow + Logfire wired in).

**Routing strategy** (root_agent):
1. Keyword match against 5 domain allow-lists (curriculum, translation,
   corpus, research, geospatial).
2. If no keyword hit, call LiteLLM with a 1-shot classifier prompt.
3. Stream results back via AG-UI /agent endpoint with token-by-token
   SSE.

### 4.2 OCR & Handwriting Recognition (~3,500 LOC)

The OCR layer is a **multi-model comparison harness** with Irish-specific
evaluation metrics — there's no single "best" OCR model for Irish, so the
right answer is "run all 10 and pick by your content type".

**Model registry** (`ocr/model_registry.py`, 543 lines, 10 models × 6 backends):

| Model | Best for | Backend |
|:--|:--|:--|
| olmOCR-2 | Printed Irish, structured tables | LiteLLM |
| Qwen2.5-VL | Handwritten + printed mixed | Transformers |
| DeepSeek-OCR | Dense print (legal, exam papers) | LiteLLM |
| Granite-Docling | Document layout preservation | LiteLLM |
| GPT-4o | General fallback | OpenAI |
| Claude 3.5 Sonnet | Marking schemes, complex layouts | Anthropic |
| Llama 3.2 Vision | Local-only inference | Ollama |
| UCCIX-13B | Irish-specialised fine-tune | MLX |

**Gaelic-specific metrics** (`ocr/gaelic_metrics.py`, 391 lines):
- **Character Error Rate (CER)** with NFC normalisation
- **Word Error Rate (WER)** with Irish-aware tokenisation
- **Tironian et** (⁊) accuracy
- **Punctum delens** (ḃ ċ ċ ċ ġ ṁ ṗ ṡ ṫ) precision
- **Fada** (á é í ó ú) accuracy

**Irish-language processing** (`ocr/irish_processing.py`, 646 lines):
- Irish content detection (vs English/Welsh/Scottish)
- Dialect classification (Connacht / Munster / Ulster)
- Spelling standard detection (pre-1948 vs modern)
- Quality scoring + model fallback chains

**Handwriting dataset generation** (`ocr/irish_htr_dataset.py`):
Generates training data from the Dúchas folklore manuscripts via line
segmentation + transcription alignment. Page → line → character crops
ready for CTC training.

### 4.3 Celtic Language Data (~3,000 LOC)

Six Celtic language DLT sources feeding the lakehouse:

| Source | DLT module | Records | Refresh |
|:--|:--|:--|:--|
| Dúchas (Schools' Collection) | `language.gaeilge.duchas` | ~750K | Quarterly |
| Canúint (pronunciation) | `language.gaeilge.canuint` | ~5K dialect audio | On-demand |
| Téarma (terminology) | `language.gaeilge.tearma` | ~100K terms | Weekly |
| Gaois.ie API | `language.gaeilge.gaois` | ~25K docs | Daily |
| Universal Dependencies (Irish) | `language.gaeilge.universal_dependencies` | ~5K trees | On release |
| Cross-Celtic cognates | `language/cognates.yaml` | ~2K pairs | Curated |

**Six-language support** (Goidelic + Brythonic): Irish (Gaeilge),
Scottish Gaelic (Gaidhlig), Welsh (Cymraeg), Breton (Brezhoneg),
Manx (Gaelg), Cornish (Kernowek). Sample reference texts for each
language live in `language/<lang>/<lang>_samples.yaml`.

### 4.4 ML Pipelines (~2,500 LOC)

Four end-to-end pipelines that orchestrate DLT + Dagster + Modal +
external models:

| Pipeline | What it does | LOC |
|:--|:--|:-:|
| `irish_document_scanner` | Full pipeline: DLT fetch → Dagster orchestrate → Modal compute (ColPali/Qwen-VL/FIBO) → LanceDB → mobile export | 734 |
| `dialect_classifier` | 3-class Irish dialect classification (acoustic / Wav2Vec2 / Whisper) | 787 |
| `transcript_aligner` | Audio-transcript alignment (CTC, DTW, WhisperX) for speech datasets | 350+ |
| `llm_router` | Multi-provider LLM routing with circuit breakers, cost-aware selection | 325 |

**Resource model** (in `pipelines/resources.py`):
- `LiteLLMResource` — single source of truth for LLM provider config
- `LanceDBResource` — vector store connection
- `DuckDBResource` — analytics DB connection (Dagster-managed)

### 4.5 Text Alignment (~2,000 LOC)

Bilingual alignment is the bridge from raw parallel corpora to training
data. Five tools:

- **IrishEnglishAligner** — sentence/paragraph alignment using
  sentence-transformers + dynamic programming
- **ColPaliAligner** — visual document alignment with bounding-box
  refinement (for image-rich sources)
- **DatasetGenerator** — turns aligned pairs into training-ready datasets
- **IrishG2P** — grapheme-to-phoneme for TTS and pronunciation
- **Exports** — HuggingFace, JSONL, Parquet, TMX formats

### 4.6 RAG Evaluation (RAGAS, ~1,050 LOC)

The headline number: **agentic multi-query RAG outperforms single-query
baseline by 22.7 percentage points (87.9% vs 65.2%)** on the curriculum
RAG benchmark.

- `ragas_pipeline.py` (754 lines) — full evaluation harness
- `run_evaluation.py` (304 lines) — CLI runner with Irish language support

Each evaluation run produces a MLflow-tracked run with metrics per
question, per source, and per retrieval strategy. The portal's
`/monitoring/llm` route surfaces the latest run.

### 4.7 Content Quality (~800 LOC)

Three quality scorers that gate content into the lakehouse:

- **ContentQualityAssessor** — document structure, Irish language ratio,
  fada accuracy, curriculum-specific metrics
- **CompletenessScorer** — curriculum document completeness (coverage of
  learning outcomes, assessment modes, etc.)
- **CanuintValidator** — audio alignment consistency, speaker diversity,
  dialect balance validation

### 4.8 Model & Data Catalog (`catalog/`)

Two YAML files act as the source of truth for what models and data
sources exist:

- `models.yaml` (126 lines) — 13 models across text-gen, embeddings,
  speech, vision
- `sources.yaml` (153 lines) — 16 data sources + 3 training mixes

Any new model or data source must be registered here.

---

## 5. Infrastructure

### 5.1 llama-swap (dynamic GGUF model serving)

`compose.yaml` runs `llama-swap` — a single Rust process that loads
GGUF models on demand. `llama-swap-config.yaml` declares 11 models
across 3 profiles (text / vision / image) with auto-swap on first
request. Memory budget: ~48GB RAM (3 models resident at a time).

Endpoints:
- `http://localhost:10240/v1/chat/completions` (OpenAI-compatible)
- `http://localhost:10240/v1/embeddings`
- `http://localhost:10240/v1/audio/speech` (TTS)

### 5.2 Secret injection

`secrets.env` is a Locket template (NEVER committed; resolved at runtime
from Infisical `dev-baile`). All 11 required Infisical items are
documented in the file's comment block.

### 5.3 Pangolin routing

`pangolin.yaml` exposes the inference server at
`llamaswap.cianfhoghlaim.ie` via Traefik forward-auth. No public
auth — clients must be auth'd via the upstream gateway.

---

## 6. Integration with the rest of the monorepo

| Subsystem | How it integrates |
|:--|:--|
| **oideachais/** | DLT sources write to the shared DuckLake; Dagster assets import from `language.*` and `agents.tools.*`; CocoIndex flows consume BAML extracts from here |
| **croilar/** | The croilar `portal/` reads RAGAS evaluation runs from MLflow; `notebooks/aleyum/` and `notebooks/cianfhoghlaim/` consume DLT outputs; the `motherduck_sync` Dagster asset ships tables to MotherDuck for the Dive iframe |
| **infrastructure/** | Uses the shared `lakehouse_lakehouse` Docker network; llama-swap connects to the LiteLLM gateway; all secrets flow through Infisical → Locket |
| **código infra** | DLT sources import from `sruth.oideachais.*`; evaluation references oideachais RAG setup; pipelines reference Dagster orchestration, DLT ingestion, LanceDB storage |

---

## 7. Development

### 7.1 Running tests

```bash
cd meaisínfhoghlaim
uv run pytest tests/ -v
```

### 7.2 Adding a new OCR model

1. Add an entry to `ocr/model_registry.py` with the model name, backend
   (LiteLLM/MLX/Transformers/etc.), best-for-use-case, and 1-2 example
   prompts.
2. Add the model to `catalog/models.yaml`.
3. Update `evaluation/ragas_pipeline.py` if you want the new model
   included in the next evaluation run.
4. Add a row to the OCR model comparison harness via
   `ocr/comparison_runner.py`.

### 7.3 Adding a new DLT source

1. Create `language/<domain>/<source>.py` (or `language/gaeilge/<source>.py`
   for Irish).
2. The source should respect `USE_LOCAL_SCRAPES=true` and route to
   `stedding/dev/eile/ingest_queue/<source>/` if the flag is set.
3. Export the source as a `@dlt.source` decorated function.
4. Add the source to `oideachais/data_platform/dlt_sources/` (the
   pipeline registration).
5. Add the source to `catalog/sources.yaml`.
6. Add a Dagster asset in `oideachais/data_platform/dagster_defs/assets/`
   that materialises the source.

### 7.4 Adding a new agent

1. Create `agents/<your_agent>.py` with a public class (e.g. extending
   `agents.root_agent.RootAgent`).
2. Export the class from `agents/__init__.py`.
3. Add a route in `agents/api/main.py` if the agent needs an HTTP
   surface.
4. Add a tool in `agents/tools/` if the agent needs new tool
   capabilities.
5. Update the root agent's keyword allow-list in
   `agents/root_agent.py:KEYWORD_MAP` to route queries to the new
   agent.
6. Update `catalog/sources.yaml` to reference the new agent.

---

## 8. Project structure

```
meaisínfhoghlaim/
├── compose.yaml                    # llama-swap stack
├── llama-swap-config.yaml           # 11 models, 3 profiles
├── sidecar.yaml                     # Locket secret injection
├── pangolin.yaml                    # Traefik reverse proxy
├── secrets.env                      # Locket template (Infisical)
│
├── agents/                          # ★ AI agent framework
│   ├── config.py                    # Global config: models, langs, nations
│   ├── root_agent.py                # QueryRouter + RootAgent
│   ├── enhanced_orchestrator.py     # AG-UI streaming orchestrator
│   ├── curriculum_agent.py          # Curriculum search via LanceDB + DuckDB
│   ├── translation_agent.py         # Celtic language translation (6 langs)
│   ├── corpus_agent.py              # Folklore search + dictionary
│   ├── research_agent.py            # Deep research with citation collection
│   ├── education_research_agent.py    # Cross-nation policy research (ADK)
│   ├── bunchloch_research_agent.py    # Local academic research (ADK)
│   ├── geospatial_agent.py          # LSOA/Data Zone spatial analysis
│   ├── statistics_agent.py          # Education metrics + benchmarking
│   ├── curriculum_comparison_agent.py # Cross-nation curriculum mapping
│   ├── agui_curriculum_agent.py     # AG-UI protocol curriculum agent
│   ├── mcp_curriculum_agent.py      # MCP-enabled multi-tool agent
│   ├── voice_agent.py               # Pipecat voice pipeline
│   ├── op_sync.py                   # Agent ops sync
│   ├── tools/                       # Agent tool implementations
│   ├── callbacks/                   # Citation formatting callbacks
│   └── api/                         # FastAPI service layer (port 8000)
│       ├── main.py                  # Observability-wired server
│       ├── ag_ui_protocol.py        # AG-UI streaming protocol
│       ├── routes/                  # /agent, /curriculum, /search, /geo, /tts
│       ├── services/                # chatterbox TTS
│       └── storage/                 # Persistent storage
│
├── ocr/                             # ★ OCR / HTR system
│   ├── model_registry.py            # 10 models, 6 backends (543 lines)
│   ├── comparison_runner.py         # Multi-model CER/WER comparison
│   ├── gaelic_metrics.py            # Irish-specific metrics (391 lines)
│   ├── irish_processing.py          # Dialect + spelling standard detection
│   ├── irish_htr_dataset.py         # Dúchas-based HTR dataset generator
│   ├── line_segmentation.py         # Page → line cropping
│   ├── vision_comparison.py         # Vision model comparison via LiteLLM
│   ├── vlm_finetune_comparison.py   # VLM fine-tuning comparison
│   ├── adapters.py                  # PaddleOCR, Docling, Unstract, Dots adapters
│   ├── pylaia_comparison.py         # PyLaia HTR baseline
│   ├── observability.py             # OCR-specific observability
│   └── config/                      # Caching, LightRAG, PDF extractors
│
├── language/                        # ★ Celtic language data + DLT sources
│   ├── cognates.yaml                # Cross-Celtic comparisons
│   ├── gaeilge/                     # Irish: Dúchas, Canúint, Téarma, Gaois, UD
│   ├── gaidhlig/                    # Scottish Gaelic samples
│   ├── cymraeg/                     # Welsh samples
│   ├── brezhoneg/                   # Breton samples
│   ├── gaelg/                       # Manx sample
│   └── kernowek/                    # Cornish samples
│
├── pipelines/                       # ★ End-to-end ML pipelines
│   ├── irish_document_scanner.py    # DLT + Dagster + Modal + export (734 lines)
│   ├── dialect_classifier.py        # 3-method Irish dialect classification
│   ├── transcript_aligner.py        # Audio-transcript alignment
│   ├── llm_router.py                # Multi-provider LLM router with circuit breaker
│   ├── vlm_bridge.py                # Vision-language model bridge
│   ├── canuint_audio_slicer.py      # Canúint audio segmentation
│   └── resources.py                 # Pipeline resource definitions
│
├── alignment/                       # ★ Bilingual text alignment
│   ├── aligner.py                   # Sentence-level Irish↔English alignment
│   ├── colpali_aligner.py           # Visual document alignment
│   ├── dataset_generator.py         # Training dataset generation
│   ├── irish_g2p.py                 # Grapheme-to-phoneme for Irish
│   ├── character_interpolator.py     # Character-level HTR alignment
│   ├── canuint_exporter.py          # Canúint → training exports
│   ├── export.py                    # HuggingFace, JSONL, Parquet, TMX
│   └── quality.py                   # Alignment quality validation
│
├── evaluation/                      # ★ RAG evaluation
│   ├── ragas_pipeline.py            # Baseline vs agentic comparison (754 lines)
│   └── run_evaluation.py            # CLI runner with Irish language support
│
├── quality/                         # ★ Content quality
│   ├── content_quality.py           # Document quality scoring
│   ├── completeness.py              # Curriculum document completeness
│   └── canuint_validator.py         # Audio alignment + dialect balance
│
├── catalog/                         # ★ ML model + data catalog
│   ├── models.yaml                  # 13 models (text/embeddings/speech/vision)
│   └── sources.yaml                 # 16 data sources + 3 training mixes
│
├── services/                        # ★ Microservice entry points
│   ├── agent_fastapi.py             # 12-agent FastAPI wrapper
│   ├── pipeline_fastapi.py          # Pipeline FastAPI wrapper
│   └── celery_worker.py             # Background task worker
│
└── scripts/                         # Utility scripts
    ├── download_hf_models.sh        # HuggingFace model downloader
    └── convert_hf_to_gguf.sh        # HF → GGUF conversion for llama-swap
```

---

## 9. Why this is its own quadrant

Meaisínfhoghlaim is the *only* part of the monorepo that:

- Runs **GPU workloads** (llama-swap on Mac M-series via MLX, or Modal
  cloud GPUs for fine-tuning).
- Maintains **Celtic language models and datasets** (no other
  subproject has OCR/ASR/TTS for Irish).
- Hosts the **agent runtime** (12 specialised agents, 5 frameworks —
  Custom, ADK, Agno, CopilotKit, Pipecat — plus the MCP server).
- Runs the **evaluation harness** that gates new RAG strategies from
  reaching production (22.7pp agentic improvement is the headline
  number).

Everything else either **consumes** meaisínfhoghlaim's outputs
(oideachais writes them to the lakehouse, croilar visualises them in
the portal) or **provides** the infrastructure it runs on (infrastructure
stacks, LiteLLM gateway).

It's the AI brain of the platform — and like any brain, it's the
hardest part to swap out, so it's the part we own most carefully.

---

## 10. License

MIT.
