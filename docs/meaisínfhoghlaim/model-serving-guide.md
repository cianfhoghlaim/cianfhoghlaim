# Model Serving & Inference on Apple Silicon & Local Hardware

**Merged From:**
- `models/llamacpp.md`, `models/mlx-lm.md`, `models/gguf.md`
- `models/Local macOS MLX_MPS LLM Workflow.md`, `models/Setting Up Local LLM Services on Mac.md`
- `models/LLM Serving with MLflow & Langfuse.md`, `models/llama.cpp-imlementation.md`
- `models/stack.md`, `models/model.md`, `models/llm.md`

---

## Table of Contents

1. [The Inference Stack: Overview](#inference-stack-overview)
2. [GGUF Format & Quantization](#gguf-format--quantization)
3. [llama.cpp: Universal Inference Engine](#llamacpp)
4. [MLX-LM: Apple Silicon Optimization](#mlx-lm)
5. [Llama-Swap: Dynamic Model Orchestration](#llama-swap)
6. [LiteLLM: Unified API Gateway](#litellm)
7. [Observability: MLflow + Langfuse](#observability)
8. [Hardware Reference](#hardware-reference)

---

## Inference Stack Overview

### The Three Backends

| Backend | Best For | Platform | Format |
|---------|----------|----------|--------|
| **llama.cpp** | Universal LLM inference, VLM with mmproj | All (CPU/CUDA/Metal/Vulkan) | GGUF |
| **MLX-LM** | Apple Silicon-optimized inference & fine-tuning | macOS (M1-M4) | MLX/NPZ |
| **PyTorch MPS** | Specialized models (DeepSeek-OCR, PaddleOCR-VL) | macOS (fallback) | safetensors |

### The Orchestration Layer

```text
Client (OpenAI SDK)
    │
    ▼
LiteLLM Gateway (port 4000)
    │
    ├──→ Llama-Swap (port 8081) → llama.cpp Server (GGUF models)
    ├──→ MLX Server (port 8082) → MLX models (Granite-Docling, Gemma-3)
    └──→ Cloud Fallback (Z.AI / OpenAI)
```

---

## GGUF Format & Quantization

**GGUF** (GPT-Generated Unified Format) is the standard file format for llama.cpp:
- Single-file design (tokenizer + weights + metadata in one binary)
- Memory-mapped execution for fast loading
- Supports quantization from 2-bit to 8-bit

### Quantization Selection Guide

| Type | Bits | 7B Model Size | Quality Impact | Use Case |
|------|------|---------------|----------------|----------|
| **F16** | 16 | ~14 GB | Baseline | Research, exact reproduction |
| **Q8_0** | 8 | ~7.5 GB | Negligible | High-precision production |
| **Q6_K** | 6 | ~5.5 GB | <0.1% | Balanced high-performance |
| **Q4_K_M** | 4 | ~4 GB | ~1-2% | **Recommended default** |
| **Q3_K_M** | 3 | ~3 GB | Moderate | Memory constrained |
| **Q2_K** | 2 | ~2 GB | Significant | Extreme edge cases |

**Always prefer K-quants** (Q4_K_M) over legacy formats (Q4_0).

### Converting to GGUF

```bash
# 1. Download model from HuggingFace
huggingface-cli download meta-llama/Llama-3.1-8B-Instruct --local-dir ./models/

# 2. Convert to F16 GGUF
python convert_hf_to_gguf.py ./models/ --outtype f16 --outfile model-f16.gguf

# 3. Quantize (recommended: Q4_K_M)
./llama-quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M
```

### Vision Models (VLM): The mmproj Pattern

VLMs require TWO GGUF files:
- `model.gguf` — The LLM weights (can be quantized)
- `mmproj.gguf` — The vision encoder/projector (keep at F16)

```bash
llama-server \
  -m Qwen3-VL-Instruct-Q4_K_M.gguf \
  --mmproj mmproj-Qwen3-VL-Instruct-f16.gguf \
  --port 8080 -ngl 99 -c 32768 -fa
```

---

## llama.cpp

Open-source C/C++ inference engine (85K+ GitHub stars) for running LLMs locally with minimal dependencies.

### Hardware-Specific Build

```bash
# CPU only
cmake -B build && cmake --build build --config Release

# CUDA (NVIDIA)
cmake -B build -DGGML_CUDA=ON && cmake --build build --config Release

# Metal (macOS - automatic)
cmake -B build && cmake --build build --config Release

# Vulkan (cross-platform)
cmake -B build -DGGML_VULKAN=ON && cmake --build build --config Release

# ROCm (AMD)
cmake -B build -DGGML_HIP=ON && cmake --build build --config Release
```

### Performance Optimization

**CPU Inference:**
- Use dual-channel/quad-channel RAM (single biggest factor)
- Thread count = physical cores only (never hyperthreads)
- Enable Flash Attention (`-fa`) — 5-10x faster prompt processing
- Memory lock (`--mlock`) prevents OS swapping

**GPU Inference:**
- Ensure model fits entirely in VRAM (`-ngl 999` for full offload)
- Reduce threads to 2-4 when using GPU
- KV cache quantization saves 30-60% VRAM (`--cache-type-k q8_0`)

### Production Server

```bash
llama-server \
  -m model-q4_k_m.gguf \
  --host 0.0.0.0 --port 8080 \
  --api-key $(cat /run/secrets/key) \
  -ngl 999 -fa -c 16384 \
  --parallel 4 --cont-batching
```

OpenAI-compatible API — use any OpenAI SDK client by pointing `base_url` to `http://localhost:8080/v1`.

### Expected Performance (8B Q4_K_M)

| Hardware | Tokens/s |
|----------|----------|
| Apple M1 Max | 25-30 |
| NVIDIA RTX 4090 | 100-120 |
| AMD 7950X CPU | 15-20 |

---

## MLX-LM

Apple Silicon-optimized framework using Unified Memory Architecture (UMA). Models share one memory pool between CPU and GPU.

### Quick Start

```bash
pip install mlx-lm

# Generate
mlx_lm.generate --model mlx-community/Llama-3.2-3B-Instruct-4bit \
  --prompt "Explain quantum computing" --max-tokens 200

# Interactive chat
mlx_lm.chat --model mlx-community/Mistral-7B-Instruct-v0.3-4bit

# OpenAI-compatible server
mlx_lm.server --model mlx-community/Llama-3.2-3B-Instruct-4bit --port 8080
```

### Memory Requirements

| RAM | Capable Models |
|-----|---------------|
| 8GB | 3B models, 7B with 4-bit |
| 16GB | 7-8B models comfortably |
| 32GB+ | 13-34B models |

### LoRA/QLoRA Fine-Tuning on MLX

```bash
# QLoRA with 4-bit base model (recommended)
mlx_lm.lora \
  --train \
  --model mlx-community/Mistral-7B-Instruct-v0.2-4bit \
  --data ./data \
  --batch-size 8 \
  --lora-layers 16 \
  --lora-rank 16 \
  --lora-alpha 32 \
  --learning-rate 1e-5 \
  --iters 2000 \
  --adapter-path ./adapters
```

### Prompt Caching (Multi-Turn)

```python
from mlx_lm.models.cache import make_prompt_cache

cache = make_prompt_cache(model)
response1 = generate(model, tokenizer, prompt1, prompt_cache=cache)
response2 = generate(model, tokenizer, prompt2, prompt_cache=cache)  # Uses cached context
```

### Popular MLX Models

```python
# Small (3B) - 8GB RAM
"mlx-community/Llama-3.2-3B-Instruct-4bit"
"mlx-community/Phi-3-mini-4k-instruct-4bit"

# Medium (7-8B) - 16GB RAM
"mlx-community/Mistral-7B-Instruct-v0.3-4bit"
"mlx-community/Llama-3.1-8B-Instruct-4bit"
"mlx-community/Qwen2.5-7B-Instruct-4bit"

# Large (13B+) - 32GB+ RAM
"mlx-community/Llama-2-13B-chat-4bit"
"mlx-community/Mixtral-8x7B-Instruct-v0.1-4bit"
```

---

## Llama-Swap

Dynamic model orchestration — loads/unloads models on demand to maximize limited VRAM.

### How It Works

1. Intercepts requests for specific model names
2. Checks if requested model is already loaded
3. If not, gracefully stops the current model, launches the new one
4. Waits for health check, then proxies the request

### Configuration

```yaml
# swap_config.yaml
healthCheckTimeout: 300
startPort: 10000

models:
  qwen-coder:
    cmd: |
      /opt/llama.cpp/llama-server \
        -m /models/Qwen2.5-Coder-32B-Instruct-Q4_K_M.gguf \
        --port ${PORT} -ngl 99 -c 16384

  olm-ocr:
    cmd: |
      python -m mlx_openai_server \
        --model-path mlx-community/olmOCR-2-7B-MLX-4bit \
        --port ${PORT} --model-type vlm
```

Llama-Swap can manage ANY executable that listens on `${PORT}` — llama.cpp, MLX server, or custom FastAPI services.

---

## LiteLLM

Unified API gateway normalizing all backends to OpenAI-compatible format.

### Gateway Configuration

```yaml
model_list:
  # Local GGUF via Llama-Swap
  - model_name: gpt-oss
    litellm_params:
      model: openai/gpt-oss-120b
      api_base: http://127.0.0.1:8081/v1
      api_key: sk-local
      timeout: 600  # Large models need extra load time

  # Local MLX
  - model_name: granite-docling
    litellm_params:
      model: openai/ibm-granite/granite-docling-258M-mlx
      api_base: http://127.0.0.1:8082/v1

  # Cloud fallback
  - model_name: glm-4-plus
    litellm_params:
      model: zai/glm-4.6v

  # Tiered routing with fallback
  - model_group: coding-assistant
    models: [qwen-coder, gpt-4o-mini]  # Try local first, fall back to cloud
    routing_strategy: priority
```

### Fallback & Resilience

```yaml
model_list:
  - model_name: coding-assistant
    litellm_params:
      model: openai/qwen-coder
      api_base: "http://localhost:8081/v1"
    fallback: "gpt-4o-mini"  # Auto-reroute on failure
```

---

## Observability

### Langfuse + LiteLLM

```yaml
litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]

environment_variables:
  LANGFUSE_PUBLIC_KEY: os.environ/LANGFUSE_PUBLIC_KEY
  LANGFUSE_SECRET_KEY: os.environ/LANGFUSE_SECRET_KEY
```

### MLflow Integration

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.litellm.autolog()  # Automatic prompt/config/output capture
```

---

## Hardware Reference

### Memory by Model Size (Q4_K_M quantization)

| Model Size | RAM Required | Example GPUs |
|-----------|-------------|-------------|
| 1-3B | 4-8 GB | M1, RTX 3060, T4 |
| 7-8B | 8-16 GB | M1 Pro, RTX 3070, A10 |
| 13-34B | 16-32 GB | M1 Max, RTX 3090/4090 |
| 70-72B | 32-48 GB | M2 Ultra, dual RTX 3090, A100 |
| 120B+ | 64-96 GB | M3 Max 128GB, dual H100 |

### Apple Silicon Reference

| Device | RAM | Max Model (Q4) |
|--------|-----|----------------|
| MacBook Air M1/M2 | 8-16 GB | 7B |
| MacBook Pro M1 Pro | 16-32 GB | 13-34B |
| MacBook Pro M3 Max | 36-128 GB | 70-120B |
| Mac Studio M2 Ultra | 64-192 GB | 120B+ |

### Cloud GPU Options

| Provider | GPUs | Notes |
|----------|------|-------|
| **RunPod** | H100, A100, A10, L4 | Good availability |
| **Lambda Labs** | H100, A100 | Research-focused |
| **Vast.ai** | Various | Marketplace pricing |
| **Google Colab Pro+** | A100 | $50/month |
