# Proposal — `refactor-quadrants-to-sruth`

## Why

The Cianfhoghlaim monorepo has 8 top-level directories (`sruth/oideachais/`, `sruth/meaisinfhoghlaim/`, `sruth/tuatha/`, `sruth/croilar/`, `infrastructure/`, `leabharlann/`, `spaces/`, `dlthub/`) but the prose, prompts, skills, and subagent roster throughout the codebase already adopt a different mental model: the 5 **sruthanna** (Irish for *flows*) — `oideachais`, `infrastructure`, `meaisinfhoghlaim`, `croilar`, `tuatha`. The convention is documented in:

- `opencode.json` (5 sruth-specialist subagents)
- The `build` and `plan` agent prompts ("dispatch the 5 sruth subagents", "5 sruthanna")
- 19+ skill files that reference `sruth/oideachais/dlt_sources/`, `sruth/tuath/docs/`, `sruth/tuath/ui/`, etc.
- The root `README.md` (lines 335–341): *"In `opencode.json`, the four traditional top-level subprojects (oideachais, meaisinfhoghlaim, tuatha, croilar) plus infrastructure are referred to as the five sruthanna — flows — rather than 'quadrants'..."*
- `infrastructure/stacks/motherduck/blueprint.yaml` — already uses `pipeline: sruth/oideachais` and `pipeline: sruth/crypteolas` (forward-looking)

But the **filesystem still uses root-level directories**. This creates a permanent divergence between documented convention and actual layout — every new skill, openspec change, or agent run has to translate between two parallel mental models.

In addition, three structural issues have accumulated:

1. **`baml_src/` duplication**: 13 files at root + 20 files in `sruth/oideachais/baml_src/` + 5 in `sruth/tuatha/baml_src/` + 9 in `sruth/croilar/baml_src/` + 6 in `sruth/crypteolas/baml_src/` + a duplicate `sruth/croilar/baml/` directory (byte-for-byte identical to `sruth/croilar/baml_src/`) — three sets of duplicate BAML files need merging.
2. **`dg.toml` staleness**: the root `dg.toml` uses the deprecated `[[workspace.projects]]` syntax, references a now-moved `sruth/crypteolas/apps/crypteolas_demo/` path, and is missing a per-sruth `dg.toml` for `oideachais` (the largest sruth). One pre-sruth reference names `meaisin_heartbeat` instead of `meaisinfhoghlaim`.
3. **README drift**: lines 55, 69, 137–138, and 287–303 of root `README.md` reference 5 generic subagents (`explorer`, `data-engineer`, `ai-engineer`, `frontend-dev`, `devops-architect`) that do not exist in `opencode.json`.

This change refactors the filesystem to match the documented sruth/ convention, modernizes the Dagster workspace, de-duplicates the BAML corpus, and corrects the README.

## What Changes

### 1. Move 5 sruthanna into `sruth/`

| Sruth | Source | Destination |
|:--|:--|:--|
| **codeolas** | `codeolas/` | `sruth/codeolas/` |
| **oideachais** | `sruth/oideachais/` | `sruth/oideachais/` |
| **meaisinfhoghlaim** | `sruth/meaisinfhoghlaim/` | `sruth/meaisinfhoghlaim/` |
| **tuatha** | `sruth/tuatha/` | `sruth/tuatha/` |
| **crypteolas** | `sruth/crypteolas/` | `sruth/crypteolas/` |
| **croilar** | `sruth/croilar/` | `sruth/croilar/` |

`infrastructure/`, `leabharlann/`, `openspec/`, `spaces/`, `dlthub/`, `archive/`, `scripts/`, `cian_mac_an_déisigh_uí_liatháin/`, and `.agents/skills/` remain at root as cross-cutting concerns.

### 2. Use explicit `sruth.<flow>.` Python import prefix

All Python imports are updated from `from oideachais.X import Y` to `from sruth.oideachais.X import Y` (no PYTHONPATH manipulation — explicit is better than implicit). Same pattern for the other 5 sruthanna.

### 3. Preserve all Cognee + Dagster asset key names

No rename of `oideachais.*` → `sruth_oideachais.*` — legacy asset keys are preserved to keep existing Dagster runs, Cognee datasets, and LanceDB tables valid.

### 4. Consolidate `baml_src/` per sruth

- **Root `baml_src/` is DELETED** (13 .baml + 2 .md files migrated first; deletion is the final commit, gated by a verification step).
- **3 BAML file merges** (root + oideachais duplicates):
  - `clients.baml` (root + oideachais `clients.baml` + oideachais `clients_0.baml` → single `sruth/oideachais/baml_src/clients.baml`)
  - `curriculum_extraction.baml` (root + oideachais `curriculum_extraction.baml` + oideachais `curriculum_extraction_0.baml` → single `sruth/oideachais/baml_src/curriculum_extraction.baml`)
  - `official_media.baml` (root + oideachais → single `sruth/oideachais/baml_src/official_media.baml`)
- **5 BAML files move from oideachais to meaisinfhoghlaim** (AI/ML/OCR/HTR/speech-pipeline domain):
  - `audio_extraction.baml`, `celtic_sources.baml`, `ocr_extraction.baml`, `ocr_validation.baml`, `gaois/{duchas,folklore_extraction,logainm,tearma}.baml` (4 files)
- **`sruth/croilar/baml/` is DELETED** (9 byte-for-byte duplicates of `sruth/croilar/baml_src/`).
- **`sruth/meaisinfhoghlaim/baml_src/` is NEW** (didn't exist previously; populated from root + oideachais migrations).

### 5. Modernize Dagster workspace

- Root `dg.toml`: migrate from deprecated `[[workspace.projects]]` to current `[[workspace.locations]]` syntax per current Dagster docs.
- **NEW** `sruth/oideachais/dg.toml` (currently missing) with `module_name = "oideachais.data_platform.dagster_defs.definitions"` and `location_name = "oideachais"`.
- 5 existing per-sruth `dg.toml` files updated for new paths.
- Update stale root `dg.toml` entry: `path = "sruth/crypteolas/apps/crypteolas_demo"` → `path = "sruth/crypteolas/apps/crypteolas_demo"` (the `apps/crypteolas_demo/` directory now lives under the moved `sruth/crypteolas/`).
- Rename any reference to `meaisin_heartbeat` back to `meaisinfhoghlaim` (per Q5 user decision; the Dagster skill mentions `meaisin_heartbeat` but this is incorrect — `meaisinfhoghlaim` is the canonical name).

### 6. 4 atomic commits (one per sruth)

Per Q4 user decision, the refactor is split into 4 atomic commits so each is independently revertable:

| Commit | Sruth | Notes |
|--:|:--|:--|
| `refactor: move codeolas to sruth/` | codeolas | Standalone library, no Dagster code-location, no baml_src |
| `refactor: move oideachais to sruth/` | oideachais | Largest sruth (228 assets); creates new `dg.toml` and `pyproject.toml`; consolidates 3 BAML merges |
| `refactor: move meaisinfhoghlaim to sruth/` | meaisinfhoghlaim | Creates new `baml_src/` and `pyproject.toml`; pulls 5 BAML files from oideachais |
| `refactor: move tuatha, crypteolas, croilar to sruth/` | tuatha + crypteolas + croilar | 3 sruth in one commit (Q4 acknowledged); deletes `sruth/croilar/baml/`; updates `sruth/crypteolas/apps/crypteolas_demo` → `sruth/crypteolas/apps/crypteolas_demo` |

Plus 2 follow-on commits:

| Commit | Purpose |
|:--|:--|
| `chore: delete root baml_src after migration verification` | Final commit — gated by a `grep` verification step confirming every root `baml_src/` file has a corresponding file in some `sruth/<flow>/baml_src/` |
| `docs: update READMEs and skills for sruth/ convention` | Fix root README subagent naming (lines 55, 69, 137–138, 287–303); update 7 per-sruth READMEs; update 19+ skill files |

**Total commits**: 6.

## Impact

### Files touched (~250 files, ~920 lines)

| Area | Files | Edits |
|:--|--:|--:|
| BAML moves + merges + deletions | ~40 | ~80 |
| Compose stack path updates | 4 | ~15 |
| README updates (8 files; preserve README lines 312–596) | 8 | ~225 |
| Dagster workspace restructure | 8 | ~15 |
| `[tool.uv.workspace] members` | 1 | ~15 |
| `package.json` workspaces | 1 | ~10 |
| `turbo.json` outputs | 1 | ~5 |
| `mise.toml` `cd <sruth>` paths | 1 | ~30 |
| Per-sruth `pyproject.toml` (NEW) | 4 | ~50 |
| Python imports (`sruth.<flow>.` prefix) | ~50 | ~150 |
| Dagster asset keys (preserved, not renamed) | 0 | 0 |
| Cognee dataset names (preserved, not renamed) | 0 | 0 |
| CocoIndex mount_table_target paths | 12 | ~24 |
| openspec/changes/*/tasks.md (paths) | ~28 | ~100 |
| 19+ skill files path examples | 19 | ~60 |
| 9 AGENTS.md routing tables | 9 | ~30 |

### Docker Compose stacks affected (4 files, ~15 lines)

- `infrastructure/stacks/sruth/oideachais/compose.yaml` — bind-mount paths `../../../../sruth/oideachais/...` → `../../../../sruth/oideachais/...`; `working_dir` and `dockerfile` paths
- `infrastructure/stacks/agent-os/compose.yaml` — `context: ../../../oideachais` → `../../../sruth/oideachais`; `context: ../../../sruth/tuatha/crypteolas` → `../../../sruth/crypteolas`
- `infrastructure/stacks/frontend/compose.yaml` — `context: ../../../../sruth/oideachais/web/apps/{web,api}` → `../../../../sruth/oideachais/web/apps/{web,api}`; `tuatha-ui`, `croilar-web`, `croilar-portal` paths
- `infrastructure/stacks/frontend/scripts/dev-start.sh` — `cd "$ROOT/tuatha"` → `cd "$ROOT/sruth/tuatha"`; `cd "$ROOT/sruth/croilar/apps/web"` → `cd "$ROOT/sruth/croilar/apps/web"`

### Files preserved (NOT touched)

- `README.md` lines 312–596 (the "About the author, the name, and the lineage" section) — recently updated with the serious, citation-anchored heritage claim framework (see `extend-culture-heritage-to-8-articles`)
- 7 pre-existing unstaged changes in the working tree (the `.gitignore`, `archive/anti-phish` submodule, `spaces/data-engineering` submodule, `cookes_corner_shantalla_2001.jpeg`, `stirling-pdf backup_202606251017.sql`, etc.) — leave untouched

### Behaviour change

- All 5 sruth-specialist subagents in `opencode.json` continue to work unchanged (they already reference `<sruth>/` paths conceptually)
- Dagster workspace loads 5 code-locations instead of 6 (the 3 separate paths for `tuatha`, `sruth/tuatha/crypteolas`, `sruth/crypteolas/apps/crypteolas_demo` collapse into `sruth/tuatha` + `sruth/crypteolas` + `sruth/crypteolas/apps/crypteolas_demo`)
- All 9 croilar BAML files resolve correctly via `sruth/croilar/baml_src/` (the duplicate `sruth/croilar/baml/` is deleted; only `sruth/croilar/baml_src/` remains)
- New `sruth/meaisinfhoghlaim/baml_src/` directory is the canonical home for 14 BAML files (1 from root + 5 from oideachais + 4 in gaois/ subdir + 4 new schemas found in sruth/oideachais/baml_src per Q5 audit)

### Documentation change

- Root `README.md` lines 55, 69, 137–138, 287–303: subagent roster corrected to match `opencode.json` (5 sruth specialists: `sruth/oideachais/infrastructure/sruth/meaisinfhoghlaim/sruth/croilar/tuatha`, NOT 5 generic roles)
- Root `README.md` lines 13–24: top-level table updated with `sruth/` path prefix on the 4 sruthanna
- 7 per-sruth READMEs: updated with `sruth/` paths and (for codeolas) expanded
- 19+ skill files: their pre-existing `sruth/oideachais/...` path examples are now correct (verified by `ccc` re-index)
- 9 AGENTS.md files: routing tables updated

### No new packages, no new agents, no new infra, no breaking changes to runtime behaviour

## Non-goals

- **No new front-end surface** — pure filesystem refactor
- **No Dagster asset rename** — `oideachais.*` keys preserved
- **No Cognee dataset rename** — `oideachais`, `leabharlann`, `culture_heritage` etc. preserved
- **No Dagster code-location behaviour change** — only paths change; the 5 code-locations load the same Python modules
- **No new BAML extraction function** — only file consolidation + relocations
- **No 1Password migration reintroduction** — the Infisical + Locket + mise pattern is preserved
- **No README personal section change** (lines 312–596 are preserved verbatim)

## Acceptance

- `openspec validate refactor-quadrants-to-sruth --strict` exits 0 with all spec deltas having ≥1 Scenario per ADDED/MODIFIED Requirement
- 6 commits land on `origin/q3-2026-oideachais-consolidation` in order (codeolas → oideachais → meaisinfhoghlaim → sruth/tuatha/sruth/crypteolas/croilar → root baml_src deletion → README/skill updates)
- `dg build` succeeds for all 5 code-locations from the repo root
- `dg dev` smoke test loads all 5 code-locations and lists defs without errors
- `mise run py:typecheck` passes
- `mise run turbo typecheck` passes
- `mise run lint:skills` reports 123/123 skills pass
- `mise run validate-stacks` reports all 94 stacks healthy
- `mise run validate:tenants` passes
- `bun run ccc:index` rebuilds the semantic index with the new sruth/ paths
- `git grep "from oideachais\."` returns no results (all imports updated to `sruth.oideachais.`)
- `git grep "from tuatha\."` returns no results (all imports updated to `sruth.tuatha.`)
- `git grep "from meaisinfhoghlaim\."` returns no results (all imports updated to `sruth.meaisinfhoghlaim.`)
- `git grep "from croilar\."` returns no results (all imports updated to `sruth.croilar.`)
- `git grep "from crypteolas\."` returns no results (all imports updated to `sruth.crypteolas.`)
- `git grep "from codeolas\."` returns no results (all imports updated to `sruth.codeolas.`)
- `ls baml_src/` returns "No such file or directory" (root baml_src deleted)
- `ls sruth/oideachais/baml_src/` contains the merged `clients.baml`, `curriculum_extraction.baml`, `official_media.baml`
- `ls sruth/meaisinfhoghlaim/baml_src/` contains `audio_extraction.baml`, `celtic_sources.baml`, `ocr_extraction.baml`, `ocr_validation.baml`, `image_generation.baml`, `gaois/`
- `ls sruth/oideachais/dg.toml` exists (NEW)
- `ls sruth/oideachais/pyproject.toml` exists (NEW)
- Root `dg.toml` uses `[[workspace.locations]]` syntax (modernized)
- Root `dg.toml` references `sruth/crypteolas/apps/crypteolas_demo` (NOT the stale `sruth/crypteolas/apps/crypteolas_demo`)
- Root `dg.toml` references `meaisinfhoghlaim` (NOT `meaisin_heartbeat`)
- `ls sruth/croilar/baml/` returns "No such file or directory" (duplicate deleted)
- README.md personal section (lines 312–596) unchanged
- README.md lines 55, 69, 137–138, 287–303 corrected to reference real subagents

## Cross-references

- `infrastructure/stacks/motherduck/blueprint.yaml` — already uses `pipeline: sruth/oideachais` and `pipeline: sruth/crypteolas` (forward-looking)
- `opencode.json` — 5 sruth-specialist subagents + build + plan (the canonical subagent roster)
- `.agents/skills/celtic-asset-generation/SKILL.md` — already references `sruth/oideachais/dlt_sources/`, `sruth/oideachais/cocoindex_flows/`, `sruth/oideachais/dagster/`, `sruth/oideachais/agents/`, `sruth/oideachais/core/storage/`
- `.agents/skills/tuatha-mmo/SKILL.md` — already references `sruth/tuath/ui`, `sruth/tuath/docs/`
- `.agents/skills/ui-components/SKILL.md` — already references `sruth/` frontends
- `.agents/skills/monorepo/SKILL.md` — already says "Every `sruth/` frontend (`sruth/oideachais/web`)"
- `openspec/specs/oideachais-pipeline/spec.md` — references `sruth/oideachais/data_platform/dagster_defs/` (will be updated to `sruth/oideachais/`)
- `openspec/specs/oideachais-leabharlann/spec.md`, `oideachais-cocoindex-v1/spec.md`, `celtic-asset-generation/spec.md` — same
- `README.md` lines 335–341 — already explains sruth = flow (the "why" for this change)