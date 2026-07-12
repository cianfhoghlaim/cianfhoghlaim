# Beszel — Lightweight Server Monitoring

## Overview

Beszel is a lightweight, self-hosted server monitoring solution consisting of a central Hub (dashboard) and per-host Agents. It collects CPU, memory, disk, network, and Docker container metrics with a clean web UI. Written in Go and Svelte, it is designed as a simpler alternative to Grafana + Prometheus for small-to-medium deployments.

## Why This Matters for Kings' College Galway

The Kings' College Galway infrastructure spans three physical hosts (arm1-oci, cax41-hetzner, bunchloch MacBook) running 89 Docker Compose stacks. Beszel provides a single dashboard showing resource utilisation across all three nodes, alerting when the MacBook's 48 GB unified memory approaches saturation during LLM inference or when the ARM1's 24 GB RAM is strained by concurrent data pipelines. This is operational visibility without the complexity of a full Prometheus/Grafana stack for infrastructure monitoring (Prometheus is reserved for application-level metrics).

## Key Features

- **Multi-host monitoring** — One Hub, multiple Agents; agent binary is <5 MB
- **Docker integration** — Per-container CPU, memory, and network metrics
- **SSH key-based auth** — Agents authenticate to Hub using ed25519 keys
- **Disk and network IO** — Track read/write throughput and disk usage per mount
- **Clean dashboard** — Svelte-based web UI with real-time graphs

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/beszel
docker compose up -d
```

### Deploy Agent on Additional Hosts

```bash
docker compose --profile agent up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. The Beszel Hub runs on the control plane; agents are deployed on each workload host (Hetzner, MacBook) via separate compose files or direct binary installation.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `BESZEL_PORT` | No | Hub dashboard port | `8090` |
| `BESZEL_AGENT_PORT` | No | Agent listening port | `45876` |
| `BESZEL_SSH_KEY` | Yes | SSH public key for agent authentication | — |

## Access

- **Dashboard**: `https://beszel.cianfhoghlaim.ie` (private, Pangolin Member role)
- **Agent**: Internal only (port 45876, not exposed publicly)
- **Auth**: Hub has built-in authentication; agents use SSH key pairs

## Upstream

- **Repository**: <https://github.com/henrygd/beszel>
- **Documentation**: <https://beszel.dev>
- **Latest**: Active development (2025) — Go rewrite with Svelte UI adding Docker container metrics and improved agent communication

## Screenshot

The Beszel Hub dashboard at port 8090 shows a grid of system cards (one per monitored host), each displaying live CPU, memory, disk, and network graphs. Individual host views provide per-container metrics breakdown and historical charts.
