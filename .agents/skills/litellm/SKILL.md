---
name: litellm
description: Expert assistance for unified LLM access with LiteLLM v1.97 (per-model routing groups, cosign-verified Docker, MCP Gateway GA, OAuth 2.0 v2, DCR, Rust-based /v1/messages, tool-result guardrails, OpenTelemetry v2 metrics, vector stores, workflows, providers incl. OpenAI / Anthropic / Azure AI / Bedrock / DeepSeek / xAI / Gemini / ModelScope / LibertAI / Parasail / Pinstripes / TinyFish / FastCRW).
---

# LiteLLM - Unified LLM Interface

**Version:** 1.97.0 | **Last Updated:** 2026-08-21
**Live evidence**: PyPI `litellm==1.97.0` (2026-08-21); `ghcr.io/berriai/litellm-database:v1.97.0` pinned in `bonneagar/stacks/litellm/compose.yaml` per `openspec/changes/2026-08-21-litellm-1.91-to-1.97-and-mcp-oauth-2.0-v1/`.

## What's new in v1.97 (the upgrade)

The bump from v1.91.0 → v1.97.0 is per `2026-08-21-litellm-1.91-to-1.97-and-mcp-oauth-2.0-v1`. Highlights:

- **MCP Gateway GA** (v1.85): the `/v1/mcp` endpoint is now stable. Expose MCP servers through the proxy.
- **OAuth 2.0 v2** (v1.91): the v2 auth resolver replaces custom auth code. Hermes no longer needs its own `--auth` flag.
- **DCR** (v1.95): Dynamic Client Registration support for MCP-OAuth clients.
- **Rust `/v1/messages`** (v1.95): the Rust-based endpoint (used by Claude Code + Hermes). Routed via Pangolin `/v1/messages` path.
- **Tool-result guardrails** (v1.97): safety hooks around MCP tool invocations.

## 0. Versioning & cosign verification (v1.84.0+)

Starting with v1.84.0 LiteLLM follows PEP 440. The `-stable` suffix is gone.
Both `litellm:1.97.0` and `litellm:v1.97.0` resolve to the same image.
All Docker images are cosign-signed with the key from commit `0112e53`:

```bash
cosign verify \
  --key https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub \
  ghcr.io/berriai/litellm-database:v1.97.0
```

## Overview

LiteLLM provides a unified interface for 100+ LLM providers:

- **Unified API**: OpenAI-compatible interface for all providers
- **Fallbacks**: Automatic model failover and retries
- **Load Balancing**: Distribute requests across deployments
- **Cost Tracking**: Monitor and control LLM spending
- **Proxy Server**: Deploy as a gateway for your organization

**Documentation**: https://docs.litellm.ai

## When to Use This Skill

Activate when users need:

- "Call multiple LLM providers with one API"
- "Add fallback models for reliability"
- "Track LLM costs and usage"
- "Deploy an LLM proxy gateway"
- "Switch between providers without code changes"

## Core Concepts

### 1. Basic Usage

```python
from litellm import completion

# OpenAI
response = completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Anthropic
response = completion(
    model="claude-sonnet-4-20250514",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Google
response = completion(
    model="gemini/gemini-1.5-pro",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Access response
print(response.choices[0].message.content)
```

### 2. Model Naming Convention

```python
# Provider prefixes
"gpt-4o"                        # OpenAI (no prefix needed)
"claude-sonnet-4-20250514"                # Anthropic
"gemini/gemini-1.5-pro"         # Google
"bedrock/anthropic.claude-3"    # AWS Bedrock
"azure/gpt-4"                   # Azure OpenAI
"ollama/llama3.2"               # Ollama (local)
"together_ai/mistral-7b"        # Together AI
"replicate/meta/llama-2"        # Replicate
"huggingface/bigscience/bloom"  # Hugging Face
"openrouter/anthropic/claude"   # OpenRouter
"vertex_ai/gemini-pro"          # Google Vertex AI
"sagemaker/my-endpoint"         # AWS SageMaker
"cohere/command-r"              # Cohere
"deepseek/deepseek-chat"        # DeepSeek
```

### 3. Streaming

```python
from litellm import completion

# Streaming response
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a story"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 4. Async Support

```python
import asyncio
from litellm import acompletion

async def main():
    response = await acompletion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    return response.choices[0].message.content

result = asyncio.run(main())
```

### 5. Embeddings

```python
from litellm import embedding

# OpenAI embeddings
response = embedding(
    model="text-embedding-3-small",
    input=["Hello world", "Goodbye world"]
)

# Access embeddings
embeddings = [item["embedding"] for item in response.data]

# Other providers
response = embedding(model="cohere/embed-english-v3.0", input=["text"])
response = embedding(model="bedrock/amazon.titan-embed-text-v1", input=["text"])
```

### 6. Fallbacks

```python
from litellm import completion
import litellm

# Enable fallbacks
litellm.num_retries = 3

# Define fallback models
response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}],
    fallbacks=["claude-sonnet-4-20250514", "gemini/gemini-1.5-pro"]
)

# With context manager
from litellm import Router

router = Router(
    model_list=[
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "gpt-4o",
                "api_key": "sk-..."
            }
        },
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "claude-sonnet-4-20250514",
                "api_key": "sk-ant-..."
            }
        }
    ],
    fallbacks=[{"gpt-4": ["claude-sonnet-4-20250514"]}]
)

response = router.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### 7. Load Balancing

```python
from litellm import Router

router = Router(
    model_list=[
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "gpt-4o",
                "api_key": "key-1"
            }
        },
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "gpt-4o",
                "api_key": "key-2"
            }
        }
    ],
    routing_strategy="least-busy"  # or "round-robin", "latency-based-routing"
)

# Requests distributed across deployments
response = router.completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### 8. Cost Tracking

```python
from litellm import completion
import litellm

# Enable cost tracking
litellm.success_callback = ["langfuse"]  # or other callback

response = completion(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello"}]
)

# Access cost info
print(f"Prompt tokens: {response.usage.prompt_tokens}")
print(f"Completion tokens: {response.usage.completion_tokens}")
print(f"Total cost: ${litellm.completion_cost(response)}")
```

### 9. Local Inference with llama-swap

LiteLLM works **complementarily** with local inference tools like llama-swap:

- **llama-swap**: VRAM management and model hot-swapping for local inference
- **LiteLLM**: Unified API routing and observability across all compute sources

```
┌─────────────────────────────────────────────────────────────┐
│  Application Layer (Agno, LangChain, etc.)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  LiteLLM Proxy (Routing & Observability)                    │
│  - Unified API interface                                    │
│  - Cost tracking across all providers                       │
│  - Fallback chains & load balancing                         │
│  - Centralized logging to Langfuse                          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   Cloud APIs       llama-swap        Ollama
   (OpenAI,         (VRAM Mgmt)       (Simple
    Claude,              │             Local)
    Gemini)              │
                         ▼
                   llama.cpp server
                   (OpenAI-compatible)
```

#### llama-swap Configuration

llama-swap handles automatic model loading/unloading for memory-constrained hardware:

```yaml
# llama-swap config.yaml
models:
  qwen-7b:
    path: /models/qwen2.5-7b-instruct-q4_k_m.gguf
    n_gpu_layers: 35
    ctx_size: 8192

  llama-70b:
    path: /models/llama-3.3-70b-q4_k_m.gguf
    n_gpu_layers: 60
    ctx_size: 4096

# Only one model loaded at a time, auto-swap on request
max_loaded_models: 1
```

#### LiteLLM Proxy with llama-swap

```yaml
# LiteLLM config.yaml
model_list:
  # Cloud models (high capability, higher cost)
  - model_name: smart
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  # Local via llama-swap (zero cost, VRAM managed)
  - model_name: local-7b
    litellm_params:
      model: openai/qwen-7b
      api_base: http://localhost:8080/v1  # llama-swap endpoint
      api_key: "not-needed"

  - model_name: local-70b
    litellm_params:
      model: openai/llama-70b
      api_base: http://localhost:8080/v1
      api_key: "not-needed"

# Fallback: try local first, then cloud
router_settings:
  fallbacks:
    - local-7b: ["smart"]
```

#### Usage Pattern

```python
from openai import OpenAI

# Connect to LiteLLM proxy
client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="sk-your-master-key"
)

# Request routes through LiteLLM → llama-swap → llama.cpp
# Model hot-swapping handled automatically
response = client.chat.completions.create(
    model="local-7b",  # LiteLLM routes to llama-swap
    messages=[{"role": "user", "content": "Hello"}]
)
```

#### When to Use Each Layer

| Layer | Role | Best For |
|-------|------|----------|
| **llama-swap** | VRAM management | Multi-model local dev, memory constraints |
| **LiteLLM** | API routing | Unified interface, cost tracking, fallbacks |
| **Both together** | Full stack | Production with local + cloud hybrid |

## Proxy Server

### Quick Start

```bash
# Install
pip install 'litellm[proxy]'

# Start proxy
litellm --model gpt-4o --port 4000

# Or with config
litellm --config config.yaml
```

### Configuration (config.yaml)

```yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

  - model_name: gpt-4
    litellm_params:
      model: azure/gpt-4-deployment
      api_base: https://my-resource.openai.azure.com
      api_key: os.environ/AZURE_API_KEY

  - model_name: claude
    litellm_params:
      model: claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: local-model
    litellm_params:
      model: ollama/llama3.2
      api_base: http://localhost:11434

litellm_settings:
  drop_params: true
  num_retries: 3
  request_timeout: 60

router_settings:
  routing_strategy: least-busy
  num_retries: 3
  timeout: 30

general_settings:
  master_key: sk-your-master-key
  database_url: postgresql://user:pass@localhost/litellm

# Rate limiting
litellm_settings:
  max_budget: 100  # $100 max
  budget_duration: 1d  # per day
```

### Use Proxy

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:4000/v1",
    api_key="sk-your-master-key"
)

response = client.chat.completions.create(
    model="gpt-4",  # Routes to configured model
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Docker Deployment

```yaml
# docker-compose.yaml
version: '3.8'
services:
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=postgresql://postgres:postgres@db/litellm
    volumes:
      - ./config.yaml:/app/config.yaml
    command: ["--config", "/app/config.yaml"]

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=litellm
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Provider Configuration

### OpenAI
```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

response = completion(model="gpt-4o", messages=[...])
```

### Anthropic
```python
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

response = completion(model="claude-sonnet-4-20250514", messages=[...])
```

### Azure OpenAI
```python
os.environ["AZURE_API_KEY"] = "..."
os.environ["AZURE_API_BASE"] = "https://your-resource.openai.azure.com"
os.environ["AZURE_API_VERSION"] = "2024-02-15-preview"

response = completion(
    model="azure/your-deployment-name",
    messages=[...]
)
```

### AWS Bedrock
```python
os.environ["AWS_ACCESS_KEY_ID"] = "..."
os.environ["AWS_SECRET_ACCESS_KEY"] = "..."
os.environ["AWS_REGION_NAME"] = "us-east-1"

response = completion(
    model="bedrock/anthropic.claude-3-sonnet",
    messages=[...]
)
```

### Ollama (Local)
```python
response = completion(
    model="ollama/llama3.2",
    api_base="http://localhost:11434",
    messages=[...]
)
```

### Google Vertex AI
```python
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/credentials.json"
os.environ["VERTEXAI_PROJECT"] = "your-project"
os.environ["VERTEXAI_LOCATION"] = "us-central1"

response = completion(
    model="vertex_ai/gemini-pro",
    messages=[...]
)
```

## Callbacks and Observability

### Langfuse Integration

```python
import litellm

# Set callbacks
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]

# Configure Langfuse
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-..."
os.environ["LANGFUSE_SECRET_KEY"] = "sk-..."
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"

response = completion(model="gpt-4o", messages=[...])
```

### Custom Callbacks

```python
import litellm

def my_callback(kwargs, completion_response, start_time, end_time):
    print(f"Model: {kwargs['model']}")
    print(f"Response: {completion_response}")
    print(f"Duration: {end_time - start_time}")

litellm.success_callback = [my_callback]
```

## Common Patterns

### Multi-Provider Chat Application

```python
from litellm import completion, Router

router = Router(
    model_list=[
        {"model_name": "fast", "litellm_params": {"model": "gpt-4o-mini"}},
        {"model_name": "smart", "litellm_params": {"model": "gpt-4o"}},
        {"model_name": "cheap", "litellm_params": {"model": "ollama/llama3.2"}}
    ]
)

def chat(message: str, model_type: str = "fast"):
    return router.completion(
        model=model_type,
        messages=[{"role": "user", "content": message}]
    ).choices[0].message.content
```

### Rate Limited Requests

```python
from litellm import Router

router = Router(
    model_list=[...],
    redis_host="localhost",
    redis_port=6379,
    cache_responses=True
)

# Requests are rate limited and cached
response = router.completion(model="gpt-4", messages=[...])
```

### Budget Management

```yaml
# config.yaml for proxy
litellm_settings:
  max_budget: 1000  # $1000 total
  budget_duration: 30d  # per month

user_settings:
  - user_id: team-a
    max_budget: 100
    budget_duration: 1d
  - user_id: team-b
    max_budget: 200
    budget_duration: 1d
```

## Best Practices

1. **Use Router for Production**: Better fallback and load balancing
2. **Enable Retries**: Set `num_retries=3` for reliability
3. **Track Costs**: Enable callbacks for cost monitoring
4. **Use Proxy for Teams**: Centralized key management and rate limiting
5. **Cache Responses**: Reduce costs with response caching

## Troubleshooting

### API Key Issues
- Verify environment variable names match provider
- Check key permissions and quotas
- Use `litellm.set_verbose = True` for debugging

### Timeout Errors
- Increase `request_timeout` parameter
- Use shorter prompts or streaming
- Check network connectivity

### Model Not Found
- Verify model name matches provider's naming
- Check if model is available in your region
- Ensure provider prefix is correct

## Resources

- **Documentation**: https://docs.litellm.ai
- **GitHub**: https://github.com/BerriAI/litellm
- **Supported Models**: https://docs.litellm.ai/docs/providers
- **Proxy Docs**: https://docs.litellm.ai/docs/proxy

## Recent additions (post 2025-01)

| Version | What changed | Where to apply |
|:--|:--|:--|
| 1.84.0  | PEP 440 + cosign-signed Docker | `pip install litellm==1.84.0`; `cosign verify` against commit `0112e53` |
| 1.84.0  | `router_settings.routing_groups` (per-model strategies) | `router_settings.routing_groups: [{group_name, models, routing_strategy}]` |
| 1.84.0  | Pass-through endpoints default to `auth: true` | `auth: false` on public webhook entries |
| 1.84.0  | Master-key alias `litellm_proxy_master_key` | Update spend-log + Prometheus filters |
| 1.85.0  | OpenAI Realtime GA + `gpt-realtime-2` pricing | `POST /openai/v1/realtime` |
| 1.85.0  | NVIDIA Riva STT provider | `audio_transcription` |
| 1.86.0  | OTel-standard server spans + weighted-routing failover | proxy telemetry |
| 1.87.0  | MCP UI for OAuth servers; Prometheus user budget metrics | UI / `/metrics` |
| 1.88.0  | Claude Opus 4.8; MCP access-group authorization | `claude-opus-4.8`; MCP gates |
| 1.89.0  | Claude Fable 5; A2A agent providers | `claude-fable-5`; A2A provider routes |
| 1.90.0  | 6 new providers (ModelScope, LibertAI, Parasail, Pinstripes, TinyFish, FastCRW) | `<provider>/...` prefix |
| 1.90.0  | OpenTelemetry v2 metrics parity (`gen_ai.client.*`) | `litellm.observability.opentelemetry_integration` |
