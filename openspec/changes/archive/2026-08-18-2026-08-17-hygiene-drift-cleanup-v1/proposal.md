# 2026-08-17-hygiene-drift-cleanup-v1

## Why

After the BIEP v3 + VLM/OCR + Lakehouse + Centralized Registry push (35 commits, 10 openspec changes shipped: `ba76f5ff3` through `33b2de574`), three classes of loose ends remain that block the "bring-up" wave:

**1. Verifications of "already-shipped" mega-change deliverables.**
- A1 (lakehouse-unified-data-plane): code shipped at `33b2de574`, but the 5 deprecation banners on the deprecated `cognee/`, `graphiti/`, `falkordb/`, `memgraph/`, `lancedb/` stacks are missing.
- A2 (jurisdiction-sensor-jobs): `orchestration/sensors/jobs.py` exists and exports the 8 `define_asset_job` instances, but the `mise run lint:dagster:sensor-job-coverage` regression gate from the spec is not implemented.
- A6 (OCR vision activation completion): the new `orchestration/components/biiep_ocr_ensemble_component.py` exists in the working tree, but the spec's requirement to wire the BAML `Collector` API (to close the "0 rows_landed" loop) is not yet on the critical path.

**2. Real drift gaps uncovered by deep ccc + firecrawl validation of the 4 data-platform libraries (BAML, CocoIndex, DLT, Pangolin).**
- CocoIndex `>=1.0.14,<1.0.8,!=1.0.8` — we are **6 minor versions behind** (v1.0.20 is current per `https://github.com/cocoindex-io/cocoindex/releases` verified 2026-08-11). The 6 versions in between add BigQuery/Snowflake/Valkey targets, LiveMap, rate limiting, batched target writes, the **`deps=` parameter** for `@coco.fn` (which we don't use — our memoized functions don't invalidate on prompt changes), and zvec FTS fields.
- BAML `ClientRegistry` and `Collector` patterns are absent across all `baml_src/**/*.baml` files. Every function uses bare `client<llm>` blocks; no fallback chains exist at the BAML layer.
- Pangolin OIDC: the canonical pattern (`Auto Provision Users` + `require_pkce: true` + `pkce_challenge_method: S256` per `https://docs.pangolin.net/manage/identity-providers/pocket-id`) is not documented in-repo.
- DLT 1.28 nested_hints `__` regression (dlt-hub/dlt#4247) does NOT affect us (verified via grep: no `__` path fragments in `dlt_sources/**/*.py` nested_hints), but the regression gate should exist.

**3. Real-world loose ends from the openspec-validate + lint-drift-docs gates.**
- 7 stale count claims across 4 AGENTS.md files (per the `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1` change proposal).
- 6 outdated numbers in `INDEXING_AND_COGNITION.md`.
- 5 missing per-spec AGENTS.md files (from the `repo-hygiene-agent-routing` spec).
- `guides.yml` lint failures.
- Branch hygiene: 33 feat/* branches pending force-push cleanup (#139).
- 6 open issues (#81, #82, #107, #139, #141, #146) addressed by spec changes that haven't shipped.

This change ships **35 tasks** to close all three classes in a single 4-day wave, so that Mega-1 (the BIEP v3 bring-up mega-change) can proceed against a clean baseline.

## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-08-15-knowledge-sync-loop-v1` (the Layer 6 sync:dagster will catch any new asset drift)
`Blocked by (soft): 2026-08-15-retrospective-pre-v7-cleanup-v1` (Layer 6 sync:dagster is the canonical place for safe `--fix` mode)
`Affected repos: cianfhoghlaim`

## What Changes

### Phase 1 — Verify the 3 already-shipped changes (~1 day, 9 tasks)

- Add 5 deprecation banners to `bonneagar/stacks/{cognee,graphiti,falkordb,memgraph,lancedb}/compose.yaml` pointing at the unified `bonneagar/stacks/lakehouse/`.
- Verify `orchestration/sensors/jobs.py` exports the 8 `define_asset_job` instances; add `scripts/dagster_sensor_job_coverage_lint.py` (~30 LOC) + `mise.toml` task.
- Verify `orchestration/components/biiep_ocr_ensemble_component.py` is correctly wired; add BAML `Collector` API integration at `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:_run_path_baml()` (the `_ragas_vote` MLflow observability hook fires only when `evaluate_ensemble()` is called — wiring the Collector closes the false-success loop).
- Run `dagster asset materialize --select biiep_ocr_ensemble` end-to-end against a real Ireland LC PDF and confirm `rows_landed > 0`.

### Phase 2 — Library upgrade + pattern adoption (~1 day, 10 tasks)

- **Bump CocoIndex pin** from `>=1.0.14,<1.0.8,!=1.0.8` to **`>=1.0.20,<2.0.0`** in `pyproject.toml` (resolves the highest-leverage drift — 6 versions behind).
- **Run `bun run cocoindex update --pip`** to refresh the venv; verify all196 CocoIndex files still AST-parse cleanly.
- **Add `deps=` parameter** to the 14 `@coco.fn(memo=True)` sites in `cocoindex_flows/european_nations_cross/{law,education,medicine}_embedding.py`, `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py`, and the biep_parity factories — declare module-level prompt strings + model names as memoization dependencies (per `cocoindex-io/cocoindex#1836`).
- **Add BAML `ClientRegistry` patterns** to `.agents/skills/baml/SKILL.md` §3 with code samples for the OCR ensemble's primary/fallback chain (per `docs.boundaryml.com/guide/baml-advanced/llm-client-registry`).
- **Add BAML `Collector` API** to `.agents/skills/baml/SKILL.md` §4 (per `docs.boundaryml.com/guide/baml-advanced/collector-track-tokens`) — covers `collector.last.usage.input_tokens`, `collector.last.raw_llm_response`, `collector.last.calls[-1].http_response`.
- **Verify DLT pin** is `>=1.28.1` and add `mise.toml` task `lint:dlt:nested-hints` that fails on path fragments containing `__` (per dlt-hub/dlt#4247).
- **Add Pangolin OIDC config doc** at `docs/PANGOLIN_OIDC_CONFIG.md` documenting `Auto Provision Users` + PKCE S256 + `certResolver: letsencrypt` (HTTP-01) + the 4 PocketID endpoint URLs.

### Phase 3 — Migrate 15 hardcoded model strings in `meaisinfhoghlaim/models/routing.py` to `model_for()` (~0.5 days, 3 tasks)

- Migrate 6 hardcoded `uccix-mistral-24b` references + 8 hardcoded `gemma-4-26B-A4B` references + 1 hardcoded `molmo2-8b` reference + the final fallback at line 97 to `model_for("text_llm", "irish"|"default"|..., language="ga"|"en"|...)` lookups (per the `centralized-model-registry` spec).
- Update `openspec/specs/drift-remediation/spec.md` to reflect that `meaisinfhoghlaim/process/llm_router.py` was already migrated by the 2026-07-30 change, and that the remaining gap is `models/routing.py`.
- Add `tests/test_routing_model_registry.py` (~30 LOC) verifying all 15 migrated strings resolve via `model_for(...)`.

### Phase 4 — Drift cleanup + AGENTS.md rebaseline + Locket version gate (~0.5 days, 7 tasks)

- **Fix 7 stale count claims** across `AGENTS.md`, `agents/tuatha/AGENTS.md`, `bonneagar/AGENTS.md`, `notebooks/AGENTS.md` (stack count 89→98, spec count 89→94, notebook count 52→54).
- **Fix 6 outdated INDEXING_AND_COGNITION.md numbers** (chunks, docs, MCPs, agents, skills, health-check snippets).
- **Regenerate the 5 missing per-spec AGENTS.md files** by running `mise run sync:all`.
- **Repair `guides.yml`** per `2026-08-13-guides-yml-repair-and-docs-integrations-index-v1`.
- **Add `mise.toml` task `lint:locket-version`** that fails if any `compose.yaml` references `bpbradley/locket:infisical` < v0.18.0 (the camelCase Infisical v0.161+ fix is gated on upstream; the shim at `bonneagar/locket-shim/cianfhoghlaim-locket-shim.py` is the workaround).
- **Force-push the 33 feat/* branches** (#139) — operator action.
- **Run `mise run lint:drift-docs`** — final validation gate.

### Phase 5 — Skill consolidation (skill-refs check + skill-lint) (~0.5 days, 4 tasks)

- Run `mise run lint:skills` (validates all 157 skills have frontmatter).
- Run `validate_skill_references.py` (the per-spec AGENTS.md cross-reference check).
- Cognify the 7 most-updated skills into Cognee (per `2026-08-13-skill-consolidation-and-extension-v1`).
- Re-run `mise run sync:all` to push the per-spec AGENTS.md regeneration.

### Phase 6 — Pre-deploy + headroom + branch hygiene (~0.5 days, 2 tasks)

- Run `scripts/fetch-image-digest.sh` against `ghcr.io/openclaw/openclaw` and `ghcr.io/openchamber/openchamber` from a host with live GHCR access; update both compose.yaml files to the real SHA256 (#81).
- Run `scripts/arm1-oci-headroom-check.sh` and decide whether to proceed with `openclaw + openchamber` deploy (#82).

## Impact

- Code: ~10 files modified, ~5 files created
- New tasks in `mise.toml`: `lint:dagster:sensor-job-coverage`, `lint:dlt:nested-hints`, `lint:locket-version`, `lint:registry:ocr-stub`
- Spec deltas: 6 specs affected (1 MODIFIED + 5 ADDED across 6 capabilities)

## Success criteria

1. `openspec validate 2026-08-17-hygiene-drift-cleanup-v1 --strict` exits 0
2. `mise run lint:dagster:sensor-job-coverage` exits 0 (all 8 sensor job_names have matching jobs)
3. `mise run lint:dlt:nested-hints` exits 0 (no `__` path fragments)
4. `mise run lint:locket-version` exits 0 (all Locket refs >= v0.18.0 OR shim-substituted)
5. `dagster asset materialize --select biiep_ocr_ensemble` returns `rows_landed > 0`
6. `tests/test_routing_model_registry.py` passes
7. `mise run lint:drift-docs` exits 0 (all AGENTS.md number claims match ground truth)
8. `mise run lint:skills` exits 0
9. `openspec archive 2026-08-17-hygiene-drift-cleanup-v1 --yes` succeeds