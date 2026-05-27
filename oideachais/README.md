# Oideachais (The Engine)

The `oideachais` directory forms the core data engine and lakehouse of the `cianfhoghlaim` stack. It orchestrates the extraction, loading, and transformation (ELT) of all Irish curriculum and examination data.

## The DuckLake Architecture

We utilize an offline-first, highly federated lakehouse architecture rather than expensive cloud data warehouses.

### 1. Extraction (DLT & Firecrawl)
*   **Pipelines**: Located in `data_platform/dlt_sources/ireland/`.
*   **Sources**: `ncca.ie`, `curriculumonline.ie`, and `examinations.ie`.
*   **Offline Fallback (`USE_LOCAL_SCRAPES`)**: To avoid burning Firecrawl API credits and risking rate limits during development, our DLT pipelines automatically intercept network calls and load from `stedding/ingest_queue/`. This queue contains over 7,000 cached structural documents (JSON payloads with base64 PDFs and Markdown).

### 2. Orchestration (Dagster)
*   **Multi-Partitioned Assets**: We track the materialized state of the Irish curriculum dynamically. For example, `ireland/curriculum/junior_cycle` is partitioned by language and subject (e.g., `en|mathematics`).
*   **Centralized Sink**: All pipelines write to a unified DuckDB database (`curriculum_unified.duckdb`) to ensure that syllabi, exam papers, and examiner reports can be seamlessly joined using SQL.

### 3. Storage (DuckDB + Garage S3)
*   The raw binaries (PDFs) are streamed into local S3-compatible object storage (`Garage S3` or `Cloudflare R2`), while the metadata and extracted text are cataloged in DuckDB (managed by `Lakekeeper`).

### 4. Interactive Frontend (TanStack Start)
*   The structured data is surfaced through highly-reactive, SSR-first frontend applications located in `web_app/` and `dashboard/`, utilizing TanStack DB for offline differential data syncs.

---

## Agent Guidelines
If modifying these pipelines, you MUST assume the `data-engineer` persona.
- Ensure you run `scripts/sync_agent_docs.sh` to update telemetry after altering the DLT pipeline schema.
- **NEVER** use absolute imports originating from the root (e.g., `from oideachais.data_platform...`) inside `data_platform`. Use relative imports to prevent Dagster module resolution crashes.

---

## Deploying Dagster, MotherDuck, and the Agentic Stack

Your `oideachais` application is already well-structured with Docker Compose, handling the orchestration (Dagster), the backend (FastAPI + LiteLLM), and the frontend (TanStack Start + CopilotKit).

### Step 1: Hydrate Secrets for MotherDuck and Cloudflare
Ensure your local environment or `.infisical.env` template has the required credentials. `storage/config.py` is already set up to read `MOTHERDUCK_TOKEN` and fallback to local DuckDB.

Run your Infisical sync to hydrate via `mise`:
```bash
cd scripts/infisical/
bun run init-vault.ts
```

### Step 2: Spin up the environment
Navigate to the `oideachais` directory and start the stack:
```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway/oideachais
docker-compose up -d dagster api frontend litellm
```
Because of `USE_DUCKLAKE="true"`, Dagster and the FastAPI API will route DuckDB queries to MotherDuck while utilizing your `curriculum_unified.duckdb` data. The TanStack frontend at `http://localhost:3000` will stream the CopilotKit AI interactions.

## Automating the Pipeline (Dagster + dlt + cocoindex + R2)

I have scaffolded a new Dagster asset file for you at `oideachais/assets/leaving_cert_assets.py` to automate this workflow. Here is how the architecture handles it:

1.  **Extraction (Garage S3 + `dlt`)**: 
    A `dlt` pipeline scrapes curriculumonline.ie and examinations.ie. The raw PDF binary files are routed instantly to Garage S3 (`s3://education-documents/syllabus/`). `dlt` infers the schema and writes the metadata (subject, year, S3 path) directly into MotherDuck.
2.  **Vision Indexing (`cocoindex` + LanceDB)**: 
    Dagster triggers an asset that retrieves the PDFs from Garage S3 and passes them to `cocoindex` (powered by ColPali). Instead of brittle text OCR, ColPali creates multi-vector embeddings of the page visuals (crucial for Math formulas and Biology diagrams) and stores them in LanceDB/MotherDuck.
3.  **Agentic Generation (FIBO + tuatha)**:
    We invoke the existing `tuatha/fibo_generation` logic. The system extracts CurriculumConcept and LearningOutcome nodes. BAML + LiteLLM generate visual FIBO JSON configurations (e.g., `diagram_type="molecular"` for Chemistry).
4.  **Caching & Distribution (Cloudflare R2)**:
    The finalized JSON study plans and FIBO-generated images are uploaded to a Cloudflare R2 bucket. Using Cloudflare's edge caching provides zero-egress, low-latency delivery directly to your TanStack web application.

## Study Plans & Marking Schemes for 2026 Sample Subjects

By cross-referencing your 2026 Leaving Certificate Timetable with the tuatha research and syllabus data, here is how the CopilotKit agent formulates marking schemes and study plans for the students:

*   **Gaeilge (Irish)**: Generates spaced repetition modules for grammar leading up to the clustered exams, using FIBO to generate visual narrative arcs for *Sraith Pictiúr* and prose.
*   **English**: Parses past examiners' reports to extract the core grading logic: PCLM (Purpose, Coherence, Language, Mechanics). The agent uses Graphiti memory to cross-reference the student's chosen comparative texts against the PCLM rubric.
*   **Mathematics**: Retrieves visual equations and geometric proofs from past papers. FIBO generates step-by-step resolution diagrams for common 50-mark question formats.
*   **Geography & History**: Extracts the concept of SRPs (Significant Relevant Points), where 2 marks are awarded per distinct factual point. FIBO visualizes geographical processes (e.g., tectonic plate boundaries).
*   **Biology & Chemistry**: The exams heavily penalize missing mandatory keywords. `cocoindex` extracts diagrams of mandatory experiments (e.g., titrations, cell plasmolysis). The agent generates active recall quizzes targeting these exact keywords.

## Next Steps

1.  Navigate to the UI at `http://localhost:3000`. 
2.  Open the CopilotKit chat interface. 
3.  You can now prompt the agent: "Show me the marking scheme breakdown for the 2026 Biology mandatory experiments using the MotherDuck index." The agent will query DuckDB, retrieve the ColPali image embeddings of the syllabus, and stream the generated study plan directly to the frontend.
