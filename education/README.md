# Oideachais: Cross-Border Celtic Education Platform

Oideachais is an advanced, AI-driven educational data platform standardizing curriculums across the British Isles. It fundamentally aligns the English (GCSE, A-Level) and Irish (Junior Cycle, Senior Cycle) educational frameworks through unified, semantically-searchable vectors.

This repository serves as the central orchestrator for scraping, structuring, embedding, and visualizing the educational ecosystems.

---

## 🏗️ Architecture & Core Components

Oideachais relies on a robust open-source stack spanning data engineering, machine learning, and reactive frontends. 

### 1. Data Engineering & ELT (`dlt_sources` & `dagster_defs`)
The project extracts raw educational data using **dlt (data load tool)**, orchestrated seamlessly by **Dagster**.
*   **English Standardization:** Dagster targets gov.uk, AQA, Edexcel, and OCR, parsing Key Stages 1-5 into a rigid `CrossNationCurriculumSpec` using BAML.
*   **Irish Standardization:** Highly concurrent `dlt` pipelines scrape curriculumonline.ie, ncca.ie, and examinations.ie, normalizing data into the `CurriculumDocument` Pydantic schema.
*   **The Power of `dlt`:** `dlt` acts as the vital bridge, converting scraped Firecrawl data into strictly typed DuckDB tables through its declarative Python pipelines.

### 2. Infrastructure & Storage (`infrastructure/docker`)
The backend is a unified "Lakehouse" architecture optimized for sovereign, zero-egress data processing.
*   **DuckLake & Lakekeeper:** DuckDB serves as the core federated query engine, routing through DuckLake on PlanetScale for SQL catalog management, and Lakekeeper for standard Iceberg cataloging.
*   **LanceDB:** We register Lance namespaces natively to manage our dense vector embeddings (BGE-M3) for semantic cross-curriculum search.
*   **Garage & R2:** Garage S3 on Hetzner provides cheap local storage for intermediate computation, while Cloudflare R2 provides the global distribution tier.

### 3. Machine Learning & Agents (`machine_learning` & `adk`)
AI agents sit natively within the pipeline to structure unstructured PDFs and provide dynamic user interaction.
*   **OCR & Vision:** We utilize top-tier models like `Qwen2.5-VL-7B` and `olmOCR-2-7B` to safely parse complex Irish language elements (fadas) and math equations from raw Exam Papers.
*   **AI Routing:** A `litellm` router dynamically shifts workloads between local models (`UCCIX-Llama2-13B-Instruct` for Gaelic), Anthropic, and Gemini (leveraging our hackathon deployments).
*   **ADK & MCP:** Our Agent Development Kit coordinates dynamic tasks via Model Context Protocol (MCP) servers like `chunkhound` (semantic search) and `zai-mcp-server` (visual diagram reasoning). BAML enforces strict schema conformity across all generative outputs.

### 4. Interactive Frontends (`web` & `marimo`)
The data is visualized through a dual-frontend approach.
*   **TypeScript Web App:** A TanStack Router React application, heavily relying on Convex for real-time reactivity and CopilotKit for an "Agentic GUI" (`agui`).
*   **Marimo Notebooks:** A suite of reactive Python notebooks used for curriculum network analysis, grade forecasting, and direct, interactive SQL querying of our DuckDB and LanceDB catalogs.

---

## 🚀 Deployment & CI/CD

We have completely deprecated legacy Forgejo pipelines in favor of native **GitHub Actions**.
*   `docker-build.yml`: Automates the containerization of the web, API, and Dagster nodes.
*   `dagster-ci.yml`: Performs rigorous validation, Ruff linting, and MyPy checking.
*   **Komodo & Pangolin:** Our self-hosted deployment relies on Komodo to coordinate the Docker Compose stacks, exposed securely via Pangolin tunnels to Hetzner.

### Local Setup
Ensure your `1Password` CLI is authenticated to inject secrets natively:
```bash
op run --env-file .env.local -- docker compose up -d
dagster dev
