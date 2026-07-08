# Kavita — Ebook + Manga Reader

Self-hosted ebook + manga reader with OPDS support for cross-device
sync (iOS/Android/Kobo).

## Architecture

- **Container:** `kavita` (jvmouse/kavita:0.8.6)
- **Port:** 5000 (Web UI)
- **Library mount:** `/stedding/library` (host) → `/library` (container, RO)
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
wget --spider http://localhost:5000/api/Health
```
