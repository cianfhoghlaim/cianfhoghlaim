# Oideachais Documentation Hub

This directory contains the theoretical and architectural research that forms the foundation of the `cianfhoghlaim` stack. 

The documents here are strictly organized and map 1:1 to their concrete implementation directories across the monorepo.

## Documentation Index & Interoperability Mapping

### 1. `bonneagar/` (Infrastructure)
*   **Focus:** Zero-trust architecture, fleet orchestration, and edge security.
*   **Key Documents:** 
    *   `komodo/Komodo Deployment and Workflow Integration.md`
    *   `pangolin/Implementing External Authentication in Pangolin Using Tinyauth.md`
*   **Implemented In:** The root `infrastructure/` directory. (e.g., `infrastructure/pulumi/oci/deploy.ts` handles the Komodo handoff, and `infrastructure/pangolin/sidecar.yaml` handles the TinyAuth deployment).

### 2. `data_engineering/`
*   **Focus:** Extract-Load-Transform (ELT) pipelines, DuckLake integration, and orchestrators.
*   **Key Documents:**
    *   `data-architecture.md` (Explains the DLT -> Ducklake -> LanceDB flow).
*   **Implemented In:** The `oideachais/data_platform/` directory. `dagster` orchestrates the `dlt_sources/ireland` pipelines, yielding parsed JSON payloads to local S3 compatible storage (`Garage S3`) and querying via DuckDB.

### 3. `meaisínfhoghlaim/` (Machine Learning & AI)
*   **Focus:** LLM routing, Agentic behavior, and Semantic schemas.
*   **Key Documents:**
    *   `BAML, Graphiti, Tanstack AI Pipeline.md`
*   **Implemented In:** The `meaisínfhoghlaim/` directory and `oideachais/baml_src/`. Claude/Gemma models extract learning outcomes into deterministic schemas using BAML, which are then embedded via `CocoIndex` into `LanceDB` and temporally mapped via `Graphiti`.

### 4. `tuatha/` (Web3 & Edge MMO)
*   **Focus:** Real-time state synchronization, ECS databases, and micro-transactions.
*   **Key Documents:**
    *   `celtic_mmo.md`
    *   `Technical Integration Plan...md`
*   **Implemented In:** The `tuatha/` directory. Utilizing `SpacetimeDB` for ultra-low latency game state and `x402` for semantic token transactions in the educational RPG.

### 5. `web/` (Frontend)
*   **Focus:** React frameworks, local-first syncing, and Server-Side Rendering.
*   **Key Documents:**
    *   `TanStack DB Integration and Comparison.md`
*   **Implemented In:** `oideachais/web_app/` and `oideachais/dashboard/`. Utilizing `TanStack Start` and `BetterAuth` to interact with the underlying Lakehouse catalog dynamically.

## Maintaining Consistency

When adding new architectural paradigms to this directory, ensure they are actively linked or explicitly prototyped in their respective functional quadrants. Use the `scripts/sync_agent_docs.sh` tool to automatically measure the volume of data pipelines and ensure that telemetry across the repo remains synchronized with these theoretical designs.
