# Pangolin — KCG Summary

## What It Is
Pangolin is an open-source identity-aware reverse proxy by Fosrl. It combines WireGuard VPN tunnels, Traefik reverse proxy, Pocket ID OIDC authentication, and CrowdSec intrusion detection into a single stack for zero-trust service access.

## Why This Matters for Kings' College Galway
Pangolin is the outermost security layer. Every one of the 89 stacks is exposed as a private Pangolin resource behind WireGuard tunnels and Pocket ID SSO. The `pangolin.yaml` and `blueprint.yaml` files in every stack directory define how each service is routed and who can access it.

## Key Patterns
- **Private by default**: All services use private Pangolin resources requiring WireGuard + Pocket ID Member role
- **Traefik middleware**: TinyAuth forward authentication, CrowdSec intrusion detection, TLS termination
- **Gerbil controller**: WireGuard peer management without manual key distribution
- **Docker label-based config**: `pangolin.private-resources.<name>.*` labels on containers

## Source Files
Full source code was removed (2026-06-05). Available at <https://github.com/fosrl/pangolin>. Live deployment configs are in `infrastructure/stacks/infrastructure/pangolin/`.
