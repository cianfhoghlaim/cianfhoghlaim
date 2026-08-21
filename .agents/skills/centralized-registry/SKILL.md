---
name: centralized-registry
description: The single source of truth for models, schemas, pipelines, and stacks. Load when adding/changing/toggling any model, schema, pipeline, or stack. Covers MODEL_REGISTRY (52 entries / 7 families including the 22-entry ocr_vision subset + 6 CLASSICAL_OCR backends + BIEP v2 4-path ensemble), notebooks/_shared/schema.py (5 introspection helpers), deployment-choice.yaml (the enablement file), notebooks/00_control_panel.py (the 5-tab marimo control panel), and the central registry audit via mise run lint:registry. Per the centralized-model-registry + centralized-schema-registry + deployment-control-panel openspec capabilities (post-2026-08-15; §11 OCR/VLM Pipeline added 2026-08-13).
---

# Centralized Registries — Models, Schemas, Pipelines, Stacks

**Version**: 2026-08-13 | **Last Updated**: 2026-08-13 (added §11 OCR/VLM Pipeline)

The Cianfhoghlaim platform now has **one canonical source of truth** for
every model, schema, pipeline, and stack. This replaces the ~70
hardcoded model strings + 96 hand-written Pydantic duplicates + 54
nearly-identical CocoIndex Apps + 619 empty placeholder YAMLs that
the 2026-08-15 audit found.

## 1. The 4 canonical artifacts

| Artifact | Path | Purpose |
|:--|:--|:--|
| **`MODEL_REGISTRY`** | `meaisinfhoghlaim/models/model_registry.py` | 52 entries across 7 families (ocr_vision / text_llm / embedder / rerank / image_gen / voice / translation). |
| **`schema` introspection** | `notebooks/_shared/schema.py` | 5 helpers: `schema_introspect`, `schema_introspect_table`, `schema_introspect_full`, `list_dlt_sources`, `list_cocoindex_apps`, `list_baml_classes`. |
| **`deployment-choice.yaml`** | repo root | The canonical enablement file. Read/written by the marimo notebook + web UI + CLI. |
| **00_control_panel notebook** | `notebooks/00_control_panel.py` | The 5-tab marimo control panel (Models / Pipelines / Datasets / Stacks / Registry). |

## 2. MODEL_REGISTRY — the single source for models

### The 7 families

| Family | Count | Examples |
|:--|--:|:--|
| `ocr_vision` | 20 | `qwen3-vl-8b`, `molmo2-8b`, `gemma-4-26B-A4B`, `dots-ocr`, `unstract-api` |
| `text_llm` | 13 | `minimax-m3`, `qwen3.6-27b-mtp`, `uccix-mistral-24b`, `claude-sonnet-4-20250514` |
| `embedder` | 3 | `BAAI/bge-m3`, `BAAI/bge-large-en-v1.5`, `all-MiniLM-L6-v2` |
| `rerank` | 3 | `jina-reranker-v2-base-multilingual`, `rerank-v3.5`, `gte-rerank-v2` |
| `image_gen` | 5 | `local/image/flux2-dev`, `local/image/z-image-turbo`, `local/image/qwen-image`, `local/image/sdxl`, `local/image/fibo` |
| `voice` | 5 | `whisper-large`, `wav2vec2-irish`, `chatterbox`, `aba-tts`, `ResembleAI/chatterbox` |
| `translation` | 3 | `opus-mt`, `m2m100`, `nllb` |

### The 2-axis key API

```python
from meaisinfhoghlaim.models import (
    MODEL_REGISTRY,            # the registry object
    model_for,                 # resolve a single model key
    filter_models,             # filter by family (returns list[ModelRegistryEntry])
)

# Resolve a single model
default = model_for("text_llm", "default")              # → "minimax-m3"
irish  = model_for("text_llm", "irish", language="ga")  # → "uccix-mistral-24b"
embed  = model_for("embedder", "default")               # → "BAAI/bge-m3"
voice  = model_for("voice", "tts")                      # → "chatterbox"

# Filter by family
embedders = filter_models("embedder")  # → [3 ModelRegistryEntry entries]
for e in embedders:
    print(f"{e.key} ({e.upstream_id}) — {e.role}")

# Direct registry access
entry = MODEL_REGISTRY["minimax-m3"]
print(f"family={entry.family}, role={entry.role}, upstream={entry.upstream_id}")
```

### Adding a new model

To add a new model to the registry, append a `ModelRegistryEntry`
to the relevant family section in
`meaisinfhoghlaim/models/model_registry.py` (one of the 7
`_xxx_entries()` functions):

```python
def _text_llm_entries() -> dict[str, ModelRegistryEntry]:
    entries = {
        # ... existing entries ...
        "my-new-model-v1": ModelRegistryEntry(
            key="my-new-model-v1",
            family="text_llm",
            role="default",  # or any free-form role string
            display_name="My New Model v1",
            unsloth_id=None,  # or "unsloth/my-new-model-GGUF" if local
            mlx_id=None,
            upstream_id="myorg/my-new-model",  # canonical HF ID
            backend="hf",  # or "openai", "google", "anthropic", etc.
            available=True,
            litellm_alias="my-new-model-alias",  # None if not via LiteLLM
            env_var="MY_NEW_MODEL_API_KEY",
            notes="Used by the X agent (per the audit 2026-08-15).",
        ),
    }
    return entries
```

Then run `mise run lint:registry` to verify no drift was introduced.

### Audit drift

```bash
mise run lint:registry            # reports 0 hardcoded model strings
mise run lint:registry --strict   # exits non-zero if drift detected
```

The lint walks `agents/`, `baml_src/`, `notebooks/`, `web/`,
`orchestration/`, `spaces/` and uses AST-aware regex against a tight
family-prefix whitelist. New strings (not in the canonical
`MODEL_REGISTRY` key set) trip the linter.

### List all models

```bash
mise run models:list            # 52 entries grouped by family
mise run models:count           # just the counts (informational)
```

## 3. Schema introspection — discover the lakehouse

5 helpers in `notebooks/_shared/schema.py`:

```python
from notebooks._shared.schema import (
    schema_introspect,               # every BIEP DuckDB table + column metadata
    schema_introspect_table,         # the canonical column metadata for any table
    schema_introspect_full,          # DuckDB + LanceDB + BAML union (control panel Tab 3)
    list_dlt_sources,                # all 920 @dlt.source + 4900 @dlt.resource functions
    list_cocoindex_apps,             # all CocoIndex Apps + their LanceDB mount targets
    list_baml_classes,               # all 838 BAML classes + their parent files
    read_deployment_choice,          # read deployment-choice.yaml (atomic + fcntl.flock)
    write_deployment_choice,         # write deployment-choice.yaml (atomic + fcntl.flock)
    deployment_choice_path,          # canonical path to deployment-choice.yaml
)
```

### Usage

```python
from notebooks._shared.db import connect_md
conn = connect_md()

# 1. Discover the lakehouse schema
rows = schema_introspect_full(conn)  # DuckDB + Lance + BAML
print(f"Found {len(rows)} columns across all tables")

# 2. Check what DLT sources are wired
sources = list_dlt_sources()
print(f"Found {len(sources)} DLT sources/resources")

# 3. Check what CocoIndex Apps are loaded
apps = list_cocoindex_apps()
print(f"Found {len(apps)} CocoIndex Apps")

# 4. Check what BAML classes are extracted
classes = list_baml_classes()
print(f"Found {len(classes)} BAML classes")

# 5. Read/write deployment-choice.yaml
state = read_deployment_choice()
state["enabled_models"]["my-new-model-v1"] = True
write_deployment_choice(state)
```

## 4. Deployment control panel

### Open the 5-tab marimo notebook

```bash
mise run notebook:control-panel
# or: marimo edit notebooks/00_control_panel.py
```

The 5 tabs:
1. **Models** — every MODEL_REGISTRY entry grouped by family. Toggle on/off.
2. **Pipelines** — every DLT source + every CocoIndex App. Toggle on/off.
3. **Datasets** — read-only view of every BIEP DuckDB table + LanceDB mount + BAML class (via `schema_introspect_full`).
4. **Stacks** — every Docker Compose stack. Toggle on/off.
5. **Registry** — full MODEL_REGISTRY view + drift count.

### The deployment-choice.yaml file

The notebook reads/writes `deployment-choice.yaml` at the repo root:

```yaml
version: 1

enabled_models:
  minimax-m3: true
  uccix-mistral-24b: true
  qwen3-vl-8b: true
  # ... 50+ entries ...

enabled_pipelines:
  ireland_jurisdiction_pipeline: true
  european_nations_embedding_factory: true
  # ... 28 entries ...

enabled_stacks:
  litellm: true
  langfuse: true
  # ... 8 high-priority stacks ...

monitoring:
  registry_audit: true
  baml_ts_codegen: true
```

The same file is read/written by the web UI control panel (deferred to
issue #143) and the CLI (deferred to issue #146).

## 5. ADK agent construction (LiteLlm migration)

After the 2026-08-15 drift fix, every ADK agent routes through the
LiteLLM gateway via the canonical `litellm_model("minimax")` helper:

```python
from agents.adk.litellm_agent import make_litellm_agent, litellm_model

# Option A: Use the make_litellm_agent helper
agent = make_litellm_agent(
    name="my_agent",
    description="Routes through the KCG minimax LiteLLM gateway.",
    model_alias="minimax",
    tools=[my_tool],
    instruction="...",
)

# Option B: Use litellm_model with LlmAgent directly
from google.adk.agents import LlmAgent
agent = LlmAgent(
    name="my_agent",
    model=litellm_model("minimax"),
    description="...",
)
```

The 32 hardcoded `LlmAgent(model=config.model_name)` sites that were
bypassing the registry are now all routed through `MODEL_REGISTRY`.

## 6. Dagster JurisdictionAssetsBase

The base class for the 10 per-jurisdiction Dagster asset wrappers.
Lives at `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`:

```python
from orchestration.defs.2_materials._base.jurisdiction_assets_base import (
    JurisdictionAssetsBase,
    IrelandAssets,                # the reference implementation
    make_jurisdiction_assets,     # dynamic factory for one-line rollouts
    all_jurisdiction_assets,      # list of all 10 AssetsDefinition
)
```

Each per-jurisdiction file becomes a ~30-LOC subclass instead of the
current ~378-LOC. Full rollout saves ~3,300 LOC across 10 files
(issue #146).

## 7. CocoIndex factory pattern

The canonical example: `cocoindex_flows/european_nations/_factory.py`
collapses 40 nation CocoIndex Apps into one factory. See
`cocoindex/AGENTS.md` "The factory pattern" section.

## 7. CocoIndex factory pattern

The canonical example: `cocoindex_flows/european_nations/_factory.py`
collapses 40 nation CocoIndex Apps into one factory. See
`cocoindex/AGENTS.md` "The factory pattern" section.

## Marimo v14 Helper Modules

The canonical shared notebook helpers are:

- `notebooks/_shared/marimo_patterns.py` — reusable v14 dashboard patterns
  and CLI/interactive execution helpers.
- `notebooks/_shared/area_shims/biiep_v3_dashboard.py` — BIEP v3 dashboard
  surface and area-specific shims.
- `notebooks/_shared/ragas_gauge.py` — RAGAS evaluation gauge rendering.

Use `LITELLM_BASE_URL` for LLM routing in notebooks and helper modules; do not
introduce hardcoded gateway URLs. The helpers support the 17 BIEP v3 dashboards,
the 7 grouped dashboards, and the consolidated `notebooks/sync_health.py`
sync-health dashboard.

## 8. The 3 openspec capabilities

| Spec | One-liner |
|:--|:--|
| [`centralized-model-registry`](../../openspec/specs/centralized-model-registry/spec.md) | The 4 canonical artifacts + the 4 Requirements (registry family coverage, no-hardcode-consumption, model_for() API, lint:registry audit). |
| [`centralized-schema-registry`](../../openspec/specs/centralized-schema-registry/spec.md) | BAML is the source of truth + Pydantic + Zod are codegen + 96 Pydantic dupes removed + `schema_introspect_full()`. |
| [`deployment-control-panel`](../../openspec/specs/deployment-control-panel/spec.md) | The marimo notebook + web UI + CLI for picking models/pipelines/datasets/stacks. |

## 9. Reference

- `openspec/changes/archive/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/`
  (the archived change record)

## Pre-commit hook

A pre-commit hook blocks commits that introduce hardcoded model strings:

```bash
mise run pre-commit-install  # install the hook
mise run pre-commit-run      # run on all files manually
git commit --no-verify       # skip (rare)
```

The hook runs `mise run lint:registry` (which invokes
scripts/registry_audit.py) and fails the commit if any hardcoded
model name/ID is found in `agents/`, `baml_src/`, `notebooks/`,
`web/`, `orchestration/`, `spaces/`, or `meaisinfhoghlaim/` that
isn't routed through `MODEL_REGISTRY`.
- `openspec/specs/centralized-model-registry/spec.md` (4 Requirements)
- `openspec/specs/centralized-schema-registry/spec.md` (4 Requirements)
- `openspec/specs/deployment-control-panel/spec.md` (5 Requirements)
- `meaisinfhoghlaim/models/model_registry.py:MODEL_REGISTRY`
- `notebooks/_shared/schema.py` (5 helpers)
- `notebooks/00_control_panel.py` (the 5-tab notebook)
- `scripts/registry_audit.py` (the drift detector)
- `agents/adk/litellm_agent.py` (the LiteLlm helper)
- `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`
- `cocoindex_flows/european_nations/_factory.py` (the factory pattern)
- `deployment-choice.yaml` (the canonical enablement file)

## 10. The 6 follow-up issues

| # | Title | Work |
|--:|:--|:--|
| [#141](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/141) | Complete remaining MODEL_REGISTRY migrations (Phase 1.3-1.10 + 1.12-1.19) | 15 remaining model hardcodes |
| [#142](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/142) | Activate BAML TypeScript codegen (baml_client_ts/) | TS codegen via Node @baml/cli |
| [#143](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/143) | Build web UI control panel | 5 TanStack Start routes |
| [#144](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/144) | Pydantic dedup rollout (7 remaining subjects) | ~1320 LOC reduction |
| [#145](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/145) | CocoIndex factory rollout (Irish LC + BI parity) | 14 files → 2 factories |
| [#146](https://github.com/cianfhoghlaim/cianfhoghlaim/issues/146) | Dagster JurisdictionAssetsBase rollout | ~3300 LOC reduction |

---

## 11. OCR/VLM Pipeline

The OCR/VLM surface lives under `meaisinfhoghlaim/`. This
section is the canonical entrypoint for any agent adding,
modifying, or evaluating vision models, OCR backends,
PDF converters, alignment methods, or the BIEP v2 4-path
ensemble.

### 11.1 The `ocr_vision` family in `MODEL_REGISTRY`

The `ocr_vision` family is a 22-entry subset view of
`MODEL_REGISTRY` exposed via
`MODEL_REGISTRY.filter(family="ocr_vision")`. Each entry
groups by `role` into 4 tiers:

| Tier | Models |
|:--|:--|
| **tier1_heavy** (≥ 27B params, full-document) | `qwen3-vl-30b-a3b`, `qwen3.6-27b-mtp` |
| **tier2_medium** (8-12B params, page-level) | `gemma-4-12B`, `gemma-4-26B-A4B`, `glm-4.6v-flash`, `qwen3-vl-8b`, `internvl3-8b` |
| **tier3_light** (≤ 4B params, fast inference) | `gemma-4-E2B`, `gemma-4-E4B`, `qwen3-vl-4b` |
| **specialist** (single-purpose OCR/VLM) | `deepseek-ocr-2`, `olmocr-2-7b-1025`, `granite-docling-258M`, `uccix-mistral-24b`, `uccix-llama-3.1-8b`, `dots-ocr`, `paddleocr-vl-1.6`, `molmo2-4b`, `molmo2-8b`, `unstract-api`, `docling-serve` |
| **legacy** (deprecated, kept for back-compat) | `uccix-llama2-13b`, `llama-3.2-vision-11b` |

Resolve via the canonical 2-axis key:

```python
from meaisinfhoghlaim.models import MODEL_REGISTRY

# Pick the M4-Max optimal model
m4_max = MODEL_REGISTRY.resolve("ocr_vision", "tier1_heavy")
# → "qwen3-vl-30b-a3b"

# Pick by language
irish_specialist = MODEL_REGISTRY.filter(family="ocr_vision", role="specialist")
# → 11 entries (deepseek-ocr-2, olmocr-2-7b-1025, ...)

# List all available (non-legacy)
available = MODEL_REGISTRY.filter(family="ocr_vision", available=True)
# → 20 entries (excludes the 2 legacy entries)
```

### 11.2 The 6 `CLASSICAL_OCR` backends

The classical OCR registry (`meaisinfhoghlaim/models/registry.py:CLASSICAL_OCR`)
holds 6 Docker-backed backends — each runs as a separate
Compose stack at `bonneagar/stacks/ocr-classical/<name>/`:

| Key | Image | Port | Notes |
|:--|:--|--:|:--|
| `docling-serve` | `docker.io/ds4sd/docling-serve:latest` | 5001 | IBM Docling — 258M params, DocTags layout. The "safety net" when VLM extraction fails. |
| `paddleocr` | `docker.io/paddlepaddle/paddleocr:latest` | 8888 | PaddlePaddle OCR — multilingual, first-party GGUF. |
| `paddleocr-vl` | `docker.io/paddlepaddle/paddleocr-vl:latest` | 8889 | PaddleOCR-VL — vision-language variant for diagrams. |
| `tesseract` | `docker.io/tesseractshadow/tesseract4re:latest` | 8880 | Tesseract 4 + LSTM. English/Irish/Latin scripts. |
| `pylaia` | `docker.io/ocrhn/pylaia:latest` | 8881 | PyLaia HTR — best for handwritten Irish manuscripts. |
| `trocr` | `docker.io/microsoft/trocr:latest` | 8882 | Microsoft TrOCR — transformer-based HTR for printed + handwritten. |

All 6 are wrapped by `meaisinfhoghlaim/backends/adapters.py:OCRAdapterRegistry`
(the 4th backend protocol) and are reachable via the
`select_ocr_backend()` helper:

```python
from meaisinfhoghlaim.models.registry import CLASSICAL_OCR, select_ocr_backend
backend = select_ocr_backend(task="handwritten_irish", quality="high")
# → "pylaia" (the optimal choice for handwritten Irish manuscripts)
```

### 11.3 The BIEP v2 4-path ensemble (`EnsembledExtractor`)

The flagship extraction pipeline. Located at
`meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:EnsembledExtractor`.
Runs 4 OCR paths in parallel via `asyncio.gather`:

| Path | Tool | Input | Output format |
|:--|:--|:--|:--|
| 1. **BAML** | `Docling-serve` → text → BAML function | PDF | Typed Pydantic row |
| 2. **Unstract** | `Docling-serve` → Unstract workflow → JSON | PDF | Structured JSON |
| 3. **qwen3_vl** | `qwen3-vl-8b` page-level image → JSON | Page images | Structured JSON |
| 4. **gemma4** | `gemma-4-26B-A4B` page-level image → JSON | Page images | Structured JSON |

Each path output lands in its own per-jurisdiction DuckLake
table. The RAGAS `biiep_extraction_consensus` metric then
votes the canonical row.

**Webhook emission** (post-2026-08-15): on every successful
extraction, the canonical envelope is POSTed to
`os.getenv("OCR_WEBHOOK_URL", "")` via `httpx.AsyncClient`
(fire-and-forget). Schema (per
`british-isles-education-pipeline-v3` spec delta):

```python
{
  "document_id": "<uuid>",
  "capability": "<forms|layout|tables+latex|doctags|gaelic|english>",
  "backend_used": "<paddleocr|mlx-omni|olmocr|docling-serve|llama-swap|dots-ocr>",
  "model": "<model name>",
  "result_url": "<s3://lakehouse/ocr/...>",
  "duration_ms": <int>,
  "trace_id": "<opentelemetry trace id>",
  "completed_at": "<iso-8601 utc>"
}
```

Invocation:

```python
from meaisinfhoghlaim.ocr.ensemble.ensembled_extractor import EnsembledExtractor

extractor = EnsembledExtractor(
    document_id="<uuid>",
    pdf_path="leabharlann/ncca/lc_mathematics_2024.pdf",
    jurisdiction="ireland",
)
result = await extractor.extract()
# `result` is a RAGAS-voted Envelope with the canonical row
```

### 11.4 The 7 PDF converters (`meaisinfhoghlaim/document_factory/`)

Each converter transforms a PDF into markdown/dict/structured
output. All live under
`meaisinfhoghlaim/document_factory/converters/`:

| Converter | Module | Best for |
|:--|:--|:--|
| `docling` | `docling_converter.py` | Layout-aware extraction (DocTags) |
| `marker` | `marker_converter.py` | High-quality markdown + figure extraction |
| `unstructured` | `unstructured_converter.py` | Partitioning + element classification |
| `deepseekocr` | `deepseekocr_converter.py` | Compressed-document specialist (DeepSeek-OCR-2) |
| `pymupdf4llm` | `pymupdf4llm_converter.py` | Fast text extraction (PyMuPDF4LLM) |
| `curriculum_document` | `../curriculum_document.py` | Curriculum document representation |
| `pdf_factory` | `../pdf_factory.py` | Orchestrator — picks the right converter per document |

The `pdf_factory` is the canonical entrypoint — it routes
each PDF to the optimal converter based on document type,
language, and quality requirements.

### 11.5 The 4 alignment methods + `ColPaliAligner`

`meaisinfhoghlaim/alignment/aligner.py` ships 4 methods
for Irish-English cross-lingual alignment:

| Method | Best for | Quality |
|:--|:--|:--|
| `VecAlign` | Large parallel corpora | High (deep embedding) |
| `HunAlign` | Medium corpora, sentence-level | Medium (HMM-based) |
| `GaoisAlign` | Irish terminology alignment | High (Gaois-trained) |
| `Hybrid` | Production (VecAlign + HunAlign fallback) | Highest |

Plus the `ColPaliAligner` (`colpali_aligner.py`) for
manuscript bbox extraction — uses ColPali vision embeddings
to map extracted text back to manuscript page coordinates.

```python
from meaisinfhoghlaim.alignment import aligner

a = aligner.IrishEnglishAligner(method="hybrid")
result = a.align_parallel_texts(
    irish=["Tá an lá go hálainn.", "Is maith liom an Ghaeilge."],
    english=["The day is beautiful.", "I like Irish."],
)
# → AlignmentResult with per-sentence confidence scores
```

### 11.6 The Irish HTR dataset

`meaisinfhoghlaim/datasets/irish_htr_dataset.py` (25KB) is
the canonical training dataset for Irish handwriting
recognition (HTR). Built from 3 sources:

1. **NLI manuscripts** (National Library of Ireland) — scanned
   18th-19th century Irish-language manuscripts
2. **RIA archives** (Royal Irish Academy) — handwritten
   letters + diaries
3. **School copybooks** — modern (20th century) school
   copybook scans

The dataset is the training source for the `pylaia` classical
backend + the `uccix-mistral-24b` specialist VLM.

### 11.7 The M4-Max dispatch helper

`meaisinfhoghlaim/models/registry.py:select_optimal_for_m4_max()`
returns the recommended OCR/VLM model for the M4 Max 64GB
workstation:

```python
from meaisinfhoghlaim.models.registry import select_optimal_for_m4_max

m4_max_model = select_optimal_for_m4_max()
# → "gemma-4-26B-A4B" (the M4-Max optimal choice)

# With a constraint
m4_max_irish = select_optimal_for_m4_max(task="irish_handwritten")
# → "uccix-mistral-24b" (the Irish HTR specialist)
```

### 11.8 llama-swap GGUF inference

The local inference path is configured by
`meaisinfhoghlaim/models/llama_swap_config.yaml` (the
llama-swap GGUF server config). It exposes all 22
`VISION_MODELS` entries as GGUF endpoints behind a single
OpenAI-compatible API:

```yaml
# llama_swap_config.yaml — relevant snippet
models:
  "qwen3-vl-8b":
    name: "Qwen3-VL-8B-Instruct"
    gguf: "unsloth/Qwen3-VL-8B-Instruct-GGUF"
    cmd: >-
      llama-server -m unsloth/Qwen3-VL-8B-Instruct-GGUF/qwen3-vl-8b-instruct-q4_k_m.gguf
      --port 8080 --host 0.0.0.0 -ngl 99
```

The `docling-serve` classical backend is the safety net —
when llama-swap is unavailable, the adapter falls back
automatically.

### 11.9 BAML `clients_ocr_ensemble.baml` patterns

`baml_src/clients_ocr_ensemble.baml` declares the 3
ensemble clients used by the BIEP v2 4-path pipeline:

| Client | Provider | Used by |
|:--|:--|:--|
| `LocalVision` | llama-swap | Path 3 (qwen3_vl) + Path 4 (gemma4) |
| `ExtractEnStrong` | BAML function (calls Path 1) | Path 1 (BAML) |
| `UnstractFlow` | Unstract API | Path 2 (Unstract) |

Each client references `MODEL_REGISTRY` (no hardcoded
model strings) and exposes a typed BAML function that
the BIEP v2 pipeline consumes.

### 11.10 RAGAS-voted chunk emission

The `EnsembledExtractor` emits RAGAS-voted chunks after
the 4-path consensus. The voting metric is
`biiep_extraction_consensus` (registered in
`scripts/ragas_metrics.py`). Each chunk carries:

- `chunk_id` (UUID)
- `document_id` (parent PDF)
- `path_votes` (4 booleans — which paths agreed)
- `consensus_score` (RAGAS score, 0-1)
- `text` (the canonical chunk text)
- `bbox` (page-level coordinates, from ColPali)

### 11.11 The `meaisinfhoghlaim/ocr/` back-compat shim

The nested `meaisinfhoghlaim/ocr/` sub-package exists for
**back-compat only**. It re-exports `VISION_MODELS` + the
ensemble with a `DeprecationWarning`:

```python
# LEGACY — emits DeprecationWarning
from meaisinfhoghlaim.ocr.models.registry import VISION_MODELS

# CANONICAL — no warning
from meaisinfhoghlaim.models.registry import VISION_MODELS
```

The canonical home for all OCR/VLM models is
**`meaisinfhoghlaim.models.registry`** (per the v4 platform
convention: the outer `models/` package is canonical).
The `meaisinfhoghlaim/ocr/` shim will be removed in v5 of
the registry.

### 11.12 The `image_generation_agent` consumer (NEW 2026-08-13)

The `image_generation_agent` (registered in
`agents/agent_registry.py:AGENT_REGISTRY` as the 13th main agent,
per Phase L of the
2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change)
consumes the 5 `image_gen` MODEL_REGISTRY entries for 2D asset
generation + Babylon.js texture creation.

The agent's 5 tools live at `agents/adk/tools/image_generation.py`:

| Tool | Purpose | Role |
|:--|:--|:--|
| `list_image_models` | List the 5 `image_gen` entries + availability | (inspector) |
| `generate_2d_asset` | Generate a 2D image (subject illustration, sprite, diagram) | `default`, `fast`, `bilingual`, `legacy` |
| `generate_texture` | Generate a Babylon.js PBR texture | `diagrams` |
| `style_match` | Generate N style-preserved variants | `default` |
| `cocoindex_register` | Register the generated asset in the CocoIndex | (always) |

The BAML client wiring is at `baml_src/clients_image_gen.baml` with
5 client<llm> blocks (ImageGenDefault + ImageGenFast +
ImageGenBilingual + ImageGenLegacy + ImageGenDiagrams). Each client
routes via `model_for('image_gen', role)` — never hardcodes a model
string.

The CocoIndex flow is at
`cocoindex_flows/media/image_generation_flow.py` (R1–R4 conformance +
the canonical `bge-m3` embedder + LanceDB target table
`cianhoghlaim.media.image_gen_chunks`).

### 11.13 Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new OCR/VLM model | `meaisinfhoghlaim/models/registry.py:VISION_MODELS` (or `model_registry.py:MODEL_REGISTRY` for the 7-family view) |
| Add a new classical OCR backend | `meaisinfhoghlaim/models/registry.py:CLASSICAL_OCR` + `bonneagar/stacks/ocr-classical/<name>/` |
| Add a new image_gen model | `meaisinfhoghlaim/models/model_registry.py:MODEL_REGISTRY` (family=`image_gen`) + `agents/adk/image_generation_agent.py` |
| Add a new `image_gen` BAML client | `baml_src/clients_image_gen.baml` + `agents/adk/tools/image_generation.py` |
| Run the image_gen agent | `agents/adk/image_generation_agent.py:image_generation_agent` |
| Wire a model into BAML | `baml_src/clients_ocr_ensemble.baml` (the 3 ensemble clients) |
| Run the 4-path ensemble | `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:EnsembledExtractor` |
| Add a new PDF converter | `meaisinfhoghlaim/document_factory/converters/<name>_converter.py` + register in `pdf_factory.py` |
| Add a new alignment method | `meaisinfhoghlaim/alignment/aligner.py:AlignmentMethod` (StrEnum) |
| Evaluate a new OCR backend | `meaisinfhoghlaim/evaluation/` (the OCR evaluation harness) |
| Train an Irish HTR model | `meaisinfhoghlaim/datasets/irish_htr_dataset.py` (25KB training data) |
| Configure local inference | `meaisinfhoghlaim/models/llama_swap_config.yaml` (the llama-swap config) |
| Pick the optimal M4-Max model | `select_optimal_for_m4_max()` (the dispatch helper) |

### 11.14 Cross-references

- [`meaisinfhoghlaim/README.md`](../../meaisinfhoghlaim/README.md) — the deeper sub-package docs (the canonical home for OCR/HTR/Alignment)

### 12. Firecrawl MCP — the external search surface (NEW 2026-08-14)

Per the `2026-08-14-firecrawl-mcp-ccc-dual-search-v1` change, **Firecrawl MCP
is the canonical external search surface** (analogous to how ccc is the
internal code search surface and Cognee is the internal docs search
surface). The FirecrawlMCPClient wrapper at
`agents/meaisinfhoghlaim/firecrawl_mcp/client.py` exposes all 12 MCP tools
with Pydantic validation + Langfuse `@observe`. The agent routing table
for ccc vs cognee vs firecrawl_search is documented at `AGENTS.md`
§"Triple-search architecture" and the
[`dual-search-architecture`](../openspec/specs/dual-search-architecture/spec.md)
spec. The Firecrawl API key lives in Infisical under the
`firecrawl-api-key` secret (per the `.agents/skills/secrets-management/SKILL.md`
contract). The agent reference corpus (built by the Phase 4a change)
federates `firecrawl_search` + Cognee + Graphiti + LanceDB over the
`docs_index` table.
- [`meaisinfhoghlaim/AGENTS.md`](../../meaisinfhoghlaim/AGENTS.md) — the agent routing for the meaisinfhoghlaim sub-tree
- [`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md`](../../openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md) — the 10 OCR backends across the canonical 6
- [`openspec/specs/meaisin-24-ocr-models/spec.md`](../../openspec/specs/meaisin-24-ocr-models/spec.md) — the 24 VISION_MODELS spec (v4 registry)
- [`openspec/specs/celtic-language-pipeline/spec.md`](../../openspec/specs/celtic-language-pipeline/spec.md) — the 6 Celtic-language OCR consumer
- [`.agents/skills/centralized-registry/SKILL.md`](./SKILL.md) — this skill (the canonical model registry)
- [`.agents/skills/baml/SKILL.md`](../baml/SKILL.md) — the BAML extraction pattern
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) — the CocoIndex v1 embedding layer

---

**Last updated**: 2026-08-13 (added §11.12 image_generation_agent consumer row + the 5 `image_gen` BAML clients + the CocoIndex flow + the 5 tools; updated the routing table with the image_gen entry).
**Owner**: Build agent.