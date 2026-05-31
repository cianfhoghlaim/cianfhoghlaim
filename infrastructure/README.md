# Infrastructure (The Foundation)

This quadrant provisions and secures the underlying compute, tunneling, and machine identity for the `cianfhoghlaim` stack. It ensures a Sovereign, Zero-Trust environment across both the Oracle Cloud (OCI) control plane and the local MacBook workload host.

## Infrastructure as Code (IaC) Philosophy

**Ansible is the absolute source of truth.** We do not rely on manual `.local` environment overrides or standalone configuration scripts in production.
- Playbooks (`infrastructure/ansible/playbooks/`) and Roles define the desired state.
- Local deployment directories (like `.local/komodo` on the MacBook) are **ephemeral deployment targets**. If you edit files there manually, they will be overwritten on the next Ansible run.

## Core Architecture

### 1. OCI Provisioning (Pulumi)
*   **Location**: `infrastructure/pulumi/oci/`
*   **Function**: Bootstraps an Ampere A1 (ARM) instance (`arm1-oci`) on the Oracle Cloud free tier. 
*   **Automation**: Executes a seamless handoff. Once the VM is provisioned, Pulumi updates the Infisical vault with the new public IP, regenerates the Ansible inventory, and triggers the playbook to install Pangolin and Komodo.

### 2. Fleet Orchestration (Komodo)
*   **Location**: `infrastructure/komodo/`
*   **Function**: Edge-first fleet orchestrator. It manages our declarative Docker Compose blueprints (e.g., the `oideachais` stack) across disconnected servers without requiring Kubernetes.
*   **Architecture**:
    - **Komodo Core** (Control Plane) runs on the MacBook (`bunchloch`).
    - **Komodo Periphery** (Agents) run on edge nodes (e.g., Oracle Cloud).
    - *Crucial Detail*: Periphery agents connect securely *outbound* via WebSockets (`wss://komodo.cianfhoghlaim.ie`). This means edge nodes do not need inbound firewall ports opened or complex reverse tunnels configured to receive instructions.

### 3. Zero-Trust Mesh Networking (Pangolin)
*   **Location**: `infrastructure/pangolin/`
*   **Function**: Pangolin (backed by WireGuard) creates a secure outbound-only mesh, eliminating the need for Cloudflare Tunnels or brittle SSH Reverse Tunnels for internal service-to-service communication.
*   **Pangolin Client**: By installing the native Pangolin Client on your devices (like your MacBook), you securely join the WireGuard VPN mesh. This grants direct access to internal subnets/resources across clouds (like the remote Infisical DB or local staging apps) natively, without managing `ssh -R` tunnels.

## Edge Security & Authentication (Pocket ID + TinyAuth)

We use an Identity-Aware Proxy pattern to secure services at the edge without modifying the underlying application code.

*   **Identity**: `Pocket ID` handles OIDC and Passkey (WebAuthn) authentication.
*   **Gatekeeper**: `TinyAuth` runs as a `forwardAuth` middleware on Traefik.
*   **Flow**: `User Request` → `Traefik` → `TinyAuth (Forward Auth)` → `Pocket ID (Passkey/OIDC)` → `Target App`.

### The "Magic" Auth Label
To protect *any* internal stack automatically, you just add **one single label** to its Docker Compose or Pangolin blueprint (`pangolin.yaml`). Traefik will pause the request, bounce the user to Pocket ID for SSO, and only allow traffic through once a valid JWT is issued.

```yaml
    labels:
      - "pangolin.resource.middlewares=tinyauth"
```

## Secrets Management (Infisical + Locket)

No manual `.env` files are permitted. All machine identities, OCI keys, and API tokens live in the `dev-baile` Infisical vault.

### For Developers (Mise Hooks)
- Uses **mise hooks** combined with the **Infisical CLI** to automatically inject secrets when entering a project directory (e.g., `cd oideachais`).
- Executes a fast `infisical export` (~1s) behind the scenes based on a `.env.infisical` template.
- Secrets are automatically unset when you leave the directory for security hygiene.

### For Infrastructure (Locket Sidecar)
- Production Docker clusters use the `ghcr.io/bpbradley/locket:infisical` sidecar container.
- At deployment time, Locket dynamically authenticates to the Infisical API, resolves templates, and injects the raw secrets directly into the application containers (preventing secrets from persisting on disk).

## Deploying Infrastructure Stacks (The Workflow)

Our repository features a unified structure for pre-configured stacks under `infrastructure/stacks/` (e.g., `engineering/litellm`, `storage/dagster`).

Each stack generally contains:
1. `compose.yaml`: The core application definitions.
2. `pangolin.yaml`: The routing and proxy blueprint (adding public domains, ports, and `tinyauth` middleware).

### Step-by-step Komodo Deployment Guide
To deploy a new service and integrate it into the Pangolin mesh:
1. Go to **Komodo UI** → **Stacks**.
2. Create a new Stack pointing to this GitHub repository.
3. Set the path to the desired tool (e.g., `infrastructure/stacks/storage/dagster`).
4. In the Compose Files section, type: `compose.yaml, pangolin.yaml`.
5. Deploy to a Periphery agent (e.g., your MacBook or the Oracle Cloud).
6. **Result**: 
   - Komodo spins up the container.
   - Locket injects the necessary secrets from Infisical.
   - Newt broadcasts the Pangolin labels to Traefik.
   - The app instantly gets a secure, valid subdomain (e.g., `https://dagster.cianfhoghlaim.ie`) protected by Pocket ID SSO!
