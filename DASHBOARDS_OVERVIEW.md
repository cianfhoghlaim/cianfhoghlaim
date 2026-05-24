# Oideachais Sovereign Infrastructure & Dashboard Overview

This report provides a structural mapping and overview of the essential open-source package dashboards utilized within the `cianfhoghlaim` stack. It specifically focuses on the integration of **Komodo, Pangolin, Infisical, Dagster, DuckLake, and LanceDB**, analyzing both the live remote control plane and the locally orchestrated data platform.

## 1. Sovereign Infrastructure & Security (Control Plane)

The infrastructure routing, container orchestration, and authentication layer are hosted on the `arm1-oci` control plane, utilizing a zero-trust mesh ingress pattern.

*   **Pangolin (`pangolin.cianfhoghlaim.ie`)**: Manages the tunneled mesh ingress. Features include routing rules, active tunnel monitoring, and Traefik middleware associations.
*   **Komodo (`komodo.cianfhoghlaim.ie`)**: Central orchestration platform. Features include:
    *   **Fleet Management**: Tracking of connected periphery nodes (e.g., `bunchloch - MacBook M4`).
    *   **Resource Metrics**: CPU and memory utilization graphs.
    *   **Deployments**: Triggering declarative deployment blueprints.
*   **Infisical (`132.145.27.89:8080`)**: Centralized secret management. 
    *   **Vaults**: Specifically the `dev-baile` vault.
    *   **Machine Identity**: Seamless secret overriding using the `init-vault.ts` / `locket` injection tools.
*   **TinyAuth (`tinyauth.cianfhoghlaim.ie`) / Pocket ID (`pocket-id.cianfhoghlaim.ie`)**: The identity assurance layer. Used as a `forwardAuth` middleware in Pangolin to protect the other open-source UIs.

*(Note: Live screenshots of the remote OCI dashboards were unavailable at the time of writing due to upstream network/tunnels returning HTTP 521).*

## 2. Data Engineering & Analytics (Oideachais Pipeline)

The modern data pipeline for the Irish education curriculum relies heavily on `dlt`, `Dagster`, `DuckDB` (via DuckLake), and `LanceDB` (via CocoIndex flows).

### 2.1 Dagster Orchestration (`localhost:3000`)
The `oideachais` stack uses Dagster as the primary pipeline orchestrator.

![Dagster Local Dashboard](./dashboards/dagster_local.png)

**Key Features Observed:**
*   **Asset Graph**: Visualization of the `ireland/curriculum/` assets (Early Childhood, Primary, Junior Cycle, Senior Cycle, Short Courses).
*   **Multi-Partitions**: Support for partition matrixes separating assets by subject and language (e.g., `mathematics|en`, `gaeilge|ga`).
*   **DLT Hub Pro Integration**: The implementation natively registers the extracted datasets and caching layers using the new `dlthub` project wrapper via `apply_dlthub_wrappers()`.

### 2.2 DuckLake & Garage (The Lakehouse)
The platform utilizes a modern offline-first lakehouse architecture.
*   **DuckLake**: Backed by DuckDB metadata and S3 API object storage.
*   **DLT Ingestion**: The `curriculum_source` dynamically bypasses live API scraping when offline, pulling from `stedding/site_scrape_samples` (yielding over 13k JSON payloads rapidly without API throttling).

## 3. AI, Knowledge Graphs & Models

The curriculum extraction heavily utilizes LLM parsing (BAML) and embeddings for later semantic search and agentic access.

*   **BAML Parsing**: Extracts structured curricula using Claude/Gemma models. Defined in `baml_src/curriculum_extraction.baml`.
*   **CocoIndex Flows**: Once extracted, data enters `cocoindex_flows` for chunking and vectorized embedding generation.
*   **LanceDB**: Stores the resulting embeddings.
*   **LiteLLM (`litellm.cianfhoghlaim.ie`)**: Routes the traffic for BAML extractions. Target models verified in the routing tables include `gemma-2.0-flash` (standard inference) and specialized configurations for vision/language models like `glm4.6v` and `colpali`.
*   **Graphiti / Cognee**: Maintains the explicit temporal/semantic link schemas between learning outcomes (e.g., `PREREQUISITE_FOR`, `BUILDS_ON`).

## 4. Automation Improvements & Fixes Implemented
To ensure the pipeline could be successfully evaluated:
1.  **Infisical Synchronization**: Updated `init-vault.ts` to seamlessly parse `.infisical.env` templates, automatically creating missing `dev-baile` environment folders (`/browserbase`, `/firecrawl`, `/pydantic-logfire`) and seeding keys.
2.  **DLT Hub Compatibility**: Resolved dependency and pathing conflicts with `dlthub` (`v0.22.1` vs `v0.27.0`) and fixed absolute `dlt_sources` imports within the data platform.
3.  **Local Scrape Optimization**: Modified `curriculum_source.py` to seamlessly fallback to `site_scrape_samples`, ensuring pipeline runs successfully without encountering Firecrawl rate limits.
