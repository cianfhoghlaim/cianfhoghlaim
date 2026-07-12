# SiYuan — Block-based Note-taking

Block-based, local-first, bidirectional-linking note-taking app.
Supports Markdown, databases, math (KaTeX), and graph views.

## Architecture

- **Container:** `siyuan` (b3log/siyuan:v3.1.0)
- **Port:** 6806 (Web UI)
- **Storage:** Local workspace at `/siyuan/workspace`
- **Host:** bunchloch (MacBook M4 Max)

## Files (6-file GOLD_STANDARD)

| File | Purpose |
|:--|:--|
| `compose.yaml` | Base compose — no Locket refs |
| `compose.dev.yaml` | Local dev override (no-op locket) |
| `sidecar.yaml` | Locket sidecar (Infisical) |
| `secrets.env` | Infisical URI template |
| `pangolin.yaml` | Pangolin private-resource route |
| `blueprint.yaml` | Pangolin private-resource blueprint |
| `.env.example` | Non-secret dev defaults |
| `.env.dev` | Dev secrets (gitignored) |

## Usage

```bash
# Production
docker compose -f compose.yaml -f sidecar.yaml up -d

# Development
docker compose -f compose.yaml -f compose.dev.yaml -f sidecar.yaml up -d
```

## Health check

```bash
wget --spider http://localhost:6806/
```
