---
title: 'Tuath Celtic Educational MMO'
domain: 'architecture'
status: 'stable'
description: 'The tuatha/ Celtic MMO quadrant. FastAPI + Axum + Babylon.js + Crypteolas + x402.'
read_when:
  - working in tuatha/
  - extending the MMO or the Crypteolas token
updated: '2026-06-13'
supersedes: []
truth: sole
ccc_query_hints:
  - tuath mmo
  - celtic educational mmo
  - babylon crypteolas x402
---

# Tuath Celtic Educational MMO

> The `tuatha/` quadrant is one of the 5 in the Cianfhoghlaim monorepo.
> For the project identity + quadrant map, see
> [`docs/00-core/CLAUDE.md`](../../00-core/CLAUDE.md).

Tuath is a gamified Celtic language learning platform that combines an
MMO-style game world with AI-powered educational content. It exposes:

- a **FastAPI backend** (Python) — REST API with authentication and content serving
- an **Axum API** (Rust) — payment-protected premium endpoints via x402
- **Google ADK agents** — multi-agent orchestration for educational support
- a **TanStack Start frontend** — modern React SSR admin
- a **Babylon.js game client** — 3D browser-based game engine
- a **SpacetimeDB module** — real-time multiplayer synchronization
- a **Crypteolas token** — x402 payments for premium content; see [`docs/06-product/crypteolas.md`](../../06-product/crypteolas.md)

## Workspace members

`tuatha/` is a uv-workspace **member** with **3 sub-members**:

| Sub-member | Purpose |
|---|---|
| `tuatha/codeolas/` | Code intelligence library (Tree-sitter + CocoIndex; ingest of code repos) |
| `tuatha/crypteolas/` | Crypto / DeFi research (GitHub, protocols, analytics) |
| `tuatha/apps/crypteolas_demo/` | Demo app |

## Front-end topology

`tuatha/ui/` uses **Babylon.js** (not TanStack). It is the *only*
front-end in the monorepo that does not use TanStack. See
[`docs/05-web/frontend-topology.md`](../../05-web/frontend-topology.md)
for the full topology.

## Data plane

- **In-game state**: SpacetimeDB (real-time, low-latency).
- **Premium content**: served from `oideachais/` (DuckLake) — paid
  via x402 micro-transactions in Crypteolas token.
- **Dagster assets**: `tuatha/dagster_assets/` for the MMO's
  curriculum-in-game asset graph (separate from `oideachais/dagster_defs/`).

## Where the canonical docs live

- Babylon.js / game engine: [`docs/06-product/babylonjs.md`](../../06-product/babylonjs.md)
- Crypteolas / x402: [`docs/06-product/crypteolas.md`](../../06-product/crypteolas.md)
- Game dev: [`docs/06-product/game-development.md`](../../06-product/game-development.md)
- Front-end topology: [`docs/05-web/frontend-topology.md`](../../05-web/frontend-topology.md)
- Educational product: [`docs/06-product/educational-platform.md`](../../06-product/educational-platform.md)
- Celic MMO design: [`docs/06-product/celtic-mmo.md`](../../06-product/celtic-mmo.md)

## See also

- [`tuatha/DEVELOPMENT.md`](../../../tuatha/DEVELOPMENT.md) — runtime README
- [`tuatha/README.md`](../../../tuatha/README.md) — project overview
- [`tuatha/gaeilge.md`](../../../tuatha/gaeilge.md) — Irish-language notes
