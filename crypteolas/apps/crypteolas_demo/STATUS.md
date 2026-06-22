# Status — `apps/crypteolas_demo`

> **Read this first if you are picking up work in this sub-app.**
> This document explains what was flattened, what was stubbed, and
> what gaps remain to be filled to make the demo fully functional.

## What this app is

A standalone demo application that bundles:

- **TanStack Start TypeScript frontend** (in `src/`) — the DeFi
  analytics + AI chat + x402 micropayments dashboard.
- **Python Gradio UI** (in `ui/`) — the EduVision curriculum-to-image
  generation app (FIBO JSON + LanceDB + ColPali).
- **Python Agno agent team** (in `crypto_agents.py` + `mcp_tools.py`) —
  research, analysis, and pipeline-triggering agents for DeFi questions.
- **MCP server** (`mcp_tools.py`) — exposes crypto analytics tools to
  Claude Code and other MCP-compatible clients.
- **Two parallel Dagster code-locations**:
  - `defs/` (FIBO/EduVision: curriculum → asset generation).
  - `pipelines/defs/` (Crypteolas: CoinGecko, DeFiLlama, Binance, Aave,
    Pendle data ingestion + analytics + scraping + knowledge graph).
- **Dagster code-location entry point** (`definitions.py`) — registers
  the FIBO assets + resources.
- **Foundry Solidity contracts** (in `anam-contracts/`) — Anam Cara DAO,
  Cuchulainn NFT, Tuath Token.
- **BAML schemas** (in `scéimre/`) — curriculum extraction, FIBO
  prompt generation, validation, whitepaper extraction, etc.

The `crypteolas_demo` Python package is the importable surface; the
TanStack app and the Dagster code-locations are loaded by their
respective toolchains.

## What was changed during the consolidation

The prior `tuatha/tuatha_1/` carried the `fibo` Python package as a
nested project. It was flattened into `tuatha/apps/crypteolas_demo/`
and re-rooted as the `crypteolas_demo` package. The following changes
were applied:

| Change | From | To |
|:--|:--|:--|
| Package name | `fibo` | `crypteolas_demo` |
| Root module | `fibo` | `crypteolas_demo` |
| Broken `__init__.py` | `from agents.crypto_agents import …` (didn't exist) | `from .crypto_agents import …` (re-exports the public surface) |
| `fibo.X` imports in `definitions.py` | `from fibo.defs.X import Y` | `from defs.X import Y` |
| `crypteolas.X` imports (external package) | `from crypteolas.config.llm import …` | `from foinse.llm import …` (file already at this path) |
| `crypteolas.X` imports (Dagster pipelines) | `from crypteolas.pipelines.X import Y` | `from pipelines.X import Y` (the implementations already live in this directory) |
| `crypteolas.pipelines.knowledge.graph_schema` | External | `from pipelines.knowledge.graph_schema import …` |
| `sruth.códeolas` import in `agents/adk/architecture_agent.py` | (n/a) | This was in crypteolas, not this app — see the crypteolas STATUS.md. |
| BAML output_dir | `output_dir = "../baml_client"` (would have collided with `tuatha/baml_client/`) | `output_dir = "./baml_client"` (isolated) |
| Docker Compose | 4 services incl. `agno` (broken build context + missing Dockerfile) | 3 services (postgres, litellm, redis); `agno` removed; the existing `tuatha/agents/orchestrator.py` covers orchestration |
| Dockerfile | `node:22-alpine` + `pnpm` | `oven/bun:1.3.0-alpine` + `bun install` |

## What was stubbed

The TanStack Start frontend as shipped is a buildable shell. The
following pieces have been added as stubs so `bun install` and
`bun run typecheck` succeed:

| Stub | Path | Purpose |
|:--|:--|:--|
| `package.json` | `tuatha/apps/crypteolas_demo/package.json` | Bun workspace manifest (Vinxi + React 19 + Wagmi deps). |
| `tsconfig.json` | `tuatha/apps/crypteolas_demo/tsconfig.json` | TypeScript config; `@/*` alias to `./src/*`. |
| 12 `src/lib/*` modules | `tuatha/apps/crypteolas_demo/src/lib/{auth,x402,copilot,query,mcp,web3}` | Stubs with `TODO: implement` and minimal type signatures. See "Stubbed TS modules" below. |
| 3 `models/*` modules | `tuatha/apps/crypteolas_demo/models/{colpali,fibo_mlx,qwen_vlm}.py` | Stubs that raise `NotImplementedError` at runtime so the Dagster assets and the Gradio UI can at least import. |

### Stubbed TS modules (12)

| Path | Status |
|:--|:--|
| `src/lib/auth/client.ts` | Stub: returns `null` from `getSession()`. |
| `src/lib/auth/server.ts` | Stub: every method raises. |
| `src/lib/x402/middleware.ts` | Stub: `withPayment` raises. |
| `src/lib/x402/payment-service.ts` | Stub: `recordPayment` raises. |
| `src/lib/x402/pricing.ts` | **Working**: `PRICING_CONFIG` table is real data. |
| `src/lib/x402/networks.ts` | **Working**: `NETWORKS` table is real data (Cronos/Base/Ethereum/Polygon). |
| `src/lib/x402/provider.tsx` | Stub: React context + `useX402()` hook. |
| `src/lib/copilot/runtime.tsx` | Stub: `CopilotProvider` raises. |
| `src/lib/query/client.ts` | **Working**: `getQueryClient` returns a real TanStack Query client. |
| `src/lib/query/hooks.ts` | Stub: every hook raises. |
| `src/lib/web3.ts` | Stub: Wagmi config + ENS resolvers return `null`. |
| `src/lib/mcp/copilot-actions.ts` | **Working**: `COPILOT_ACTIONS` table is real data (7 actions). |

### Stubbed Python model modules (3)

| Path | Status |
|:--|:--|
| `models/colpali.py` | Stub: `ColPaliEmbedder.embed()` raises. |
| `models/fibo_mlx.py` | Stub: `FiboMLXGenerator.generate()` raises. |
| `models/qwen_vlm.py` | Stub: `Qwen3VLClient.generate()` raises. |

These satisfy the imports in `defs/curriculum/resources.py`,
`defs/fibo_generation/resources.py`, and `ui/components/image_preview.py`.
The Dagster code-location loads successfully; the actual model calls
will fail at runtime until the real implementations land.

## Dagster integration

The `crypteolas_demo` Dagster code-location is registered in the tuatha
workspace. Run it locally with:

```bash
cd tuatha/apps/crypteolas_demo && uv run dagster dev -m crypteolas_demo.definitions
```

(The exact module path depends on how Dagster is launched from the
workspace root. See `tuatha/dg.toml` for the registered
code-locations.)

## How to use

```python
# Python — import the public surface
from crypteolas_demo import (
    CryptoResearchAgent, CryptoAnalysisAgent, CryptoPipelineAgent,
    create_crypto_agent_team, chat_with_team,
)
from crypteolas_demo import server, TOOLS  # MCP exports

# Or run from the demo root:
# cd tuatha/apps/crypteolas_demo
# uv run python -m mcp_tools          # starts the MCP server on stdio
# uv run python -m crypto_agents     # uses the agent team
```

```bash
# TypeScript — install and typecheck the stub
cd tuatha/apps/crypteolas_demo
bun install
bun run typecheck
```

```bash
# Docker — postgres + litellm + redis (the broken `agno` service was removed)
cd tuatha/apps/crypteolas_demo
docker compose up -d postgres litellm redis
```

## What is NOT yet implemented (TODO list)

1. The 12 `src/lib/*` modules — replace stubs with real implementations.
2. The 3 `models/*` modules — install ColPali, FIBO-MLX, Qwen3-VL weights.
3. `defs/curriculum/sources.py` references a `..pipelines.curriculum_dlt`
   module that does not exist.
4. `defs/curriculum/sources.py` uses
   `Path(__file__).parent.parent.parent.parent.parent / "education_sources"`
   — this 5-level-up lookup was correct for the prior `tuatha/tuatha_1/`
   location but is now wrong. Update the path.
5. `analyze_images` in `defs/fibo_generation/assets.py` instantiates
   the stubbed `FiboMLXGenerator` and will fail at runtime.
6. `wrangler.toml` (in `tuatha/crypteolas/wrangler.toml`, not here)
   references a `workers/index.ts` that does not exist; the
   Cloudflare Workers side of the demo is not yet built.
