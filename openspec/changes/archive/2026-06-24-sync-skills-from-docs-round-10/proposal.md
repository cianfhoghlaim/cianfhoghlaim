# Change: sync-skills-from-docs-round-10

## Why

A tenth round of `docs/*` consolidation. The user asked
to absorb the remaining docs/ sprawl into .agents/skills/.
The 9 prior rounds processed `02-data-platform`,
`05-celtic-language`, `06-product`, `07-skills`,
`teanga/`, `web/`, `sruth/tuatha/`. This round targets the
last 10 subtrees: 00-deploy-plans, 01-cognee,
02-architecture, 02-audit, 03-agents, 03-pipelines,
06-infrastructure (config only), 07-standards,
08-mirrors (the marimo clones), 08-screenshots.

**Scope**: 287 .md files (261 in `08-mirrors/`, 26
elsewhere) across 10 subtrees. After this round,
`docs/` contains only the KCG config (.yaml/.toml) +
untracked top-level files + a few out-of-scope subdirs
(notebooks/, scripts/, hackathons/, hmgcc/,
docs_examples_consolidated/, openspec/ — flagged for
round 11).

The 261 files in `08-mirrors/` are full upstream clones
of `marimo-team/marimo` and `marimo-team/marimo-docs`.
They were not migrated by the round-9 `08-mirrors/`
cleanup (which targeted the 11 game/infra-stack
mirrors). No `_summaries/` subdir, no KCG-authored
annotations, no `supersedes:` frontmatter on any of
the 261 .md files. All content is upstream. KCG
coverage already lives in `.agents/skills/marimo/SKILL.md`
(round 7+8 work).

## What Changes

### 3 new skills

- **`.agents/skills/kcg-deploy-runbooks/SKILL.md`**
  (~180 lines) — the 5 deferred deploy plans from
  `openspec/plans/tangent_*` rewritten as KCG-anchored
  phased action plans: micro-credentials ledger, cross-
  lingual tutor, automated grading, immersive content
  (flashcard + marimo), policy simulator (temporal
  curriculum diff). 5 references + 1 runbook how-to.

- **`.agents/skills/agent-docs-patterns/SKILL.md`**
  (~100 lines) — the canonical frontmatter schema
  (`title/domain/status/related_skills/ccc_query_hints/
  entities`) and the `agent-docs` skill router pattern.
  1 reference.

- **`.agents/skills/kcg-docs-consolidation/SKILL.md`**
  (~150 lines) — the 1,038→36 retrospective, the
  discovery inventory (1,036 files, 152 duplicate
  filenames, 82 Irish-language files), the dedup
  patterns. Useful as a reference for future rounds. 2
  references.

### 8 existing skills expanded

- `cognee` (+4 sections): KCG architecture diagram, KCG
  Docker stack, KCG per-cluster cognify model, supporting
  infrastructure
- `agent-observability` (+6 sections): Dagster Cognee
  integration, Cognee ingestion workflow, Cognee→
  Langfuse tracing, KCG MCP inventory, Cognee 7-phase
  workflow, Datadog/MLflow/Langfuse/Ragas patterns
- `ccc` (+2 sections): KCG integration, KCG ccc-ready
  index health
- `tuatha-mmo` (+1 section): KCG quadrant reference
- `agentic-frontend-frameworks` (+3 sections): MCP
  protocol, MCP servers, Agent framework index
- `celtic-asset-generation` (+3 sections): KCG AI/ML
  pipeline, KCG critical constraints, KCG docs taxonomy
- `kcg-convergence` (+1 section): Team-workflow stack
  + the migration report as reference
- `ui-components` (+1 section): KCG UI design language
  (Celtic tokens, 3 primary + 5 secondary inspirations)

### Files moved (~30)

- 5 deploy plans → `kcg-deploy-runbooks/references/`
- 1 02-architecture TUATH_MMO → `tuatha-mmo/references/`
- 5 02-audit files → 2 new skills + 2 existing skills
- 3 03-agents files → `agentic-frontend-frameworks/references/`
- 1 03-pipelines AI_ML_PIPELINE → `celtic-asset-generation/references/`
- 1 00_index.md → `celtic-asset-generation/references/`
- 11 01-cognee files → `cognee/`, `agent-observability/`,
  `ccc/` references
- 2 07-standards files → `agent-observability/`,
  `celtic-asset-generation/` references
- 3 08-screenshots files → `kcg-convergence/`,
  `ui-components/` references
- 4 hackathon/HMGCC clippings → `upstream-mirrors/references/clippings/`

### Files deleted (~263)

- 261 `08-mirrors/marimo/` + `marimo-docs/` files
  (`git rm -rf`)
- 2 docs top-level tombstones (`00_index.md`, `INDEX.md`)
- 5 `00-deploy-plans/` files (moved to references)
- 11 `01-cognee/` files (moved to skills' references)
- 1 `02-architecture/` file (moved to tuatha-mmo)
- 5 `02-audit/` files (moved to skills' references)
- 3 `03-agents/` files (moved to skill references)
- 1 `03-pipelines/` file (moved to skill)
- 2 `07-standards/` files (moved to skill references)
- 3 `08-screenshots/` files (moved to skill references)
- 27 `docs_examples_consolidated/` files (external
  boilerplate, no KCG content)
- 4 hackathon files
- 1 HMGCC TRL file
- 5 `docs/openspec/` files (historical research, deleted)

### Disk recovered: 175 MB

`docs/08-mirrors/marimo/` (169 MB) + `marimo-docs/`
(6.2 MB) deleted via `git rm -rf`.

## Impact

- **Affected specs (1)**: `agent-observability` (the
  round-4 spec) — adds 1 new requirement
  (KCG MCP inventory + 5 canonical MCP servers)
- **Affected code**: none. Skills + OpenSpec only.
- **Affected skills** (11 total): 3 new + 8 expanded
- **Net docs/ size change**: 287 - 30 (moved) - 263
  (deleted) - 6 (out-of-scope, still there) = -253
  files + 175 MB freed
- **Net `.agents/skills/` size change**: +~3,000 lines
  (3 new SKILL.md bodies + 30+ references + 8 expanded
  SKILL.md sections)

## Success criteria

- `openspec validate sync-skills-from-docs-round-10
  --strict` passes
- The 3 new skills exist at
  `.agents/skills/{kcg-deploy-runbooks,agent-docs-
  patterns,kcg-docs-consolidation}/SKILL.md`
- The 8 expanded skills have new sections (each ending
  with a "See [reference path] for the full deep dive"
  footer)
- The 261 `08-mirrors/` files are removed (175 MB freed)
- The 263 total deletions are clean
- `docs/08-mirrors/` is gone

## Rollback

Skills-only. Rollback = restore the 263 deleted + 30
moved files from git, drop the 3 new skill directories
+ the 8 expanded SKILL.md changes. The 175 MB of
mirrors can be re-cloned from upstream. No data, code,
or runtime state is affected.

## Out-of-scope for round 10 (flagged for round 11)

- `docs/notebooks/` (95 MB of .ipynb files)
- `docs/scripts/` (12 .py + 2 .yaml KCG code snippets
  misplaced in `docs/`)
- `docs/hackathons/Google Cloud Rapid Agent Hackathon…pdf`
  (1 PDF)
- `docs/hmgcc/*.pdf` (4 security PDFs)
- `docs/06-infrastructure/` (config only; YAML/TOML
  stays in `docs/` — to be addressed in round 11)
