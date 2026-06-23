# Change: sync-skills-from-docs-round-9

## Why

A ninth round of `docs/*` consolidation. The user asked
to process `docs/web/` (98 .md files + 2 cloned subdirs)
and `docs/tuatha/08-mirrors/` (93 MB of 11 cloned
upstream repos), then **delete both `docs/web/` and
`docs/tuatha/` entirely**.

This is the final "clean-up" round for the web +
mirror sprawl. The web/ directory mirrors the topical
subdir pattern from `docs/tuatha/` (00-nav / 01-tanstack
/ 02-betterauth / 03-ag-ui / 04-alchemy / 05-convex /
06-effect / 07-react-frontend / 08-repos / 09-clippings)
plus 2 cloned repos (`chrome-devtools-mcp/`,
`tanmaxx-17/`).

The 8 prior rounds absorbed every other `docs/*`
subdirectory. This round targets the last two
substantive sprauls: the web knowledge base (which maps
to the existing `tanstack-start`, `better-auth`,
`ag-ui`, `convex`, `effect-ts`, `orpc`, `cloudflare`,
`pydantic-ai`, `monorepo`, `ui-components`, `stagehand`,
`pdf`, `copilotkit`, `celtic-asset-generation`,
`tuatha-mmo` skills) and the 93 MB of skeletonised
upstream repos under `docs/tuatha/08-mirrors/`.

The 11 mirror source trees in `08-mirrors/` are
re-cloneable from upstream (SpacetimeDB, wgpu, x402,
gdext, agui_kotlin, hophacks, react-native-*,
AnyLanguageModel, spacetimedb-cookbook,
spacetimedb-typescript-sdk) — the KCG-authored summaries
already live in the `upstream-mirrors` skill (round 8),
so the 93 MB of source trees is no longer needed for
offline reference. The web/ cloned repos
(`chrome-devtools-mcp`, `tanmaxx-17`) are also external
content; chrome-devtools-mcp coverage lives in the
`stagehand` + `sruth-browser` skills, and tanmaxx-17 is
a third-party demo referenced from the `tanstack-start`
skill.

## What Changes

### 2 new skills

- **`.agents/skills/web-mirrors/SKILL.md`** (188 lines)
  — registry of 8 KCG-authored upstream summaries for
  the web stack: TanStack, Convex, Hono, oRPC, AG-UI,
  Cloudflare Workers, Restate (coding-agent + UI
  summaries). Sister to the existing `upstream-mirrors`
  skill (game/infra stack). The 8 references are the
  `repo-*.md` files from `docs/web/08-repos/`.

- **`.agents/skills/agentic-frontend-frameworks/SKILL.md`**
  (287 lines) — the umbrella skill that stitches TanStack
  Start + CopilotKit + AG-UI + Convex + Hono + oRPC +
  Cloudflare + Pydantic AI / Agno / Google ADK for the
  KCG agentic-web pattern. Fills the round-6 capability
  spec gap. The 3 references are the 3 `agentic-*` and
  `full-stack-*` files from `docs/web/07-react-frontend/`.

### 14 existing skills expanded (+1,536 lines)

- `tanstack-start` (+145) — KCG TanStack patterns (round-9
  deep dive from the 650-line TANSTACK_ANALYSIS)
- `better-auth` (+91) — Self-hosted stack + KCG multi-
  layer auth (SIWE + Drizzle + Expo + Postgres)
- `ag-ui` (+100) — Kotlin mobile SDK + AG-UI vs A2UI vs
  MCP-UI vs Open-JSON-UI
- `convex` (+145) — KCG Convex patterns (6 subsections)
- `effect-ts` (+159) — KCG integration patterns (Effect
  → TanStack Start, Effect → Convex, etc.)
- `orpc` (+146) — oRPC integration patterns (vs tRPC/
  gRPC, EventIterator, OpenAPI)
- `cloudflare` (+77) — Alchemy IaC
- `pydantic-ai` (+70) — AG-UI protocol
- `copilotkit` (+45) — AG-UI vs A2UI vs MCP-UI
- `stagehand` (+37) — Chrome DevTools MCP
- `monorepo` (+97) — Effect-TS + oRPC integration
- `ui-components` (+89) — Frontend idea catalog
- `pdf` (+83) — PDF.js examples
- `tuatha-mmo` (+138) — iOS sandwich architecture
- `celtic-asset-generation` (+89) — Frontend idea catalog
  (design mining)

### Files moved (52 total)

- 27 KEEP-NEW files → various skills' `references/`
- 7 WEB-MIRROR files → `web-mirrors/references/`
- 18 CLIPPING files → various skills'
  `references/clippings/`

### Files deleted (38 + 13 subdirs = 51 total)

**38 .md files deleted from `docs/web/`:**
- 3 nav tombstones (`00-nav/INDEX.md`,
  `00-nav/INDEX-from-bonneagar-web-research.md`,
  `00-nav/README.md`)
- 4 tanstack indexes/summaries
  (`README_TANSTACK_ANALYSIS.md`, `TANSTACK_INDEX.md`,
  `TANSTACK_QUICK_REFERENCE.md`, `TANSTACK_SUMMARY.md`)
- 3 alchemy empty examples
- 1 `07-react-frontend/Asset Management for Full-Stack
  App.md` (dedup with `tuatha-mmo/references/asset-
  management-pixelart.md` from round 8)
- 1 `09-clippings/Release v28.0.0…` (dedup with
  `upstream-mirrors/references/clippings/wgpu-v28-
  release.md` from round 8)
- 1 `08-repos/repo-restate-ui-readme.md` (trivial)
- 1 `README.md` (tombstone; content moved to the 2 new
  skills)
- 16 `chrome-devtools-mcp/` files
- 3 `tanmaxx-17/` files
- 4 misc duplicates / empty files

**13 subdirs deleted:**
- 2 cloned subdirs in `docs/web/`:
  `chrome-devtools-mcp/`, `tanmaxx-17/`
- 11 cloned upstream repos in `docs/tuatha/08-mirrors/`:
  SpacetimeDB, wgpu, x402, gdext, agui_kotlin,
  hophacks-spacetimedb-workshop, react-native-godot,
  react-native-reusables, spacetimedb-cookbook,
  spacetimedb-typescript-sdk, AnyLanguageModel

**2 whole directories deleted:**
- `docs/web/` (after all moves done)
- `docs/tuatha/` (after the 08-mirrors subdir is gone —
  this is the final "delete tuatha" step from the user)

### Disk recovered

- `docs/tuatha/08-mirrors/`: **93 MB** (SpacetimeDB 41M +
  x402 26M + spacetimedb-cookbook 9.6M +
  react-native-reusables 7.9M + gdext 5.0M + wgpu 840K +
  spacetimedb-typescript-sdk 944K + hophacks 328K +
  react-native-godot 76K + agui_kotlin 80K +
  AnyLanguageModel 48K)
- `docs/web/`: ~3.5 MB

## Impact

- **Affected specs (1)**: `agentic-frontend-frameworks`
  (the round-6 capability spec) — adds 3 new requirements
  (TanStack Start + AG-UI + Convex + Hono + oRPC + Pydantic
  AI integration; 4 canonical surfaces; AG-UI protocol
  table)
- **Affected code**: none. Skills + OpenSpec only.
- **Affected skills** (16 total): 2 new + 14 expanded
- **Net docs/ size change**: 96.5 MB → 0 (both `docs/web/`
  and `docs/tuatha/` deleted entirely)
- **Net `.agents/skills/` size change**: +~3,000 lines
  (2 new SKILL.md bodies + 52 references + 14 expanded
  SKILL.md sections)

## Success criteria

- `openspec validate sync-skills-from-docs-round-9
  --strict` passes
- The 2 new skills exist at
  `.agents/skills/{web-mirrors,agentic-frontend-frameworks}/SKILL.md`
- The 14 expanded skills have new sections (each ending
  with a "See [reference path] for the full deep dive"
  footer)
- The 38 listed docs files are removed
- The 13 subdirs are removed (2 in `docs/web/`, 11 in
  `docs/tuatha/08-mirrors/`)
- `docs/web/` is gone
- `docs/tuatha/` is gone
- The `agentic-frontend-frameworks` skill has its
  capability spec wired up (the round-6 capability was
  previously unbacked)

## Rollback

Skills-only. Rollback = restore the 52 moved + 38
deleted + 13 subdir-deleted files from git, drop the 2
new skill directories + the 14 expanded SKILL.md
changes. No data, code, or runtime state is affected.
