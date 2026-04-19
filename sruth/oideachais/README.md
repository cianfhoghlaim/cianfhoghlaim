# Oideachais - Celtic Education Platform

Oideachais is a pan-Celtic curriculum search, content management, and learning outcomes platform. It leverages AI to bridge the gap between official curriculum documents and interactive learning experiences.

## 🏗 Platform Architecture

### 🚀 Frontend (TanStack Start)
- **Benefit**: Type-safe, full-stack React application with high-performance streaming.
- **Role**: Provides the primary interface for students and educators to search and interact with the curriculum.

### 🔌 API (FastAPI)
- **Benefit**: High-concurrency, asynchronous Python backend.
- **Role**: Handles LLM orchestration, vector search queries, and real-time streaming of AI responses using Gemini 2.0 and Claude 3.7.

### 🌊 Pipeline (Dagster)
- **Benefit**: Asset-based data orchestration.
- **Role**: Manages the flow of data from raw PDF/HTML ingestion to final vector embeddings.
- **April 2026 Features (v1.13 "Octopus's Garden")**: Leverages the new AI skills (`dagster-io/skills`) for pipeline automation, Partitioned Asset Checks for granular data quality, and Python 3.14 support.

### 💾 Storage (DuckDB & LanceDB)
- **Benefit**: 
  - **DuckDB**: Fast local analytical processing using DuckLake v1.0 (production-ready SQL lakehouse format, released April 2026).
  - **LanceDB**: Multi-modal vector storage utilizing v0.31.0 (April 2026) for namespace-backed federated database support.
- **Convergence**: Data is persisted to Cloudflare R2 for durability while being queried locally for speed.

## 🛠 Deployment Configuration

- **Development**: Managed via `compose.dev.yaml` for local hot-reloading.
- **Production**: Deployed as a **Komodo Stack** on the **MacBook M4 Max**.
- **Secrets**: Injected via **Locket** sidecar, pulling from 1Password.
- **Routing**: Securely exposed via **Pangolin** at `oideachais.cianfhoghlaim.ie`.
