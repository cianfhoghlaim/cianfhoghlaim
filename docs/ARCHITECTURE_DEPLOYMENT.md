# 🚀 Architecture & End-to-End Deployment Guide

The deployment strategy utilizes a **Two-Tier "Pangolin Convergence" Architecture**:
1. **Control Plane (`arm1.oci`)**: An Oracle Cloud instance hosting the routing, identity, orchestration (Pangolin, Komodo, Pocket-ID, Infisical), and artifact storage (Garage S3).
2. **Workload Host (`bunchloch` / Hetzner)**: High-performance environments executing memory-intensive workloads (Dagster, LanceDB embeddings, SpacetimeDB game state, local AI inference) connected via zero-trust WireGuard tunnels.

---

### Step 1: Secret Hydration (Infisical + Mise)
**Never manually create `.env` files.** The platform uses `mise` directory hooks and a `locket` sidecar pattern to inject secrets securely.

1. Ensure the `.infisical.env` template contains your required structure.
2. Initialize and synchronize the vault:
   ```bash
   cd scripts/infisical/
   bun run init-vault.ts
   ```
   *(This syncs local secrets with the remote `dev-baile` Infisical vault. In production, Locket reads these URIs directly into RAM).*

---

### Step 2: Infrastructure Provisioning (Pulumi & Komodo)
The cloud environment (OCI Control Plane) is bootstrapped completely via IaC (Infrastructure as Code).

1. **Bootstrap the Control Plane:**
   ```bash
   cd infrastructure/pulumi/oci/
   bun run setup.ts save-cloudflare --token <token> --zone-id <zone-id>
   bun run deploy.ts deploy
   ```
2. **What this automates:**
   * Pulumi provisions an ARM Ampere A1 instance.
   * Modifies Cloudflare DNS and WAF rules.
   * Flushes `iptables` and regenerates the Ansible inventory automatically.
   * Executes the Ansible playbook (`infrastructure/ansible/playbooks/deploy-infrastructure.yml`) which installs Docker, Komodo Core, and Pangolin.

---

### Step 3: Zero-Trust Networking (Pangolin)
All services sit behind a secure perimeter consisting of Traefik, CrowdSec, and Pocket ID (Passkeys/OIDC).

1. Spin up the Pangolin network overlay locally:
   ```bash
   cd infrastructure/pangolin/
   docker compose -f compose.yaml -f sidecar.yaml up -d
   ```
2. **Synchronize Blueprints**: Dynamically map local and remote services (like `*.cianfhoghlaim.ie`) to internal stack ports securely over WireGuard:
   ```bash
   ./scripts/sync-blueprints.sh
   ```

---

### Step 4: The Machine Learning Intelligence Layer (`meaisínfhoghlaim`)
This quadrant handles extracting, mapping, and structuring the raw educational data into a semantic knowledge base.

1. Unstructured documents are processed through strict type-safe schemas utilizing **BAML** (Boundary AI Markup Language). 
2. The structured data is ingested into **Cognee** (graph pipeline routing) and **Graphiti** (temporal tracking to build curriculum prerequisites). 
3. *Note: Local development spins up LanceDB/Neo4j endpoints implicitly when activating `tuatha`.*

---

### Step 5: Orchestrating the Lakehouse Data Pipelines (`oideachais`)
Dagster handles the stateful processing of syllabus extraction, metadata generation, and data lake loading.

1. **Start the Orchestrator:**
   ```bash
   cd oideachais/data_platform
   uv sync
   dagster dev -m dagster_defs.definitions
   ```
2. **Execute DLT Extraction:**
   Inside the Dagster UI, trigger the `dlt` pipelines (e.g., `ireland_curriculum`). 
   *Tip: Ensure `os.environ['USE_LOCAL_SCRAPES'] = 'true'` to hit the `stedding/ingest_queue/` cache, avoiding costly Firecrawl API rate-limits.*
3. Data is loaded into **Garage S3** (PDFs) and partitioned into **MotherDuck** (relational queries) or the local `curriculum_unified.duckdb`.

---

### Step 6: Deploying the Application Layer (Tuatha & TanStack Start)
The edge layer consumes the data for the MMO gamification and web frontends.

1. **Start the Edge MMO Layer (`tuatha`):**
   ```bash
   cd tuatha/
   docker compose -f docker-compose.yaml -f compose.dev.yaml up -d
   ```
   *This starts:*
   * **SpacetimeDB** (`localhost:3011`): The ECS database/server handling real-time multiplayer states.
   * **x402 Middleware**: An ASGI router that intercepts API calls to AI agents. It checks SpacetimeDB identities to deduct `Pinginn`/`Screpall` tokens prior to executing LLM generation tasks.

2. **Start the Awen Hub Frontend (`oideachais` Web App):**
   ```bash
   cd oideachais/web_app
   bun install
   bun run dev
   ```
   *This TanStack Start application connects to MotherDuck (via `web_app/src/server/motherduck.js` proxy) and streams the agent outputs using CopilotKit (`AgUI`).*
