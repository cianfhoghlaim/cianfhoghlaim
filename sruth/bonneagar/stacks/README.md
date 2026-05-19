# Bonneagar Stacks - Infrastructure as Code

This directory contains the modular Docker stacks managed by **Komodo** and routed via **Pangolin**. These stacks follow the **Pangolin Convergence** strategy, utilizing OCI for the Control Plane and a 48GB MacBook M4 Max for primary workloads.

## 📁 Stack Categories

### 🛠 [Engineering](./engineering)
*Tools for development, automation, and workflow orchestration.*
- **Coder**: Self-hosted VS Code environments for consistency across dev/prod.
- **Crawl4AI**: LLM-optimized web scraping (v0.8.6: Adaptive crawling, Deep Crawl Crash Recovery, Cloud API Beta).
- **LiteLLM**: Unified AI gateway for routing to Gemini, GPT, and local models (Supporting Claude 3.7 Thinking & MCP bridge).
- **Windmill**: High-performance low-code platform for Python/TypeScript pipelines.

### 🛡 [Infrastructure](./infrastructure)
*Core services for networking, identity, and observability.*
- **Pangolin**: Zero-trust service discovery and secure routing (v1.17: Full RBAC, Identity-Aware Proxy, Log Streaming).
- **Komodo**: Core + Periphery orchestration (v2.1.2: PKI Ed25519 auth, Outbound Periphery, Docker Swarm support).
- **Pocket-ID**: Lightweight OIDC provider for unified project identity.
- **Dozzle**: Real-time log viewer for all containerized services.
- **DnsServer**: Local DNS control for internal service resolution.

### 🧠 [Machine Learning](./machine_learning)
*AI observability, experiment tracking, and memory management.*
- **Langfuse v3**: Distributed LLM tracing with Postgres + Clickhouse backend.
- **MLflow**: End-to-end ML lifecycle management and model registry.
- **Cognee**: Automated GraphRAG and semantic memory construction.
- **Graphiti**: Dynamic knowledge graph visualization and storage.

### 💾 [Storage](./storage)
*Converged data lakehouse and database technologies.*
- **FerretDB v2**: PostgreSQL-backed MongoDB API with native vector search.
- **LanceDB**: High-performance vector database for RAG and multi-modal data.
- **FalkorDB / Memgraph**: Low-latency graph databases for complex relationship mapping.
- **Dagster**: Asset-based data orchestration for curriculum pipelines.
- **LakeFS / Lakekeeper**: Version control for data lakes and Iceberg REST catalog.

### 🧰 [Tools](./tools)
*Utility services for productivity and specialized tasks.*
- **Perplexica (Vane)**: AI-powered research engine for deep web/doc search.
- **Actual**: Private, self-hosted personal finance and budgeting.
- **Linkwarden**: Collaborative bookmark manager and webpage archiver.
- **Audiobookshelf**: Self-hosted server for audiobooks and podcasts.

## 🚀 The Pangolin Convergence Strategy

The project has transitioned to a **Two-Tier Architecture**:

1.  **OCI Tier (`arm1-oci`)**:
    - **Role**: Global Control Plane.
    - **Focus**: Availability, Routing, Identity.
    - **Key Stacks**: Pangolin, Komodo Core, Pocket-ID, DnsServer.

2.  **Local Tier (`bunchloch`)**:
    - **Role**: High-Performance Workload Host.
    - **Focus**: Compute Density, Memory (48GB), Low-Latency Storage.
    - **Key Stacks**: Langfuse, MLflow, Vector DBs, Graph DBs, Scraping (Crawl4AI), Data Engineering (Dagster).

## 🛡 Security & Secrets

- **Secrets Management**: Handled by **Locket**, which injects secrets from Infisical at runtime.
- **Connectivity**: All traffic is encrypted and routed via Pangolin tunnels, eliminating the need for open ports.
