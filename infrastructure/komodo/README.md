# Komodo Infrastructure

GitOps-managed infrastructure using Komodo for container orchestration.

## Architecture

This environment implements a decoupled control plane architecture using **Komodo v2.2** and **Pangolin 1.18**:

1. **MacBook (Control Plane):** Runs **Komodo Core**, managing the database, states, and the web UI.
2. **Oracle Cloud Free Tier (Workloads):** Runs **Komodo Periphery**, an execution agent that reports back to Core.
3. **Pangolin Tunnels:** The Oracle instance runs **Newt** (Pangolin client) to securely tunnel out to the MacBook. Oracle Periphery connects back to the Core's private HTTPS endpoint via Pangolin multi-site HA and Private Resources.

## Secrets Management

Secrets are managed via **Infisical** and injected using **Locket** (`ghcr.io/bpbradley/locket:infisical`). 
Locket acts as a sidecar that mounts ephemeral memory (`tmpfs`) to provide runtime secrets strictly to the Docker containers without writing to disk. Development scripts wrap `docker compose` with `locket exec` for CLI injection.

*No legacy passkeys or Infisical API tokens are stored in the git repository or host variables.*

## Requirements

- Komodo Core 2.x
- Periphery v2 pinned docker tags (`ghcr.io/moghtech/komodo-periphery:2`)
- Infisical Secret Manager with Universal Auth Client Secret.
- Pangolin 1.18+ (HTTPS Private Resources)

## Directory Consolidation

*   `core-stack/`: Komodo Core definitions
*   `periphery-stack/`: Komodo Periphery standalone definition
*   `../ansible/`: Main infrastructure provisioning automation
