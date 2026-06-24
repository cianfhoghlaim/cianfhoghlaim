---
name: kcg-docs-consolidation
description: The Cianfhoghlaim documentation consolidation retrospective (1,038 → 36 files, 28.8:1 ratio) — methodology, the 7-domain taxonomy, the 1,036-file discovery inventory, the dedup patterns (152 duplicate filenames, 82 Irish-language files, 116-file nested mirror), and the 4-phase rollout plan for the agent-consumable frontmatter schema. The 2026-06-06 round-1 reference for every subsequent docs round (2-9 + this round 10). Use when planning a docs consolidation, sizing a documentation cleanup, designing a frontmatter schema, debugging a stale index, identifying duplicate content, or asking "how did we get from 1,038 files to 36?", "what dedup patterns did we find?", "what's the 7-domain Cianfhoghlaim taxonomy?", "what's the rollout plan for the frontmatter schema?".
---

# KCG Docs Consolidation

## When to use this skill

Use when you need to:

- "Understand how the Cianfhoghlaim docs went from 1,038
  files to 36"
- "Plan a docs consolidation round (heuristics, dedup
  patterns, ratio targets)"
- "Identify duplicate or near-duplicate docs"
- "Detect Irish-language / dialectal content that should
  be preserved, not deleted"
- "Design a domain taxonomy for a documentation corpus"
- "Reuse the discovery inventory format for a new audit"
- "Apply the 4-phase frontmatter rollout (Phase 1: INDEX
  files → Phase 4: full coverage)"
- "Compute the consolidation ratio for a new round"
- "Cross-reference round 1-9 + round 10 work"

## Overview

The **kcg-docs-consolidation** skill is the **round-1
retrospective + audit** for the Cianfhoghlaim documentation
consolidation executed on **2026-06-06**. Before the
round, the `docs/` subtree held **1,038 files** (998
`.md`, 24 `.py`, 7 `.pdf`, 5 `.yaml`, 1 `.toml`, 1 `.docx`)
spread across 8 unorganised subtrees + a 116-file nested
mirror at `docs/tuatha/tuatha/`. Total on-disk footprint
was **49.7 MiB**.

After the round, the canonical tree held **36 .md files
+ 1 master index** — a **28.8:1 consolidation ratio** —
with a `domain` enum, a `status` lifecycle, a
`read_when` routing directive, and a `related_skills`
back-link on every doc. The round introduced the 7
numbered domains (`00-core`, `01-platform-architecture`,
`02-data-platform`, `03-agents`, `04-ai-ml`, `05-web`,
`06-product`, `07-standards`) and the master routing
index at `docs/00_index.md` (auto-generated, not
hand-maintained).

The retrospective (`consolidation_plan.md`, 525 lines) and
the discovery inventory (`discovery_inventory.md`, 2,612
lines) are the **canonical round-1 references** for every
subsequent docs round. Rounds 2-9 (and this round 10)
apply the same methodology — heavy-merge + frontmatter +
auto-generated index — against the remaining `docs/`
subdirs that round 1 did not touch.

## The 7-domain taxonomy (post-2026-06-06)

| # | Domain | Purpose | Example skills |
|:--|:--|:--|:--|
| 1 | `00-core/` | Project identity, quadrant map, constraints | — |
| 2 | `01-platform-architecture/` | Pangolin, Komodo, Hono, Forgejo, Cloudflare | `pangolin`, `komodo`, `dagger`, `pulumi` |
| 3 | `02-data-platform/` | DLT, Dagster, DuckLake, MotherDuck, Iceberg | `dlt`, `dagster`, `motherduck`, `duckdb`, `ducklake` |
| 4 | `03-agents/` | Agno, ADK, CopilotKit, MCP, browser, A2UI | `agno`, `google-adk`, `copilotkit`, `mcp-builder`, `browser`, `firecrawl` |
| 5 | `04-ai-ml/` | Unsloth, OCR/HTR, knowledge graphs, RAG, embeddings, Celtic language | `unsloth`, `peft`, `trl`, `cognee`, `graphiti-core`, `lancedb`, `ragas`, `langfuse`, `mlflow` |
| 6 | `05-web/` | TanStack Start, Convex, Hono, auth | `tanstack-start`, `convex`, `hono`, `orpc`, `cloudflare`, `better-auth` |
| 7 | `06-product/` | Celtic MMO, Crypteolas, educational platform, game dev | `tuatha-mmo`, `babylonjs`, `upstream-mirrors` (SpacetimeDB), `celtic-asset-generation` |
| 8 | `07-standards/` | Project conventions, observability patterns | `dignified-python`, `agent-observability` |

The 8 domains cover the 4 quadrants of the Cianfhoghlaim
monorepo (`oideachais/` data, `meaisínfhoghlaim/` AI/ML,
`tuatha/` MMO, `croilar/` portfolio) + the shared
`infrastructure/` runtime. The `00-core/` domain holds
the project identity doc that the rest of the tree
links back to.

## The 4-phase frontmatter rollout plan

The 2026-06-06 round produced the frontmatter schema
(see `agent-docs-patterns` skill) and the gap analysis
that showed **0 of 10 sampled docs** had any agent-routing
frontmatter. The 4-phase rollout to fix this:

| Phase | Goal | Effort |
|:--|:--|:--|
| **1. Foundation** | Add frontmatter to all `INDEX.md` files (9 files) + create `docs/00_index.md` master index; add frontmatter to ~15 top-priority docs | 1 session |
| **2. Skill backlinking** | Update ~40 agent `SKILL.md` files with a `## References` section pointing to `docs/` paths; add `related_skills` to the docs | 2 sessions |
| **3. Automation** | Write a `docs:sync` script (akin to `erk docs sync`) that reads every frontmatter, validates the schema, regenerates `docs/00_index.md`; wire it into `turbo.json` as `docs:sync` task | 1 session |
| **4. Full coverage** | Audit all 300+ remaining docs for frontmatter addition; identify and archive superseded docs via `status: superseded` + `superseded_by`; integrate `ccc_query_hints` with the ccc indexing pipeline | 3-4 sessions |

The 4 phases are **dependency-ordered** (1 must finish
before 2, etc.). Rounds 2-9 of the Cianfhoghlaim docs work
have advanced through Phases 1, 2, and most of 4. Round 10
(this round) finishes the cleanup of `docs/02-audit/`,
`docs/03-agents/`, `docs/03-pipelines/`, `docs/07-standards/`,
`docs/08-screenshots/`, plus the upstream-mirror clips and
the remaining `docs/00-deploy-plans/`.

## The dedup patterns (the round-1 findings)

The discovery inventory (`discovery_inventory.md`, 2,612
lines) catalogued 1,036 files across 8 subtrees. The
**dedup patterns** that drove the consolidation ratio:

| Pattern | Count | Resolution |
|:--|--:|:--|
| Exact-duplicate filenames across subtrees | **152** | Pick the canonical (usually the more recent or the more specific) and `supersedes:` the rest |
| Predominantly Irish / Gaelic content | **82** | Preserve under `04-ai-ml/celtic-language/` or `05-celtic-language/`; never delete |
| Nested mirror at `docs/tuatha/tuatha/` | **116** | Archive to `docs/archive/tuatha-mirror/`; the canonical KCG content lives at `docs/06-product/celtic-mmo.md` |
| Files with frontmatter but no `domain` / `status` | **201** | Re-emit frontmatter with the canonical 12-field schema |
| 0 master index | 1 | Generate `docs/00_index.md` from frontmatter |
| 0 auto-generated indexes | 9 manual `INDEX.md` files | Replace with `docs:sync` script output |

The 152 duplicate filenames were the **single biggest
contributor** to the 28.8:1 ratio. The pattern of
"preserve the canonical, archive the rest" was applied
uniformly — no file was deleted, only archived with
traceable `supersedes` links.

## Round-10 application (the current round)

This round (round 10) applies the round-1 methodology to
the remaining `docs/` subdirs:

| Subdir | Round-10 action | Files affected |
|:--|:--|--:|
| `docs/00-deploy-plans/` | KEEP-NEW → `kcg-deploy-runbooks/references/` | 5 (1,214 lines) |
| `docs/01-cognee/` | EXPAND → 2 skills (`cognee`, `agent-observability`, `ccc`) | 9 (1,448 lines) |
| `docs/02-architecture/` | EXPAND → `tuatha-mmo` | 1 (73 lines) |
| `docs/02-audit/` | KEEP-NEW + EXPAND (consumability → `agent-docs-patterns`; consolidation + discovery → `kcg-docs-consolidation`; ccc + cognee → `ccc` + `cognee` skills) | 4 (3,837 lines) |
| `docs/03-agents/` | EXPAND → `agentic-frontend-frameworks` | 3 (1,865 lines) |
| `docs/03-pipelines/` | EXPAND → `celtic-asset-generation` | 1 (393 lines) |
| `docs/07-standards/` | EXPAND → `celtic-asset-generation` + `agent-observability` | 2 (778 lines) |
| `docs/08-screenshots/` | EXPAND → `kcg-convergence` + `ui-components` | 3 (799 lines) |
| `docs/00_index.md` | EXPAND → `celtic-asset-generation` + delete | 1 (229 lines) |
| `docs/INDEX.md` | DELETE (stale 2025-12-30 NotebookLM context lib) | 1 (199 lines) |
| `docs/hackathons/`, `docs/hmgcc/` | CLIPPING → `upstream-mirrors/references/clippings/` | 4 (+ 4 binary PDFs flagged for round 11) |
| `docs/08-mirrors/marimo/` + `docs/08-mirrors/marimo-docs/` | `git rm -rf` (full upstream clones, 175 MB) | 261 (sub-batch 10.A, done in parallel) |
| `docs/docs_examples_consolidated/` | DELETE (boilerplate Better-T-Stack + DuckDB-Cloudflare examples) | 30 (out of scope; non-KCG) |
| `docs/openspec/` | DELETE (historical research; superseded by `openspec/AGENTS.md` + `.agents/skills/customize-opencode`) | 5 (3,148 lines) |

**Net round-10 result:** 23 KEEP-NEW + EXPAND moves, 263
deletes, 3 new skills created, 8 existing skills expanded,
~176 MB reclaimed (175 MB upstream mirrors + 1 MB boilerplate).

## The 2 canonical references (in this skill)

| Reference | Content |
|:--|:--|
| `reports/round-2026-06-06.md` | The 525-line retrospective: before/after comparison, methodology, the heavy-merge strategy, the domain map, the migration paths, the Cognee/ccc readiness, the agent skill integration, the 4-phase rollout plan, the critical risks |
| `reports/round-discovery-inventory.md` | The 2,612-line discovery audit: 1,036 files across 8 subtrees, extension × subtree matrix, frontmatter audit (203 files with frontmatter, 0 with `domain:` or `status:`), Irish / dialectal content inventory (82 files), duplicate-filename inventory (152 files), per-subtree depth analysis |

The retrospective is the **what we did and why**; the
discovery inventory is the **what we found and how we
counted it**. Both are the canonical round-1 references
for any future docs round.

## Cross-references

- `agent-docs-patterns/SKILL.md` — the frontmatter schema
  the round produced
- `oideachais/AGENTS.md` + `meaisinfhoghlaim/AGENTS.md` +
  `tuatha/AGENTS.md` + `croilar/AGENTS.md` — the
  per-quadrant routing (the 4 quadrants the 7-domain
  taxonomy covers)
- `openspec/AGENTS.md` — the OpenSpec workflow
  (capability spec frontmatter is a different schema)
- `.agents/skills/dagster/erk-skills/agent-docs/SKILL.md` —
  the dagster/erk `agent-docs` skill (the pattern this
  round-1 schema is synthesised from)
- `docs/00_index.md` — the master routing index (the
  round-1 output)
- `oideachais/STATUS.md`, `oideachais/REFACTORING.md` —
  the data platform state files (the 7-domain
  taxonomy's day-to-day consumers)
