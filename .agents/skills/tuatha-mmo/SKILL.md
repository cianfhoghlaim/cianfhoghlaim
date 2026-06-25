---
name: tuatha-mmo
description: The Tuatha British Isles Formative Assessment MMO — Babylon.js 7 + WebGPU client, Rust + SpacetimeDB server, x402 micropayments (gated game features only), SIWE auth, and the Crypteolas educational-achievement ledger (skill tree badges, NOT a financial token), all organised around the Pent-Elemental Cosmology (Spirit / Water / Fire / Earth / Air + Anam Cara). The 4 sub-modules (game / crates / crypteolas / ui) form one cohesive product: a Babylon.js front-end, a SpacetimeDB authoritative state engine, a TanStack Start web app, and a Python achievement-ledger. Use when adding a 3D scene, wiring a Babylon.js zone, deploying the SpacetimeDB server, onboarding a new agent (Celtic Tutor / Mythology Narrator / Quest Guide / Research Assistant), designing a formative-assessment quest, or asking "how does the British Isles formative assessment MMO fit together?".
---

# Tuatha British Isles Formative Assessment MMO

## When to use this skill

Use when you need to:

- "Add a 3D scene or Babylon.js zone to the Tuatha MMO"
- "Add a SpacetimeDB table or reducer"
- "Design a formative-assessment quest" — see the
  `.agents/skills/british-isles-formative-assessment/` skill
  for the pedagogical framework
- "Add a skill-tree badge to the achievement ledger" — see
  `sruth/tuatha/sruth/crypteolas/achievements/`
- "Wire x402 micropayments for a gated game feature" — x402
  is **only** for paid game features, not for educational
  content
- "Onboard a new formative feedback agent (tutor / narrator /
  quest / research)" — see `sruth/oideachais/agents/adk/`
- "Deploy the MMO to `bunchloch` or `arm1-oci`"
- "Cross-compile the iOS / KMP / RN / Godot client"
- "Configure the pent-elemental cosmology (Spirit / Water /
  Fire / Earth / Air + Anam Cara)"
- "Understand the relationship between `game/`, `crates/`,
  `sruth/crypteolas/`, and `ui/`"
- "Optimise the 60 FPS rendering budget or the embedding 100×
  batch rule"

## Overview

Tuatha is a **British Isles Formative Assessment MMO** that
fuses a Babylon.js 3D game client, a Rust + SpacetimeDB
authoritative state engine, a TanStack Start web front-end,
and a Python educational-achievement ledger (Crypteolas) into
a single product. The game world is built around the
**Pent-Elemental Cosmology**: five realms (Spirit / Water /
Fire / Earth / Air) joined by the **Anam Cara** (soul friend)
social mechanic. The educational backbone is a fleet of 4 AI
agents (Celtic Tutor, Mythology Narrator, Quest Guide,
Research Assistant) that deliver **formative feedback** during
quests, mapped to the NCCA / CfE / CfW / CCEA / SQA curriculum
frameworks.

The 4 agents live at `sruth/oideachais/agents/adk/` (Phase 5 of the
6-phase refactor plan moved them from `sruth/tuatha/agents/adk/`;
the tuatha files are now thin re-exports). The pedagogical
framework they implement lives in
`.agents/skills/british-isles-formative-assessment/`.

**Important framing (Phase 6 of the 6-phase refactor plan):**

- **Formative, not summative**: the MMO gives continuous
  feedback during learning, not a final grade. The Leaving
  Cert / GCSE / A-Level are out of scope.
- **Educational crypto as achievements, not finance**: the
  Crypteolas ledger holds skill-tree badges (per curriculum
  framework × level), not CELT tokens. x402 micropayments
  are reserved for gated game features (cosmetics, premium
  quests, paid DLC), never for educational content.
- **British Isles scope, not "Celtic" broadly**: the 5
  frameworks are NCCA (IE) / CfE (SCT) / CfW (WLS) / CCEA
  (NI) / SQA (SCT post-16). The "Celtic" framing in
  agent names is preserved for continuity, but the curriculum
  is the British Isles 5.

Tuatha is one of 4 quadrants of the Cianfhoghlaim monorepo
and is registered as a top-level uv workspace member
(`tuath`).

The 4 sub-modules, in the layout they ship in:

| Path | Tech | Role |
|:--|:--|:--|
| `sruth/tuatha/game/` | Babylon.js 7 (TS) + WebGPU | 3D game client (the MMO front-end) |
| `sruth/tuatha/crates/` | Rust + SpacetimeDB + Axum | Game engine (authoritative state) |
| `sruth/tuatha/sruth/crypteolas/` | Python + educational-achievement ledger | Skill-tree badges + x402 settlement for paid game features |
| `sruth/tuatha/ui/` | TanStack Start | Web front-end for the educational game |

The 4 dev servers run in parallel:

| Server | Port | Tech |
|:--|:--|:--|
| Game server (HTTP) | 3000 | Rust + Axum |
| Game server (WebSocket) | 3001 | SpacetimeDB |
| Game client (dev) | 8080 | Babylon.js (Vite) |
| Web front-end | 3002 | TanStack Start |

## The Pent-Elemental Cosmology

The game world is divided into **5 elemental realms**, each
tied to a curriculum theme and a Celtic language:

| Realm | Element | Curriculum theme | Celtic language | Sample agent |
|:--|:--|:--|:--|:--|
| **Anam** | Spirit | Bardic lore, mythology, history | Gaeilge | Mythology Narrator |
| **Uisce** | Water | Geography, marine biology, climate | Gaeilge + Gàidhlig | Research Assistant |
| **Tine** | Fire | Chemistry, physics, energy | Gaeilge | Celtic Tutor |
| **Talamh** | Earth | Mathematics, geology, agriculture | Cymraeg | Quest Guide |
| **Aer** | Air | Astronomy, weather, music | Gaeilge + Cymraeg | Celtic Tutor |

Each realm is a **Babylon.js scene** + a **SpacetimeDB
namespace** (own tables, own reducers, own auth scopes).
Inter-realm travel happens through **Anam Cara** (soul
friend) portals — when two players forge an Anam Cara bond,
they share a private mini-realm that crosses elements.

The cosmology is encoded as data, not as hard-coded scenes:
the `RealmConfig` table holds the realm metadata, the
`AnamCara` table holds the social bonds, and the
`RealmEdge` table holds the portal graph. A realm can be
added by writing a new row.

## The 4-agent system

The educational backbone is 4 specialised agents, each
backed by a BAML client + a Celtic-language model:

| Agent | Role | Primary model | Language |
|:--|:--|:--|:--|
| **Celtic Tutor** | In-world teaching NPC (formative feedback on language quests) | `ReliableAI/UCCIX-Llama3.1-70B` | en + ga |
| **Mythology Narrator** | Stories / cycles (Tuatha Dé Danann, Táin Bó Cúailnge, Fionn mac Cumhaill) — formative context for cultural quests | `ReliableAI/UCCIX-Llama3.1-70B` | en + ga |
| **Quest Guide** | Quest design + graduated hints (Level 1: nudge → Level 4: step-by-step) | `litellm/anthropic/claude-sonnet-4` | en |
| **Research Assistant** | Long-form reasoning + cross-nation comparative research | `litellm/gemini-2.5-flash` (fast) → `litellm/anthropic/claude-sonnet-4` (strong) | en + ga + cy |

The agents are CopilotKit AG-UI components rendered in the
TanStack Start UI; their state lives in SpacetimeDB (the
agent's memory, the player's mastery) and in Cognee
(long-term knowledge). A2UI streams UI events over
`ws://localhost:3000/a2ui`.

The full Tuath agent system (1586 lines) is in
`references/tuath-agent-architecture.md`. The canonical
implementations live at `sruth/oideachais/agents/adk/` (Phase 5 of
the 6-phase refactor plan moved them from
`sruth/tuatha/agents/adk/`; the tuatha files are now thin
re-exports). Each agent is one of the 4 formative feedback
channels documented in
`.agents/skills/british-isles-formative-assessment/`.

## British Isles formative assessment (Phase 6)

**The MMO is a formative-assessment product, not a summative
one.** Per the user's plan (Phase 6 of the 6-phase refactor):
"crypto = educational achievements (not finance)". The
pedagogical framework — NCCA / CfE / CfW / CCEA / SQA
mapping, the 4 formative feedback channels, the 3 quest
types, the 4 graduated hint levels, the achievement-ledger
schema — is captured in
`.agents/skills/british-isles-formative-assessment/`.

Key Phase 6 refactor outcomes:

- **Formative vs. summative**: the MMO is the former. The
  Leaving Cert / GCSE / A-Level are out of scope. The
 4 agents deliver per-quest, per-response, per-misconception
  feedback; the player always leaves with progress + feedback,
  never a binary right/wrong.
- **Achievement ledger, not financial token**: the Crypteolas
  crypto data platform holds skill-tree badges (per
  curriculum framework × level) + cross-quest masteries
  (1 per Pent-Elemental Cosmology realm). x402 micropayments
  remain in the tech stack for **gated game features only**
  (cosmetics, premium quests, paid DLC), never for
  educational content.
- **British Isles scope, not "Celtic" broadly**: the 5
  frameworks are NCCA (IE) / CfE (SCT) / CfW (WLS) / CCEA
  (NI) / SQA (SCT post-16). The "Celtic" framing in agent
  names is preserved for continuity, but the curriculum
  is the British Isles 5.
- **OpenSpec change**: `tuatha-formative-assessment-v1`
  (archived 2026-06-24) adds 1 MODIFIED + 1 ADDED Requirement
  to the `tuatha-platform` spec.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          TUATHA MMO STACK                           │
└─────────────────────────────────────────────────────────────────────┘

Browser (Babylon.js 7 + WebGPU)
   │  ▲  WebSocket
   │  │
   ▼  │
SpacetimeDB (Rust)
   │  ▲
   │  │
   ▼  │
Axum HTTP (Rust) ─── SIWE (Sign-In With Ethereum)
   │                ─── x402 micropayments
   │                ─── CopilotKit A2UI
   │
   ▼
TanStack Start (TS) ─── Cloudflare Workers
   │
   ▼
Crypteolas (Python) ─── Bitcoin / Ethereum / Solana
   │                ─── EAS attestations
   │                ─── Flower federated learning
   ▼
Dagster (Python) ─── Celtic curriculum assets
   │             ─── Mythology embeddings
   │             ─── Crypteolas trades
   ▼
FalkorDB + LanceDB + Memgraph + MotherDuck
```

The state engine is **sovereign** — SpacetimeDB holds
authoritative game state; nothing else writes. The Axum
HTTP layer is read-only + a webhook sink for off-game events
(SIWE nonce, x402 settlement, EAS attestations).

## Deployment

The MMO deploys to the 3-tier KCG topology (see
`kcg-bunchloch`):

| Tier | Role for Tuatha |
|:--|:--|
| `arm1-oci` (control plane) | Pangolin / Traefik routes the `*.tuatha.cianfhoghlaim.ie` domain |
| `cax41-hetzner` (storage) | S3 / Lance Namespace REST serves the Babylon.js asset CDN |
| `bunchloch` (workload) | Runs the SpacetimeDB container + the Axum server + the TanStack Start SSR |

The SpacetimeDB container is published from `sruth/tuatha/crates/`
via the GitHub Action at `infrastructure/ci/spaces-sync.yml`
and the Dagger CI/CD pipeline. The TanStack Start UI is
deployed to Cloudflare Workers via the `sruth/tuatha/ui/`
`bun run deploy` script.

Secrets are injected by Locket sidecars from the `dev-baile`
Infisical environment. The `secrets.env` template lives at
the root of the repo; see `secrets-management` skill for the
3-way contract.

## Performance budgets

| Surface | Budget | Notes |
|:--|:--|:--|
| Babylon.js client | 60 FPS at 1440p | WebGPU preferred, WebGL2 fallback |
| SpacetimeDB reducer | < 5 ms p99 | hot path; no LLM calls inside reducers |
| Axum endpoint | < 50 ms p99 | 1-shot LLM calls routed via A2UI streaming |
| TanStack Start SSR | < 200 ms TTFB | Cloudflare Workers edge cache |
| CocoIndex embedding | 100× batch minimum | 100+ chunks per `SentenceTransformerEmbedder` call |
| LanceDB HNSW search | < 20 ms p99 | IVF_HNSW_PQ index, nprobes=8 |

The full performance tuning guide (883 lines) is in
`references/tuatha-performance-tuning.md`.

## Quick routing (from `sruth/tuatha/AGENTS.md`)

When working in `sruth/tuatha/`, route to the right sub-area:

| Working on | Read | Skill |
|:--|:--|:--|
| 3D scenes, MMO client | `sruth/tuatha/game/` | `.agents/skills/babylonjs/`, this skill |
| Rust + SpacetimeDB server | `sruth/tuatha/crates/` | this skill + `.agents/skills/upstream-mirrors/SKILL.md` (spacetimedb mirror) |
| Crypto data platform | `sruth/tuatha/sruth/crypteolas/` | `.agents/skills/sruth/crypteolas/`, this skill |
| Web front-end | `sruth/tuatha/ui/` | `.agents/skills/tanstack-start/`, this skill |
| SIWE auth | `sruth/tuatha/auth/siwe.py` | `.agents/skills/better-auth/` + this skill |
| x402 micropayments | `sruth/tuatha/sruth/crypteolas/x402.py` | `.agents/skills/upstream-mirrors/SKILL.md` (x402 mirror) |
| Celtic-language models | `sruth/oideachais/baml_src/celtic_linguistics.baml` | `.agents/skills/celtic-language-ai/` |
| Agent observability | Dagster + Langfuse | `.agents/skills/agent-observability/` |
| Deploy the stack | `infrastructure/stacks/sruth/tuatha/` | `.agents/skills/stack-ops/` |

## References (in this skill)

- `references/tuath-api-reference.md` — full FastAPI + Axum
  API spec for the Tuath backend.
- `references/tuatha-pipelines.md` — canonical pipeline
  diagram (DLT + CocoIndex + Dagster).
- `references/tuath-agent-architecture.md` — the 1586-line
  Tuath agent system (Celtic Tutor / Mythology Narrator /
  Quest Guide / Research Assistant).
- `references/babylonjs-game-client.md` — TuathGame +
  SceneManager + SpacetimeDB Babylon 7 client.
- `references/educational-game-development.md` — full
  educational game dev pipeline (longer than the DIAGE copy).
- `references/diage-educational-game-pipeline.md` — DIAGE
  game-engine + Manim science viz (teanga copy).
- `references/diage-physics-chem-game-pipeline.md` — same
  content as the educational DIAGE copy.
- `references/anam-engine-selection.md` — Anam MMO
  ecosystem CopilotKit + x402 + KMP (tuatha copy).
- `references/anam-mmo-engine-selection.md` — same as engine
  selection (teanga copy).
- `references/mythology-pent-elemental-cosmology.md` —
  Spirit / Water / Fire / Earth / Air + Anam Cara MMO design.
- `references/celtic-os-postmog-architecture.md` — window
  manager Product-OS for the British Isles (tuatha copy).
- `references/celtic-os-product-os.md` — same content
  (teanga copy).
- `references/celtic-languages-detection.md` — langdetect +
  langcode + model gap mitigation for Tuatha.
- `references/celtic-naming-lexicography.md` — anam / tír /
  aran / gaelg / cymr / yern philology + Web3 conflicts.
- `references/agentic-education-platform.md` — CopilotKit +
  AgUI + MCP + x402 academy architecture.
- `references/adding-dlt-data-sources.md` — how-to add a DLT
  source to the Tuatha pipeline.
- `references/data-platform-integration-plan.md` — the
  2836-line data platform plan (Crypto Analytics worked
  example).
- `references/sovereign-mmo-state-stack.md` — SpacetimeDB +
  DuckDB-WASM + TanStack MMO.
- `references/crypteolas-copilotkit-integration.md` —
  Crypteolas portfolio analysis + market monitoring + trade
  execution.
- `references/crypteolas-fl-crypto.md` — federated learning
  + crypto payments on iPhone (SyftBox + Flower + x402).
- `references/crypteolas-ios-marketplace.md` — Apple MLX +
  x402 + Flower + PySyft iOS marketplace.
- `references/cianfhoghlaim-scoilverse-l2e.md` — EBSI +
  Hypercerts + Solana + Mythology + Vargas learn-to-earn.
- `references/ios-sandwich-architecture.md` — Hybrid-Native
  Sandwich KMP + Swift + Rust + UniFFI.
- `references/british-isles-game-dev-pipeline.md` — 2.5D game
  terrain from OS data + Met Office.
- `references/hades-bitcraft-pipeline.md` — Supergiant +
  SpacetimeDB + agentic research pipeline.
- `references/anam-meteorological-particles.md` — Catmull-Rom
  + Bicubic + GRIB2 + SpacetimeDB particle system.
- `references/diare-game-reverse-engineering.md` — Ghidra +
  Frida + FFmpeg + UnityPy + Storybook agentic SRE.
- `references/rust-fullstack-gaming.md` — Rust workspace +
  SpacetimeDB + Godot GDExtension + Alloy.
- `references/spacetimedb-ogham-integration.md` — CISP /
  Megalithic Portal Ogham ETL + Solana dNFT + Metaplex.
- `references/spacetimedb-blockchain-strategy.md` —
  Token-2022 + EIP-7702 + SpacetimeDB + Metaplex Core.
- `references/mmo-geospatial-visual-rag.md` — DuckDB +
  MotherDuck + RisingWave + SpacetimeDB WebGPU MMO.
- `references/spacetimedb-tuatha-guide.md` — SpacetimeDB
  tables + reducers + TS SDK.
- `references/adding-babylonjs-zones.md` — how-to add
  Celtic-language Babylon.js zones.
- `references/tuatha-deployment-guide.md` — Cloudflare
  Workers + R2 + SpacetimeDB production deploy.
- `references/tuatha-tanstack-frontend.md` — routes +
  components + SIWE + X402Paywall + TuathCopilot.
- `references/tuatha-performance-tuning.md` — batch embedding
  100×, HNSW, game client 60 FPS.
- `references/cross-platform-guide.md` — KMP + Swift +
  React Native + Godot Tuatha client.
- `references/gdext-godot-rust-guide.md` — gdext setup +
  SpacetimeDB SDK integration.
- `references/clippings/copilotkit-ag-ui-a2ui.md` — AG-UI vs
  A2UI.
- `references/clippings/copilotkit-useagent-hook.md` —
  useAgent hook (teanga copy).
- `references/clippings/copilotkit-useagent-hook-2.md` —
  useAgent hook (tuatha copy, dedup pair).
- `references/clippings/kmp-vs-react-native.md` — KMP vs RN.
- `references/clippings/deisi-wikipedia.md` — Déisi Wikipedia
  (Irish mythology reference).
- `references/clippings/mcp-ui.md` — MCP-UI protocol.

## Cross-references

- `.agents/skills/tuatha-platform/SKILL.md` — the existing
  Tuatha quadrant router (this skill is the deeper dive into
  the MMO + Crypteolas product).
- `.agents/skills/babylonjs/SKILL.md` — the Babylon.js 3D
  engine (used in `sruth/tuatha/game/`).
- `.agents/skills/kcg-bunchloch/SKILL.md` — the 3-tier
  topology where the MMO deploys.
- `.agents/skills/stack-ops/SKILL.md` — the GOLD_STANDARD
  6-file pattern (used to deploy the Tuatha stack).
- `.agents/skills/secrets-management/SKILL.md` — the
  Infisical + Locket secret injection.
- `.agents/skills/better-auth/SKILL.md` — the SIWE auth
  pattern (used for `sruth/tuatha/auth/siwe.py`).
- `.agents/skills/celtic-language-ai/SKILL.md` — the Celtic
  LLMs (Celtic Tutor / Mythology Narrator backends).
- `.agents/skills/agent-observability/SKILL.md` — the
  Langfuse + MLflow + RAGAS observability stack (the agent
  agent-os for the 4 agents).
- `.agents/skills/upstream-mirrors/SKILL.md` — the
  SpacetimeDB / wgpu / x402 KCG mirror summaries.
- `sruth/tuatha/AGENTS.md` — the existing entry point.
- `sruth/tuatha/DEVELOPMENT.md` — 593-line developer guide.
- `sruth/tuatha/README.md` — product spec.
- `openspec/specs/tuatha-platform/spec.md` — the canonical
  spec for the Tuatha quadrant.

## iOS sandwich architecture (round-9 deep dive)

The Tuatha MMO ships a hybrid-native iOS client. The
"iOS sandwich" is the canonical 3-layer pattern:
**Kotlin (common business logic) → Swift bridge
(iOS-only APIs) → Compose / SwiftUI (UI)**. The
`references/swift-kmp-bridge.md` reference (390 lines)
documents the bridge pattern.

### The 3-layer iOS sandwich

```
┌──────────────────────────────────────────────────┐
│  Compose / SwiftUI       ← UI (per-platform)    │
│  (iOS / Android / Desktop)                       │
├──────────────────────────────────────────────────┤
│  Swift bridge            ← iOS-only APIs        │
│  (StoreKit, ARKit, …)   (via swiftklib + cinterop)│
├──────────────────────────────────────────────────┤
│  Kotlin commonMain       ← shared business logic │
│  (AG-UI client, SpacetimeDB, MMO state, …)       │
└──────────────────────────────────────────────────┘
```

### The Swift bridge pattern (5 steps)

1. **Swift bridge file** — `iosApp/iosApp/bridges/ReviewBridge.swift`:

   ```swift
   import StoreKit
   import UIKit

   @objc public class ReviewBridge: NSObject {
     @objc public static func requestReview() {
       if #available(iOS 14.0, *) {
         if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
           SKStoreReviewController.requestReview(in: scene)
         }
       }
     }
   }
   ```

2. **Expect class in commonMain**:

   ```kotlin
   package core.presentation.utils
   expect class FeedbackManager(context: Any = Unit) {
     fun showFeedBackDialog()
   }
   ```

3. **Gradle + swiftklib**:

   ```kotlin
   // libs.versions.toml
   [plugins]
   swiftklib = { id = "io.github.ttypic.swiftklib", version = "0.5.4" }

   // shared module build.gradle.kts
   plugins { alias(libs.plugins.swiftklib) }
   swiftklib {
     create("bridges") {
       path = file("../iosApp/iosApp/bridges")
       packageName("com.company.project.bridges")
     }
   }
   kotlin { listOf(iosX64(), iosArm64(), iosSimulatorArm64())
     .forEach { iosTarget ->
       iosTarget.compilations {
         val main by getting { cinterops { create("bridges") } }
       }
     }
   }
   ```

4. **iosMain actual** — calls the bridge:

   ```kotlin
   actual class FeedbackManager actual constructor(context: Any) {
     @OptIn(ExperimentalForeignApi::class)
     actual fun showFeedBackDialog() { ReviewBridge.requestReview() }
   }
   ```

5. **androidMain actual** — uses the Google Play Core
   in-app review API (`ReviewManagerFactory.create(ctx)
   .launchReviewFlow(activity, info)`).

The same pattern is the canonical way to call
`StoreKit` (iOS), `ARKit`, `GameKit`, `HealthKit`, or
any other iOS-only API from shared Kotlin code — no
Cocoapods required.

### Why this matters for Tuatha

- **AG-UI Kotlin SDK** (see `ag-ui` skill §"Kotlin
  mobile SDK") runs in `commonMain` and talks to the
  same agent backend as the web client
- **SpacetimeDB TS SDK** runs in `commonMain` via
  the Kotlin/JS interop; the Rust server is shared
  with the web client
- **Swift bridges** unlock iOS-only features
  (StoreKit for IAP, ARKit for AR quests, GameKit
  for leaderboards) without forking the codebase
- **Crypteolas** uses the same sandwich for the
  Apple MLX on-device inference (x402 + Flower + SyftBox)

### British exam builder (companion reference)

The `references/british-exam-builder.md` (374 lines)
isn't about the MMO itself — it's the **KCG companion
project** for building British-Isles exam papers
(AQA / OCR / Edexcel / WJEC / CCEA) that the MMO's
NPCs use to assess the player's mastery. Key patterns:

- **dnd-kit** for drag-and-drop question reordering
  (sidebar-to-canvas clone pattern, not move)
- **JCQ-compliant JSON schema** for exam items:
  `board`, `qualification`, `taxonomy`, `cognitiveLevel`,
  `content` (polymorphic block), `marks`, `interactionType`
- **CopilotKit `useCopilotReadable`** to feed the exam
  metadata to the AI tutor agent
- **Polymorphic content blocks** (LaTeX, tables,
  vector graphics) — exam questions are not just text
- **Tiering** (Foundation vs Higher) — drag metadata
  warns the user if a Foundation question is dropped
  on a Higher paper

The exam builder lives in `sruth/oideachais/web/src/components/
exam-builder/` and consumes the leaving-cert TanStack
paper corpus that the MMO's NPCs cite in dialogue.

See `references/swift-kmp-bridge.md` for the full
390-line iOS bridge guide, and
`references/british-exam-builder.md` for the full 374-line
British exam builder architecture.

## KCG quadrant reference

The canonical 73-line reference for the `sruth/tuatha/` quadrant
as a whole, viewed from the post-2026-06-06 docs
restructure. Tuath is the gamified Celtic language learning
platform — one of the 5 quadrants in the Cianfhoghlaim
monorepo — that exposes a FastAPI backend, an Axum payment
API (x402), Google ADK agents, a TanStack Start admin
frontend, a Babylon.js 3D game client, a SpacetimeDB
real-time state module, and the Crypteolas token.

**Workspace structure** (a uv-workspace with 3 sub-members):

| Sub-member | Purpose |
|:--|:--|
| `sruth/tuatha/codeolas/` | Code intelligence library (Tree-sitter + CocoIndex; ingest of code repos) |
| `sruth/tuatha/sruth/crypteolas/` | Crypto / DeFi research (GitHub, protocols, analytics) |
| `sruth/crypteolas/apps/crypteolas_demo/` | Demo app |

**Front-end topology**: `sruth/tuatha/ui/` uses **Babylon.js**
(not TanStack) — the *only* front-end in the monorepo that
doesn't use TanStack.

**Data plane**:
- **In-game state**: SpacetimeDB (real-time, low-latency)
- **Premium content**: served from `sruth/oideachais/` (DuckLake)
  — paid via x402 micro-transactions in Crypteolas token
- **Dagster assets**: `sruth/tuatha/dagster_assets/` for the
  MMO's curriculum-in-game asset graph (separate from
  `sruth/oideachais/dagster_defs/`)

The 6 canonical KCG docs for Tuath live in `docs/06-product/`:
`babylonjs.md`, `crypteolas.md`, `game-development.md`,
`educational-platform.md`, `celtic-mmo.md`; and
`docs/05-web/frontend-topology.md` for the front-end
taxonomy.

The frontmatter of the source (`title: Tuath Celtic
Educational MMO`, `domain: architecture`, `status: stable`,
`truth: sole`) declares this the **sole** KCG canonical
for the Tuath quadrant — superseding earlier
`docs/sruth/tuatha/` subtree content (which has been consolidated
in rounds 1-9).

See `references/TUATH_MMO.md` for the full 73-line
canonical reference: the quadrant intro, the 7 surfaces
(FastAPI + Axum + ADK + TanStack Start + Babylon.js +
SpacetimeDB + Crypteolas), the workspace member table, the
front-end topology note, the 3-plane data architecture
(SpacetimeDB + DuckLake + Dagster), the 6-doc cross-reference
list, and the "see also" runtime pointers
(`sruth/tuatha/DEVELOPMENT.md`, `sruth/tuatha/README.md`,
`sruth/tuatha/gaeilge.md`).

## 2026-06 update: Babylon.js 7 + SpacetimeDB v2 + x402

The Tuatha Celtic Educational MMO has 3 framework updates in 2026-06.

### Babylon.js 7 + WebGPU (the default renderer)

Babylon.js 7 (released 2026-05) is now the KCG-canonical Babylon.js version. The 7 release flips the default renderer from WebGL2 to WebGPU. The KCG pattern:

```typescript
// sruth/tuatha/game/scenes/init.ts
import { Engine, Scene, WebGPUEngine } from "@babylonjs/core";

const canvas = document.getElementById("renderCanvas");
const engine = await WebGPUEngine.CreateAsync(canvas);  // WebGPU preferred
// Falls back to WebGL2 if WebGPU is not available:
const engine2 = new Engine(canvas, true, { ... });
```

WebGPU enables:

- Compute shaders (for procedural Celtic knot generation)
- Better performance on Apple M-series (M1/M2/M3/M4 unified memory)
- Future Babylon.js 8 features (deferred rendering, mesh shaders)

### SpacetimeDB v2 (the authoritative state engine)

SpacetimeDB v2 is the Rust-based authoritative state engine. The 4 KCG MMO server modules (`sruth/tuatha/crates/{services,solana,stdb-modules,wgpu}/`) are pinned to v2.x.

Key v2 features:

- **Row-level access control** — the player can only see their own NPC dialogue
- **Subscriptions** — the client subscribes to a query; the server pushes updates only when the result changes
- **WebSocket compression** — 60% smaller payloads for the Celtic language graph updates
- **WASM reducers** — the client can run reducers in WASM (offline-capable quest tracking)

The KCG pattern: `sruth/tuatha/crates/stdb-modules/src/tables/` defines the 20+ tables (Player, NPC, Quest, Achievement, Soul, etc.).

### x402 micropayments on Base L2 (gated game features only)

x402 is the HTTP micropayments protocol on Base L2. The Tuatha MMO uses x402 ONLY for gated game features (premium Celtic content packs, the Crypteolas achievement-ledger cosmetic skins) — not for the core educational flow.

The 4 KCG x402 endpoints are:

- `POST /api/v1/mmo/cosmetic/skin` — gated skin purchase
- `POST /api/v1/mmo/quest/premium` — premium Celtic quest pack
- `POST /api/v1/mmo/ledger/badge-mint` — mint a skill-tree badge
- `GET  /api/v1/mmo/leaderboard/cel-balance` — CELT balance lookup

The educational flow (Aistear, Primary, JC, SC, Tertiary curriculum + formative assessment + Celtic language + mythology) is FREE and never gated. The x402 endpoints are non-curriculum, opt-in, paid features.

The crypteolas achievement-ledger is a skill-tree badge system, NOT a financial token. The ledger records:

- Curriculum framework (Aistear, Primary, JC, SC, Tertiary, or custom)
- Skill level (Bronze, Silver, Gold, Celtic, Mythic)
- Learning outcome code (per the 4 formative feedback channels)
- Agent issuer (one of the 4 agents: Celtic Tutor, Mythology Narrator, Quest Guide, Research Assistant)
- Evidence (the curriculum artefact the badge was earned from)

### Pair this skill with

- `babylonjs/SKILL.md` — the Babylon.js 7 + WebGPU detail
- `dagster-pipelines/SKILL.md` — the Dagger pipeline that builds the MMO client
- `dagster/SKILL.md` — the Dagster orchestration of the 23 MMO assets
- `secrets-management/SKILL.md` — the Locket pattern for the MMO API keys
- `upstream-mirrors/SKILL.md` — the KCG-mirrored upstream docs for SpacetimeDB, wgpu, x402
