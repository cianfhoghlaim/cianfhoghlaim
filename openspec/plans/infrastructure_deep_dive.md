---
title: 'Infrastructure Deep Dive'
status: research
supersedes: []
superseded_by: [openspec/specs/infrastructure/spec.md]
last_touched: 2026-06-13
---

# Infrastructure Deep Dive: Education Workspace

This document provides a deep analysis of the storage and infrastructure layers within the `sruth/bonneagar` directory, focusing on the converged architecture utilizing Oracle Cloud (OCI) and the local high-performance MacBook M4 Max.

## 1. Architectural Overview: Pangolin Convergence

The infrastructure has evolved from a distributed Hetzner model to a **Convergence Model**. This strategy minimizes latency for data-heavy AI operations while maintaining a cloud-based control plane for orchestration.

- **OCI (arm1-oci)**: Acts as the **Control Plane**. Hosts global routing (Pangolin), orchestration (Komodo Core), and persistent identity (Pocket-ID).
- **MacBook (bunchloch)**: Acts as the **Data Persistence Layer**. With 48GB unified memory, it handles memory-intensive vector search, graph databases, and analytics pipelines.

## 2. Storage Substrate: Converged Object Storage

The architecture balances local high-speed access with global cloud availability:

### Local S3 Tier (MacBook)
- **Purpose**: Ultra-low latency "Hot" storage for active curriculum processing and ML inference.
- **Technology**: Garage S3 or MinIO (depending on stack requirements).
- **Benefits**:
  - **Zero Latency**: Direct NVMe access for LanceDB vector files and DuckDB Parquet files.
  - **Privacy**: Processing stays entirely on-premises during the ingestion phase.

### Cloudflare R2
- **Purpose**: The "Warm" / Global Distribution tier.
- **Benefits**: Zero egress costs globally. Used to sync processed curriculum artifacts from the MacBook to the OCI control plane and external clients.

## 3. Metadata Layer: Federated Discovery

### Lakekeeper (Iceberg REST Catalog)
- **Role**: High-performance Rust-native Apache Iceberg REST catalog.
- **Deployment**: Hosted on **arm1-oci** to ensure the catalog is always reachable, even when the MacBook is offline.

### LanceDB (Vector Truth)
- **Role**: Primary vector store for RAG. 
- **Convergence**: LanceDB files are stored on the **MacBook**'s NVMe for maximum embedding performance and backed up to R2.

### DuckDB / DuckLake
- **Role**: SQL-native analytical processing.
- **Database**: Integrated with PlanetScale or local SQLite for metadata tracking.
- **Benefit**: Provides ultra-fast local joins across Iceberg, Lance, and relational data.

## 4. Compute Engine: MacBook M4 Max

The **48GB MacBook M4 Max** is the primary compute engine for:
1.  **Crawl4AI**: High-concurrency scraping of curriculum documents.
2.  **LLM Inference**: Local model hosting for privacy-sensitive linguistic analysis.
3.  **Dagster**: Asset-based orchestration of the education pipeline.

## 5. Observability Stack (Converged)

Managed via Komodo stacks on the MacBook:
- **Langfuse**: Tracing and evaluation for all LLM calls. Uses Postgres + Clickhouse for scale.
- **MLflow**: Experiment tracking and model registry.
- **Logfire**: Structured logging for Python services.

## 6. Infrastructure Orchestration (Komodo & Locket)

- **Komodo**: Manages the deployment lifecycle across OCI and MacBook.
- **Locket**: Injects secrets directly from 1Password into containers, eliminating manual `.env` management and ensuring security across the convergence.

## Summary

This converged infrastructure leverages the best of both worlds: the high-performance unified memory of the MacBook M4 Max for AI workloads and the reliable, globally reachable control plane of OCI. By unifying these via Pangolin and Komodo, the Cianfhoghlaim project achieves enterprise-grade observability and scale on personal-grade, sovereign hardware.
