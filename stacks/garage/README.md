# Garage — Distributed S3-Compatible Storage

## Overview

Garage is a lightweight, self-hosted S3-compatible object storage system built in Rust by the Deuxfleurs collective. It uses a CRDT-based consensus protocol to provide geo-distributed, resilient storage without the complexity of traditional distributed systems. Each Garage instance can operate standalone or as part of a multi-node cluster.

## Why This Matters for Kings' College Galway

Garage is the foundational storage substrate for the entire data platform. Every study asset image, every Parquet data file, every DuckLake table, every LanceDB vector index lands in Garage S3 before being catalogued by Lakekeeper. Running our own S3-compatible storage eliminates cloud egress fees on the ~2 TB of curriculum data, HuggingFace model weights, and generated assets. The CRDT architecture means storage survives individual node failures — critical when exam paper processing runs can take hours.

## Key Features

- **S3-compatible API** — Drop-in replacement for AWS S3; works with boto3, s3fs, DuckDB S3 connector
- **CRDT-based consensus** — No single leader; nodes converge on a consistent state without Raft/Paxos complexity
- **Geo-distributed** — Deploy nodes across OCI and Hetzner for regional resilience
- **Multi-tenant** — Bucket-level access control with access key/secret key pairs
- **Lightweight** — Single binary, ~30 MB memory at idle, written in Rust

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/garage
docker compose up -d
```

### Docker Compose (Production with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)

Deployed via Komodo on arm1-oci. Komodo syncs from Forgejo and applies `compose.yaml` + `sidecar.yaml`. The `garage.toml` configuration file is mounted read-only from the stack directory. Locket resolves `GARAGE_RPC_SECRET` and `GARAGE_ADMIN_TOKEN` from the Infisical `dev-baile` vault.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `GARAGE_RPC_PORT` | No | RPC inter-node communication port | `3901` |
| `GARAGE_S3_API_PORT` | No | S3 API endpoint port | `3900` |
| `GARAGE_K2V_API_PORT` | No | K2V (key-to-value) API port | `3902` |
| `GARAGE_WEB_PORT` | No | Web console port | `3903` |
| `GARAGE_ADMIN_PORT` | No | Admin API port | `3904` |
| `RUST_LOG` | No | Log level | `garage=info` |
| `RUST_BACKTRACE` | No | Backtrace on panic | `1` |

## Access

- **S3 API**: `http://localhost:3900` (local), `s3.cianfhoghlaim.ie` (Pangolin-routed)
- **Admin API**: `http://localhost:3904`
- **Auth**: Access key / secret key pairs managed via Garage CLI

## Upstream

- **Repository**: <https://git.deuxfleurs.fr/Deuxfleurs/garage>
- **Documentation**: <https://garagehq.deuxfleurs.fr/documentation/quick-start/>
- **Latest**: v1.0.1 (December 2024) — first stable release after 4 years of development; production S3 compatibility

## Screenshot

Garage is a headless storage service. The web console at port 3903 provides a minimal dashboard showing cluster status, node health, and bucket layout.
