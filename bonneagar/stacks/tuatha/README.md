# Tuatha — Educational MMO + Celtic Curriculum Game World

## Overview

Tuatha (Irish: "tribe / people") is the educational Massive Multiplayer Online (MMO) layer of the Cianfhoghlaim platform. It pairs a Babylon.js 3D game client (browser-side, MapLibre-native) with a Python + DuckDB + LanceDB backend, exposing a Celtic-curriculum knowledge graph as explorable terrain. Tuatha is the only stack in the platform that is **publicly reachable** — the game UI lives behind TinyAuth + rate limiting but does not require login to enter the world.

## Why This Matters for Kings' College Galway

Tuatha is the project's gamification + immersive-learning surface. Where Croílár (internal) and Cianfhoghlaim (curriculum-data) are read/write platforms for staff, Tuatha is the public face — a place where students pilot avatars through procedurally-generated Celtic landscapes, learn Irish (Gaeilge) vocabulary in context, and run quests tied to the BIEP Leaving Certificate syllabus. The Pangolin + Komodo + Infisical stack is used here to (a) tighten the public surface to three named routes (`tuath-api`, `tuath.cianfhoghlaim.ie`, `tuath-ui`), (b) inject all LLM + payment + game secrets through the Locket sidecar instead of hardcoding them, and (c) ship TinyAuth passkey auth (via Pocket ID) as the gate for the API + UI surfaces.

## Key Features

- **Babylon.js 3D game client** — WebGL/WebGPU procedural terrain, Celtic architectural vocabulary, MapLibre overlay for Irish-language place-name tags
- **SpacetimeDB multiplayer state** — sub-millisecond state sync for avatars + quests + classroom events
- **DuckDB + LanceDB backend** — local-first analytics, BIEP syllabus lookup, curriculum-graph RAG
- **Langfuse + MLflow observability** — LLM call tracing + experiment tracking for the in-game tutor NPC
- **dlt data ingestion** — player asset registry + credential events feed into the central `md:oideachais` MotherDuck lakehouse

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/tuatha
cp .env.example .env.local  # edit values as needed
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on `bunchloch` (MacBook M4). Tuatha may be brought up after Pocket ID (OIDC auth) and Pangolin (proxy) — its API + UI surfaces require Pocket ID's OIDC issuer for the TinyAuth middleware.

```bash
komodo deploy stack tuatha --server bunchloch
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `TUATH_PORT` | No | API listening port | `8002` |
| `LANGFUSE_HOST` | No | LLM tracing endpoint | `http://langfuse:3000` |
| `LANGFUSE_PUBLIC_KEY` | Yes | Langfuse public key | _(from Locket)_ |
| `LANGFUSE_SECRET_KEY` | Yes | Langfuse secret key | _(from Locket)_ |
| `OPENAI_API_KEY` | Yes | In-game NPC LLM (GPT-4o-mini default) | _(from Locket)_ |
| `ANTHROPIC_API_KEY` | No | Claude for the curator NPC (optional) | _(from Locket)_ |
| `X402_PAYMENT_URL` | No | x402 micro-payment endpoint for in-game currency | _(from Locket)_ |
| `LOCKET_MODE` | No | `watch` (default), `oneshot`, or `disabled` | `watch` |

## Access

- **Game**: `https://tuath.cianfhoghlaim.ie` (public, rate-limited)
- **API**: `https://tuath-api.cianfhoghlaim.ie` (TinyAuth passkey-gated)
- **UI Dashboard**: `https://tuath-ui.cianfhoghlaim.ie` (TinyAuth passkey-gated)

## Sources

- **Player assets pipeline**: `tuatha/dlt/player_assets.py` — dlt source emitting rows to `cianfhoghlaim.tuatha.player_assets` (MotherDuck DuckLake)
- **Credential events pipeline**: `tuatha/dlt/credential_events.py` — dlt source emitting rows to `cianfhoghlaim.tuatha.credential_events` (MotherDuck DuckLake + Langfuse trace)
- **Bootstrap**: `tuatha/scripts/bootstrap.sh` — one-command local dev (build images + populate fixtures + run dlt)

## Onboarding (First Time)

```bash
# 1. Run the TUI onboarding wizard
./scripts/onboard-tuatha.sh

# 2. Wire to Pangolin + Komodo + Infisical
./scripts/wire-tuatha.sh

# 3. Bind Pocket ID as Resource IdP
./scripts/wire-tuatha-resource-idp.sh

# 4. Schedule secret rotation (cron)
./scripts/rotate-tuatha-secrets.sh --install-cron
```

## Upstream

- **Babylon.js**: <https://www.babylonjs.com>
- **SpacetimeDB**: <https://spacetimedb.com>
- **MapLibre**: <https://maplibre.org>
- **dlt**: <https://dlthub.com>
- **LanceDB**: <https://lancedb.com>
- **Langfuse**: <https://langfuse.com>
