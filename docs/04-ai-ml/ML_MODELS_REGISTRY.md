---
title: 'Meaisínfhoghlaim - ML Models'
domain: 'ai_ml'
status: 'stable'
description: 'Machine learning model registry, training notebooks, and inference backends.'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/ML_MODELS_REGISTRY.md
ccc_query_hints:
  - meaisínfhoghlaim - ml models
truth: partial

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
