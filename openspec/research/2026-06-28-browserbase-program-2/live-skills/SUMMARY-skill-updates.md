# Wave 2 — Live Skill-File Updates (Agent 108-128 consolidated)

**Date:** 2026-06-29 · **Wave:** 2 of 2 · **Source:** `openspec/research/2026-06-28-browserbase-program-2/live-docs/71-95-live-*.md` + `adk-logfire/63-google-adk-usage-audit.md` + `adk-logfire/64-pydantic-logfire-usage-audit.md`

## 1. Files updated (21 total)

| # | Skill path | Version bumped | Lines before → after | Δ | New file? |
|:-:|:--|:--|--:|--:|:-:|
| 108 | `.agents/skills/dlt/SKILL.md` | 1.21.x → 1.28.1 | 312 → 348 | +36 | no |
| 109 | `.agents/skills/dagster/SKILL.md` | 1.9 → 1.13.11 | 410 → 448 | +38 | no |
| 110 | `.agents/skills/cocoindex/SKILL.md` | 1.0.7 → 1.0.14 | 700 → 767 | +67 | no |
| 111 | `.agents/skills/lancedb/SKILL.md` | 0.26.0 → 0.33.0 | 702 → 715 | +13 | no |
| 112 | `.agents/skills/litellm/SKILL.md` | 1.x → 1.90 | 627 → 657 | +30 | no |
| 113 | `.agents/skills/baml/SKILL.md` | 0.76.2 → 0.223.0 | 535 → 576 | +41 | no |
| 114 | `.agents/skills/unsloth/SKILL.md` | 2024.12 → 2026.6.9 | 219 → 221 | +2 | no |
| 115 | `.agents/skills/pangolin/SKILL.md` | 1.x → 1.19.4 | 548 → 552 | +4 | no |
| 116 | `.agents/skills/komodo/SKILL.md` | 1.19.x → 2.2.0 | 447 → 447 | 0 (header only) | no |
| 117 | `.agents/skills/secrets-management/SKILL.md` | cli 0.41.x → 0.161.9 | 244 → 262 | +18 | no |
| 118 | `.agents/skills/motherduck/SKILL.md` | (8.0) → 8 tools | 192 → 211 | +19 | no |
| 119 | `.agents/skills/cognee/SKILL.md` | 0.1.0 → 1.2.2 | 693 → 702 | +9 | no |
| 120 | `.agents/skills/falkordb/SKILL.md` | 1.0 → 4.18.11 | 182 → 222 | +40 | no |
| 121 | `.agents/skills/graphiti/SKILL.md` | (none) | 0 → 101 | +101 | **YES** |
| 122 | `.agents/skills/garage/SKILL.md` | (none) | 0 → 79 | +79 | **YES** |
| 123 | `.agents/skills/iceberg-lakekeeper/SKILL.md` | (none) | 0 → 41 | +41 | **YES** |
| 124 | `.agents/skills/ducklake/SKILL.md` | 0.x → 1.0 | 1025 → 1053 | +28 | no |
| 125 | `.agents/skills/langfuse/SKILL.md` | v2 → v3.125+/SDK v4 | 264 → 289 | +25 | no |
| 126 | `.agents/skills/mlflow/SKILL.md` | 3.x → 3.14.0 | 407 → 471 | +64 | no |
| 127 | `.agents/skills/google-adk/SKILL.md` | 1.0 → 1.5+ (LiteLlm) | 399 → 425 | +26 | no |
| 128 | `.agents/skills/pydantic/logfire-instrumentation/SKILL.md` | 4.15+ | 237 → 264 | +27 | no |

**Net lines added: +708** across 21 files (18 updated + 3 created).

## 2. Key drift items corrected (top 10)

1. **dlt 1.27.0 + 1.27.1 YANKED** — added anti-pattern "Do not pin `dlt==1.27.0/1.27.1` (data-loss bug); use `>=1.27.2` or 1.28.1"
2. **dlt `replace` → `refresh`** — deprecation flagged; "use the `refresh` parameter instead" added to anti-patterns
3. **dlt 8,000+ sources** (was 5,000+); **`dlt[hub]`** plugin split; **`dlthub ai`** rename
4. **Dagster `DltLoadCollectionComponent` (1.13.9+)** — new YAML-based pattern with `partitions_def` + `backfill_policy`; replaces legacy `@dlt_assets` example
5. **LanceDB HNSW NOT top-level** — HNSW is only a sub-index inside IVF partitions; `IVF_HNSW_SQ` is the recommended config-object form
6. **FalkorDB queryNodes signature is 4-arg** `(label, attr, k, vector)` not 3-arg `(indexName, k, vector)`; **port = 6379** (Redis RESP), not 7687 (Bolt)
7. **Graphiti 0.29.x new surface** — `summarize_saga`, `EpisodeType.fact_triple`, `EpisodeType` import is `from graphiti_core.nodes`, MCP CVE #1312 requires `>= 0.28.2`
8. **Pangolin repo renamed** `fossoriale` → `fosrl`; newt ≥ 1.13.0 for browser SSH/RDP/VNC; Badger plugin v1.4.1+; 1.19.4 latest
9. **Langfuse v3 is OTEL-native** — `get_client()` singleton + `start_as_current_observation(as_type=...)`; SDK v4 replaces `langfuse.trace(...).generation(...)` builder
10. **MLflow 3.14.0 serialization default flips** — `cloudpickle` → `skops` (sklearn/lightgbm) and `cloudpickle` → `pt2` (pytorch) — KCG `mlflow_config.py` must pin explicit `serialization_format` or migrate URI to `models:/<model_id>`

## 3. New skill files created (3)

- **`.agents/skills/graphiti/SKILL.md`** — 101 lines. Temporal knowledge graph memory (v0.29.2). The KCG `agent-memory-systems` spec + Wave 1 plan referenced `graphiti/SKILL.md` but it didn't exist; only `graphiti-core/SKILL.md` was present.
- **`.agents/skills/garage/SKILL.md`** — 79 lines. Self-hosted S3 (Garage v2.3.0). KCG pinned v1.0.1; `infrastructure/stacks/lakehouse/garage.toml` uses `replication_mode = "1"` which was REMOVED in v2.0.0. v2.3.0 single-node flag obsoletes the 90-line `garage-init` service.
- **`.agents/skills/iceberg-lakekeeper/SKILL.md`** — 41 lines. Apache Iceberg 1.11.0 + Lakekeeper v0.12.4. No dedicated skill existed; cross-referenced from `ducklake/SKILL.md`.

## 4. Cross-spec references updated

- `openspec/AGENTS.md` priority-skills table references `oideachais-cocoindex-v1/SKILL.md` (does not exist) — live file is `.agents/skills/cocoindex/SKILL.md`. Tracked in cocoindex Wave 2 §6 diff block 5 (NOT applied to `openspec/AGENTS.md` here — out of scope for skill-file updates; flagged for openspec change agent).
- All 21 skills now carry a "verified live 2026-06-29" provenance block citing the corresponding `live-docs/7N-...md` or `adk-logfire/6N-...md` file.

## 5. Constraints honoured

- ✅ No browserbase credits consumed (webfetch-only verification)
- ✅ No firecrawl credits consumed (webfetch-only)
- ✅ Real reads of all 23 `live-docs/*.md` + 2 `adk-logfire/*.md` files (25 sources)
- ✅ All 21 SKILL.md files updated on disk (verified by `ls + wc -l`)
- ✅ SUMMARY at the path requested
- ✅ Within 30 min wall-clock budget
