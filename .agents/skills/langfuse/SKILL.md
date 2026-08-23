---
name: langfuse
description: Expert assistance for LLM observability with Langfuse (Python SDK v4, JS/TS SDK v5 on platform v3.125+). Use when users need OpenTelemetry-native tracing, prompt management, evaluation, scores API v3, or experiments.

## What's new in 2026-08/09

This skill was refreshed as part of the 2026-08-23 omnibus skill refresh
(per the  change). Key
updates:

- **2026-08 tooling**: aligned with the latest versions of upstream
  libraries (per the dev-tooling version-pinning change)
- **2026-08 patterns**: documented new features surfaced via the
  Phase 3 (surfaces round) refactor
- **Cross-references**: linked to adjacent skills (per the AGENTS.md
  dispatch matrix)

See the linked spec changes for full details.

---

# Langfuse - OpenTelemetry-Native LLM Observability Platform

**Version:** Python SDK v4.12.0 / JS SDK v5.9.0 / Platform v3.125+ | **Last Updated:** 2026-06-29

## Overview

Langfuse is an open-source LLM observability platform:

- **Tracing**: Capture and analyze LLM calls
- **Prompt Management**: Version and manage prompts
- **A/B Testing**: Compare different prompts and models
- **Analytics**: Deep insights into LLM performance
- **Multi-Model Support**: Works with all major LLM providers

**Documentation**: https://langfuse.com/docs

## When to Use This Skill

Activate when users need:

- "Monitor LLM performance"
- "Manage and version prompts"
- "A/B test different prompts"
- "Debug LLM applications"
- "Track LLM costs and latency"

## Core Concepts

### 1. Basic Setup

```python
pip install langfuse
```

```python
from langfuse import Langfuse

# Initialize client
langfuse = Langfuse(
    public_key="pk-lf-...",
    secret_key="sk-lf-...",
    host="https://cloud.langfuse.com"  # or your self-hosted instance
)
```

### 2. Tracing LLM Calls

```python
from langfuse.decorators import observe

@observe()
def generate_response(query: str):
    """Trace a simple function."""
    return llm.generate(query)

# With explicit trace creation
trace = langfuse.trace(
    name="chat_completions",
    metadata={"user_id": "123"}
)

generation = trace.generation(
    name="gpt-4-response",
    model="gpt-4",
    input={"query": "What is AI?"},
    output={"response": "AI is..."},
    usage={"prompt_tokens": 10, "completion_tokens": 20}
)
```

### 3. Prompt Management

```python
# Create a prompt
prompt = langfuse.create_prompt(
    name="curriculum_tutor",
    prompt="You are a helpful tutor for {subject}. Help students learn {topic}.",
    config={"temperature": 0.7, "max_tokens": 500}
)

# Get prompt with variables
compiled = langfuse.get_prompt("curriculum_tutor").compile(
    subject="Mathematics",
    topic="algebra"
)

# Version prompts
prompt_v2 = langfuse.create_prompt(
    name="curriculum_tutor",
    version=2,
    prompt="You are an expert tutor in {subject}. Guide students through {topic} with examples.",
    config={"temperature": 0.5, "max_tokens": 700}
)
```

### 4. A/B Testing

```python
# Create experiment
experiment = langfuse.create_experiment(
    name="prompt_optimization",
    description="Testing different prompt styles"
)

# Run with different variants
@observe(name="variant_a")
def run_variant_a(query: str):
    return llm.generate(f"Answer this: {query}")

@observe(name="variant_b")
def run_variant_b(query: str):
    return llm.generate(f"Please provide a detailed answer to: {query}")

# Compare results
result_a = run_variant_a("What is algebra?")
result_b = run_variant_b("What is algebra?")
```

### 5. Session Tracking

```python
# Create session
session = langfuse.create_session(
    user_id="user_123",
    metadata={"subject": "Mathematics", "grade": "Junior Cycle"}
)

# Add traces to session
trace1 = session.trace(name="question_1")
trace2 = session.trace(name="question_2")

# Analyze session performance
sessions = langfuse.fetch_sessions(user_id="user_123")
```

## Advanced Features

### Evaluation Scoring

```python
from langfuse import Score

# Add manual scores
generation.score(
    name="relevance",
    value=0.9,
    comment="Highly relevant to user query"
)

# Add automated scores
generation.score(
    name="latency",
    value=generation.end_time - generation.start_time,
    comment="Response time in seconds"
)
```

### User Feedback

```python
# Capture user feedback
generation.score(
    name="user_feedback",
    value=1,  # 1-5 scale
    comment="Helpful response"
)

# Track thumbs up/down
generation.score(
    name="thumbs_up",
    value=True,
    comment="User liked the response"
)
```

### Cost Tracking

```python
# Langfuse automatically tracks costs
# Configure pricing
langfuse.configure_costs(
    model_pricing={
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    }
)

# Query costs
costs = langfuse.fetch_costs()
```

## Best Practices

### Tracing

1. **Granularity**: Add traces at appropriate levels (session, trace, generation)
2. **Metadata**: Include relevant metadata for filtering and analysis
3. **Context**: Capture user context and environment information

### Prompt Management

1. **Versioning**: Always version prompts when making changes
2. **Variables**: Use clear variable names in prompts
3. **Testing**: A/B test prompts before production deployment

### Analytics

1. **Regular Review**: Regularly review traces and scores
2. **Alerts**: Set up alerts for unusual patterns
3. **Optimization**: Use data to optimize prompts and models

## Configuration

### Environment Variables

```bash
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Self-Hosting

```bash
# Docker
docker run -p 3000:3000 \
  -e LANGFUSE_SALT=your-salt \
  -e DATABASE_URL=postgresql://... \
  langfuse/langfuse

# Kubernetes
helm repo add langfuse https://langfuse.github.io/charts
helm install langfuse langfuse/langfuse
```

## Installation

```bash
pip install langfuse
# or
npm install langfuse
```

## Project Integration

### Use Cases

| Scenario | Pattern |
|----------|---------|
| Agent Monitoring | Trace all agent interactions |
| Prompt Optimization | A/B test prompt variants |
| Cost Analysis | Track LLM costs by model |
| Quality Assurance | Score and evaluate responses |

### Related Skills

- [`ragas`](.skills/ragas/SKILL.md) - RAG evaluation framework
- [`agno`](.skills/agno/SKILL.md) - Agent framework with observability
- [`google-adk`](.skills/google-adk/SKILL.md) - Google's agent framework

## Live version (verified 2026-06-29, Agent 90)

- **Python SDK v4.12.0** + **JS/TS SDK v5.9.0** on **Platform v3.125+**
- The v3 release is **OTEL-native** (no more `langfuse.trace(...).generation(...)` builder)
- New `get_client()` singleton; v4 prefers env-var auth over `Langfuse(public_key=...)` constructor
- `start_as_current_observation(as_type="generation"|"agent"|"tool"|"event")` is the v3 pattern (replaces `@observe()` with implicit type)
- Scores API v3 — typed `value` (NUMERIC/BOOLEAN/CATEGORICAL/TEXT)
- LiteLLM integration: `callbacks: ["langfuse_otel"]` + `LANGFUSE_OTEL_HOST` (was `callbacks: ["langfuse"]` + `LANGFUSE_HOST`)
- JS multi-package install: `@langfuse/tracing`, `@langfuse/otel`, `@langfuse/client`, `@langfuse/browser`, `@langfuse/openai`, `@langfuse/langchain`
- Frontend scores: `@langfuse/browser` (2026-06-18, public-key only)
- Self-host: must pin to `v3.125.0+` for Python SDK v4

## Anti-patterns (v3/v4)

1. Direct `Langfuse(public_key=..., host=...)` constructor → v4 prefers `get_client()` + env vars.
2. `openai.langfuse_public_key = "pk-lf-..."` setattr → removed in v4.
3. `callbacks: ["langfuse"]` (LiteLLM) → replaced by `callbacks: ["langfuse_otel"]`.
4. `langfuse.score(...)` with float `value` only → v3 typed value.
5. `@observe()` without explicit `as_type=` → v3 prefers context-manager.
6. `langfuse.create_experiment(...)` → replaced by `run_experiment()` + Datasets API.
7. `langfuse.fetch_sessions(...)` → replaced by `/api/public/v2/observations` + `query-via-sdk` (2026-05-15).
8. Self-host `langfuse/langfuse:latest` → must pin to **v3.125.0+** for Python SDK v4.
9. Wrapping the whole OpenAI client with `@observe()` → v3 has dedicated `from langfuse.openai import openai` drop-in.
10. Calling `langfuse.flush()` inside `@observe()` body → v3 flush is global + automatic.
