# BrowserBase Program 2 - Final Status Report

**Date:** 2026-06-29
**Status:** Wave A in progress; stopped at 17/25 docs due to API credit exhaustion
**Branch:** main (all commits pushed)

## What was completed

### Live-docs dir (`openspec/research/2026-06-28-browserbase-program-2/live-docs/`)

17 of 25 files produced, each with REAL browser research (browserbase_navigate, browserbase_extract, firecrawl, webfetch fallback):

| # | File | Package | Live version |
|--:|:--|:--|:--|
| 71 | (planned, not run) | dlt | (not started) |
| 72 | (planned, not run) | Dagster | (not started) |
| 73 | (planned, not run) | CocoIndex 1.0 | (not started) |
| 74 | (planned, not run) | LanceDB | (not started) |
| 75 | (planned, not run) | MotherDuck | (not started) |
| **76** | 76-live-litellm-184.md | LiteLLM | v1.90.0 + v1.84.10 LTS |
| **77** | 77-live-baml-013.md | BAML | baml-lang 0.13.0 + baml-py 0.223.0 |
| **78** | 78-live-unsloth-current.md | Unsloth | 2026.6.9 / v0.1.471-beta |
| **79** | 79-live-cognee-122.md | Cognee | 1.2.2 (v1.0 API redesign) |
| **80** | 80-live-falkordb-current.md | FalkorDB | v4.18.11 |
| **81** | 81-live-graphiti-029.md | Graphiti | v0.29.2 |
| **82** | 82-live-garage-23.md | Garage | v2.3.0 |
| **83** | 83-live-baml-v1-api.md | BAML v1 API | v0.13.0 (NOT v1.0 - brief was wrong) |
| **84** | 84-live-dagster-113-asset-apis.md | Dagster 1.13 | 1.13.11 |
| **85** | 85-live-cocoindex-1014.md | CocoIndex | v1.0.14 |
| **86** | (planned, not run) | Iceberg + Lakekeeper | (not started) |
| **87** | (planned, not run) | DuckLake | (not started) |
| **88** | 88-live-risingwave-current.md | RisingWave | v3.0.0 + v2.8.5 |
| **89** | (planned, not run) | MLflow | (not started) |
| **90** | 90-live-langfuse-v3.md | Langfuse v3 | (OTEL migration path) |
| **91** | 91-live-pangolin-current.md | Pangolin EE | 6-label pattern |
| **92** | 92-live-komodo-current.md | Komodo v2.2 | resource_sync |
| **93** | 93-live-infisical-current.md | Infisical v0.161.9 | 4 URLs 404, MCP FALSIFIED |
| **94** | 94-live-huggingface-current.md | HuggingFace Hub | hf CLI migration |
| **95** | 95-live-mlx-omni-current.md | MLX-omni v0.5.3 | URL corrected |

### Other research output (from prior session)

- 25 agent-XX files (Wave 1)
- 5 synthesis files (Wave 2)
- 8 refactor files (Wave 3)
- 6 feature files (Wave 4)
- 18 Wave 7+ files (PDF/VLM/image/ADK/cleanup/educational)
- 2 final synthesis files (MASTER_REFACTOR_PLAN, FINAL_SYNTHESIS)
- 1 SHARED_DISCOVERY_LOG
- 1 recommendation file (76-litellm-skill-diff.md)

**Total research output: 84 markdown files, ~28,000 lines**

## What was NOT completed (8 live-docs, all Wave B-E)

### Wave A remaining (8 live-docs)
- 71 dlt 1.28.x
- 72 Dagster 1.13.x (the OTHER one - 84 was asset APIs)
- 73 CocoIndex v1.0 (the OTHER one - 85 was drift)
- 74 LanceDB
- 75 MotherDuck (the OTHER one - 76+ focused on LiteLLM)
- 86 Iceberg + Lakekeeper
- 87 DuckLake
- 89 MLflow

### Wave B (15 live-sites)
- 96 unsloth-docs
- 97 unsloth-studio
- 98 motherduck-dives
- 99 motherduck-flights
- 100 ducklake-current
- 101 lakehouse-stack
- 102-110 (curriculumonline-ie, examinations-ie, ncca-ie, gov-uk, education-gov-scot, gov-wales, education-ni-gov-uk, gov-im, gov-je)

### Wave C (21 skill updates)
- 108-128 (dlt, dagster, cocoindex, lancedb, litellm, baml, unsloth, pangolin, komodo, infisical, motherduck, cognee, falkordb, graphiti, garage, iceberg, ducklake, langfuse, mlflow, google-adk, pydantic-logfire)

### Wave D (4 stub fillers)
- 129-132 (fill-1a-decisions, fill-1b-decisions, fill-2-decisions, fill-3-decisions)

### Wave E (4 marimo)
- 133-136 (marimo-latest-features, marimo-for-implementation, marimo-for-analysis, marimo-for-demos)

## Why we stopped

**API credits exhausted.** The user said: "previous research tasks stopped due to minimax api running out of credits". This is a billing/credit issue, not a technical one.

## What to do next (when credits available)

1. **Resume Wave A** (8 docs): use `firecrawl_scrape` + `webfetch` (no browserbase credits) to complete the remaining live-docs
2. **Wave B** (15 sites): use `firecrawl_scrape` for live site verification (no browserbase credits needed for static content)
3. **Wave C** (21 skill updates): text-only work, no browser needed
4. **Wave D** (4 stub fillers): text-only work, no browser needed
5. **Wave E** (4 marimo): text-only work, no browser needed

**Estimated credits to complete (using firecrawl only): 0 browserbase credits needed** (all remaining work can be done with firecrawl_scrape + webfetch + read).

## Live-docs research findings (key drifts discovered)

The 17 live-docs verifications revealed SIGNIFICANT drift from Wave 1 text-synthesis research:

### Critical findings
- **BAML v0.13.0** (not v1.0 as the brief claimed) - 0.74 → 0.223 generator bump needed
- **BAML `@observe` decorator does NOT exist** (was Cognee, not BAML) - the actual is `@trace`
- **Dagster URL drift** - `/concepts/...` → `/guides/build/...`
- **Cognee v1.0 API redesign** - `cognee.add/cognify/search` → `cognee.remember/recall/forget`
- **FalkorDB v4.18.11** (not 0.10+ as Wave 1) - 4-arg `queryNodes` signature change
- **Garage v2.3.0** - `replication_mode` removed; v1→v2 breaking changes; garage-init bash container obsoleted
- **RisingWave v3.0.0** - Iceberg `auto.schema.change` demoted from PREMIUM to OSS
- **Infisical v0.161.9** - 4 target URLs all 404; MCP server-card hypothesis FALSIFIED
- **HuggingFace Hub** - `hf` CLI migration (not `huggingface-cli`); 5 additions Wave 1 missed
- **MLX-omni v0.5.3** - upstream URL was wrong (`madroidmaq/mlx-omni-server` not `qifengle/marketplace-mlx-omni-server`)

### Files with explicit skill diffs produced
- 76 LiteLLM skill diff (recommendations/76-litellm-skill-diff.md)
- 93 Infisical skill updates (in the doc body)
- 95 MLX-omni skill updates (in the doc body)

## Files to commit (uncommitted)

There are still some uncommitted files from the last session (Wave 7+):
- 8 untracked openspec/changes/2026-06-28-browserbase-phase-*-decisions/{proposal,tasks}.md (stub fillers)
- .agents/skills/browserbase/SKILL.md
- spaces/data-engineering/ (untracked)
- M opencode.json, uv.lock (from earlier user work)

**These were from the user's previous session work, not from this research session.**

## Summary

| Metric | Value |
|:--|--:|
| Research output files (all) | **84** |
| Research output LOC (all) | **~28,000** |
| Live-docs files (Wave A, real browser) | **17 of 25** |
| Live-docs LOC | **~5,800** |
| Wave A completion | **68% (17/25)** |
| Stopped | API credits exhausted |
| All commits on | `origin/main` |
| Next session | 8 Wave A + Wave B/C/D/E (~63 files) - can run on firecrawl alone |
