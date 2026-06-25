---
name: upstream-mirrors
description: The 11 KCG-authored mirror summaries of upstream repositories that the Cianfhoghlaim monorepo depends on — SpacetimeDB (Rust authoritative state), wgpu (WebGPU rendering), x402 (HTTP micropayments), AnyLanguageModel (Apple unified LLM API), agui_kotlin (Kotlin AG-UI), hophacks SpacetimeDB workshop, ireland maps, react-native-godot, react-native-reusables, spacetimedb-cookbook, spacetimedb-typescript-sdk. Use when asking "how does KCG use SpacetimeDB?", "what is the x402 stack?", "which wgpu version ships in Tuatha?", or "what's pinned in the upstream mirror?" — this skill is the registry + the KCG annotations on top of each upstream.
---

# Upstream Mirrors (KCG registry)

## When to use this skill

Use when you need to:

- "What does the SpacetimeDB mirror pin?"
- "Which wgpu version does Tuatha use?"
- "What is the x402 stack in KCG?"
- "How do I integrate AnyLanguageModel in an iOS app?"
- "Where are the KCG notes for react-native-godot?"
- "What is the hophacks SpacetimeDB workshop?"
- "What's the difference between spacetimedb / spacetimedb-cookbook /
  spacetimedb-typescript-sdk mirrors?"
- "Update a KCG mirror from its upstream"

## Overview

The **upstream-mirrors** skill is the KCG registry of the 11
mirrored upstream repositories that the Tuatha / Celtic
Educational MMO + Crypteolas stack depends on. The mirrors
live under `docs/sruth/tuatha/08-mirrors/` (KEEP — the source
trees stay); the `_summaries/` subdir (the KCG-authored
annotations) lives under `references/` in this skill.

The 11 mirrors are:

| # | Mirror | KCG summary | Use case |
|:--|:--|:--|:--|
| 1 | `SpacetimeDB` | `references/spacetimedb.md` | Rust authoritative state engine for Tuatha |
| 2 | `spacetimedb-cookbook` | `references/spacetimedb-cookbook.md` | Patterns + recipes (the KCG recipes list) |
| 3 | `spacetimedb-typescript-sdk` | `references/spacetimedb-typescript-sdk.md` | The TS SDK used by the Babylon.js client |
| 4 | `wgpu` | `references/wgpu.md` | WebGPU rendering (Celtic shaders, particle systems) |
| 5 | `x402` | `references/x402.md` | HTTP micropayments (Celtic Knowledge Grid, MMO paywalls) |
| 6 | `AnyLanguageModel` | `references/anylanguagemodel.md` | Apple unified LLM API (MLX + llama.cpp) |
| 7 | `agui_kotlin` | `references/agui-kotlin.md` | Kotlin AG-UI client (KMP cross-platform) |
| 8 | `hophacks-spacetimedb-workshop` | `references/hophacks-spacetimedb-workshop.md` | SpacetimeDB hands-on (training material) |
| 9 | `ireland` (maps) | `references/ireland-maps.md` | Irish + UK geographic data (Celtic OS) |
| 10 | `react-native-godot` | `references/react-native-godot.md` | RN + Godot bridge for the cross-platform MMO client |
| 11 | `react-native-reusables` | `references/react-native-reusables.md` | Re-usable RN UI primitives (the Celtic OS shell) |

## The mirror policy

The KCG mirror policy is:

1. **Source trees stay** under `docs/sruth/tuatha/08-mirrors/`
   (the full clone, including the history).
2. **KCG-authored summaries** live under
   `references/<mirror>.md` in this skill. Each summary
   captures: pinned version, KCG use case, KCG-specific
   patches, and a "what's different in KCG?" note.
3. **External clippings** (release notes, blog posts)
   live under `references/clippings/` in this skill.
4. **Patches** KCG applies to a mirror (if any) live in
   `references/<mirror>-patches.md`.

The summary is the **canonical entry point**; the mirror
tree is the verbatim upstream.

## The KCG use of each mirror (1-liner)

- **SpacetimeDB** — the authoritative state engine for the
  Tuatha MMO. Runs on `bunchloch`; serves tables, reducers,
  and the WebSocket protocol.
- **spacetimedb-cookbook** — the KCG recipes list (5
  recipes: zones, weather, quest, Anam Cara bond, EAS
  attestation).
- **spacetimedb-typescript-sdk** — the SDK used by the
  Babylon.js game client (and the TanStack Start UI).
- **wgpu** — the WebGPU rendering layer for the Tuatha
  Celtic shader system. Pinned to v28 (the version with
  mesh shaders + immediates).
- **x402** — the HTTP micropayment protocol that backs the
  Celtic Knowledge Grid paywall + the MMO's Anam Cara
  cosmetics.
- **AnyLanguageModel** — Apple's unified Swift API for
  MLX + llama.cpp; the iOS / macOS / visionOS entry point.
- **agui_kotlin** — the Kotlin AG-UI client used by the
  KMP cross-platform Tuatha client.
- **hophacks-spacetimedb-workshop** — training material for
  the SpacetimeDB hands-on session.
- **ireland** (maps) — Irish + UK geographic data (used by
  the Celtic OS map renderer).
- **react-native-godot** — the RN + Godot bridge for the
  cross-platform MMO client.
- **react-native-reusables** — re-usable RN UI primitives
  (the Celtic OS shell).

## References (in this skill)

- `references/spacetimedb.md` — SpacetimeDB KCG summary.
- `references/spacetimedb-cookbook.md` — SpacetimeDB cookbook
  KCG summary.
- `references/spacetimedb-typescript-sdk.md` — SpacetimeDB TS
  SDK KCG summary.
- `references/wgpu.md` — wgpu KCG summary.
- `references/x402.md` — x402 KCG summary.
- `references/anylanguagemodel.md` — AnyLanguageModel KCG
  summary.
- `references/agui-kotlin.md` — agui_kotlin KCG summary.
- `references/hophacks-spacetimedb-workshop.md` — hophacks
  SpacetimeDB workshop KCG summary.
- `references/ireland-maps.md` — ireland (maps) KCG summary.
- `references/react-native-godot.md` — react-native-godot KCG
  summary.
- `references/react-native-reusables.md` — react-native-reusables
  KCG summary.
- `references/crypteolas-crypto-integration.md` — Crypteolas
  crypto integration (x402 + MCPay + AP2 + Web3).
- `references/x402-payment-guide.md` — x402 server / client /
  Axum middleware Tuatha guide.
- `references/x402-celtic-knowledge-grid.md` — x402 + MCP +
  mcp-ui + Bria + Convex / BitCraft Celtic grid.
- `references/llm-serving-mlflow-langfuse.md` — llama-swap +
  mlx-vlm + LiteLLM + Z.AI gateway.
- `references/wgpu-tuatha-guide.md` — wgpu + particle system +
  Celtic shaders Tuatha setup.
- `references/clippings/agent-native-rails-compare.md` — 6
  agent-native rails comparison (MCP / A2A / AP2 / ACP /
  x402 / Kite).
- `references/clippings/wgpu-v28-release.md` — wgpu v28
  release notes.
- `references/clippings/better-auth-siwe.md` — Better Auth
  SIWE.

## Cross-references

- `.agents/skills/kcg-bunchloch/SKILL.md` — the 3-tier
  topology where the mirrors (SpacetimeDB, wgpu, llama-swap,
  mlx-omni-server) are deployed.
- `.agents/skills/stack-ops/SKILL.md` — the GOLD_STANDARD
  6-file pattern (the way the mirrors are dockerised).
- `.agents/skills/better-auth/SKILL.md` — the SIWE auth
  pattern (covered by the `better-auth-siwe` clipping).
- `.agents/skills/celtic-language-ai/SKILL.md` — the
  AnyLanguageModel mirror's role in the Celtic LLM stack.
- `.agents/skills/tuatha-mmo/SKILL.md` — the consumer of the
  SpacetimeDB, wgpu, x402, agui_kotlin, react-native-godot,
  and react-native-reusables mirrors.
- `.agents/skills/irish-llm-on-device/SKILL.md` — the
  consumer of the AnyLanguageModel mirror.
- `docs/sruth/tuatha/08-mirrors/` — the source trees (KEEP).
