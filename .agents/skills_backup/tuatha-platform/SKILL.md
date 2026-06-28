---
name: tuatha-platform
description: Tuatha Celtic Educational MMO + crypteolas crypto platform quadrant router. Use for routing changes to the tuath uv workspace (game engine, Babylon.js 3D client, Rust + SpacetimeDB server, BAML Celtic content extraction, Dagster assets, SIWE auth, x402 micropayments).
---

# Tuatha Platform — Celtic MMO + Crypto

## When to use this skill

Use when you need to:

- "Route a change to the right sruth/tuatha/ sub-module"
- "Add a new 3D scene to the Tuatha game client"
- "Wire BAML Celtic content extraction for a new lesson"
- "Add a Dagster asset for the tuatha content pipeline"
- "Set up SIWE auth or x402 micropayments"
- "Configure FalkorDB + LanceDB for the tuatha knowledge graph"

## Overview

The `sruth/tuatha/` quadrant houses the **Celtic Educational MMO**
+ **crypteolas crypto platform**. It is one of the 4 quadrants
of the Cianfhoghlaim monorepo and is registered as a top-level
uv workspace member.

The 4 sub-modules:

| Path | Tech | Purpose |
|:--|:--|:--|
| `sruth/tuatha/game/` | Babylon.js (TS) | 3D game client (the MMO front-end) |
| `sruth/tuatha/crates/` | Rust + SpacetimeDB | Game engine (the MMO server) |
| `sruth/tuatha/sruth/crypteolas/` | Python + Bitcoin/Ethereum/Solana | Crypto data platform |
| `sruth/tuatha/ui/` | TanStack Start | Web front-end for the educational game |

The tuatha quadrant has its own Dagster code-location at
`sruth/tuatha/dg.toml` and contributes BAML schemas to
`baml_src/ui_components.baml` and `baml_src/image_generation.baml`.

The BAML schemas for the tuatha UI components are in
`baml_src/ui_components.baml` and `baml_src/image_generation.baml`.

## Quick routing table (from `sruth/tuatha/AGENTS.md`)

When working in `sruth/tuatha/`, route to the right sub-area:

| Working on | Read | Skill |
|:--|:--|:--|
| 3D scenes, MMO client | `sruth/tuatha/game/` | `.agents/skills/babylonjs/` |
| Rust + SpacetimeDB server | `sruth/tuatha/crates/` | (SpacetimeDB — TBD skill) |
| Crypto data platform | `sruth/tuatha/sruth/crypteolas/` | (per-asset skills) |
| Web front-end | `sruth/tuatha/ui/` | `.agents/skills/tanstack-start/` |
| BAML Celtic content | `baml_src/ui_components.baml` | `.agents/skills/baml/` |
| Dagster assets | `sruth/tuatha/dg.toml` + `sruth/tuatha/dagster_assets/` | `.agents/skills/dagster/` |
| Knowledge graph | `sruth/tuatha/knowledge_graph/` | `.agents/skills/falkordb/` |
| SIWE auth | `sruth/tuatha/auth/siwe.py` | (SIWE — TBD skill) |
| x402 micropayments | `sruth/tuatha/sruth/crypteolas/x402.py` | (x402 — TBD skill) |
| Celtic-language models | `sruth/oideachais/baml_src/celtic_linguistics.baml` | `.agents/skills/celtic-language-ai/` |
| Dagger CI/CD for the sruth/tuatha/ build | `.dagger/` | `.agents/skills/dagger/` |

## Quick Start

The canonical sruth/tuatha/ quick start (corrected from
`docs/06-product/TUATH_QUICKSTART.md`):

```bash
# 1. Start the backend (Postgres + FalkorDB + LanceDB + MinIO)
cd sruth/tuatha/
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

## Project structure (KCG `sruth/tuatha/`)

```
sruth/tuatha/
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
├── sruth/crypteolas/                    ← Python crypto data platform
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
├── sruth/crypteolas/                     ← crypto data platform
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

The sruth/tuatha/ quadrant runs the following Dagster assets:

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

The Dagster code-location is registered at `sruth/tuatha/dg.toml`
and the assets are in `sruth/tuatha/dagster_assets/`.

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
- You're working in `sruth/tuatha/`
- You're adding a new 3D scene, Dagster asset, or Celtic
  content asset
- You need to set up SIWE auth, x402 micropayments, or
  FalkorDB queries for the game
- You need to deploy the tuatha stack to `bunchloch` or
  `arm1-oci`

❌ **Don't use when:**
- You're working in `sruth/oideachais/` (use
  `.agents/skills/oideachais-pipeline/SKILL.md`)
- You're working in `sruth/meaisinfhoghlaim/` (use
  `.agents/skills/meaisinfhoghlaim-platform/SKILL.md`)
- You're working in `sruth/croilar/` (use
  `.agents/skills/croilar-portfolio/SKILL.md`)

## Cross-references

- `sruth/tuatha/AGENTS.md` — the existing entry point (this skill
  is the expanded version)
- `sruth/tuatha/DEVELOPMENT.md` — 593-line developer guide
- `sruth/tuatha/README.md` — 42k product spec (read for product
  context)
- `.agents/skills/babylonjs/SKILL.md` — the Babylon.js 3D
  engine (used in `sruth/tuatha/game/`)
- `.agents/skills/tanstack-start/SKILL.md` — the TanStack
  Start front-end (used in `sruth/tuatha/ui/`)
- `.agents/skills/baml/SKILL.md` — the BAML extraction
  language (used in `sruth/tuatha/dagster_assets/`)
- `.agents/skills/dagster/SKILL.md` — the Dagster orchestrator
  (used to schedule tuatha assets)
- `.agents/skills/celtic-language-ai/SKILL.md` — the Celtic
  language models
- `.agents/skills/dagger/SKILL.md` — the Dagger CI/CD (used
  to build the sruth/tuatha/ stack)
- `.agents/skills/hono/SKILL.md` — the Hono API layer (used
  in the sruth/tuatha/ backend)
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
- KCG `sruth/tuatha/`: the Celtic MMO + crypto platform

## Sovereign game state (SpacetimeDB + DuckDB-WASM + TanStack + CopilotKit)

The tuatha architecture replaces the traditional 3-tier
MMO stack (headless game server + database + REST API)
with a **sovereign** model: the database *is* the
server, the client carries a local analytical engine,
and the AI agent has direct governed access to both.
This is the "Database-as-Server" + "Thick Client"
synthesis that the Tuath `Anam` and `Ogham` ledgers
require.

### The 4 components

| Layer | Tech | Role |
|:--|:--|:--|
| **Authoritative state** | SpacetimeDB (Rust reducers) | ACID transactions, "Education Tax" calc, Anam state |
| **Application shell** | TanStack Start (Vite, SSR-off for `/play`) | Server Functions proxy LLM API keys; routes; bundler |
| **Analytical engine** | DuckDB WASM (in a Web Worker) | "Global learning velocity", tax-simulation, "what-if" |
| **Agentic semantic binding** | CopilotKit (AG-UI / A2UI) | NL → structured queries against local DuckDB + reducer calls |

### SpacetimeDB: Database-as-Server

SpacetimeDB runs Rust logic **inside the database
transaction loop**. The 4 core `tuatha` tables:

| Entity | Rust struct | Purpose |
|:--|:--|:--|
| `Anam` | `AnamState` | `knowledge_level`, `particle_count`, `color_vector` |
| `Ledger` | `OghamLedger` | `pending_balance`, `synced_balance`, txn history |
| `Tasks` | `TaskLog` | `task_id`, `verification_status`, `timestamp` |
| `Agents` | `MechRequest` | Queue for Olas Mech AI verification tasks |

The **Education Tax** reducer runs in the database —
not the client — so the tax rate is enforced by the
authoritative store. The client only *requests* the
transfer; the DB computes and applies the tax.

The **data flow bifurcation** is critical: SpacetimeDB
owns the *low-frequency state* (ledgers, levels) and
the client handles *high-frequency state* (Anam particle
vector changing 60 times a second) via transient
interpolation. SpacetimeDB's WebSocket uses **SATS-JSON**
(not BSATN) for the client protocol — slower but
JSON-parseable, which feeds directly into DuckDB
without a binary-decode hop.

### DuckDB-WASM: the thick client

The browser runs DuckDB inside a **Web Worker** so the
UI thread stays at 60fps. The pipeline:

1. **Ingestion**: SpacetimeDB `onInsert` event →
   JavaScript object → micro-batch buffer (100ms
   flush or 1000 items).
2. **Insertion**: small batches use parameterised SQL
   `INSERT`; large snapshots (initial table load)
   use **Apache Arrow** via
   `insertArrowFromIPCStream` for 10-100x faster
   ingestion.
3. **Persistence**: DuckDB persists to the **Origin
   Private File System (OPFS)** so the player's
   Anam/Ledger history survives across sessions —
   this is the *Indigenous Data Sovereignty* layer.

The client sends `last_synced_timestamp` to SpacetimeDB
on reconnect and only receives the delta, so re-loads
are O(changes), not O(total history).

### TanStack Start: SSR-off for /play

`/play` and `/dashboard` routes set `ssr: false` —
the server returns a skeletal shell, the JS bundle
loads, the WASM modules init, the WebSocket connects,
*then* the UI renders. Public routes (`/`, `/about`)
keep SSR for SEO.

**Server Functions** (the security boundary):
- `generateCopilotToken()` — runs only on the server,
  signs an ephemeral OpenAI/Anthropic key for the
  CopilotKit client. The browser never sees the
  master `OPENAI_API_KEY`.
- Olas Mech proxy for task verification when
  browser-to-blockchain direct interaction is
  undesirable.

**Vite config** must enable: `vite-plugin-wasm`
(`.wasm` ES imports), `vite-plugin-top-level-await`
(module-level await in DuckDB-WASM init), and
`build.target = "esnext"` to prevent the await
transpilation from breaking WASM instantiation.

### CopilotKit: the agentic semantic layer

`useCopilotReadable` provides the Copilot with the
**DuckDB table schemas** (not the data — that's too
big for the context window). The Copilot then writes
SQL via `useCopilotAction` against the local DuckDB
worker, and the response hydrates the UI.

Example: a player asks "How am I doing in my Irish
lessons?" → the agent generates a SQL query
`SELECT avg(score), count(*) FROM TaskLog WHERE
task_kind = 'gaeilge' AND identity = $me` →
DuckDB returns → CopilotKit renders a chart.

The key insight: **the AI never queries the server**
for analytical questions. The local DuckDB has the
full snapshot; the server only provides deltas.
This makes the AI agent massively cheaper and faster
than a server-side analytics pipeline.

### The "Indigenous Data Sovereignty" angle

The OPFS-persisted DuckDB file is **the player's
data**. They can export it, back it up, or migrate
it to another server. This aligns with the
**Tuath Proof-of-Learning (PoL)** model: the player
*owns* their learning history, and the MMO's role is
to host the synchronous multi-player layer on top.

## Dagster assets for MMO (Hades + BitCraft agentic research)

The sruth/tuatha/ Dagster code-location
(`sruth/tuatha/dagster_assets/`) ships 4 core assets
(`celtic_curriculum`, `mythology_content`,
`celtic_embeddings`, `mythology_embeddings`). The
2026 extension adds 2 new asset groups based on
the **Hades + BitCraft** research-pattern:

- **`hades_asset_pipeline`**: agentic research
  pipeline that scrapes Supergiant Games GDC talks,
  tech blogs, and the SpacetimeDB GitHub repo →
  indexes in a LangGraph Plan-Execute-Verify loop
  → emits per-frame asset specs (Hades hybrid
  3D-to-2D normal-map pipeline).
- **`bitcraft_spacetimedb_sync`**: SpacetimeDB
  `clockworklabs/SpacetimeDB` change-detection +
  Rust SDK release monitor + auto-update of the
  tuatha `crates/` bindings when a breaking
  change is detected.

### The agentic research pipeline (LangGraph DCG)

The Hades+BitCraft research agent runs a directed
cyclic graph (DCG) with 4 nodes:

1. **Planner Node** — decomposes the high-level query
   into sub-tasks (e.g. "Hades 3D-to-2D normal maps"
   → "search GDC Vault", "search r/gamedev", "analyse
   Supergiant tech blog").
2. **Search Node** — DuckDuckGo + Tavily + GDC Vault
   scraper (BeautifulSoup + Selenium with session
   auth for member-only content).
3. **Filter Node** — LLM evaluates URLs, drops
   marketing pages, keeps technical blogs.
4. **Critique Node** — LLM reads scraped content; if
   it lacks specific implementation details, it
   modifies the search query and loops back.

Output is a `ResearchState` TypedDict:

```python
class ResearchState(TypedDict):
    query: str
    sources_found: List[str]
    raw_content: Annotated[List[str], operator.add]
    final_report: str
    iteration_count: int
```

The agent monitors breaking changes in
`clockworklabs/SpacetimeDB` and `godot-rust/gdext` —
if the `spacetimedb-sdk` C# or Rust bindings change
in a way that breaks the tuatha netcode, the asset
emits a `MaterializeResult` with a `breaking_changes`
field that pings the technical director.

### The Hades hybrid 3D→2D pipeline

Supergiant's *Hades* visual identity is a "pre-rendered
isometric projection" — a 3D model rendered once to
2D sprite sheets with normal maps + material IDs +
emissive, then played back as flat sprites. The KCG
extension uses **Unreal Engine 5's Movie Render Queue
(MRQ)** as the source engine, and the final game
client (Godot 4 or Unity 6) as the runtime.

Per-character pipeline:

1. **Animation** in Maya/Blender → imported to UE5.
2. **Staging** in a "Baking Level" with a Turntable
   blueprint.
3. **MRQ capture** with these render passes:
   - **Final Image (RGB)** — the visual look
   - **World Normal (RGB)** — for runtime re-lighting
   - **Opacity (A)** — for masking
   - **Emissive (RGB)** — for the neon *Hades* glow
4. **Rotation loop** — 8-32 compass directions via
   `unreal.MoviePipelineQueueSubsystem` + Python.
5. **Output** — Multi-layer EXR preserving normals +
   colour in sync.

The Godot 4 alternative (lighter, indie-friendly) is
the **SubViewport technique**: at runtime during a
load screen, the game instantiates the 3D model in a
`SubViewport`, plays the animation, captures frames
into a `SpriteFrames` resource. This enables
**character customisation** — re-bake in 2s when the
player changes armour, no 10,000 PNG offline combos.

### The BitCraft SpacetimeDB backend

Clockwork Labs' *BitCraft Online* pioneered the
SpacetimeDB MMO pattern. The KCG extension adopts
this for the Tuath backend:

- **Reducers** = game logic (e.g. `CraftItem`).
  They are ACID transactions — when a client requests
  a craft, the DB runs the reducer, updates state,
  and persists instantly.
- **Subscriptions** = client `SELECT * FROM MapObjects
  WHERE distance(player, obj) < view_distance`. The
  DB pushes WebSocket updates when the query result
  changes (no polling).
- **Scaling** = horizontal by sharding `MapObjects`
  by region. No dedicated game server to crash;
  no Postgres save race condition.

### Dagster asset wiring (the 2 new groups)

```python
from dagster import asset, AssetExecutionContext, define_asset_job

@asset(group_name="hades_research")
def hades_3d_to_2d_pipeline(context: AssetExecutionContext):
    """Run the agentic research DCG on the latest Supergiant GDC talks."""
    state = run_langgraph_dcg(
        query="Hades 3D-to-2D normal map baking pipeline",
        max_iterations=3,
    )
    return MaterializeResult(
        metadata={
            "report": state["final_report"],
            "sources": state["sources_found"],
            "iteration_count": state["iteration_count"],
        }
    )

@asset(group_name="bitcraft_spacetimedb")
def bitcraft_spacetimedb_compat(context: AssetExecutionContext):
    """Monitor SpacetimeDB Rust SDK breaking changes; emit alert asset."""
    breaking = monitor_spacetimedb_breaking_changes(
        repo="clockworklabs/SpacetimeDB",
        crates_to_check=["spacetimedb", "spacetimedb-sdk"],
    )
    return MaterializeResult(
        metadata={
            "breaking_changes": breaking,
            "tuatha_impact": assess_tuatha_impact(breaking),
        }
    )
```

The 2 new groups (`hades_research`, `bitcraft_spacetimedb`)
sit alongside the existing 4 (`celtic_curriculum`,
`mythology_content`, `celtic_embeddings`,
`mythology_embeddings`) in the `sruth/tuatha/dg.toml`
code-location.

See [`tuatha-mmo/references/sovereign-mmo-state-stack.md`](../tuatha-mmo/references/sovereign-mmo-state-stack.md)
for the full 327-line sovereign game-state deep dive
(SpacetimeDB Rust reducers, TanStack Vite config,
DuckDB-WASM OPFS persistence, CopilotKit schema-first
context) and
[`tuatha-mmo/references/hades-bitcraft-pipeline.md`](../tuatha-mmo/references/hades-bitcraft-pipeline.md)
for the 329-line LangGraph DCG + UE5 MRQ baking
pipeline + SpacetimeDB scaling patterns.
