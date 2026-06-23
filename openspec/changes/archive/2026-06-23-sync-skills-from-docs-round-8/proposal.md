# Change: sync-skills-from-docs-round-8

## Why

An eighth round of `docs/*` consolidation. The user asked
to process `docs/tuatha/` (95 MB, 85 .md files) and
`docs/teanga/` (40 MB, 56 .md + 2 PDFs) with two key
deltas from prior rounds:

1. **Goal**: create 3 critical end-to-end workflow
   documents for Celtic language asset generation, Irish
   language, and the Tuatha MMO game.
2. **Output shape**: new mega-skills (per the user's
   answer), with long-form KCG docs moving into per-skill
   `references/` subdirs (NOT staying in `docs/`).
3. **teanga/ + tuatha/**: merge `teanga/` into `tuatha/`
   skills, then delete `teanga/`.

The 6 prior rounds absorbed every other `docs/*`
subdirectory. This round targets the largest remaining
sprawl (Celtic + Irish + MMO + Crypteolas), which was
deliberately deferred while the underlying skills
(`celtic-language-ai`, `irish-edtech`, `tuatha-platform`,
`babylonjs`, `unsloth`, `trl`, `peft`, `tts`, `asr`,
`embedding-pipeline`, `kcg-ml-models`,
`kcg-leabharlann-pipeline`) matured.

The `08-mirrors/` subtree (93 MB of skeletonised upstream
repos: SpacetimeDB, x402, wgpu, gdext, react-native-*)
stays untouched per the user's "Keep all 11 mirrors" answer
— the offline reference value outweighs the repo bloat.
The 11 KCG-authored mirror summaries in
`08-mirrors/_summaries/` are pulled into a new
`upstream-mirrors` skill so the summaries survive a
`git mv` of the mirror trees.

## What Changes

### 4 new skills

- **`.agents/skills/celtic-asset-generation/SKILL.md`**
  (298 lines) — the canonical Celtic language asset
  generation pipeline: BAML extraction → CocoIndex v1
  embedding → Cognee/FalkorDB cognify → Graphiti temporal
  memory → LanceDB vector. Tripartite Data Landscape
  (NCCA / SEC / Dept of Ed), bilingual strategy (unified
  concept node + `HAS_FORM` edges), 41 references + 2 PDFs
  (Bolmo + Molmo2) + 8 clippings.

- **`.agents/skills/tuatha-mmo/SKILL.md`** (316 lines) —
  the Celtic Educational MMO: Babylon.js 7 + WebGPU client
  + SpacetimeDB (Rust) server + x402 + SIWE + Crypteolas.
  Pent-Elemental Cosmology (Spirit/Water/Fire/Earth/Air +
  Anam Cara), the 4 sub-modules (game / crates /
  crypteolas / ui), the 4-agent system (Celtic Tutor,
  Mythology Narrator, Quest Guide, Research Assistant), 38
  references + 6 clippings.

- **`.agents/skills/irish-llm-on-device/SKILL.md`** (255
  lines) — Apple Silicon + MLX + llama.cpp +
  AnyLanguageModel. Unsloth + GGUF quantisation, ColPali +
  weak-supervision for handwriting alignment, Qwen2-VL /
  Qwen3-VL fine-tuning, ASR/TTS corpus scraping, 11
  references + 4 clippings.

- **`.agents/skills/upstream-mirrors/SKILL.md`** (147
  lines) — registry of the 11 KCG-mirrored upstream repos
  (SpacetimeDB, wgpu, x402, AnyLanguageModel, agui_kotlin,
  hophacks, ireland maps, react-native-godot,
  react-native-reusables, spacetimedb-cookbook,
  spacetimedb-typescript-sdk). 16 references + 3
  clippings.

### 8 existing skills expanded (+1,492 lines total)

- `baml` (+160): Polyglot IDL (BAML → Python+TS) section
- `celtic-language-ai` (+237): KCG Celtic LLMs (BritLLM
  + EuroLLM + Qomhrá 2025) + Diffusion NMT for low-resource
  Irish + English-pivoted CoT translation
- `cross-domain-registry` (+112): 2024-25 census + fiscal
  context for the 8 nations
- `kcg-leabharlann-pipeline` (+200): Ingestion layer
  (Browserbase + Agno + GLM-4.6v + BAML + Cognee)
- `kcg-ml-models` (+241): EuroLLM 22B entry + Inference
  backends (llama-swap + mlx-vlm + LiteLLM + Z.AI)
- `motherduck` (+138): MCP server (`mcp-server-motherduck`)
- `oideachas-pipeline` (+126): EU sources (1800-line
  catalogue)
- `tuatha-platform` (+278): Sovereign game state
  (SpacetimeDB + DuckDB-WASM + TanStack + CopilotKit) +
  Dagster assets for MMO (Hades + BitCraft agentic
  research)

### Files moved (132 total)

- 119 `git mv` of KEEP-NEW files → 4 new skills'
  `references/` subdirs
- 13 `git mv` of EXPAND files → 8 expanded skills'
  `references/` subdirs (these preserve the long-form
  sources that the expansion sections summarise)

### Files deleted (15 total)

- 5 from `docs/tuatha/` (no longer relevant):
  - `docs/tuatha/INDEX.md` (tombstone — content in
    `tuatha-mmo` SKILL.md)
  - `docs/tuatha/ANALYSIS.md` (tombstone — content in
    `tuatha-mmo` SKILL.md)
  - `docs/tuatha/README.md` (rewritten in this change)
  - `docs/tuatha/00-nav/GRAPHICS_INDEX.md` (content in
    `tuatha-mmo` references)
  - `docs/tuatha/03-data-pipelines/Agentic Web Scraping
    Pipeline.md` (duplicate of teanga copy; the teanga
    copy is now `kcg-leabharlann-pipeline/references/...`)

- 5 from `docs/teanga/` (per MERGE_MAP DELETE):
  - `docs/teanga/INDEX.md`, `docs/teanga/README.md`
  - `docs/teanga/notebooklm_1.md`
  - `docs/teanga/Gaelic in the Digital Age...md`
  - `docs/teanga/Auto-Optimize Pydantic Models...md`

- 10 from `references/` (dedup pairs where the
  tuatha-copy survived but the teanga-copy is the
  canonical)

- 1 whole directory:
  - `docs/teanga/` (after all moves done — per the
    user's "Merge teanga/ into tuatha/, delete teanga/"
    answer)

### `08-mirrors/_summaries/` (11 files)

Moved to `.agents/skills/upstream-mirrors/references/`.
The 11 mirror source trees in `08-mirrors/` stay
untouched.

## Impact

- **Affected specs (2)**:
  - `tuatha-platform` (existing) — adds 2 new requirements
    (Pent-Elemental Cosmology; x402 + SIWE + Crypteolas
    Federated Learning)
  - `celtic-asset-generation` (NEW capability spec)
- **Affected code**: none. Skills + OpenSpec only.
- **Affected skills** (12 total): 4 new + 8 expanded
- **Net docs/` size change**: 95 MB → 1.4 MB (the
  `08-mirrors/` 93 MB + the 4 tuatha/04-game-tech,
  05-ios-ml, 06-tokenomics subdirs which are now empty of
  KCG-authored content)
- **Net `.agents/skills/` size change**: +~16,500 lines
  (4 new SKILL.md bodies + 96 reference files moved in +
  21 clippings)

## Success criteria

- `openspec validate sync-skills-from-docs-round-8
  --strict` passes
- The 4 new skills exist at
  `.agents/skills/{celtic-asset-generation,tuatha-mmo,
  irish-llm-on-device,upstream-mirrors}/SKILL.md`
- The 8 expanded skills have new sections (each ending
  with a "See [reference path] for the full deep dive"
  footer)
- The 15 listed docs files are removed
- `docs/teanga/` is gone
- The 3 priority end-to-end workflows are the new skills'
  SKILL.md bodies (Celtic asset generation, Irish on-device
  LLM, Tuatha MMO)

## Rollback

Skills-only. Rollback = restore the 132 moved + 15
deleted files from git, drop the 4 new skill directories
+ the 8 expanded SKILL.md changes. No data, code, or
runtime state is affected.
