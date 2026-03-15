# Infrastructure Deep Dive: Education Workspace

This document provides a deep analysis of the storage and infrastructure layers within the `education/infrastructure` directory, specifically focusing on the `docker` subdirectory which houses the deployment manifests for DuckLake, LanceDB, Garage, Hetzner, and the Observability stack.

## 1. Architectural Overview

The infrastructure is designed around a **Modular Hybrid Data Lakehouse**, unifying multiple data formats (Iceberg, Lance, DuckLake) under a single compute umbrella (DuckDB). It leverages a federated storage layer that prioritizes data sovereignty, zero-egress compute locality, and cost efficiency, spanning both self-hosted and cloud-managed resources.

## 2. Storage Substrate: Federated Object Storage

Rather than a single data bucket, the architecture utilizes a federated model balancing performance, cost, and distribution:

### Garage S3 (Hetzner)
- **Purpose**: The primary "hot" storage tier.
- **Technology**: Garage is an S3-compatible, open-source object storage system built on a Conflict-free Replicated Data Type (CRDT) architecture, making it highly resilient on commodity hardware.
- **Deployment**: Hosted on Hetzner VPS instances.
- **Benefits**:
  - **Data Sovereignty**: Kept in GDPR-compliant EU zones under direct control.
  - **Zero-Egress Locality**: Co-locating compute (Lakekeeper/DuckDB) with Garage nodes on Hetzner's private network eliminates internal processing egress fees.
  - **Cost-Efficiency**: Hetzner's low storage costs drastically undercut hyperscalers.
- **Critical Config**: Requires virtual-host addressing configuration (and wildcard DNS) to ensure S3 SDKs (like Lance and Iceberg) can communicate with it.

### Cloudflare R2
- **Purpose**: The "warm" / global distribution tier.
- **Benefits**: Zero egress costs globally. Used to serve data to external consumers (e.g., local laptops, external ML training) without incurring AWS-style egress penalties.

## 3. Metadata Layer: The "Grand Unification"

A sophisticated federated metadata approach is used to simultaneously support disparate formats.

### Lakekeeper (Iceberg REST Catalog)
- **Role**: High-performance, Rust-native Apache Iceberg REST catalog acting as the central truth for Iceberg tables.
- **Database**: Lakekeeper mandates PostgreSQL. Thus, a self-hosted PostgreSQL container is deployed alongside it on Hetzner to ensure low-latency.

### Lance Namespace (The "Trojan Horse")
- **Role**: Stores high-dimensional vector data for AI/ML workloads.
- **Integration**: Uses `lance-namespace-impls/iceberg.py` to register Lance tables inside the Lakekeeper catalog using a dummy schema and a specific property `table_type=lance`.
- **Benefit**: Provides a Single Pane of Glass in Lakekeeper, displaying both standard analytical tables (Iceberg) and vector tables (Lance).

### DuckLake
- **Role**: A SQL-native catalog format that stores table metadata directly in a transactional database.
- **Database**: DuckLake relies on **PlanetScale**, a serverless MySQL platform built on Vitess, ensuring massive horizontal scalability for metadata operations.
- **Benefit**: Allows fast local development (validating logic locally) before deploying seamlessly to cloud runtimes like MotherDuck.

## 4. Compute Engine: DuckDB

**DuckDB** serves as the universal federated query engine. By loading specific extensions (`httpfs`, `iceberg`, `lance`, `ducklake`, `mysql`), a single DuckDB session can query and join analytical reports from Iceberg, user metadata from DuckLake/PlanetScale, and vector embeddings from Lance—all while pulling from both Garage S3 and Cloudflare R2 concurrently.

## 5. Observability Stack

The platform deploys comprehensive open-source observability tools, managed via Docker Compose and Komodo stacks:

- **Langfuse** (`docker/langfuse`): Open-source LLM observability and evaluation. It stores its telemetry and trace data. Note: The infrastructure shows an active migration strategy of Langfuse's backend from self-hosted PostgreSQL to PlanetScale for better scalability.
- **MLflow** (`docker/mlflow`): Open-source platform for the machine learning lifecycle. It provides experiment tracking, model registry, and metric logging.
- **Logfire** (`docker/logfire`): An observability platform tailored for Python and Pydantic, providing structured logging and tracing.
- **Cognee** (`docker/cognee`): AI memory management, integrating with the observability tools to persist context.

## 6. Infrastructure Orchestration (Komodo & Docker)

The `education/infrastructure/docker` folder contains the blueprint and compose files for deploying these services. 
- `komodo/` directory features TOML manifests (e.g., `ducklake-hetzner.toml`, `lance-hetzner.toml`, `lakekeeper-hetzner.toml`) to deploy these specific stacks onto Hetzner servers (like `cax41-hetzner`).
- These automated CI/CD procedures ensure that the entire stack (Garage, Lakekeeper, Lance Namespace, Observability) can be securely deployed and rolled back using Komodo.

## Summary

This infrastructure leverages open-source projects (Garage, Lakekeeper, Lance, DuckDB, Langfuse, MLflow) to create a high-performance, cost-effective, and fully sovereign data lakehouse. By splitting metadata across Postgres (for Iceberg/Lance) and PlanetScale (for DuckLake) and unifying queries via DuckDB, the `education` workspace offers a powerful, hyperscaler-independent platform for multimodal AI and analytics.
