# Project Growth Audit & Infrastructure Report 
**Date**: May 2026
**Target Environment**: `cianfhoghlaim.ie` (Cloudflare Pages/Workers & Edge Networks)

## 1. Architectural Evolution

The `oideachais` and `meaisínfhoghlaim` projects have transitioned from monolithic, legacy React interfaces to a deeply integrated, agent-first, Web3-compatible architecture. We have successfully split the system into two distinct halves:

### A. The Data Engineering Platform (`oideachais/data_platform`)
- **dltHub Integration (dlt+ Cache & Projects)**: The ingestion pipelines pulling from the NCCA, State Examinations Commission, and CSO are now routed through a local `DuckDB` cache leveraging Apple's free-tier **iCloud storage**. This allows for massive transformations of local embeddings without cloud latency before final dispatch.
- **Bilingual Machine Learning (`meaisínfhoghlaim`)**: Advanced ML pipelines process English and Irish educational corpora, aligning datasets down to the word/dialect level (Connacht, Munster, Ulster).
- **Storage Strategy**: 
  - Intermediate files and artifacts are cached locally using the **iCloud tier** (`~/Library/Mobile Documents/.../AwenCache/`).
  - Production blobs are routed to **Garage** (a lightweight, S3-compatible local object store) before being synced to **Cloudflare R2** for fast edge access globally.
  - Vectors and schemas are maintained in **LanceDB Namespaces** and parsed analytically using **DuckDB**.

### B. Full-Stack Web Application (`oideachais/web_app`)
- **TanStack Start & Cloudflare**: Entirely rewrote the frontend using `TanStack Start`, allowing dynamic Server-Side Rendering directly from Cloudflare edge locations (`cianfhoghlaim.ie`), vastly improving TTFB (Time-to-First-Byte) globally.
- **MotherDuck Embedded Dives**: A game-changing addition to the data visualisation layer. The frontend now requests a secure `embed-session` token from the backend, spawning an `iframe` that runs MotherDuck's **DuckDB-Wasm** engine entirely in the client's browser. This guarantees near-instant filtering and analysis of decade-long grading curves without hitting the main database.
- **Generative UI (`CopilotKit` + `@tanstack/ai-react`)**: Integrated an Agentic UI pattern where our `Agno` (v2.0+) and `Google ADK` (v2.1+) models emit React Server Components natively instead of raw text, vastly improving the UX.

## 2. Capability Audit

### 2.1 Bilingual Asset Alignment
The pipeline securely handles massive volumes of Irish educational content:
- Junior & Senior Cycle Curriculum Frameworks (Gaeilge & English).
- State Examination Papers, Aural Transcripts, and Marking Schemes.
- Aligning and chunking data utilizing **ChunkHound** into `LanceDB` vectors to create a semantically searchable knowledge base.

### 2.2 Cocoindex Flows
Visualizing the Cocoindex integration:
```text
[Raw NCCA/SEC Data] 
       │
       ▼
(dlt Extract / Normalisation)
       │
       ▼
[iCloud DuckDB Cache] ──────► [Local Garage S3]
       │                              │
       ▼                              ▼
(ChunkHound AST processing)   [Cloudflare R2 Sync]
       │
       ▼
[LanceDB Namespaces] ◄──────► (Cocoindex Routing / Agentic Query)
```

### 2.3 Agentic Orchestration
- **Google ADK NodeRunners**: Managing the hierarchical routing. If a user asks a complex physics question, ADK routes it to the specific STEM specialist agent.
- **Agno AgentOS**: Manages stateless conversation history and coordinates Web3 micropayments via `x402` and the `Pinginn`/`Screpall` tokens.
- **MCP Tooling (Chrome DevTools, Firecrawl, Browserbase)**: Enabled agents to break out of the local context to scrape JS-rendered pages and dynamically debug applications autonomously.

## 3. Deployment Summary

The deployment to `cianfhoghlaim.ie` follows this strict sequence:
1. **Infisical (Locket)** initializes dynamic `.env` configurations via `mise`.
2. **Docker Compose** brings up the required databases (`Neo4j`, `LanceDB`, `Garage`).
3. **Dagster / DLT** synchronizes the local iCloud datasets to `MotherDuck` and `Cloudflare R2`.
4. **Cloudflare Wrangler** packages and deploys the `dist/` directory from `web_app` securely to the edge.

*End of Audit.*
