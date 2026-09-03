---
title: 'Deployment And Ai Strategy'
status: research
supersedes: []
superseded_by: [openspec/specs/infrastructure/spec.md, docs/01-platform-architecture/]
last_touched: 2026-06-13
---

# Oideachais Deployment and AI Strategy

## 1. Executive Summary

This strategy outlines the unified approach for deploying the Oideachais platform and optimizing its AI infrastructure. It combines a robust, containerized deployment stack with a cost-effective, hybrid AI architecture on Google Cloud Platform (GCP). The goal is to maximize an initial £200 GCP credit while adhering to strict open-source principles, ensuring scalability, and maintaining a secure, unified ecosystem.

## 2. Core Strategic Principles

1.  **Orchestrated Containerization:** Utilize Docker Compose and Komodo for reproducible, scalable local and cloud deployments.
2.  **Decoupled State:** Rely on Cloudflare R2 (Object Storage) and LanceDB (Vector Database) for synchronicity and redundancy across environments, keeping compute stateless.
3.  **Strict Open-Source AI First:** Prioritize open weights (Gemma, Qwen-VL, GLM), open standards (OpenAI API compatibility layer), and open-source middleware.
4.  **Radical GCP Credit Optimization:** Aggressively leverage GCP serverless free tiers (Cloud Run, Cloud Functions) and Spot VMs to stretch the £200 runway.
5.  **Unified AI Gateway:** Maintain a single secure gateway within GCP (e.g., LiteLLM or Pydantic AI) to centralize logging, manage API keys via Google Secret Manager, and route all outbound/inbound calls safely.

## 3. Technology Stack Overview

### Deployment & Infrastructure
1.  **Containerization & Local Orchestration:** Docker Compose
2.  **Resource Management & Orchestration:** Komodo
3.  **Reverse Proxy & Edge Connectivity:** Pangolin
4.  **Analytical Data Lake Engine:** DuckLake
5.  **Vector Database / Embedded Search:** LanceDB
6.  **Object Storage & Edge Caching:** Cloudflare R2

### AI Ecosystem
1.  **Managed AI:** Google Vertex AI (Gemini 1.5 Flash/Pro, Gemma via Model Garden)
2.  **Open-Source Models:** Qwen-VL, GLM (hosted internally)
3.  **AI Gateway:** LiteLLM or Pydantic AI Gateway on Cloud Run
4.  **Inference Engines:** vLLM or Ollama
5.  **Collaborative Coding:** Zed.AI (routed through the unified Gateway)

## 4. Architecture & Symbiotic Interactions

### The Unified "Stay in GCP" AI Architecture
To seamlessly route calls between proprietary and open-source models without leaving the GCP security perimeter, a unified AI Gateway will be deployed:
*   **Serverless Gateway:** Deployed via Docker to **Cloud Run** (generous free tier, scales to zero).
*   **Native Integrations:** Connects to Google Secret Manager for Vertex AI/external API credentials.
*   **Internal VPC Routing:** Routes traffic to internally hosted open-source models (via Private IP) on Spot VMs to avoid egress charges.

### Infrastructure Symbiosis
*   **DuckLake + Cloudflare R2:** DuckLake performs heavy analytical queries directly against Parquet files stored in R2, decoupling compute from storage for cost reduction and global distribution.
*   **LanceDB + Application Layer:** Provides blazing-fast semantic search over educational content, crucial for RAG pipelines, backing up to R2 for redundancy.
*   **Komodo + Docker Compose:** Komodo acts as the control plane, bringing CI/CD capabilities to standard Docker Compose files for easy rollbacks.
*   **Pangolin + Global Edge:** Securely exposes the infrastructure to the internet, providing SSL termination and DDoS protection.

## 5. Deployment Priority & Rollout

### Phase 1: Infrastructure Foundations & Budgets
*   **GCP Budgets:** Set strict billing alarms at £50, £100, £150, and £190. Setup Google Secret Manager for all keys.
*   **Cloudflare R2 Setup:** Provision S3-compatible R2 buckets as the primary sink for data lake artifacts, model checkpoints, and LanceDB backups.
*   **Docker Compose Configuration:** Establish baseline networking and volume mounts locally.
*   **Pangolin Tunneling:** Initialize secure reverse tunnels to expose environments securely.

### Phase 2: Data Persistence & AI Gateway
*   **DuckLake & LanceDB Initialization:** Deploy DuckDB to write Parquet files to R2. Set up LanceDB for vector embeddings on a backed-up volume.
*   **Deploy AI Gateway:** Create a Dockerized LiteLLM/Pydantic AI instance and deploy to Cloud Run, restricting public access but allowing internal VPC access.
*   **Configure Vertex AI:** Enable Vertex AI APIs and add Gemini 1.5 Flash and Gemma routing rules to the Gateway utilizing Prompt Caching to minimize token costs.

### Phase 3: Open-Source Models & Application Management
*   **Provision Spot VM for OS Models:** Write a Terraform/startup script for a T4/L4 Compute Engine Spot VM (60-91% discount). Automatically pull `vLLM` and pre-load Qwen-VL/GLM weights from Cloud Storage. Use a Cloud Function/Scheduler to spin up the VM only during active hours.
*   **Komodo Integration:** Utilize Komodo to manage the deployment lifecycle of the Docker Compose stack (API, frontend, workers) across environments.
*   **Connect Client Endpoints:** Point the Oideachais backend and Zed.AI custom configurations to the centralized Cloud Run Gateway.

## 6. Conclusion
By combining standardized Cloudflare R2 storage for data/embeddings, Komodo for stateless compute management, and a serverless Cloud Run AI Gateway routing to both Vertex AI and Spot VMs, Oideachais achieves a highly synchronized, scalable, and radically cost-optimized infrastructure. This unified strategy ensures the £200 GCP credit is spent purely on essential compute and tokens, with zero waste on idle infrastructure, while adhering strictly to open-source principles.
---

**Archived 2026-07-06** — moved from `openspec/plans/` to `openspec/plans/archive/2026-07-06-plans-refresh/` by the `2026-07-06-drift-cleanup-and-v4-alignment` change. The content of this plan has been absorbed into the canonical specs listed in the frontmatter `superseded_by` field (refreshed to point at post-v4 spec names).
