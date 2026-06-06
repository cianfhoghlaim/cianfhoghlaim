# Pydantic AI — Agent Framework with Structured Validation

## Overview

Pydantic AI is an agent framework built by the creators of Pydantic that combines structured data validation with LLM-powered agent logic. It lets you define agents whose inputs and outputs are validated Pydantic models — ensuring type safety throughout the agent lifecycle. Supports function calling, tool integration, and streaming responses.

## Why This Matters for Kings' College Galway

The curriculum extraction pipeline's core requirement is structured, validated output. When an agent extracts a learning outcome from a syllabus, the output must conform to the `LearningOutcome` Pydantic model — with validated fields for subject, cycle, difficulty, language, and prerequisite IDs. Pydantic AI ensures this validation is built into the agent definition itself, not bolted on as post-processing. Combined with BAML's compile-time type checking, this provides end-to-end type safety from LLM output through to the database.

## Key Features

- **Pydantic validation** — Agent inputs/outputs are type-checked Pydantic models
- **Function calling** — Agents define typed tool functions
- **Streaming** — Stream partial responses with incremental validation
- **Multi-model** — Support for OpenAI, Anthropic, Gemini, and local models
- **Dependency injection** — Injectable services and configuration

## Installation

```bash
uv add pydantic-ai
```

## Integration with Our Stack

Pydantic AI agents are used alongside BAML for structured extraction. The Pydantic models defined for curriculum data (in `oideachais/models/`) are shared between BAML schemas, Pydantic AI agents, and the Dagster asset graph. Logfire provides tracing for Pydantic model validation within agent runs.

## Upstream

- **Repository**: <https://github.com/pydantic/pydantic-ai>
- **Documentation**: <https://ai.pydantic.dev>
- **Latest**: Active development (2025) — streaming improvements, tool definition v2, Logfire integration

## Screenshot

Pydantic AI is a programmatic framework. Validation results appear in Python tracebacks with precise field-level error messages. The Logfire dashboard shows structured traces of agent runs with Pydantic model validation events highlighted. The `.agents/skills/pydantic/` skill documents Pydantic v2 patterns.
