# Meaisínfhoghlaim (The Brain)

This quadrant of the `cianfhoghlaim` stack is responsible for all artificial intelligence, semantic extraction, vector embeddings, and LLM orchestration.

## Core Architecture

### 1. BAML (Boundary AI Markup Language)
Instead of relying on brittle JSON prompt engineering, we use BAML to compile type-safe schema definitions for extracting complex educational entities (Learning Outcomes, Examiner Reports) from unstructured PDFs. 
*   **Location**: Extraction schemas are defined in the root `baml_src/` directory.

### 2. LLM Routing & Management (LiteLLM)
We centralize all calls to Anthropic, OpenAI, and Gemini using LiteLLM. 
*   **Deployment**: Hosted as part of the local `oideachais` Docker Compose stack.
*   **Specialized Models**: LiteLLM handles routing for distinct tasks, specifically utilizing:
    *   `gemma-2.0-flash` & `gemini-2.5-pro` for broad instruction-following.
    *   `colpali` and `glm4.6v` for vision-language tasks (e.g., parsing complex multi-column marking schemes from SEC).

### 3. Vector Embeddings (LanceDB & CocoIndex)
Once BAML extracts the structured data, `CocoIndex` orchestrates the chunking of the markdown and syncs the vector embeddings directly into `LanceDB`. 
*   **Integration**: CocoIndex flows are heavily utilized within the Dagster pipelines (see `oideachais/data_platform/dagster_defs`).

### 4. Temporal Knowledge Graph (Graphiti & Cognee)
Educational data is highly relational. A curriculum learning outcome often *Builds On* or is a *Prerequisite For* another. 
*   **Graphiti**: Maintains this temporal and episodic knowledge graph using Neo4j, far outperforming standard vector databases for complex curriculum reasoning.

## Security & Access
Agents executing tasks in this quadrant should leverage the `ai-engineer` persona profile (mapped in `.roomodes`) to gain the proper `baml` and `litellm` `.skills/` context. All API keys (`LLM_API_KEY`, `LANGFUSE_PUBLIC_KEY`) are dynamically injected at runtime via Infisical.
