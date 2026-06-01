---
name: langfuse
description: Expert assistance for LLM observability with Langfuse. Use when users need LLM monitoring, prompt management, A/B testing, or trace-based analytics.
---

# Langfuse - LLM Observability Platform

**Version:** >=2.0.0 | **Last Updated:** 2025-04

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
