# Sovereign Educational Infrastructure: Architecture Rationale

This document serves as the foundational rationale for the design and integration of the `cianfhoghlaim` project stack. It directly correlates the open-source architectural patterns researched in this repository with their live implementation across the four primary directories: `infrastructure`, `oideachais`, `meaisínfhoghlaim`, and `tuatha`.

## The Quadrant Model

To ensure strict separation of concerns and maintain a scalable "Local-First / Sovereign-First" deployment model, the project is decoupled into four sovereign quadrants.

### 1. `infrastructure/` (The Foundation)
**Focus:** Zero-trust networking, fleet orchestration, and machine identity.
*   **Komodo**: Used instead of standard Ansible or Kubernetes. Komodo acts as an edge-first fleet orchestrator, allowing us to manage Docker Compose blueprints across disconnected servers (e.g., the OCI control plane and the local MacBook workload host).
*   **Pangolin (Newt/Gerbil)**: Replaces Cloudflare Tunnels for internal mesh networking. While Cloudflare Tunnels expose services to the web, Pangolin provides a WireGuard-backed Service Mesh. This enables secure, internal, outbound-only communication between the MacBook M4 and the Oracle Cloud instance without opening inbound firewall ports.
*   **Infisical + Locket**: Instead of `.env` files scattered on disks, all machine identities and API keys are stored in a centralized vault. `Locket` or `init-vault.ts` injects these into Docker Compose clusters and CLI agent environments dynamically at runtime.
*   **Pocket ID & TinyAuth**: Instead of hardcoding authentication in every Python or TypeScript app, we enforce a strict **Identity-Aware Proxy** pattern. `TinyAuth` runs as a Traefik `forwardAuth` middleware, bouncing unauthenticated requests to `Pocket ID` for phishing-resistant Passkey login before traffic ever reaches the internal apps.

### 2. `oideachais/` (The Engine)
**Focus:** Extract-Load-Transform (ELT), data orchestration, and the interactive frontend.
*   **Dagster vs Airflow/Prefect**: Dagster was chosen for its Asset-driven approach. Instead of tracking "tasks," we track the materialized state of the Irish curriculum (e.g., Junior Cycle Mathematics).
*   **DLT (Data Load Tool)**: Chosen for declarative, typed ingestion of scraped websites. Crucially, the DLT pipelines are configured with an offline `stedding/site_scrape_samples` fallback, allowing rapid iteration on thousands of JSON payloads without hitting Firecrawl API rate limits.
*   **DuckLake (DuckDB + Garage S3)**: We reject expensive cloud data warehouses (Snowflake/BigQuery) in favor of a local Lakehouse architecture. `DuckDB` serves as the high-performance analytical engine, reading/writing Parquet/Iceberg tables directly to an S3-compatible object store (`Garage`) hosted locally or on Cloudflare R2.
*   **TanStack Start**: Provides a highly-reactive, SSR-first frontend for exploring the curriculum data. It perfectly complements the local-first philosophy by enabling offline differential data syncs via TanStack DB.

### 3. `meaisínfhoghlaim/` (The Brain)
**Focus:** Artificial Intelligence, LLM Routing, and Semantic Extraction.
*   **BAML (Boundary AI Markup Language)**: Prompt engineering using raw JSON structures is brittle. BAML provides compiled, type-safe schema definitions for extracting complex entities (like Learning Outcomes and Examiner Reports) from unstructured PDFs via Claude and Gemma.
*   **LiteLLM**: Centralizes API keys (Anthropic, OpenAI, Gemini) and provides a unified interface for agentic routing, fallback handling, and spend tracking.
*   **Graphiti & Neo4j**: Educational data is highly relational (e.g., Learning Outcome A *Builds On* Learning Outcome B). Graphiti maintains this temporal and episodic knowledge graph, far outperforming standard vector databases for complex curriculum reasoning.
*   **LanceDB & CocoIndex**: Used for vectorized semantic search. `CocoIndex` orchestrates the chunking of the BAML-extracted markdown and syncs the vector embeddings into LanceDB.

### 4. `tuatha/` (The Edge)
**Focus:** Distributed node state, real-time MMO mechanics, and Web3 integration.
*   **SpacetimeDB**: A breakthrough embedded database acting as both the application server and the database for the "Anam" educational MMO. It allows us to synchronize Entity-Component-System (ECS) updates in real-time across players learning Celtic languages.
*   **x402 (HTTP 402)**: Facilitates cryptographic, decentralized micropayments natively over HTTP for the "Learn-to-Earn" token economy without requiring heavy smart contract deployments for every action.

## Key Agent Workflows (MCPs & Subagents)

To maintain this stack autonomously, the CLI agents are augmented with specialized Model Context Protocol (MCP) servers:
*   **Docling / Marker MCP**: Converts complex SEC Examination PDFs and multi-column Marking Schemes into structured Markdown for BAML to process.
*   **Skyvern / Crawl4AI MCP**: Powers the asynchronous browser automation required to navigate legacy dropdowns on government websites (like `examinations.ie`).
*   **ChunkHound**: Indexes the monorepo codebase into an AST-aware semantic database, allowing agents to navigate the vast Python and TypeScript environments efficiently.

By adhering to these strict bounds (e.g., no cross-polluting `oideachais` absolute imports in `meaisínfhoghlaim`), the repository remains modular, testable, and highly resilient.
