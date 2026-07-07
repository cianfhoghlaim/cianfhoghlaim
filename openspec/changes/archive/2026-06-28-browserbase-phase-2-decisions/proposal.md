# Change: 2026-06-28-browserbase-phase-2-decisions

> **STUB — TO BE FILLED BY PHASE 2 RESEARCH AGENT.** This change
> consolidates the 21 Phase 2 decisions that emerge from the 2026-06-28
> BrowserBase 6,000-credit research program.
>
> See `openspec/research/2026-06-28-browserbase-credit-program/phase-2/`
> for the actual research output.

## Why

Phase 2 covers **light packages + 2 new prompts** — 21 prompts × 60
credits = 1,260 total credits spent on the secondary stack that the
Cianfhoghlaim platform touches but doesn't depend on for correctness:

- **Standard 19**: olake, mlflow, langfuse, planetscale, postgresql,
  openchamber, openclaw, litellm, llama-swap, huggingface, marimo,
  pangolin, komodo, infisical, mlx-omni, invokeai, nimtable, dragonfly,
  risingwave
- **Drift re-checks (2)**: dagster recheck, motherduck recheck
- **NEW per user request (2)**: P2-32 unsloth (Gemma 4 + Qwen3.6
  fine-tuning on consumer hardware), P2-33 modal (serverless GPU
  functions wrapping Unsloth)

## Cross-links

- Cross-references 2 canonical specs: `meaisinfhoghlaim-platform` and
  `infrastructure-stacks`
- Companion to: `oideachais-stack-polish`, `monorepo-restructure-v2`,
  `consolidate-embedding-batcher`
- Output tree: `openspec/research/2026-06-28-browserbase-credit-program/phase-2/`

## Requirements

_Filled by Phase 2 research agent after each prompt completes._
