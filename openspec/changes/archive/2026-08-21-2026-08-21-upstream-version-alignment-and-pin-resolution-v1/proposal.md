# 2026-08-21-upstream-version-alignment-and-pin-resolution-v1

## Summary

Align every pinned stack dependency in `bonneagar/iac/`, `meaisinfhoghlaim/`, `dlt_sources/`, `orchestration/`, and `notebooks/` with its current upstream release. The previous pins are 1–7 minor versions behind across the 16 components inventoried in `stedding/audit/2026-08-21-upstream-audit.md`. **Langfuse v3 → v4 is mandatory** before 2026-11-16 (the v3-Cloud deprecation date).

This change is the planning hub for ALL bumps. Sub-changes (one per bump) implement the actual upgrades in topological order: pin resolution → P0 (Langfuse v4) → P1 (DLT 1.30, BAML 0.224, DuckDB 1.5.4, mlflow 3.15.1) → P2 (CocoIndex 1.0.20, LanceDB 0.37.1, LiteLLM 1.97, Dagster 1.13.18, PaddleOCR 3.0.1, dots.mocr, OlmOCR-2). See Tasks §3 for the dependency graph.

## Why

- **Langfuse v3 Cloud deprecates 2026-11-16.** The repo is on v3 + Python SDK v3. Bumping to v4 is mandatory.
- **DLT 1.25+** changed `pipeline.dataset()` to include all schemas by default. The 10 jurisdiction pipelines need an audit + explicit `schema=` kwargs.
- **BAML 0.224** renamed the runtime package from `baml_core` to `baml_bridge` (2026-07-08) and removed `@@dynamic` + legacy `type_builder` syntax (BEP-066, 2026-08-06). The 7 `clients.baml*` files need an audit.
- **DuckDB 2.0 ships September 2026.** Bumping to 1.5.4 (the highest MotherDuck-supported line) buys time.
- **mlflow 3.13+** changed the `judge.align()` default optimizer (GEPA → MemAlign) and removed MLServer. The 5 BAML+Mlflow call sites need an audit.

Additionally, two **pin ambiguities** discovered during the audit need operator clarification:

- **Infisical** is at `v0.161.12` (the SERVER) but the upstream CLI is at `v0.43.x`. The audit's "v0.161.9 CLI" was incorrect.
- **Lakekeeper** is at `v0.13.1` (our image tag) but upstream docs list `0.6.x`. This is a private-fork vs upstream-naming ambiguity.

## What changes

This umbrella change introduces **a single new openspec change**: `2026-08-21-upstream-version-alignment-and-pin-resolution-v1`. It captures the audit, resolves the two pin ambiguities, and opens a sequenced set of bump sub-changes under separate change-ids (one per component).

### New MODIFIED specs under `openspec/specs/`

| Spec | Change |
|:--|:--|
| `bonneagar-infrastructure-stacks` | ADD infisical-version policy (server-pinned to v0.161.x; CLI hygiene via mise), Lakekeeper-version policy (resolve `0.13.x-tagged v0.6.x-source` fork via the `bonnieagar/lakehouse` IaC alias) |
| `centralized-model-registry` | ADD 3 new OCR models: `dots.mocr` (successor to dots.ocr-1.5), `olmocr-2` (successor to olmocr), `paddleocr-vl-1.6` (successor to `paddleocr-vl-1.5` in the registry's text_llm family) |
| `litellm-router` | ADD the v1.97 MCP-OAuth-2.0-v2 + DCR + Rust-message-bus endpoints to the canonical Pangolin reverse-proxy path |
| `langfuse-observability` | ADD the v3 → v4 migration contract (Observations-first data model; removed SDK methods; env var rename `LANGFUSE_BASEURL` → `LANGFUSE_BASE_URL`) |

### New MODIFIED specs under `openspec/changes/<id>/specs/`

This delta file ships the per-spec modifications. The actual code changes land in **per-component sub-changes** (each a separate openspec change-id), not in this umbrella.

## Impact

| Area | Affects |
|:--|:--|
| Infra | 14 sidecar.yaml + 1 compose.yaml edits (image version bumps), 1 `.env` change (Postgres file-store env var), 2 stack-doctor config updates |
| Models | `meaisinfhoghlaim/models/registry.py` + `model_registry.py` add 3 entries (`dots.mocr`, `olmocr-2`, `paddleocr-vl-1.6`), retire 0 |
| BAML | 7 `clients.baml*` files rename `baml_core` → `baml_bridge` import paths; remove `@@dynamic` + `type_builder { ... }` blocks |
| DLT | 10 jurisdiction pipelines get explicit `schema=pipeline.default_schema_name` kwargs |
| mlflow | 5 callsites verified for new `judge.align()` optimizer semantics; add `MLFLOW_ALLOW_FILE_STORE=true` |
| Dagster | Bump to 1.13.18; adopt `DltLoadCollectionComponent` `partitions_def` for per-LC-subject partitions |
| Dagster asset count | 557 → 557 (no change in asset count); however the 5 KCG Components gain partition-aware scheduling |

## Test plan

For each individual bump sub-change (`-inflight-v1`), the test plan MUST include:

1. `uv sync` produces no resolution drift.
2. `openspec validate <subchange-id> --strict` exits 0.
3. For infra-side bumps: `mise run devops:validate-stacks --strict` exits 0.
4. For data-side bumps: `mise run lint:registry` exits 0 (the centralized-model-registry lint).
5. For Dagster bumps: `dagster dev -m orchestration.definitions` loads in <60s with the same asset count (557).
6. For DLT bumps: the Ireland LC jurisdiction pipeline runs end-to-end against the 80 PDFs at `/leaving_certificate/` (proved by Phase 4) — same 80 rows, same per-subject counts.
7. For mlflow / Langfuse bumps: the 5 BAML @observe-decorated functions emit successful trace events.

## Rollback

Each individual bump sub-change MUST be revertible via:

- `git revert <subchange-id-commit>` → restores the previous image tag + pyproject.toml pin.
- `docker compose -f bonneagar/stacks/<name>/compose.yaml down && docker compose up -d` → re-pulls the downgraded image.
- DLT pipeline re-run with `dlt pipeline lc5_biep_test drop` → drops the lancedb test destination; subsequent run with old pin restores old behaviour.

The umbrella change (this one) does NOT itself change any runtime behaviour — it's a planning + audit artifact. Deleting it does not affect the deployed system.
