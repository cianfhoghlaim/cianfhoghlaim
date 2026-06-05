# BAML — Type-Safe LLM Extraction DSL

## Overview

BAML (Basically A Made-up Language) is a domain-specific language and Python/TypeScript SDK for defining structured LLM extraction schemas with compile-time type checking. It generates type-safe client code in Python or TypeScript from `.baml` schema files, ensuring that LLM outputs conform to specified data models. Created by Boundary (now part of Dagster Labs).

## Why This Matters for Kings' College Galway

BAML is the extraction layer for the entire curriculum pipeline. Every learning outcome, exam question, marking scheme component, and image generation prompt is extracted from unstructured syllabus PDFs using BAML schemas. The type-safe approach means a BAML compiler catches schema errors before they reach production — if the `LearningOutcome` model requires a `difficulty` field but the BAML prompt doesn't extract it, the compiler fails at build time. This is essential for educational content where incorrect extractions could produce wrong study materials.

## Key Features

- **Type-safe extraction** — Compile-time validation of LLM output schemas
- **Dual-language** — Generate Python and TypeScript clients from the same `.baml` file
- **Prompt-as-code** — Prompts are version-controlled in `.baml` files
- **Function composition** — Compose extraction functions into pipelines
- **LiteLLM integration** — All BAML functions call through the LiteLLM gateway

## Installation

```bash
uv add baml-py
# CLI:
bun add @boundaryml/baml
```

## Integration with Our Stack

BAML schemas live in `oideachais/baml_src/`. The `baml-cli generate` command produces Python and TypeScript clients. All BAML functions use `client LiteLLM` to call through the LiteLLM gateway's aliases (`extract`, `vision`, `image`). Dagster assets invoke BAML functions to extract structured data from curriculum documents.

## Upstream

- **Repository**: <https://github.com/BoundaryML/baml>
- **Documentation**: <https://docs.boundaryml.com>
- **Latest**: Active development — Python codegen improvements, prompt playground, testing framework

## Screenshot

BAML's VSCode extension provides syntax highlighting, autocomplete, and type checking for `.baml` files. The `baml-cli generate` command outputs type-safe Python/TypeScript code. The BAML playground shows input/output previews for testing extraction functions against sample documents.
