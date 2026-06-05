# Komodo — KCG Summary

## What It Is
Komodo is an open-source container orchestration platform by Moghtech. It provides GitOps-driven deployment management with a web UI, API, and CLI — syncing Docker Compose stacks from a Git repository across multiple servers.

## Why This Matters for Kings' College Galway
Komodo is the deployment engine for all 89 Docker Compose stacks in the `infrastructure/stacks/` directory. Every stack change committed to Forgejo is automatically synced and deployed by Komodo to the correct server (arm1-oci, cax41-hetzner, or bunchloch MacBook). This GitOps loop is what makes the infrastructure reproducible.

## Key Patterns
- **GitOps sync**: Komodo watches Forgejo repositories and applies compose.yaml + sidecar.yaml on change
- **Multi-server**: One Komodo Core manages Periphery agents on all 3 physical hosts
- **Pangolin integration**: All stacks automatically register as private Pangolin resources
- **Locket sidecar**: Secrets injected via Infisical at runtime, never in compose files

## Source Files
Full source code was removed (2026-06-05). Available at <https://github.com/moghtech/komodo>. The live deployment configs are in `infrastructure/stacks/infrastructure/komodo/`.
