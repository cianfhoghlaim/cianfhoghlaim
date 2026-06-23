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

## Celtic LLMs (EuroLLM 22B)

### `utter-project/EuroLLM-22B-Instruct-2512` — KCG canonical en↔ga model

The EuroLLM family is the **EU-funded, Apache-2.0, fully
open** LLM that includes Irish in its 35-language pre-training
mix. It is the KCG-preferred model for the `celtic_irish`
chain **when translation fidelity matters more than
latency**; the `qomhra-mistral` chain is faster but
EuroLLM-22B beats Gemma-3-27B and Qwen-3-32B on
WMT24++ / FLORES for the en↔ga pair.

| Field | Value |
|:--|:--|
| Repo | `utter-project/EuroLLM-22B-Instruct-2512` |
| License | Apache 2.0 |
| Params | 22.6B total (21B non-embedding) |
| Context | 32,768 tokens |
| Architecture | Dense Transformer, GQA 48Q / 8 KV, RoPE Θ=1M, RMSNorm, SwiGLU, 56 layers, emb 6144, FFN 16384 |
| Pre-training | 4T tokens, 3 phases: 3.6T web + parallel + wiki + arxiv; 400B annealing (CometKiwi-22 + EuroFilter); 100B anneal-to-zero with long-context up-sampling |
| Hardware | 400 × H100 on MareNostrum 5 (EuroHPC extreme-scale grant) |
| Post-training | EuroBlocks (general instruct + MT focus); best EU-made fully open model on HellaSwag/MMLU/MMLU-Pro/ARC-C/MGSM/FLORES/WMT24++ |
| Celtic coverage | Irish (`ga`) is a **first-class** pre-training language (not bolt-on) |

**Quantisation playbook on `bunchloch` M4 Max (48GB
unified):**

- GGUF `Q4_K_M` ≈ 13 GB (fits in 48GB with headroom for
  KV cache + 32k context)
- GGUF `Q3_K_M` ≈ 10.5 GB (use if running other models
  concurrently)
- MLX 4-bit ≈ 11.5 GB (preferred for Apple Silicon
  unified-memory bandwidth)

KCG inference wiring: serve via `llama-swap` on `:8080`
with `--ctx-size 32768` and `--n-gpu-layers 99`. The
LiteLLM entry (in `config.yaml`):

```yaml
- model_name: eurollm-22b
  litellm_params:
    model: openai/eurollm-22b-instruct
    api_base: http://llama-swap:8080/v1
    api_key: sk-local
    timeout: 600
```

**The 4-byte prompt template** (must use exactly this
system message for Irish quality):

```
You are EuroLLM — an AI assistant specialized in European
languages that provides safe, educational and helpful answers.
```

### Fallback chain placement

Add EuroLLM-22B as the **2nd step** in the `celtic_irish`
chain (after `qomhra-mistral`, before `britllm`):

```yaml
celtic_irish:  qomhra-mistral → eurollm-22b → uccix → britllm
```

For `celtic_gaelic` the chain stays as
`britllm → qomhra-mistral` — BritLLM-3B is stronger on
Gàidhlig because of the BritEval Scots + Scottish Gaelic
training mix; EuroLLM-22B's Gàidhlig coverage is
weaker than its Irish coverage.

## Inference backends (llama-swap + mlx-vlm + LiteLLM + Z.AI)

The KCG production inference stack is a **unified hybrid
gateway** that aggregates 3 backends behind a single
LiteLLM proxy on `:4000`. The client (BAML / Cognee /
CocoIndex) sees one OpenAI-compatible endpoint; the
gateway routes to the right backend per model.

### The 3 backends

| Format | Backend | Default port | Hardware | Why |
|:--|:--|:--|:--|:--|
| **GGUF** | `llama-swap` (router mode) | 8080 (swap port 8081) | M4 Max GPU + CPU | Hot-swap multiple quantised models in 48GB unified |
| **MLX** | `mlx-omni-server` or `mlx-vlm` | 10240 (`:8082` swap variant) | M4 Max Apple Silicon | Native Unified Memory Architecture; day-0 model support |
| **Cloud** | Z.AI (Zhipu) `zai/glm-4.6v` | HTTPS | Beijing DC | Cloud fallback for high-fidelity multimodal |

### llama-swap: hot-swap multi-model router

Standard inference servers (Ollama, vLLM, llama-server
standalone) are persistent processes that hold one model
in RAM. On a 48GB M4 Max you cannot load 2 × 70B Q4
GGUFs simultaneously. **llama-swap** resolves this with
a process manager that listens on a single port and
**SIGTERMs the active model** to load the requested one.

The `swap_config.yaml` defines the per-model `cmd`
template:

```yaml
# configs/llama-swap/swap_config.yaml
host: "127.0.0.1"
port: 8081
health_check_timeout: 300   # 5min; 120B models take 30s to mmap

models:
  "eurollm-22b":
    cmd: >
      /usr/local/bin/llama-server
      --model /opt/ai-gateway/models/gguf/eurollm-22b/eurollm-22b-instruct-Q4_K_M.gguf
      --port ${PORT}
      --ctx-size 32768
      --n-gpu-layers 99
      --flash-attn

  "britllm-3b":
    cmd: >
      /usr/local/bin/llama-server
      --model /opt/ai-gateway/models/gguf/britllm/britllm-3b-v0.1-Q5_K_M.gguf
      --port ${PORT}
      --ctx-size 8192
      --n-gpu-layers 99

  "deepseek-v3.1":
    cmd: >
      /usr/local/bin/llama-server
      --model /opt/ai-gateway/models/gguf/deepseek-v3.1/DeepSeek-V3.1-Terminus-Q4_K_M.gguf
      --port ${PORT}
      --ctx-size 65536        # 64k for "thinking" tokens
      --n-gpu-layers 99
      --cache-type-k f16

  "qwen3-vl":
    cmd: >
      /usr/local/bin/llama-server
      --model /opt/ai-gateway/models/gguf/qwen3-vl/Qwen3-VL-Instruct-Q4_K_M.gguf
      --mmproj /opt/ai-gateway/models/gguf/qwen3-vl/mmproj-Qwen3-VL-Instruct-f16.gguf
      --port ${PORT}
      --ctx-size 16384        # buffer for high-res image tokens
      --n-gpu-layers 99
```

**Critical config notes:**
- `--mmproj` is **required** for Qwen3-VL; without it
  the server runs text-only and hallucinates on image
  inputs.
- `--ctx-size 65536` for DeepSeek-V3.1 because the
  "thinking" tokens alone can be 5-10k.
- `health_check_timeout: 300` because 70B+ models take
  ~30s to mmap from SSD; the default 60s will fail.

### mlx-vlm: Apple Silicon native

For models with quirks that take weeks to stabilise in
GGUF (e.g. Granite-Docling's "DocTags" architecture,
Gemma-3's native multimodal interleaving), use
`mlx-vlm` on `:8082`. It exposes the same OpenAI
chat-completions format and slots into the LiteLLM
routing table identically:

```yaml
- model_name: granite-docling
  litellm_params:
    model: openai/ibm-granite/granite-docling-258M-mlx
    api_base: http://127.0.0.1:8082/v1
    api_key: sk-local
- model_name: gemma-3
  litellm_params:
    model: openai/google/gemma-3-27b-it-mlx
    api_base: http://127.0.0.1:8082/v1
    api_key: sk-local
```

### Z.AI cloud (GLM-4.6v + GLM-TTS)

The LiteLLM `zai` provider route gives a single endpoint
for both Zhipu's vision (`glm-4.6v`) and TTS
(`glm-4-voice`) models. The audio/speech endpoint
translation is the killer feature: clients call
`client.audio.speech.create(model="zai-speech", input="...")`
and LiteLLM rewrites it to the Z.AI voice API.

### The unified LiteLLM config

```yaml
# configs/litellm/proxy_config.yaml
general_settings:
  master_key: sk-admin-gateway-key

litellm_settings:
  success_callback: ["langfuse", "mlflow"]
  failure_callback: ["langfuse", "mlflow"]
  json_logs: true

model_list:
  # GGUF backends via llama-swap :8081
  - {model_name: eurollm-22b,   litellm_params: {model: openai/eurollm-22b-instruct,  api_base: http://127.0.0.1:8081/v1, api_key: sk-local, timeout: 600}}
  - {model_name: britllm-3b,     litellm_params: {model: openai/britllm-3b-v0.1,       api_base: http://127.0.0.1:8081/v1, api_key: sk-local}}
  - {model_name: deepseek-r1,    litellm_params: {model: openai/deepseek-v3.1,        api_base: http://127.0.0.1:8081/v1, api_key: sk-local, timeout: 600}}
  - {model_name: qwen-vision,    litellm_params: {model: openai/qwen3-vl,             api_base: http://127.0.0.1:8081/v1, api_key: sk-local}}
  # MLX backends via :8082
  - {model_name: granite-docling,litellm_params: {model: openai/ibm-granite/granite-docling-258M-mlx, api_base: http://127.0.0.1:8082/v1, api_key: sk-local}}
  - {model_name: gemma-3,        litellm_params: {model: openai/google/gemma-3-27b-it-mlx,         api_base: http://127.0.0.1:8082/v1, api_key: sk-local}}
  # Cloud backends
  - {model_name: glm-4-plus,     litellm_params: {model: zai/glm-4.6v}}
  - {model_name: zai-speech,     litellm_params: {model: zai/glm-4-voice}}
```

### Observability: Langfuse + MLflow (dual-layer)

- **Langfuse** (`:3000`): trace-level waterfall; the
  LiteLLM `success_callback: ["langfuse"]` hook pushes
  every request with gateway latency, llama-swap queue
  time, and token-generation speed. Custom pricing
  (e.g. `$0.00/token` for local models) lets you compare
  local cost vs Z.AI cost in one dashboard.
- **MLflow** (`:5000`): experiment registry; `mlflow.litellm.autolog()`
  captures the full prompt + parameters + output for
  A/B testing (e.g. "GPT-OSS-120B vs DeepSeek-V3.1 on
  the 100-query BritEval validation set").

### KCG production rules (anti-patterns)

- **Don't use Ollama** for the KCG stack — it cannot
  hot-swap models in 48GB. Use llama-swap router mode.
- **Don't forget `--mmproj` for Qwen3-VL** — the
  server starts text-only and silently hallucinates on
  image inputs. The CI lint must grep for `--mmproj`
  on every Qwen-VL swap entry.
- **Don't set LiteLLM timeout below 600s for reasoning
  models** (DeepSeek-V3.1, o1-class) — the "thinking"
  phase generates thousands of hidden tokens before the
  first visible one; default 60s timeouts fail.
- **Don't load 2 × 70B+ models simultaneously** — use
  llama-swap's exclusive execution; the `health_check_timeout`
  must be tuned per-model (300s for 120B).

See [`upstream-mirrors/references/llm-serving-mlflow-langfuse.md`](../upstream-mirrors/references/llm-serving-mlflow-langfuse.md)
for the full 381-line architecture deep dive including
the complete `swap_config.yaml` and the Z.AI audio
endpoint translation logic.
