# Kings' College Galway — Documentation

This directory contains the consolidated documentation for the Kings' College Galway platform, a unified Celtic Education Platform.

## 🏗 Architectural Overview

The platform leverages a **multi-cloud, zero-trust infrastructure** orchestrated through automated pipelines.

### Core Streams
- **[Bonneagar (Infrastructure)](bonneagar/README.md):** The backbone — IaC (Pulumi), GitOps (Komodo), Zero-Trust Networking (Pangolin), Browser Automation (Hunter-Gatherer-Operator pattern).
- **[Oideachais (Education)](../oideachais/README.md):** AI-powered education platform — TanStack Start, FastAPI, Dagster v1.13, DuckLake/LanceDB.
- **[Data Engineering](data_engineering/README.md):** Data orchestration, DLT pipelines, BAML extractors, and MotherDuck integration.
- **[Agents](agents/README.md):** Agent orchestration, Google-ADK, and multi-agent coordination.
- **[Security & Compliance](hmgcc/README.md):** HMGCC compliance standards and security hardening.

## 🔌 MCP Ecosystem

We leverage the Model Context Protocol (MCP) to bridge our agents with external tools:
- **Secrets Management:** `@infisical/mcp`
- **Scraping:** `@browserbasehq/mcp-server-browserbase`, `firecrawl-mcp`
- **Data Warehousing:** `mcp-server-motherduck`
- **Vector Storage:** `mcp-server-qdrant`
- **Graph Storage:** `mcp-memgraph`

---
*Documentation is continuously updated by autonomous agents.*
