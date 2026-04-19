# SRUTH - Stream-based Infrastructure & Intelligence

This directory contains the core "streams" (sruthanna) of the Cianfhoghlaim project, organized by domain. It represents a converged architecture utilizing local high-performance compute (48GB MacBook M4 Max) and Oracle Cloud Infrastructure (OCI).

## Directory Structure

| Stream | Description | Core Technology |
| :--- | :--- | :--- |
| `bonneagar/` | Infrastructure & Deployment | Komodo, Pangolin, Locket, Docker |
| `meaisínfhoghlaim/` | Machine Learning & AI | Langfuse, MLflow, Crawl4AI, Cognee |
| `oideachais/` | Education Platform | FastAPI, TanStack, Dagster, DuckDB |
| `códeolas/` | Codebase Intelligence | Beads, Chunkhound, Dagger |
| `tuatha/` | Community & Identity | Pocket-ID, Forgejo |
| `web/` | Web Frontends | React, TanStack Start |

## Infrastructure Strategy (Pangolin Convergence)

The project has transitioned from a distributed Hetzner/OCI model to a **Convergence Model**:

1.  **OCI (arm1-oci)**: Acts as the Control Plane. Runs Pangolin (Routing), Komodo Core (Orchestration), and identity services.
2.  **MacBook (bunchloch)**: Acts as the Primary Workload Host. With 48GB RAM, it hosts memory-intensive stacks (Vector DBs, Graph DBs, LLM Inference) and analytics (Dagster, LakeFS).

## Core Stacks & Benefits

### 🛠 Engineering & Automation
- **Coder**: Provides a self-hosted VS Code environment, ensuring consistency between dev and prod.
- **Crawl4AI**: High-performance, LLM-optimized web crawling for curriculum data ingestion.
- **Windmill**: Low-code platform for orchestrating complex Celtic language processing pipelines.

### 🛡 Infrastructure
- **Pangolin**: Secure service discovery and routing, providing zero-trust access to internal tools.
- **Komodo**: Simplifies multi-host deployment with a lightweight "Core + Periphery" agent model.
- **Locket**: GitOps-friendly secrets management using 1Password as the source of truth.

### 🧠 Intelligence & ML
- **Langfuse**: Essential for tracing LLM calls, evaluating prompt performance, and managing costs.
- **Cognee**: Implements the "GraphRAG" pattern, turning curriculum documents into queryable knowledge graphs.
- **Perplexica (Vane)**: A self-hosted AI search engine for deep research into Celtic linguistics.

### 💾 Storage & Data
- **FerretDB v2**: Offers MongoDB compatibility on top of PostgreSQL, leveraging native vector search for RAG.
- **LanceDB**: A high-performance vector database optimized for multi-modal data and large-scale embeddings.
- **DuckLake**: Converged architecture using DuckDB for local analytics and S3 for scalable storage.
