---
name: tuatha-platform
description: Tuatha Celtic Educational MMO + crypteolas crypto platform quadrant router. Use for routing changes to the tuath uv workspace (game engine, Babylon.js 3D client, Rust + SpacetimeDB server, BAML Celtic content extraction, Dagster assets, SIWE auth, x402 micropayments).
---

# Tuatha Platform — Celtic MMO + Crypto

## When to use this skill

Use when you need to:

- "Route a change to the right tuatha/ sub-module"
- "Add a new 3D scene to the Tuatha game client"
- "Wire BAML Celtic content extraction for a new lesson"
- "Add a Dagster asset for the tuatha content pipeline"
- "Set up SIWE auth or x402 micropayments"
- "Configure FalkorDB + LanceDB for the tuatha knowledge graph"

## Overview

The `tuatha/` quadrant houses the **Celtic Educational MMO**
+ **crypteolas crypto platform**. It is one of the 4 quadrants
of the Cianfhoghlaim monorepo and is registered as a top-level
uv workspace member.

The 4 sub-modules:

| Path | Tech | Purpose |
|:--|:--|:--|
| `tuatha/game/` | Babylon.js (TS) | 3D game client (the MMO front-end) |
| `tuatha/crates/` | Rust + SpacetimeDB | Game engine (the MMO server) |
| `tuatha/crypteolas/` | Python + Bitcoin/Ethereum/Solana | Crypto data platform |
| `tuatha/ui/` | TanStack Start | Web front-end for the educational game |

The tuatha quadrant has its own Dagster code-location at
`tuatha/dg.toml` and contributes BAML schemas to
`baml_src/ui_components.baml` and `baml_src/image_generation.baml`.

The BAML schemas for the tuatha UI components are in
`baml_src/ui_components.baml` and `baml_src/image_generation.baml`.

## Quick routing table (from `tuatha/AGENTS.md`)

When working in `tuatha/`, route to the right sub-area:

| Working on | Read | Skill |
|:--|:--|:--|
| 3D scenes, MMO client | `tuatha/game/` | `.agents/skills/babylonjs/` |
| Rust + SpacetimeDB server | `tuatha/crates/` | (SpacetimeDB — TBD skill) |
| Crypto data platform | `tuatha/crypteolas/` | (per-asset skills) |
| Web front-end | `tuatha/ui/` | `.agents/skills/tanstack-start/` |
| BAML Celtic content | `baml_src/ui_components.baml` | `.agents/skills/baml/` |
| Dagster assets | `tuatha/dg.toml` + `tuatha/dagster_assets/` | `.agents/skills/dagster/` |
| Knowledge graph | `tuatha/knowledge_graph/` | `.agents/skills/falkordb/` |
| SIWE auth | `tuatha/auth/siwe.py` | (SIWE — TBD skill) |
| x402 micropayments | `tuatha/crypteolas/x402.py` | (x402 — TBD skill) |
| Celtic-language models | `oideachais/baml_src/celtic_linguistics.baml` | `.agents/skills/celtic-language-ai/` |
| Dagger CI/CD for the tuatha/ build | `.dagger/` | `.agents/skills/dagger/` |

## Quick Start

The canonical tuatha/ quick start (corrected from
`docs/06-product/TUATH_QUICKSTART.md`):

```bash
# 1. Start the backend (Postgres + FalkorDB + LanceDB + MinIO)
cd tuatha/
docker compose up -d

# 2. Sync the Python deps (crypteolas + BAML + Dagster)
uv sync

# 3. Start the Rust + SpacetimeDB game server
cd crates/
cargo run --release

# 4. Start the game client (Babylon.js)
cd game/
bun dev

# 5. Start the web front-end (TanStack Start)
cd ui/
bun dev
```

The 4 dev servers run in parallel on different ports:
- Postgres: 5432
- FalkorDB: 6379
- LanceDB: 8181
- Game server: 3000 (HTTP) + 3001 (WebSocket)
- Game client: 8080 (dev)
- Web front-end: 3002

## Project structure (KCG `tuatha/`)

```
tuatha/
├── AGENTS.md                      ← entry point (this skill is the upgrade)
├── DEVELOPMENT.md                 ← 593-line developer guide
├── README.md                      ← 42k README (product spec)
├── game/                          ← Babylon.js 3D game client
│   ├── src/
│   │   ├── main.ts                ← entry point; bootstraps Engine
│   │   ├── scenes/                ← one file per scene
│   │   ├── components/            ← reusable 3D components
│   │   ├── physics/               ← Havok setup
│   │   ├── particles/              ← particle VFX
│   │   ├── state/                  ← Convex real-time sync
│   │   ├── llm/                    ← LiteLLM NPC dialogue
│   │   ├── baml/                   ← BAML scene extraction
│   │   └── audio/                  ← spatial audio
│   ├── assets/
│   │   ├── models/                 ← .glb / .gltf
│   │   ├── textures/                ← .png / .ktx2
│   │   └── audio/                   ← .mp3 / .ogg
│   └── index.html
├── crates/                        ← Rust + SpacetimeDB game engine
│   ├── Cargo.toml
│   ├── src/
│   │   ├── lib.rs                 ← entry point
│   │   ├── modules/                ← SpacetimeDB modules
│   │   ├── reducers/               ← game logic
│   │   └── api/                    ← HTTP API
│   └── tests/
├── crypteolas/                    ← Python crypto data platform
│   ├── pyproject.toml
│   ├── src/
│   │   ├── bitcoin/                ← Bitcoin RPC
│   │   ├── ethereum/               ← Ethereum RPC
│   │   ├── solana/                 ← Solana RPC
│   │   ├── x402.py                 ← micropayments
│   │   └── settlement.py           ← SpacetimeDB settlement
│   └── tests/
├── ui/                            ← TanStack Start web front-end
│   ├── app.config.ts
│   ├── src/
│   │   ├── routes/                 ← file-based routes
│   │   ├── components/             ← reusable React components
│   │   └── lib/                    ← utilities
│   └── package.json
├── dagster_assets/                ← Dagster assets for the tuatha pipeline
│   ├── celtic_curriculum.py
│   ├── mythology_content.py
│   └── *_embeddings.py
├── baml_src/                      ← BAML schemas (re-exports from /baml_src/)
├── knowledge_graph/                ← FalkorDB queries for Celtic mythology
├── auth/                           ← SIWE (Sign-In With Ethereum)
├── crypteolas/                     ← crypto data platform
├── dg.toml                         ← Dagster code-location config
└── pyproject.toml
```

## Key endpoints

| Endpoint | Server | Notes |
|:--|:--|:--|
| `http://localhost:3000/...` | Rust + SpacetimeDB | Game server (HTTP) |
| `ws://localhost:3001/...` | Rust + SpacetimeDB | Game server (WebSocket) |
| `http://localhost:3002/...` | TanStack Start | Web front-end |
| `http://localhost:8080/...` | Babylon.js dev server | Game client dev |
| `http://localhost:3000/api/auth/siwe` | Hono | SIWE auth (Sign-In With Ethereum) |
| `http://localhost:3000/api/search` | Hono | Hybrid search (FalkorDB + LanceDB) |
| `http://localhost:3000/api/curriculum` | Hono | Celtic curriculum (BAML-extracted) |
| `http://localhost:3000/api/mythology` | Hono | Celtic mythology (FalkorDB) |
| `ws://localhost:3000/a2ui` | AG-UI | CopilotKit A2UI agent events |
| `http://localhost:3000/api/x402/pay` | Hono | x402 micropayment endpoint |

## Dagster assets (KCG tuatha pipeline)

The tuatha/ quadrant runs the following Dagster assets:

- `celtic_curriculum` — BAML extraction of Celtic curriculum
  (Irish, Welsh, Scottish Gaelic, Breton) from NCCA + WJEC +
  SQA + CBAC PDFs
- `mythology_content` — extraction of Celtic mythology
  content (the Tuatha Dé Danann, Fionn mac Cumhaill, etc.)
  from leabharlann/zotero + leabharlann/gaeilge
- `celtic_embeddings` — BGE-M3 embeddings of the Celtic
  curriculum (1024-d, multilingual)
- `mythology_embeddings` — BGE-M3 embeddings of the mythology
  corpus

These assets write to:

- **DuckLake** (canonical lakehouse sink) for the curriculum
- **FalkorDB** (knowledge graph) for the mythology + Celtic
  family tree
- **LanceDB** (vector search) for the embedding indexes

The Dagster code-location is registered at `tuatha/dg.toml`
and the assets are in `tuatha/dagster_assets/`.

## KCG-specific env vars

```bash
# Database
TUATHA_POSTGRES_URL=postgres://tuatha:tuatha@localhost/tuatha
TUATHA_FALKORDB_URL=redis://localhost:6379
TUATHA_LANCEDB_URI=./lancedb_data

# LLM
LITELLM_API_BASE=https://gateway.pydantic.dev/v1
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...

# Crypto
TUATHA_BITCOIN_RPC_URL=http://localhost:8332
TUATHA_ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/...
TUATHA_SOLANA_RPC_URL=https://api.mainnet-beta.solana.com

# Auth
TUATHA_SIWE_DOMAIN=tuatha.cianfhoghlaim.ie
TUATHA_SIWE_NONCE_SECRET=...

# Observability
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
```

## When to use this skill

✅ **Use when:**
- You're working in `tuatha/`
- You're adding a new 3D scene, Dagster asset, or Celtic
  content asset
- You need to set up SIWE auth, x402 micropayments, or
  FalkorDB queries for the game
- You need to deploy the tuatha stack to `bunchloch` or
  `arm1-oci`

❌ **Don't use when:**
- You're working in `oideachais/` (use
  `.agents/skills/oideachais-pipeline/SKILL.md`)
- You're working in `meaisinfhoghlaim/` (use
  `.agents/skills/meaisinfhoghlaim-platform/SKILL.md`)
- You're working in `croilar/` (use
  `.agents/skills/croilar-portfolio/SKILL.md`)

## Cross-references

- `tuatha/AGENTS.md` — the existing entry point (this skill
  is the expanded version)
- `tuatha/DEVELOPMENT.md` — 593-line developer guide
- `tuatha/README.md` — 42k product spec (read for product
  context)
- `.agents/skills/babylonjs/SKILL.md` — the Babylon.js 3D
  engine (used in `tuatha/game/`)
- `.agents/skills/tanstack-start/SKILL.md` — the TanStack
  Start front-end (used in `tuatha/ui/`)
- `.agents/skills/baml/SKILL.md` — the BAML extraction
  language (used in `tuatha/dagster_assets/`)
- `.agents/skills/dagster/SKILL.md` — the Dagster orchestrator
  (used to schedule tuatha assets)
- `.agents/skills/celtic-language-ai/SKILL.md` — the Celtic
  language models
- `.agents/skills/dagger/SKILL.md` — the Dagger CI/CD (used
  to build the tuatha/ stack)
- `.agents/skills/hono/SKILL.md` — the Hono API layer (used
  in the tuatha/ backend)
- `.agents/skills/copilotkit/SKILL.md` — the CopilotKit UI
  (the A2UI agent)

## OpenSpec

- `openspec/specs/tuatha-platform/spec.md` — the canonical
  spec for the tuatha quadrant

## Resources

- Babylon.js: <https://www.babylonjs.com/>
- SpacetimeDB: <https://spacetimedb.com/>
- TanStack Start: <https://tanstack.com/start>
- SIWE: <https://docs.login.xyz/
- x402: <https://www.x402.org/>
- KCG `tuatha/`: the Celtic MMO + crypto platform
