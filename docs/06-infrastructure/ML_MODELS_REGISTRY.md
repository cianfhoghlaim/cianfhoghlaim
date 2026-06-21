---
truth: partial
merged_from:
  - docs/06-infrastructure/ML_STACK.md
  - docs/06-infrastructure/New in llama.cpp_ Model Management.md
---

# Meaisínfhoghlaim - ML Models

Machine learning model registry, training notebooks, and inference backends.

## Model Registry

`models/registry.yaml` - Central configuration for 70+ models.

### Categories

| Category | Count | Examples |
|----------|-------|----------|
| OCR | 2 | olmOCR-2-7B, granite-docling |
| Vision | 5 | Qwen3-VL, GLM-4.6V, Moondream2 |
| Retrieval | 3 | ColQwen2.5, ColQwen2, ColPali |
| Image Gen | 6 | FLUX.2, Z-Image-Turbo, Qwen-Image |
| Segmentation | 3 | SAM2, GroundingDINO, MoGe |
| Geospatial | 3 | OlmoEarth (base, LFMC, forest) |
| Audio | 2 | SAM-Audio (base, large) |
| Celtic LLMs | 6 | EuroLLM, BritLLM, UCCIX, Qomhrá |
| Celtic Encoders | 3 | gaBERT, ga-ELECTRA, Welsh-BERT |
| Celtic Speech | 6 | ABAIR, ÈIST, Macsen, Trawsgrifiwr |
| General | 5 | Gemma-3n, Nemotron-3, FunctionGemma |

### Formats

| Format | Backend | Port |
|--------|---------|------|
| GGUF | llama-swap | 8080 |
| MLX | mlx-omni-server | 10240 |
| safetensors | invokeai | 9090 |

## Fallback Chains

Automatic model fallback for reliability:

```yaml
vision: glm-4.6v-flash → qwen3-vl → moondream2
ocr: olmocr-2 → granite-docling
reasoning: nemotron-3-nano → gemma-3n
celtic_irish: qomhra-mistral → uccix → britllm
```

## Celtic Language Models

### Irish (Gaeilge)

| Model | Type | Size |
|-------|------|------|
| UCCIX-Llama2-13B | LLM | 13B |
| Qomhrá-Mistral-7B | LLM | 7B |
| gaBERT | Encoder | 110M |
| ABAIR | TTS/ASR | API |

### Welsh (Cymraeg)

| Model | Type | Size |
|-------|------|------|
| BritLLM-3B | LLM | 3B |
| Welsh-BERT | Encoder | 110M |
| Macsen | ASR | API |

### Scottish Gaelic (Gàidhlig)

| Model | Type | Status |
|-------|------|--------|
| BritLLM-3B | LLM | Available |
| ÈIST | ASR | Coming 2025 |

## Training

### Dataset Formats

```yaml
jsonl_chat:    # LLM fine-tuning
jsonl_vision:  # VLM fine-tuning
coco:          # Segmentation
vidore:        # Document retrieval
geotiff:       # Remote sensing
```

### Chat Templates

```yaml
gemma: "<start_of_turn>user\n{input}<end_of_turn>..."
qwen: "<|im_start|>user\n{input}<|im_end|>..."
nemotron: "<think>{reasoning}</think>{output}"
```

## Notebooks

70+ training notebooks in `notebooks/`:

- Vision model fine-tuning
- Celtic language training
- ColPali document retrieval
- Geospatial analysis

## Catalogs

- `catalog/models.yaml` - Model definitions
- `catalog/sources.yaml` - Dataset sources

---

## From: ML_STACK.md (leftover)

and make note of sources for docs and apis for the following resources:

nebius token factory $51
blaxel $430
modal $280
letta 25000 credits
confluent $400
huggingface pro, $50 credits
sidero omni 14 day trial
google cloud £200 credits (
	  https://ai.google.dev/gemini-api/docs/interactions?ua=chat and
	for gemini 3 pro + flash, 2.5 pro + flash 
	compute instances / kubernetes with sidero omni and anyscale $100
?)
z.ai’s coding plan pro (glm 4.6, glm4.6v mcp servers are useful for document processing:  https://docs.z.ai/devpack/mcp/vision-mcp-server and
  https://docs.z.ai/devpack/mcp/search-mcp-server and
  https://docs.z.ai/devpack/mcp/reader-mcp-server)
Claude code max x20
elevenlabs 210000
datadog pro 14 day trial
lancedb cloud $100
cloudflare r2 storage
planetscale postgres $5 plan
thundercompute $120
motherduck business 21 days free trial

hetzner cax41 32gb ram 320gb drive
oracle cloud free tier arm 2gb ram 200gb drive
macbook pro m4 max 48gb ram 1tb hard drive




and determine the best way to maximise our resource usage and develop the best project maximising our resource usage in the finetuning, pre or post training and use of api in agentic workflows using :

htr duchas.ie’s school collection and https://www.hiddenheritages.ai/en/s word segmentation matching to transcripts
sam-audio (for canuint.ie voice segmentation)
syllabus informing json format of fibo asset generation turned to usable 3d asset for educational software via sam3d-object
functiongemma tool calling in agent after training models to provide different irish-language functions (tts, htr)
gemma 3/3n and colpali series
qwen3-vl
GLM4.6V-flash



https://huggingface.co/unsloth/Nemotron-3-Nano-30B-A3B-GGUF
https://huggingface.co/unsloth/DeepSeek-OCR
https://huggingface.co/datasets/facebook/SA-FARI
https://huggingface.co/Aratako/T5Gemma-TTS-2b-2b
https://huggingface.co/datasets/allenai/bolmo_mix
https://huggingface.co/allenai/Bolmo-7B
https://huggingface.co/allenai/Bolmo-1B
https://huggingface.co/collections/allenai/molmo2-data
https://huggingface.co/allenai/Molmo2-4B
https://huggingface.co/briaai/FIBO

---

## From: New in llama.cpp_ Model Management.md (leftover)

[Back to Articles](https://huggingface.co/blog)

[Community Article](https://huggingface.co/blog/community) Published December 11, 2025

[llama.cpp server](https://github.com/ggml-org/llama.cpp/tree/master/tools/server) now ships with **router mode**, which lets you dynamically load, unload, and switch between multiple models without restarting.

> Reminder: llama.cpp server is a lightweight, OpenAI-compatible HTTP server for running LLMs locally.

This feature was a popular request to bring Ollama-style model management to llama.cpp. It uses a multi-process architecture where each model runs in its own process, so if one model crashes, others remain unaffected.

## Quick Start

Start the server in router mode by **not specifying a model**:

```bash
llama-server
```

This auto-discovers models from your llama.cpp cache (`LLAMA_CACHE` or `~/.cache/llama.cpp`). If you've previously downloaded models via `llama-server -hf user/model`, they'll be available automatically.

You can also point to a local directory of GGUF files:

```bash
llama-server --models-dir ./my-models
```

## Features

1. **Auto-discovery**: Scans your llama.cpp cache (default) or a custom `--models-dir` folder for GGUF files
2. **On-demand loading**: Models load automatically when first requested
3. **LRU eviction**: When you hit `--models-max` (default: 4), the least-recently-used model unloads
4. **Request routing**: The `model` field in your request determines which model handles it

## Examples

### Chat with a specific model

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ggml-org/gemma-3-4b-it-GGUF:Q4_K_M",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

On the first request, the server automatically loads the model into memory (loading time depends on model size). Subsequent requests to the same model are instant since it's already loaded.

### List available models

```bash
curl http://localhost:8080/models
```

Returns all discovered models with their status (`loaded`, `loading`, or `unloaded`).

### Manually load a model

```bash
curl -X POST http://localhost:8080/models/load \
  -H "Content-Type: application/json" \
  -d '{"model": "my-model.gguf"}'
```

### Unload a model to free VRAM

```bash
curl -X POST http://localhost:8080/models/unload \
  -H "Content-Type: application/json" \
  -d '{"model": "my-model.gguf"}'
```

## Key Options

| Flag | Description |
| --- | --- |
| `--models-dir PATH` | Directory containing your GGUF files |
| `--models-max N` | Max models loaded simultaneously (default: 4) |
| `--no-models-autoload` | Disable auto-loading; require explicit `/models/load` calls |

All model instances inherit settings from the router:

```bash
llama-server --models-dir ./models -c 8192 -ngl 99
```

All loaded models will use 8192 context and full GPU offload. You can also define per-model settings using [presets](https://github.com/ggml-org/llama.cpp/pull/17859):

```bash
llama-server --models-preset config.ini
```

```bash
[my-model]
model = /path/to/model.gguf
ctx-size = 65536
temp = 0.7
```

## Also available in the Web UI

The [built-in web UI](https://github.com/ggml-org/llama.cpp/tree/master/tools/server/webui) also supports model switching. Just select a model from the dropdown and it loads automatically.

## Join the Conversation

We hope this feature makes it easier to A/B test different model versions, run multi-tenant deployments, or simply switch models during development without restarting the server.

Have questions or feedback? Drop a comment below or open an issue on [GitHub](https://github.com/ggml-org/llama.cpp/issues).

### Community

[bukit](https://huggingface.co/bukit)

Mmproj support?

- [![](https://huggingface.co/avatars/f7540cf1ef2370e402df13b3587384f9.svg)](https://huggingface.co/grailfinder "grailfinder")
·

[sbeltz](https://huggingface.co/sbeltz)

Supported via presets.ini, where you can specify the mmproj (and other long and short arguments) per model.

[sbeltz](https://huggingface.co/sbeltz)

Awesome new feature! Can model selection be done on something other than requested model name? Like maybe specify the ranking in presets.ini, and then the highest ranked model that can satisfy the request will be the default. So maybe one model is best for short context, another (or the same with other settings) for when the context gets too long, and another when image input is required.

[xbruce22](https://huggingface.co/xbruce22)

This is good addition, Thank you.

[etemiz](https://huggingface.co/etemiz)

•

[edited 1 day ago](https://huggingface.co/blog/ggml-org/#693c57ea6107ec9c17bb2879 "Edited 4 times by etemiz")

what is the best way to get <think> </think> and the tokens in between? openAI library is removing them.. i want to run llama-server in console and talk to it using a python library that does not remove the thinking tokens.

i checked the llama-cpp-python but it does not have that.

[razvanab](https://huggingface.co/razvanab)

Now I can use llama.cpp all the time. A big thank you to the devs.

[sbeltz](https://huggingface.co/sbeltz)

Is there currently a way to have a "default" model if the request doesn't specify? Could be the currently loaded model or a specific model. (Just noticed one of my apps broke because it's used to llama-server not requiring a model name.)
