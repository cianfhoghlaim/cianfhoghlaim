---
name: kcg-ml-models
description: KCG's 70+ model registry + 5 fallback chains + 3 inference backends (GGUF / llama-swap :8080, MLX / mlx-omni-server :10240, safetensors / invokeai :9090) + llama.cpp router mode. Use when adding a new model, picking a fallback chain, debugging a model server, or asking "which model should I use for X?".
---

# KCG ML Models

## When to use this skill

Use when you need to:

- "Which model should I use for X?" (vision, OCR, reasoning,
  Celtic lang)
- "Add a new model to the KCG registry"
- "Debug a model server (llama-swap, mlx-omni-server, invokeai)"
- "Wire a fallback chain (e.g. `qomhra-mistral → uccix →
  britllm`)"
- "Switch from Ollama to llama.cpp router mode"
- "Quantise a model for the M4 Mac (GGUF + MLX)"

## The 3 inference backends

| Format | Backend | Default port | Hardware target |
|:--|:--|:--|:--|
| **GGUF** | `llama-swap` (with router mode) | 8080 | bunchloch M4 GPU + CPU |
| **MLX** | `mlx-omni-server` | 10240 | bunchloch M4 GPU (Apple Silicon) |
| **safetensors** | `invokeai` | 9090 | bunchloch M4 GPU + Metal |

The 3 backends run on the same `bunchloch` M4 Max (48GB
unified memory). The LiteLLM gateway (`:4000`) routes BAML
+ Cognee + CocoIndex calls to whichever backend serves the
model name.

## The 11 model categories

| Category | Count | Examples | Backend |
|:--|--:|:--|:--|
| **OCR** | 2 | `olmOCR-2-7B`, `granite-docling` | GGUF |
| **Vision** | 5 | `Qwen3-VL`, `GLM-4.6V`, `Moondream2` | GGUF / MLX |
| **Retrieval** | 3 | `ColQwen2.5`, `ColQwen2`, `ColPali` | safetensors |
| **Image Gen** | 6 | `FLUX.2`, `Z-Image-Turbo`, `Qwen-Image` | safetensors |
| **Segmentation** | 3 | `SAM2`, `GroundingDINO`, `MoGe` | safetensors |
| **Geospatial** | 3 | `OlmoEarth` (base, LFMC, forest) | safetensors |
| **Audio** | 2 | `SAM-Audio` (base, large) | safetensors |
| **Celtic LLMs** | 6 | `EuroLLM`, `BritLLM`, `UCCIX`, `Qomhrá` | GGUF |
| **Celtic Encoders** | 3 | `gaBERT`, `ga-ELECTRA`, `Welsh-BERT` | safetensors |
| **Celtic Speech** | 6 | `ABAIR`, `ÈIST`, `Macsen`, `Trawsgrifiwr` | API |
| **General** | 5 | `Gemma-3n`, `Nemotron-3`, `FunctionGemma` | GGUF / MLX |

**Total: 70+ models** across 11 categories. The canonical
catalog is `models/registry.yaml` + `catalog/models.yaml`.

## The 5 fallback chains

The KCG production rule: **never let a single model failure
cascade**. Every category has a 2-3 step fallback:

```yaml
vision:        glm-4.6v-flash → qwen3-vl → moondream2
ocr:           olmocr-2 → granite-docling
reasoning:     nemotron-3-nano → gemma-3n
celtic_irish:  qomhra-mistral → uccix → britllm
celtic_gaelic: britllm → qomhra-mistral  # BritLLM is stronger for Gàidhlig
```

**Implementation**: BAML `client` blocks chain the fallback
models. If `qomhra-mistral` returns empty or errors, BAML
auto-retries with `uccix`, then `britllm`. The fallback is
**per-call** (not per-session).

## llama.cpp router mode (replaces Ollama)

The canonical KCG pattern: **llama.cpp server in router mode**
(December 2025 release), not Ollama.

### Why not Ollama

- Ollama is a single-process model server (one model loaded
  at a time, slow to switch)
- llama.cpp router mode = multi-process, LRU eviction,
  on-demand loading

### How to start it

```bash
# Start in router mode (no model specified = auto-discover)
llama-server
# This scans ~/.cache/llama.cpp/ for GGUF files
# and auto-loads on first request
```

### Key options

| Flag | Description |
|:--|:--|
| `--models-dir PATH` | Directory of GGUF files (default: `~/.cache/llama.cpp/`) |
| `--models-max N` | Max models loaded simultaneously (default: 4) |
| `--no-models-autoload` | Disable auto-loading (require explicit `/models/load`) |

### Per-model presets

```ini
# config.ini
[my-model]
model = /path/to/model.gguf
ctx-size = 65536
temp = 0.7
```

```bash
llama-server --models-preset config.ini
```

## Celtic language model detail

### Irish (Gaeilge)

| Model | Type | Size | Notes |
|:--|:--|--:|:--|
| `UCCIX-Llama2-13B` | LLM | 13B | +12% over LLaMA-2-70B on Irish |
| `Qomhrá-Mistral-7B` | LLM | 7B | Fine-tuned Mistral on Gaois + UCC corpora |
| `gaBERT` | Encoder | 110M | DCU-NLP, Irish-specific BERT |
| `ABAIR` | TTS/ASR | API | NUI Galway synthesis |

### Welsh (Cymraeg)

| Model | Type | Size | Notes |
|:--|:--|--:|:--|
| `BritLLM-3B` | LLM | 3B | Multilingual Celtic + English |
| `Welsh-BERT` | Encoder | 110M | Bangor University |
| `Macsen` | ASR | API | Mozilla Common Voice |

### Scottish Gaelic (Gàidhlig)

| Model | Type | Status |
|:--|:--|:--|
| `BritLLM-3B` | LLM | Available |
| `ÈIST` | ASR | Coming 2025 |

## LiteLLM `litellm://` routing

The BAML + Cognee + CocoIndex calls all go through LiteLLM
(`:4000`). The LiteLLM config (`config.yaml`) maps BAML
client names to model servers:

```yaml
model_list:
  - model_name: extract-en
    litellm_params:
      model: openai/litellm/gemini-2.5-flash
      api_base: http://llama-swap:8080/v1
  - model_name: extract-en-strong
    litellm_params:
      model: openai/litellm/anthropic/claude-sonnet-4
      api_base: http://llama-swap:8080/v1
  - model_name: bge-large-en
    litellm_params:
      model: openai/BAAI/bge-large-en-v1.5
      api_base: http://sentence-transformers:8080/v1
```

The `litellm://` prefix is the KCG convention: the BAML
client name (`extract-en`) is resolved by LiteLLM, which
routes to the right backend.

## Apple Silicon M4 playbook

The `bunchloch` M4 Max (48GB unified memory) is the KCG
workload host. The playbook for adding a new model:

1. **Pick the backend** (GGUF for LLMs, MLX for Apple-tuned
   models, safetensors for vision/audio)
2. **Quantise** — for GGUF: `Q4_K_M` (best size/quality) or
   `Q5_K_M` (better quality, +20% RAM); for MLX: `4-bit`
   (default), `8-bit` (better quality)
3. **Download** — `huggingface-cli download <repo>` (HF
   Pro account for the higher rate limit)
4. **Place in the right cache**:
   - GGUF → `~/.cache/llama.cpp/`
   - MLX → `~/.cache/mlx/`
   - safetensors → `~/.cache/huggingface/`
5. **Register in `models/registry.yaml`**
6. **Test** — `curl http://localhost:8080/v1/chat/completions
   -d '{"model": "<name>", "messages": [{"role": "user",
   "content": "test"}]}'`

## Cross-references

- `.agents/skills/celtic-language-ai/SKILL.md` — the
  Celtic language matrix (6 langs × 4 tasks)
- `.agents/skills/cocoindex/SKILL.md` — the embedding
  pipeline (uses `bge-large-en-v1.5`)
- `.agents/skills/baml/SKILL.md` — the BAML `client`
  block (the fallback chain mechanism)
- `.agents/skills/lancedb/SKILL.md` — the LanceDB server
  (separate from the model servers)
- `.agents/skills/dagster/SKILL.md` — the LiteLLM asset
  wiring
- `models/registry.yaml` — the canonical model registry
- `catalog/models.yaml` — model definitions + versions
- `catalog/sources.yaml` — dataset sources for training
