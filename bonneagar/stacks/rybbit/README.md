# Rybbit — Self-Hosted RabbitMQ Management Alternative

## Overview

Rybbit is an open-source, self-hosted web UI for managing RabbitMQ message brokers. It provides a clean alternative to the built-in RabbitMQ management plugin, with message inspection, queue management, exchange configuration, and real-time metrics. Built as a lightweight, focused alternative for teams that want RabbitMQ management without the full plugin overhead.

## Why This Matters for Kings' College Galway

The curriculum extraction pipeline involves multiple asynchronous processing stages: DLT ingestion → Dagster orchestration → LLM extraction → embedding generation → knowledge graph construction. These stages communicate through message queues rather than direct function calls, enabling retry logic, backpressure handling, and parallel processing. Rybbit provides visibility into these message flows — which queue is backing up, which consumer is slow, which message failed and why — making the asynchronous pipeline debuggable without SSH-ing into containers and running `rabbitmqctl`.

## Key Features

- **Queue monitoring** — Real-time message counts, consumer counts, throughput
- **Message inspection** — View, requeue, or delete individual messages
- **Exchange management** — Configure topic, direct, fanout, and header exchanges
- **Lightweight** — Minimal resource footprint compared to the full RabbitMQ plugin
- **Multi-vhost** — Manage multiple virtual hosts from a single UI

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/rybbit
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Connects to the RabbitMQ broker running in the Dagster or n8n stacks.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `RABBITMQ_HOST` | Yes | RabbitMQ broker hostname | — |
| `RABBITMQ_PORT` | No | RabbitMQ management port | `15672` |
| `RABBITMQ_USER` | Yes | RabbitMQ username | — |
| `RABBITMQ_PASSWORD` | Yes | RabbitMQ password | — |
| `RYBBIT_PORT` | No | Web UI port | `4000` |

## Access

- **Web UI**: `https://rybbit.cianfhoghlaim.ie` (private, Admin role)
- **Auth**: Pocket ID SSO (read-only public view available for Members)

## Upstream

- **Repository**: <https://github.com/rybbit/rybbit>
- **Latest**: Active development — message inspection, queue management improvements, multi-vhost support

## Screenshot

Rybbit's web UI shows a dashboard with real-time queue metrics (message rates, consumer utilisation), a queue browser with message peek/inspect capability, an exchange topology visualiser showing bindings, and a virtual host selector for navigating between different message environments.
