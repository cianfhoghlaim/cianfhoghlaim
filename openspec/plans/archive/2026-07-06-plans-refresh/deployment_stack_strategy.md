---
title: 'Deployment Stack Strategy'
status: research
supersedes: []
superseded_by: [openspec/specs/infrastructure-stacks/spec.md]
last_touched: 2026-06-13
---

# Oideachais Deployment Stack Strategy

## Core Strategy

The deployment strategy for Oideachais relies on a robust, orchestrated containerized approach, prioritizing data synchronization and scalable vector storage.

### Technology Stack Overview

1.  **Containerization & Local Orchestration:** Docker Compose
2.  **Resource Management & Orchestration:** Komodo
3.  **Reverse Proxy & Edge Connectivity:** Pangolin
4.  **Analytical Data Lake Engine:** DuckLake
5.  **Vector Database / Embedded Search:** LanceDB
6.  **Object Storage & Edge Caching:** Cloudflare R2

## Deployment Priority & Rollout

### Phase 1: Infrastructure Foundations

*   **Cloudflare R2 Setup:** Before deploying application services, provision the S3-compatible R2 buckets to act as the primary sink for data lake artifacts and model checkpoints.
*   **Docker Compose Configuration:** Establish the baseline networking and volume mounts locally for seamless testing.
*   **Pangolin Tunneling:** Initialize secure reverse tunnels to expose the development/production environment securely without complex firewall configurations.

### Phase 2: Data Persistence Layer

*   **DuckLake Initialization:** Deploy DuckDB instances configured to write Parquet files directly to Cloudflare R2. This serves as our serverless, high-performance analytical engine.
*   **LanceDB Namespace:** Set up LanceDB to handle vector embeddings. Since LanceDB operates on standard file systems, it will use a dedicated, backed-up volume (synchronizing with R2 for redundancy) to store high-dimensional embeddings of educational materials.

### Phase 3: Application & Management

*   **Komodo Integration:** Utilize Komodo to manage the deployment lifecycle of the Docker Compose stack across different environments, ensuring resource limits are respected and deployments are reproducible.
*   **Oideachais Core Services:** Deploy the main API, web frontend, and background workers via Compose, managed by Komodo, and routed through Pangolin.

## Symbiotic Interactions

*   **DuckLake + Cloudflare R2:** DuckLake performs heavy analytical queries directly against Parquet files stored in R2. This decouples compute from storage, reducing costs while providing global distribution.
*   **LanceDB + Application Layer:** LanceDB provides blazing-fast semantic search over the educational content, crucial for the RAG (Retrieval-Augmented Generation) pipelines.
*   **Komodo + Docker Compose:** Komodo acts as the control plane, bringing CI/CD capabilities to standard Docker Compose files, allowing for easy rollbacks and environment duplication.
*   **Pangolin + Global Edge:** Pangolin ensures that the self-hosted or cloud-hosted infrastructure is securely exposed to the internet, providing SSL termination and DDoS protection by leveraging the broader edge network.

## Synchronicity & Scalability

By standardizing on Cloudflare R2 as the definitive source of truth for both raw data (DuckLake) and structured embeddings (LanceDB backups), we ensure synchronicity across potential multi-node deployments. Komodo manages the stateless compute layers, while state is entirely delegated to high-availability object storage and specialized vector filesystems.

---

**Archived 2026-07-06** — moved from `openspec/plans/` to `openspec/plans/archive/2026-07-06-plans-refresh/` by the `2026-07-06-drift-cleanup-and-v4-alignment` change. The content of this plan has been absorbed into the canonical specs listed in the frontmatter `superseded_by` field (refreshed to point at post-v4 spec names).
