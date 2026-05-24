# Infrastructure (The Foundation)

This quadrant provisions and secures the underlying compute, tunneling, and machine identity for the `cianfhoghlaim` stack. It ensures a Sovereign, Zero-Trust environment across both the Oracle Cloud (OCI) control plane and the local MacBook workload host.

## Core Components

### 1. OCI Provisioning (Pulumi)
*   **Location**: `pulumi/oci/`
*   **Function**: Bootstraps an Ampere A1 (ARM) instance (`arm1-oci`) on the Oracle Cloud free tier. 
*   **Automation**: Executes a seamless handoff. Once the VM is provisioned, Pulumi updates the Infisical vault with the new public IP, regenerates the Ansible inventory, and triggers the playbook to install Pangolin and Komodo.

### 2. Fleet Orchestration (Komodo)
*   **Location**: `komodo/`
*   **Function**: Edge-first fleet orchestrator. It manages our declarative Docker Compose blueprints (e.g., the `oideachais` stack) across disconnected servers without requiring Kubernetes.

### 3. Zero-Trust Mesh Networking (Pangolin)
*   **Location**: `pangolin/`
*   **Function**: We utilize Pangolin (backed by WireGuard) to replace Cloudflare Tunnels for internal service-to-service communication. It creates a secure outbound-only mesh, allowing the local MacBook (`bunchloch`) to serve heavy ML workloads to the OCI control plane without opening any inbound firewall ports.

### 4. Edge Security & Identity-Aware Proxy (Pocket ID + TinyAuth)
*   **Identity**: `Pocket ID` handles OIDC and Passkey (WebAuthn) authentication.
*   **Gatekeeper**: `TinyAuth` runs as a `forwardAuth` middleware on Traefik.
*   **Flow**: Any private service defined in Komodo simply attaches the `pangolin.resource.middlewares=tinyauth` label. Traefik pauses requests to these services, bounces them to Pocket ID for auth, and only releases traffic once a valid JWT is issued.

### 5. Centralized Secrets (Infisical + Locket)
*   **Function**: No manual `.env` files are permitted. All machine identities, OCI keys, and LLM API tokens live in the `dev-baile` Infisical vault.
*   **Injection**: `scripts/infisical/init-vault.ts` parses the local `.infisical.env` template to seed the vault. Docker clusters use the `locket` sidecar to dynamically inject these secrets at runtime.

## Cloudflare WAF & DNS
Cloudflare manages the public DNS. We ensure that records pointing to `auth.cianfhoghlaim.ie` and `komodo.cianfhoghlaim.ie` are set to `proxied: true` so they benefit from Cloudflare's Web Application Firewall (WAF) and DDoS protection before hitting the Pangolin mesh.
