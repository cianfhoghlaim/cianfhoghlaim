# Oideachais — Kings' College Galway

*A unified Celtic education platform, infrastructure mesh, and AI research laboratory by Cian Mac an Déisigh Uí Liatháin.*

---

## What This Is

A polyglot monorepo (`bun + uv + turbo`) that ingests the curriculums and exam
papers of the British Isles, then makes them interactive and bilingual through
self-hosted AI. Five cooperating streams:

| Stream | What it does | Stack |
|:--|:--|:--|
| `oideachais/` | Curriculum, exam, marking-scheme extraction; the VLM PDF pipeline; asset generation | Dagster + DLT + DuckLake + LanceDB + BAML + LiteLLM |
| `meaisínfhoghlaim/` | Model lifecycle — HF cache, GGUF conversion, llama-swap dynamic model swapper | llama-swap + llama.cpp + MLX + Bria FIBO |
| `infrastructure/` | Multi-cloud zero-trust mesh; the LLM gateway; ~50 stacks | Pulumi + Komodo + Pangolin + Locket + 1Password + LiteLLM + MLX-Omni + InvokeAI |
| `tuatha/` | Educational MMO front-end (BAML + Dagster + Rust + TanStack) | Babylon.js + Dagster + BAML |
| `docs/` | The reference corpus — `.agents/skills`, `data_engineering/`, `marimo/`, `meaisínfhoghlaim/`, `teanga/` | markdown + notebooks + skills |

The **3-way interaction** that makes this work:

```
┌─────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐
│  oideachais/        │    │  meaisínfhoghlaim/    │    │  infrastructure/     │
│  ─────────────      │    │  ──────────────────   │    │  ──────────────────  │
│  Dagster assets     │───▶│  llama-swap :8080     │◀───│  LiteLLM gateway     │
│  BAML extraction    │    │  mlx-omni :10240      │    │   :4000              │
│  Dagster assets     │    │  invokeai :9090       │    │                      │
│  (asset gen)        │    │  HF cache (124 GB)    │    │  Locket sidecar      │
│                     │    │  GGUF dir (built)     │    │  Infisical vault     │
│                     │◀───│  stedding/huggingface │───▶│  Pangolin + PocketID │
│                     │    │  hub/  gguf/  mlx/    │    │  Prometheus          │
└─────────────────────┘    └──────────────────────┘    └──────────────────────┘
```

- `oideachais/` **calls** the LiteLLM gateway at `http://litellm:4000/v1`
  through `LiteLLMResource` (Dagster) and `client LiteLLM` (BAML).
- The gateway **routes** to `llama-swap` (GGUF), `mlx-omni` (MLX), `invokeai`
  (image gen), or cloud providers (Gemini, GLM, OpenAI, OpenCode Go).
- `meaisínfhoghlaim/` **feeds** the backends with converted GGUF models
  (built from `stedding/huggingface/hub/` via the
  `meaisínfhoghlaim/scripts/convert_hf_to_gguf.sh` script) and runs
  `llama-swap` on a MacBook M4 Max 48 GB using dynamic model profiles
  (text / vision / image — only one model resident at a time).
- `infrastructure/` **secures** every connection with PocketID SSO + Pangolin
  zero-trust tunnels; **observes** every call with Langfuse + MLflow + Prometheus;
  **injects** every secret via Locket sidecars pulling from Infisical.

---

## Quickstart

```bash
# 1. Install toolchain + hydrate secrets
bun run setup         # mise + bun + uv + infisical bootstrap

# 2. Bring up the lakehouse + LLM gateway + backends
cd infrastructure/stacks/storage/lakehouse && docker compose up -d
cd ../engineering/litellm    && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../meaisínfhoghlaim     && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/mlx-omni && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/invokeai && docker compose -f compose.yaml -f sidecar.yaml up -d

# 3. Materialise the model conversion (HF → GGUF) once
cd /Users/cianmacandeisigh/dev/kings_college_galway/oideachais
uv run dagster dev -m data_platform.dagster_defs.definitions
# → http://localhost:3000 → Jobs → model_conversion → Materialize

# 4. Run the VLM PDF pipeline
USE_LOCAL_SCRAPES=true uv run python -c "
from oideachais.data_platform.agents.baml_integration import EnhancedBAMLExtractionPipeline
p = EnhancedBAMLExtractionPipeline(subject='mathematics', cycle='senior_cycle')
spec = p.extract_curriculum_specification(document_text=open('sample.txt').read())
print(spec.model_dump_json(indent=2))
"

# 5. Open the marimo ops dashboard
uv run marimo edit notebooks/mission_control.py
```

The first model conversion run takes hours (124 GB of HuggingFace safetensors
to resume + ~30 GB of GGUF output). Subsequent runs are incremental.

---

## LLM Gateway (the heart of the system)

Every LLM call in this monorepo — BAML extraction, Dagster assets, FastAPI
endpoints, marimo notebooks, TanStack web app — flows through one URL:
`http://litellm:4000/v1`. The gateway (`infrastructure/stacks/engineering/litellm`)
exposes 16 alias routes that abstract model choice, fallback, and tracing.

### Alias routes

| Alias | Primary → Fallback chain | Used by |
|:--|:--|:--|
| `extract` | `gemini-2.5-pro` → `glm-4.6` → `gemini-2.5-flash` | BAML extraction (10 functions) |
| `vision` | `local/vision/qwen25-vl` (Qwen2.5-VL GGUF) → `local/vision/gemma3-vision` → `gemini-2.5-flash` | VLM PDF processing |
| `document` | `local/document/granite-docling` (MLX) → `local/vision/qwen25-vl` | PDF → DocTags XML |
| `ocr` | `local/ocr/olmocr-mlx` (MLX) → `local/ocr/deepseek-ocr` (GGUF) → `gemini-2.5-flash` | SEC exam paper OCR |
| `math` | `local/math/qwen25-math` (GGUF) → `glm-4.6` | Math reasoning |
| `irish` | `local/irish/uccix` (UCCIX Llama2 13B) → `local/math/qwen25-math` → `gemini-2.5-flash` | Irish text generation |
| `image` | `local/image/z-image-turbo` (GGUF) → `local/image/qwen-image` → `local/image/flux2` → `local/image/sdxl` | Study asset image gen |
| `image-fibo` | `local/image/fibo` (Bria FIBO MLX) → `local/image/z-image-turbo` | Deterministic JSON-config image gen |
| `embedding-curriculum` | `celtic/embedding/bge-m3` (HF passthrough) | Curriculum vector search |
| `general` | `opencode-go/deepseek-v4-flash` → `glm-4.6` → `gpt-4o-mini` | Cheap generic tasks |
| `whisper-irish` | `celtic/asr/whisper-large` (HF passthrough) | ASR (faster-whisper in production) |
| `translation` | `celtic/translation/nllb` (HF passthrough) | 200-language translation |

Full registry in `infrastructure/stacks/engineering/litellm/config/config.yaml`.

### Why a gateway

- **One OpenAI-compatible URL** — every consumer (BAML, Dagster, FastAPI, web)
  writes the same code.
- **No direct provider SDKs** — all 10 `client Claude` references in BAML
  have been swapped for `client LiteLLM`; no Anthropic SDK in the codebase.
- **Fallback chains** — Irish-trained UCCIX 13B steps in before Gemini Flash
  for the `irish` alias, so we never return English when prompted in Irish.
- **Local-first by default** — the `ocr` and `vision` aliases start on local
  MLX/GGUF, so an offline oideachais session still works; cloud routes are
  the last fallback, not the first call.
- **Langfuse + MLflow** — every call traces lineage (which alias → which
  model → which asset) without per-callsite instrumentation.
- **PocketID SSO + Pangolin private resources** — the gateway is exposed at
  `litellm.cianfhoghlaim.ie` only to authenticated `Member` roles.

---

## Local Model Lifecycle (meaisínfhoghlaim)

The `meaisínfhoghlaim/` stream owns the **model layer** that the gateway
routes to. It's the bridge between the 124 GB of HuggingFace safetensors
in `stedding/huggingface/hub/` and the GGUFs that llama-swap can actually
serve.

### HF cache layout

```
stedding/huggingface/
├── hub/          # HuggingFace hub format (safetensors), 28 models ~124 GB
├── gguf/         # Converted GGUFs (Q4_K_M, mmproj f16) ~30 GB
└── mlx/          # Converted MLX (for mlx-omni), ~15 GB
```

### Three swap profiles (only one model resident at a time on M4 Max 48GB)

| Profile | Models |
|:--|:--|
| `text` | Qwen2.5-Math-7B, UCCIX Llama2-13B, Gemma-2-9B |
| `vision` | Qwen2.5-VL-7B (+ mmproj f16), Gemma-3-Vision, DeepSeek-OCR |
| `image` | Z-Image-Turbo, Qwen-Image, Qwen-Image-Edit-2511, FLUX.2-dev |

Per the `llamacpp.md` skill: **LLM weights are Q4_K_M, vision encoders are F16**
(quantising mmproj breaks OCR). All GGUFs are produced by
`scripts/convert_hf_to_gguf.sh` (F16 → Q4_K_M, two-stage) and re-built by the
Dagster `model_conversion` job on schedule or after HF upgrades.

### Why both MLX and GGUF

- **MLX** is Apple-Silicon-only (M-series unified memory) and is faster for
  vision/OCR (`mlx-omni` stack serves Granite-Docling-MLX, olmOCR-MLX,
  Bria FIBO-MLX).
- **GGUF** is universal (CPU/Metal/CUDA/Vulkan) and is the only path for
  NVIDIA or non-M-series hosts.
- The gateway exposes both backends; the LiteLLM aliases pick the right one
  per request.

### Image gen models (BAML-driven)

`baml_src/image_generation.baml` defines `ImagePromptSpec` + `FIBOConfig` so
the asset generation pipeline can:

1. Read a learning outcome from the syllabus
2. BAML `ExtractImagePrompt` → camera / lighting / mood / style spec
3. BAML `BuildFIBOConfig` → deterministic JSON for Bria FIBO
4. Render through the gateway's `image-fibo` alias
5. Upload the PNG to `s3://ducklake-assets/study/{subject}/{cycle}/{outcome_id}.png`
6. RAGAS evaluates faithfulness; only ≥0.8 surfaces in the web app

Supported image backends: Bria FIBO (MLX, deterministic JSON), Z-Image-Turbo
(GGUF, fast), Qwen-Image (GGUF, accurate), Qwen-Image-Edit-2511 (GGUF,
instruction-driven editing), FLUX.2-dev (GGUF, highest quality, 12-17 GB
resident), SDXL (InvokeAI).

---

## Infrastructure Mesh (Bonneagar)

### Server fleet

| Server | Hardware | Role |
|:--|:--|:--|
| `arm1-oci` | Oracle Cloud Ampere A1, 4 OCPU, 24 GB | Control plane — Pangolin, Komodo, 1Password Connect, Garage S3, Forgejo |
| `cax41-hetzner` | Hetzner CAX41 ARM, 16 vCPU, 32 GB | Workloads — Memgraph, FalkorDB, MLflow, Langfuse, LanceDB, Cognee, Graphiti, Dagster, Browser grid |
| `bunchloch` | MacBook M4 Max, 14 cores, 48 GB unified memory | Dev + analytics — LakeFS, Convex, llama-swap, mlx-omni, Bria FIBO, Aleyum portal |

### Gold-Standard stack pattern

Every stack under `infrastructure/stacks/<category>/<name>/` ships exactly 5
files (per `infrastructure/stacks/GOLD_STANDARD.md`):

```
compose.yaml       # Application services (no Locket refs)
sidecar.yaml       # Locket sidecar + service overrides
secrets.env        # {{ infisical://dev-baile/<item>/<key> }} templates
pangolin.yaml      # Traefik labels (private + Member role, PocketID)
blueprint.yaml     # Pangolin resource definition
```

### LLM-relevant stacks (Phase 2-4)

| Stack | Path | Port | Purpose |
|:--|:--|:-:|:--|
| `litellm` | `infrastructure/stacks/engineering/litellm` | 4000 | The canonical LLM gateway |
| `llama-swap` | `meaisínfhoghlaim` (top-level) | 8080 | GGUF model swapper (MacBook M4) |
| `mlx-omni` | `infrastructure/stacks/engineering/mlx-omni` | 10240 | MLX-format OpenAI server (MacBook M4) |
| `invokeai` | `infrastructure/stacks/engineering/invokeai` | 9090 | SDXL image gen |
| `langfuse` | `infrastructure/stacks/machine_learning/langfuse` | 3000 | LLM tracing |
| `mlflow` | `infrastructure/stacks/storage/mlflow` | 5000 | ML experiment tracking |
| `lakehouse` | `infrastructure/stacks/storage/lakehouse` | 3900-3904, 8181-8182, 5433 | Garage S3 + Lakekeeper + Lance Namespace |
| `cognee` | `infrastructure/stacks/machine_learning/cognee` | 8000 | AI memory (Neo4j, Memgraph, FalkorDB) |
| `graphiti` | `infrastructure/stacks/machine_learning/graphiti` | 8080 | Temporal knowledge graph |
| `dagster` | `infrastructure/stacks/storage/dagster` | 3335 | Pipeline orchestration |

### Secret flow (no `.env` ever hand-edited)

```
Infisical vault "dev-baile"   ←  source of truth
       │
       │ mise directory hook (per `mise.toml`)
       ▼
Root .env (gitignored)        ←  hydrated at runtime
       │
       │ bun run scripts/init-vault.ts  (one-time vault seed)
       ▼
.infisical.env (committed)    ←  infisical://dev-baile/<item>/<key> URIs
       │
       │ Locket sidecar (per stack's sidecar.yaml)
       ▼
/run/secrets/locket/secrets.env (tmpfs, non-root)
       │
       ▼
Container env (read-only mount)
```

The `litellm` vault item needs to be created with `master_key`, `salt_key`,
`database_url`, `postgres_user`, `postgres_password`, `postgres_db` — all
referenced in `infrastructure/stacks/engineering/litellm/secrets.env`.

---

## Oideachais Data Platform (the engine)

The Dagster asset graph has 4 layer groups:

| Group | Assets | Example |
|:--|:--|:--|
| **Ingestion** | `ireland/curriculum/{cycle}`, `uk_education_assets`, `multi_nation_curriculum_assets` | DLT sources → DuckDB / DuckLake |
| **Materials** | `ireland/exam_materials/{cycle}`, `pdf_assets` | SEC scraper → Garage S3 → ColPali OCR |
| **Model lifecycle** | `hf_models_downloaded`, `gguf_*` (10) | HF → GGUF for llama-swap |
| **Asset generation** | `image_prompts_designed` → `fibo_configs_built` → `study_assets_rendered` → `study_assets_published` | BAML → gateway → Garage S3 |

The VLM PDF processing flow (the end-to-end vision):

```
SEC PDF URL
  → DLT exam_source (Stagehand browser)
  → pdf2image @ 200 DPI (page-level batching)
  → LiteLLM gateway POST /v1/chat/completions
      with model "vision" or "ocr" alias
  → Llama-swap → Qwen2.5-VL-7B GGUF (or MLX-Omni → Granite-Docling)
  → Markdown / JSON
  → BAML ExtractExamPaperStructure / ExtractMarkingScheme
  → Embed (BGE-M3) → LanceDB
  → Graphiti / Cognee → Memgraph (prerequisite chains)
  → Langfuse trace (full lineage)
  → RAGAS eval (faithfulness, relevance) → MLflow
```

See `oideachais/README.md` §8.5 for the deep dive on why the gateway matters.

---

## End-to-End Asset Generation Example

```bash
# 1. After Dagster has loaded the senior_cycle Mathematics curriculum,
#    run the asset generation job from the UI or CLI:
cd oideachais
uv run dagster job execute -m data_platform.dagster_defs.definitions -j asset_generation

# This runs:
#   1. image_prompts_designed — BAML ExtractImagePrompt for each high-priority outcome
#   2. fibo_configs_built     — BAML BuildFIBOConfig (deterministic seed)
#   3. study_assets_rendered  — POSTs to gateway image-fibo alias
#   4. study_assets_published — uploads PNGs to Garage S3, RAGAS eval
```

Sample outcome: `LO-MATH-SC-1.1` (Differentiate polynomial functions using
the product rule) →
- ImagePromptSpec: camera=OVERHEAD, lighting=STUDIO, mood=ENCOURAGING,
  style=EDUCATIONAL_DIAGRAM
- FIBOConfig: seed=0x4d415448, width=1024, height=1024
- Renders via mlx-omni's Bria FIBO on the MacBook M4 (deterministic given
  the seed)
- PNG uploads to `s3://ducklake-assets/study/mathematics/senior_cycle/LO-MATH-SC-1.1.png`
- RAGAS scores faithfulness against the outcome text; ≥0.8 surfaces
  in the web app's study flashcard view

---

## Technology Stack Summary

| Layer | Technology |
|:--|:--|
| **Infrastructure** | Pulumi (multi-cloud: Hetzner, OCI, Cloudflare) + Komodo GitOps + Pangolin WireGuard + PocketID SSO + Locket sidecars + Infisical vault + Garage S3 + Lakekeeper Iceberg REST + Lance Namespace |
| **Storage** | DuckDB + DuckLake (PostgreSQL catalog) + LanceDB (HNSW, MVCC) + Memgraph + FalkorDB + Neo4j + MotherDuck + Cloudflare R2 |
| **Orchestration** | Dagster v1.13+ + DLT v1.4+ + SQLMesh (DuckDB virtual warehouse) + CocoIndex |
| **LLM Gateway** | LiteLLM + llama-swap (GGUF) + mlx-omni (MLX) + InvokeAI + docling-serve |
| **AI Frameworks** | BAML (type-safe extraction) + Google ADK + Agno + Pydantic AI + Langfuse + MLflow + Ragas |
| **Memory / KG** | Graphiti (bi-temporal) + Cognee (GraphRAG) + temporal knowledge graphs |
| **Fine-tuning** | Unsloth (70% VRAM reduction, 2× speed) + TRL + LoRA/QLoRA + Modal.com |
| **Embedding** | BGE-M3 (1024d, multilingual) + GaBERT (Irish 768d) + ColPali (visual, late-interaction) |
| **Translation** | NLLB-200 (200 langs, all 6 Celtic) + Helsinki OPUS-MT (Celtic pairs) + M2M-100 |
| **Speech** | Whisper-large-v3 (faster-whisper) + wav2vec2-XLSR-Irish + Chatterbox (TTS) |
| **Frontend** | TanStack Start + CopilotKit + Convex (realtime) + Hono (API) + Marimo (notebooks) + AG-UI (SSE) |
| **Browser** | Stagehand (Operator) + Crawl4AI (Gatherer) + Skyvern (Hunter) + Patchright (stealth) + Browserbase + Firecrawl |
| **Observability** | Langfuse v3 (LLM tracing) + MLflow (ML experiments) + Logfire (Python tracing) + Prometheus (infra) + Langfuse prompt mgmt + Ragas (RAG eval) |
| **Languages** | Python 3.12, TypeScript (Bun), Rust (Locket), TOML (Komodo), BAML (extraction DSL) |

---

## Personal Foundation

Built by Cian Mac an Déisigh Uí Liatháin — a qualified Mathematics & Applied
Mathematics teacher (Teaching Council of Ireland), NUI Galway HDip graduate in
Applied Statistics, Software Development, and Irish Language Studies. This
project directly maps academic modules to the architecture:

- **MA311 Applied Statistics I** → RAGAS eval, grade distributions, DLT statistical validation
- **MA378 Numerical Analysis II** → numerical ops in DuckDB, geospatial interpolation
- **MP307 Modelling II** → BAML `IdentifyPrerequisiteChain` encodes population-model dependency graphs
- **CS4423 Networks** → graph topology for Neo4j / Memgraph / FalkorDB + Graphiti temporal graphs
- **CS402 Cryptography** → zero-trust Pangolin / WireGuard design
- **CT511 Databases** → DuckDB / DuckLake schema design, vector + relational separation
- **CT545 Enterprise Java** → FastAPI service-layer pattern, gateway/repository separation
- **CT853 Algorithmics** → content-deduplication hashing, HNSW indexing strategy
- **CT870 Internet Programming** → TanStack Start frontend, multi-protocol server (MCP/AG-UI/SSE)
- **ED116 / ED305 / ED411** → pedagogical strategy for `curriculum_agent.py` and BAML extraction
- **GA101 / GF101 / GA81010** → bilingual curriculum handling, Irish G2P, canuint TTS

The Teaching Council register (ID 6c60e730-...) confirms the academic
credentials; the cian_mac_an_déisigh_uí_liatháin/ directory holds the
transcripts and reference letters.

---

## Multi-Agent Configuration

`opencode.json` defines 5 specialist sub-agents, each tied to a specific
domain and OpenCode Go model:

| Agent | Model | Focus |
|:--|:--|:--|
| `explorer` | DeepSeek V4 Flash | Codebase search, context mapping |
| `data-engineer` | Qwen 3.7 Max | Dagster, DLT, DuckDB, MotherDuck, LanceDB |
| `ai-engineer` | DeepSeek V4 Pro | BAML, LiteLLM, OCR, Graphiti, Celtic language AI |
| `frontend-dev` | Kimi K2.6 | TanStack Start, Convex, Marimo, canvas design |
| `devops-architect` | GLM 5.1 | Docker Compose, Komodo, Pangolin, Pulumi |

The `.agents/skills/` library holds 70+ skill definitions (litellm, dagster,
dlt, lancedb, motherduck, cognee, graphiti, unsloth, baml, marimo, etc.) that
the agents consult via the `skill` tool.

---

## HuggingFace Model Registry (Local Cache)

Cache location: `stedding/huggingface/hub/` (NOT `~/.cache/huggingface/`).
Env wiring in `.env`:
```
HF_HOME=/Users/cianmacandeisigh/dev/kings_college_galway/stedding/huggingface
HF_HUB_CACHE=/Users/cianmacandeisigh/dev/kings_college_galway/stedding/huggingface/hub
HF_HUB_DOWNLOAD_TIMEOUT=600
HF_TOKEN=...
HUGGINGFACE_HUB_TOKEN=...
HUGGINGFACE_TOKEN=...
```

| Model | Size | Use |
|:--|:-:|:--|
| `Qwen/Qwen2.5-VL-7B-Instruct` | 15 GB | VLM PDF processing → Q4_K_M GGUF |
| `Qwen/Qwen2.5-Math-7B-Instruct` | 14 GB | Math reasoning → Q4_K_M GGUF |
| `Qwen/Qwen2-VL-7B-Instruct` | 6.4 GB | VLM fallback → Q4_K_M GGUF |
| `deepseek-ai/deepseek-ocr` | 6.2 GB | OCR specialist → Q4_K_M + mmproj GGUF |
| `THUDM/glm-4v-9b` | 26 GB | VLM (alt) → Q4_K_M GGUF |
| `ReliableAI/UCCIX-Llama2-13B-Instruct` | stub | Irish generation — re-download |
| `google/gemma-2-9b` | stub | English fallback — re-download |
| `ResembleAI/chatterbox` | 9.7 GB | TTS (HF passthrough) |
| `BAAI/bge-m3` | 4.3 GB | Curriculum embeddings (HF passthrough) |
| `BAAI/bge-large-en-v1.5` | 3.7 GB | English embeddings |
| `vidore/colpali-v1.3` | 108 MB | Visual document retrieval |
| `cpierse/wav2vec2-large-xlsr-53-irish` | 2.4 GB | Irish ASR |
| `facebook/nllb-200-distilled-600M` | 2.3 GB | 200-lang translation |
| `facebook/m2m100_418M` | 237 MB | Translation fallback |
| `DCU-NLP/bert-base-irish-cased-v1` | 483 MB | Irish NER/POS |
| `Helsinki-NLP/opus-mt-{en-ga,ga-en,en-cy,cy-en}` | ~566 MB each | Celtic pair translation |
| `openai/whisper-large-v3` | 23 GB | ASR (faster-whisper) |
| `sentence-transformers/{all-MiniLM-L6-v2,paraphrase-multilingual-MiniLM-L12-v2}` | 888 MB, 3.9 GB | Lightweight embeddings |
| `facebook/wav2vec2-base`, `wav2vec2-large-xlsr-53` | 363 MB, 1.3 GB | ASR base models |
| `BAAI/bge-small-en-v1.5` | 383 MB | English embedding (small) |
| `Snowflake/snowflake-arctic-embed-xs` | 87 MB | Embedding (tiny) |
| `vidore/colpali-v1.2` | 318 MB | Visual retrieval (older) |

**Pending downloads** (12): briaai/FIBO + VAE + Adapters, google/siglip*, unsloth
GGUF pre-quantized variants (Z-Image-Turbo, Qwen-Image, Qwen-Image-Edit-2511,
FLUX.2-dev, DeepSeek-OCR, gemma-3-9b-it). Resume with:
`bash meaisínfhoghlaim/scripts/download_hf_models.sh`

**Disk footprint audit:** 124 GB currently in `hub/`. After conversion,
~30 GB of Q4_K_M GGUFs in `gguf/`. The `model_conversion` Dagster job
produces these on demand.

---

## Deployment Bring-up Sequence

```bash
# 1. Foundation secrets + toolchain
bun run setup                  # mise + bun + uv + infisical bootstrap

# 2. Lakehouse (Garage + PostgreSQL + Lakekeeper + Lance Namespace)
cd infrastructure/stacks/storage/lakehouse
docker compose up -d

# 3. Observability (Langfuse + MLflow + Prometheus)
cd ../machine_learning/langfuse && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../storage/mlflow         && docker compose up -d

# 4. Memory / Knowledge graph (Cognee + Graphiti)
cd ../machine_learning/cognee    && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../graphiti                  && docker compose -f compose.yaml -f sidecar.yaml up -d

# 5. LLM Gateway + backends
cd ../../engineering/litellm    && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../meaisínfhoghlaim       && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/mlx-omni   && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../../engineering/invokeai   && docker compose -f compose.yaml -f sidecar.yaml up -d

# 6. Dagster + model conversion (first time only — takes hours)
cd /Users/cianmacandeisigh/dev/kings_college_galway/oideachais
uv run dagster dev -m data_platform.dagster_defs.definitions
# → http://localhost:3000 → Jobs → model_conversion → Materialize

# 7. Pipeline run
USE_LOCAL_SCRAPES=true uv run python -c "..."

# 8. Web + notebooks
cd web && pnpm dev
cd .. && uv run marimo edit notebooks/mission_control.py
```

After this, `litellm.cianfhoghlaim.ie` is the gateway, `*.cianfhoghlaim.ie`
routes via Pangolin, and every consumer (BAML, Dagster, FastAPI, web)
calls through it.

---

## Licensing

Business Source License 1.1 — non-commercial, cultural preservation, and
academic research use permitted within Ireland, UK, EU, Commonwealth, and
aligned jurisdictions. Transitions to AGPL v3.0 after 4 years.
See [`LICENSE.md`](LICENSE.md).

---

*Built by Cian Mac an Déisigh Uí Liatháin — qualified Mathematics &
Applied Mathematics teacher (Teaching Council of Ireland), NUI Galway
graduate (Applied Statistics, Software Development, Irish Language Studies),
dual Irish-British citizen.*
