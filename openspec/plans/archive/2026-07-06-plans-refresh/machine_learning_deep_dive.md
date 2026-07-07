---
title: 'Machine Learning Deep Dive'
status: research
supersedes: []
superseded_by: [openspec/specs/oideachais-pipeline/spec.md, openspec/specs/data-pipeline/spec.md]
last_touched: 2026-06-13
---

# Machine Learning & Agent Layers Deep Dive

This document details the Machine Learning and Agent Development Kit (ADK) pipelines within the `education` workspace, specifically focusing on how models are orchestrated, OCR capabilities, BAML standardization, and the ADK/MCP agent layer.

## 1. Machine Learning Pipelines & AI Routing

The `education/machine_learning` directory contains the foundational model routing and OCR pipelines for the system.

### AI Model Routing & Fallbacks
The system relies on an intelligent LLM Router (`education/machine_learning/pipelines/llm_router.py`) built around the `litellm` interface. It provides:
- **Circuit Breakers**: Monitors failure rates for providers and automatically opens the circuit if a provider goes down.
- **Cost & Priority Awareness**: Routes requests based on defined priorities and tracks token usage. 
- **Capability Matching**: Models are tagged with capabilities (e.g., `IRISH_LANGUAGE`, `VISION`, `FUNCTION_CALLING`, `TEXT_GENERATION`).

**Core Providers/Models:**
- **Anthropic (`claude-sonnet-4-20250514`)**: Priority 10. Used for vision, reasoning, and complex extraction.
- **HuggingFace Irish Provider (`UCCIX-Llama2-13B-Instruct`)**: Priority 8. Free tier custom Irish language model.
- **OpenAI (`gpt-4o`)**: Priority 5. Fallback for reasoning and vision.
- **Gemini (`gemini-1.5-flash`)**: Priority 3. High context and cheap fallback.

### OCR & Vision Pipelines
The OCR pipeline (`education/machine_learning/ocr/model_registry.py` and `vision_comparison.py`) handles complex document understanding (like handwriting, math formulas, and Gaeilge text with fadas).
- **Model Registry**: Centralizes backend support across `MLX`, `Transformers`, `LiteLLM`, and `Ollama`.
- **Key OCR Models**:
  - `olmOCR-2-7B`: Best for structured documents, tables, and LaTeX.
  - `Qwen2.5-VL-7B` (and MLX variant): Grounding, reasoning, and multilingual support.
  - `DeepSeek-OCR`: Optimized for math and compressed documents.
  - `Granite-Docling`: Extracts DocTags for document structure.
  - `UCCIX-Llama2-13B`: Fine-tuned specifically for Gaelic OCR and processing.
- **Vision Comparison Tooling**: An async benchmark suite (`vision_comparison.py`) allows parallel evaluation of multiple vision models against specific prompts (e.g., standard layout, tables only, Irish fadas, math equations).

## 2. BAML for Outcome Standardization

BAML is a critical piece of the data engineering and ML pipeline for enforcing type-safe, structured extraction from unorganized curriculum text and exam papers.

- **Curriculum Parsing**: In `cocoindex_flows/curriculum_specification_extraction.py`, BAML acts as the primary validation layer. It parses raw DuckDB pages into strict `CurriculumSpecification` models, catching `ExamPaperStructure`, `MarkingScheme`, and `ExaminerReportInsights`.
- **Relationship Graphs**: In `cocoindex_flows/learning_outcome_graph.py`, BAML is used to enforce `LearningOutcomeRelation` extractions, ensuring that semantic links between English and Irish curriculum standards match specific ontology constraints.
- **Resilience**: The extractors lazy-load the BAML client. If schema validation fails or BAML is unavailable, the pipeline falls back to standard LLM JSON extraction using `claude-3-5-sonnet-20241022` or `gemini-1.5-flash` with robust fallback parsing.

## 3. The ADK (Agent Development Kit) & MCP Servers

The `education/adk` directory builds an orchestrator layer on top of the base ML routing. The primary component is the `MCPCurriculumAgent` (`education/adk/mcp_curriculum_agent.py`).

### Agent Orchestration
The ADK implements a multi-step research planner:
1. **Plan Generation**: The agent evaluates a query (e.g., "Compare Irish and Welsh primary maths curriculums") and builds a dynamic `ResearchPlan`.
2. **Execution**: The plan uses MCP Tools to iteratively gather and synthesize information.
3. **Cross-Nation Comparisons**: Built-in support for scaling queries across predefined regions (`ireland`, `scotland`, `wales`, `england`, `northern_ireland`).

### MCP Servers
The ADK delegates specialized tasks to Model Context Protocol (MCP) servers:
- **`chunkhound`**: Handles localized semantic code/document search with MVCC. Retrieves indexed curriculum chunks and scores them by relevance.
- **`zai-mcp-server`**: Executes visual reasoning (delegated back to the OCR models). Crucial for interpreting curriculum diagrams, extracting layout structures, or analyzing handwritten examiner notes.
- **`cognee-mcp`**: Acts as the Knowledge Graph memory, storing and retrieving entities related to educational topics.
- **`firecrawl-mcp`**: A web scraping tool to extract and format live curriculum website data into Markdown. 
- **`lancedb`**: The underlying Vector DB for dense embedding retrieval.

## Summary

The `education` layer is highly modular. The **ML Pipeline** provides raw capabilities (routing, circuit-breaking, and specialized Gaelic OCR), **BAML** enforces strict schemas over the unstructured data these models produce, and the **ADK/MCP Agent** orchestrates these tools into a unified system that can intelligently scrape, index, parse, and compare curriculums internationally.

---

**Archived 2026-07-06** — moved from `openspec/plans/` to `openspec/plans/archive/2026-07-06-plans-refresh/` by the `2026-07-06-drift-cleanup-and-v4-alignment` change. The content of this plan has been absorbed into the canonical specs listed in the frontmatter `superseded_by` field (refreshed to point at post-v4 spec names).
