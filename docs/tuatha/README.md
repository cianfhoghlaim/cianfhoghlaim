# Tuatha — Game Development Reference Library

The Tuatha Celtic Educational MMO + crypteolas crypto
platform reference library. After the round-8 docs
consolidation, all KCG-authored content lives in
`.agents/skills/`; this directory retains only the
**08-mirrors/** subtree (skeletonised upstream
repositories for offline reference: SpacetimeDB, x402,
wgpu, gdext, react-native-*, etc.).

## The 4 canonical skills

| Skill | Purpose |
|:--|:--|
| `.agents/skills/tuatha-mmo/SKILL.md` | The Celtic Educational MMO (Babylon.js + SpacetimeDB + Rust + x402 + SIWE + Pent-Elemental Cosmology). ~38 references. |
| `.agents/skills/celtic-asset-generation/SKILL.md` | The 5-stage Celtic asset generation pipeline (BAML → CocoIndex v1 → Cognee → Graphiti → LanceDB). ~41 references + 2 VLM papers (Bolmo + Molmo2). |
| `.agents/skills/irish-llm-on-device/SKILL.md` | Apple Silicon + MLX + llama.cpp + AnyLanguageModel for on-device Irish LLMs and OCR/HTR. ~15 references. |
| `.agents/skills/upstream-mirrors/SKILL.md` | Registry of the 11 KCG-mirrored upstream repos (SpacetimeDB, wgpu, x402, etc.). ~19 references. |

## The 08-mirrors/ subtree

Skeletonised copies of upstream repos (SpacetimeDB,
spacetimedb-typescript-sdk, spacetimedb-cookbook,
hophacks-spacetimedb-workshop, wgpu, gdext,
react-native-reusables, react-native-godot, agui_kotlin,
x402, AnyLanguageModel) for offline reference. The
KCG-authored summaries for these mirrors live at
`.agents/skills/upstream-mirrors/references/`.

## Quadrant

`tuatha/` is one of the 4 quadrants of the Cianfhoghlaim
monorepo:

| Path | Tech | Purpose |
|:--|:--|:--|
| `tuatha/game/` | Babylon.js (TS) | 3D game client (the MMO front-end) |
| `tuatha/crates/` | Rust + SpacetimeDB | Game engine (the MMO server) |
| `tuatha/crypteolas/` | Python + Bitcoin/Ethereum/Solana | Crypto data platform |
| `tuatha/ui/` | TanStack Start | Web front-end for the educational game |

See `tuatha/AGENTS.md` for the canonical routing table.
