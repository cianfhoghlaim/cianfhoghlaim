# BrowserBase Program 2 — FINAL SYNTHESIS (1-page team skim)

**Date:** 2026-06-29 · **Program:** 43-prompt BrowserBase research program 2 (v4 post-consolidation) · **Scope:** 25 wave-1 package/site agents → 5 wave-2 syntheses → 8 refactor specs + 6 feature specs → 7 focused-research deep-dives (PDF / VLM-OCR / image-gen / image-extract / OCR-cleanup / ADK+Logfire / educational-assets)

> **Read this first; everything else is detail.** Full source: [`openspec/research/2026-06-28-browserbase-program-2/`](./) (64 files, ~21,000 lines).

---

## 1. TL;DR (5 lines)

1. **44 agents produced 64 research files (~21,000 lines) in 1 day** — 25 wave-1 packages/sites, 5 wave-2 syntheses, 8 refactor + 6 feature specs, 7 focused-research deep-dives (PDF OCR × 4 backends, VLM × 3 models, image-gen × 3, image-extract × 2, ADK+Logfire, 5-stage pipeline, cross-lingual) — the single most-comprehensive codebase audit in Cianfhoghlaim history.
2. **11 P0 items are silently broken in prod today, 2 with hard dates** — FalkorDB ships without `vector.so` (every vector query 404s), Garage pinned 8 releases behind v2 EOL, BAML's 14 inline `client "anthropic/claude-sonnet-4-20250514"` calls bypass LiteLLM gateway, 8 of 11 aspirational HF model IDs don't exist on Hub; **LiteLLM `:main-stable` cuts over 2026-06-30 (≤2 days)** and **Infisical CLI repo migrates 2026-09-16**.
3. **Top 3 outcomes:** (a) **refactor backlog of ~30 P0/P1 + ~45 P2 + ~40 P3 = 109 items** with 80% of value in 24 items; (b) **26 new features** (7 P0 + 8 P1 + 5 P2 + 6 P3) clustered into 5 delivery themes (Realtime+Memory, Multilingual+Multimodal, Observability+Auto-improve, Edge+GPU, Content+Sites); (c) **30+ specific misunderstandings** in 4 phase stub changes + 3 celtic-asset-generation spec versions + 33 P-specs + 12 S-specs — **12 of which are runtime-breaking** (will silently lose data on first run).
4. **Cross-cutting insight:** the platform is a **3-tier sealed system (Cloudflare edge → Pangolin EE → Komodo orchestrator → 90 Docker Compose stacks)** with **one Infisical→Locket secrets backbone (130+ URIs)** and **one LLM gateway seam** that BAML's 14 inline calls violate — the gateway is the highest-leverage single point of failure.
5. **Estimated ~850 BrowserBase credits consumed** (well under the 2,000 budgeted) — concentrated in agent 23 (Ireland sites, 340) + agent 21 (HuggingFace, 120) + F-44 (codegen, 210); 28 of 44 agents used 0 credits (code/docs only).

---

## 2. The numbers

| Metric | Value | Source |
|:--|--:|:--|
| **Total research files** | 64 | `find . -name '*.md' \| wc -l` |
| **Total LOC** | ~21,000 | `find . -name '*.md' -exec wc -l {} +` |
| **Wave-1 package/site agents** | 25 | `agent-01..25.md` (7,751 lines + 503-line `SHARED_DISCOVERY_LOG.md`) |
| **Wave-2 syntheses** | 5 | `synthesis/26..30-*.md` (1,188 lines) |
| **Refactor specs (Wave 3)** | 8 | `refactors/31..38-*.md` (3,771 lines) |
| **Feature specs (Wave 3)** | 6 | `features/39..44-*.md` (2,674 lines) |
| **Focused research deep-dives** | 16 files / 7 dirs | `pdf-processing/ vlm-ocr/ image-generation/ image-extraction/ ocr-cleanup/ adk-logfire/ educational-assets/` (~5,560 lines) |
| **Cross-agent discoveries logged** | 29+ entries | `SHARED_DISCOVERY_LOG.md` (503 lines, 11 cross-deps, 4 conflicts) |
| **Total refactor backlog** | ~109 items | 11 P0 + 13 P1 + 45 P2 + 40 P3 |
| **Total feature backlog** | 26 features | 7 P0 + 8 P1 + 5 P2 + 6 P3 |
| **Misunderstandings surfaced** | 30+ across 4 phase stubs + 3 celtic-asset-generation versions + 33 P-specs + 12 S-specs | `28-misunderstandings-corrector.md` |
| **Critical runtime-breakers** | 12 | `28-misunderstandings-corrector.md:218-233` |
| **Skill files needing updates** | 21 of 51 (41%) | `30-documentation-gaps.md` (8 FAIL + 13 PARTIAL) |
| **Wall clock (program)** | ~24 hr across 44 agents | per-file headers |
| **BrowserBase credits used** | ~850 of 2,000 budgeted | sum across `agent-*.md` headers |
| **Stack inventory corrected** | 33 → 90 Docker Compose stacks | `project.md:12` was wrong |

---

## 3. Top 10 refactors by impact (quick-reference)

| # | ID | Item (file:line) | Impact | Effort | Risk | Hard date |
|:-:|:--|:--|:--|:-:|:-:|:--|
| 1 | **P0-4** | LiteLLM `:main-stable` → `:1.84.0+` (bypasses v3 supply-chain incident + Langfuse v3 OTEL) — `stacks/litellm/compose.yaml` | **HIGH** | S | high | **2026-06-30** |
| 2 | **P0-1** | FalkorDB `--loadmodule /etc/falkordb/vector.so` — `stacks/falkordb/compose.yaml:18-37` | **HIGH** (silent prod break) | S | high | — |
| 3 | **P0-2** | Garage v1.0.1 → v2.3.0 + `replication_mode` removed + `/v1/→/v2/` admin API — 4 files | **HIGH** (will fail to start) | M | med | — |
| 4 | **P1-1** | BAML 14 inline `client "anthropic/claude-sonnet-4-20250514"` → `ExtractEnStrong` (defeats Phase 0.4 derisking) — `curriculum_extraction.baml:167-1085` | **HIGH** | M | med | — |
| 5 | **P0-5** | Cognee `SearchType.INSIGHTS` → `SUMMARIES` — `cognee_service.py:376` | **HIGH** (runtime crash) | S | high | — |
| 6 | **P0-3** | dlt pin `dlt>=1.0.0` → `"dlt[hub]>=1.27.0,<1.29.0"` (1.27 `workspace` split breaks `dlt dashboard`) — `pyproject.toml:39` | **HIGH** (silent CI break) | S | med | — |
| 7 | **P0-9** | MLX-omni broken Docker `mlx-omni serve` → `mlx-omni-server --port 10240` — `Dockerfile:39` | **HIGH** (container won't start) | S | high | — |
| 8 | **P0-8** | FalkorDB Cypher injection (f-string → bound params) — `falkordb.py:170-212` | **HIGH** (security) | S | high | — |
| 9 | **P1-2** | CocoIndex HNSW `declare_vector_index` on 5 v1 Apps (100× search speedup) — `codebase_indexing.py:600-605` + 4 more | **HIGH** | S | low | — |
| 10 | **P1-11** | Cognee dataset naming (dot vs underscore) — `cognee/compose.yaml:42` vs `cross_stage_cognify.py:131` | **HIGH** (silent first-cognify miss) | S | high | — |

**Spec docs:** [26-refactor-prioritizer.md](./synthesis/26-refactor-prioritizer.md) (full P0/P1/P2/P3 backlog) · [28-misunderstandings-corrector.md](./synthesis/28-misunderstandings-corrector.md) (12 runtime-breakers ranked). **Refactor plans:** [31-garage-v2](./refactors/31-garage-v2-migration.md) · [32-baml-inline-clients](./refactors/32-baml-inline-clients-fix.md) · [33-dlt-path](./refactors/33-dlt-path-consolidation.md) · [34-lancedb-index](./refactors/34-lancedb-index-repair.md) · [35-falkordb-vector](./refactors/35-falkordb-vector-fix.md) · [36-litellm-otlp](./refactors/36-litellm-otlp-migration.md) · [37-dagster-asset-check](./refactors/37-dagster-asset-check-rollout.md) · [38-cognee-v1](./refactors/38-cognee-v1-api-migration.md).

---

## 4. Top 10 features by value (quick-reference)

| # | ID | Feature (cluster) | Value | Effort | Dependency chain |
|:-:|:--|:--|:--|:-:|:--|
| 1 | **F-01** | Realtime CDC pipeline (RisingWave v3 + olake → Iceberg v3 exactly-once) | **Unblocks streaming for all dlt batch sources** | L | F-06 → LiteLLM-OTEL → Iceberg REST |
| 2 | **F-02** | Multilingual embeddings unified on `bge-m3` (kills 2-space coexistence) | **~10× cross-App semantic search correctness** (Irish+EN+GA+CY+GV) | M | P1-3 + P1-12 → 1× GPU warm pool |
| 3 | **F-05** | Edge BAML extraction (Cloudflare Workers + `baml-edge` WASM) | **30% LiteLLM load reduction, <100ms P50** | L | P1-9 (BAML 0.223) + new `stacks/baml-edge/` |
| 4 | **F-03** | Agent observability dashboard (Langfuse v3 OTEL) | **First per-agent cost/latency attribution** | M | P1-1 → P2-7 (BAML Collector) |
| 5 | **F-04** | Serverless GPU burst (Modal A100/H100 for Unsloth >13B) | **Unlocks Gemma 4 31B / Qwen3.6 35B fine-tunes** | M | P2-6 (FastModel) + HF `hf` CLI |
| 6 | **F-06** | Cognee v1.0 `remember/recall/forget/improve` migration | **Persistent + session-aware memory** | M | P0-5 → P1-11 → F-06 → F-07 |
| 7 | **F-07** | Cognee + Graphiti dual-memory agent runtime | **"What changed" + "What's documented" in 1 query** | L | F-06 + 16-param `add_episode` |
| 8 | **F-08** | BrowserBase research-codegen workflow (codifies this very program) | **Every new package gets a 7-section doc for free** | M | `agent-experience` skill + Cognee `research_findings` + RAGAS |
| 9 | **F-14** | Celtic Teacher Corpus (TCA-gated curriculumonline) | **Unlocks 30% of curriculumonline content** | S (with teacher; L without) | Locket + Stagehand + Infisical service account |
| 10 | **F-12** | MotherDuck Dives for customer-facing analytics (replaces marimo) | **First true "Cianfhoghlaim as a product" surface** | M | F-16 (Garage v2.3) + MotherDuck BYOB |

**Spec docs:** [27-feature-backlog.md](./synthesis/27-feature-backlog.md) (full P0/P1/P2/P3 backlog + 5 cluster recommendations). **Feature plans:** [39-realtime-cdc](./features/39-realtime-cdc-pipeline.md) · [40-multilingual-embeddings](./features/40-multilingual-embeddings.md) · [41-agent-observability](./features/41-agent-observability.md) · [42-serverless-gpu-burst](./features/42-serverless-gpu-burst.md) · [43-edge-baml-extraction](./features/43-edge-baml-extraction.md) · [44-browserbase-research-codegen](./features/44-browserbase-research-codegen.md).

**Cluster delivery order (recommended):** **A** (F-01+F-06+F-07) = realtime+memory · **B** (F-02+F-10+F-11+F-19) = multilingual+multimodal · **C** (F-03+F-15+F-25) = observability+auto-improve · **D** (F-04+F-05+F-26) = edge+GPU · **E** (F-13+F-14+F-21..F-24) = content+sites.

---

## 5. Next steps (5 numbered actions)

1. **🚨 This week — land the P0 release train (1-2 weeks, 6-8 days).** The 11 P0 items are not optional. Bundle the **LiteLLM→Langfuse-OTEL + dlt-[hub] + dagster-dlt-0.29.11 + cocoindex-1.0.14 + LanceDB-0.33 + FalkorDB-vector.so + Garage-v2.3.0 + Cognee-SearchType + BAML-0.223 + MLX-omni-Docker + Infisical-2026-09-16** changes into a single coordinated release. **Top 3 by urgency:** LiteLLM `:main-stable` cutover 2026-06-30 (≤2 days), FalkorDB `vector.so` (silently broken), Garage v2 (will fail to start). All 11 specs in [`26-refactor-prioritizer.md §3`](./synthesis/26-refactor-prioritizer.md). 8 of 8 refactor plans are ready in [`refactors/`](./refactors/).

2. **📋 Write the 4 phase stub change spec-deltas (parallel to P0 train).** All 4 phase stub changes (`2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions/`) are empty placeholders awaiting `## ADDED Requirements` content. The 30+ misunderstandings are already enumerated in [`28-misunderstandings-corrector.md`](./synthesis/28-misunderstandings-corrector.md) (12 runtime-breakers ranked §7; 16 stub-change corrections §2; 8 spec-version corrections §3; 30+ P-spec corrections §4; 7 cross-cutting doc fixes §5; 15 component fixes §6). Copy-paste into the stub changes; run `openspec validate <change-id> --strict`; commit; archive after deploy.

3. **🔬 Update the 21 outdated `.agents/skills/*/SKILL.md` files (~16 person-hours, 1 engineer, <3 days).** Top 3 most-outdated: [`unsloth/SKILL.md`](../../.agents/skills/unsloth/SKILL.md) (last touched 2025-04 — misses `FastModel` + Gemma 4 + Qwen3.6 + MTP + Dynamic 2.0 GGUFs), [`dlt/SKILL.md`](../../.agents/skills/dlt/SKILL.md) (3 minors stale — misses `[hub]` extra + 1.28.0 breaking changes + native Polars), [`baml/SKILL.md`](../../.agents/skills/baml/SKILL.md) (5 pre-v4 `sruth/...` paths + inline-client antipattern + 0.76.2 generator). Full audit in [`30-documentation-gaps.md`](./synthesis/30-documentation-gaps.md). 6 new skills needed: OCR vision-model registry, 5-stage PDF pipeline, OCR backend router, mcp-server-motherduck, Infisical MCP, v4-consolidation path-mapping.

4. **🚀 Ship Cluster A (F-01 + F-06 + F-07) + Cluster B-start (F-02) next quarter — pick from 7 P0 features.** 6 feature plans are ready in [`features/`](./features/). **Highest leverage first:** F-02 (bge-m3 unification, M effort, ~10× correctness win) is the cheapest unblocker. F-01 (realtime CDC, L effort) is the biggest strategic unblocker. F-05 (edge BAML, L effort) is the highest-tech-debt-pays-off. F-04 (Modal GPU burst) is required before any >13B model work. F-08 (research-codegen) is the self-improvement flywheel — codifies this very program for reuse.

5. **🧠 Cognify the program output + wire RAGAS drift detection.** Run `cognee.cognify()` on all 64 research files into the `research_findings` Cognee dataset (already templated at `synthesis/27-feature-backlog.md:88`). Then add a RAGAS `BAML Collector(name)` asset check to the 4 phase stub changes so future package drifts auto-surface in Langfuse. This makes the program a *repeatable* 1-day exercise for any new package (replaces ad-hoc docs hunts). Template: [`44-browserbase-research-codegen.md`](./features/44-browserbase-research-codegen.md) (`bun run scripts/research-codegen.ts <package>` → emits 7-section Markdown → cognifies → RAGAS-evaluates every 5th output).

---

**Cross-references:** [SHARED_DISCOVERY_LOG.md](./SHARED_DISCOVERY_LOG.md) (29 entries, 11 cross-deps, 4 conflicts) · [29-integration-mapper.md](./synthesis/29-integration-mapper.md) (3-tier system diagram + 25-package data-flow matrix + 16 anti-patterns + 36 migration paths) · [openspec/AGENTS.md](../../AGENTS.md) (34 capability specs, 5 priority commands, 5 priority skills).
