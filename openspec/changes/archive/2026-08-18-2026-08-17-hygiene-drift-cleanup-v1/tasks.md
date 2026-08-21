# Tasks: 2026-08-17-hygiene-drift-cleanup-v1

## Phase 1 — Verify already-shipped changes (9 tasks, ~1 day)

- [ ] **P1.1** Add 1-line deprecation banner to `bonneagar/stacks/cognee/compose.yaml` pointing at `bonneagar/stacks/lakehouse/`
- [ ] **P1.2** Add 1-line deprecation banner to `bonneagar/stacks/graphiti/compose.yaml`
- [ ] **P1.3** Add 1-line deprecation banner to `bonneagar/stacks/falkordb/compose.yaml`
- [ ] **P1.4** Add 1-line deprecation banner to `bonneagar/stacks/memgraph/compose.yaml`
- [ ] **P1.5** Add 1-line deprecation banner to `bonneagar/stacks/lancedb/compose.yaml`
- [ ] **P1.6** Verify `orchestration/sensors/jobs.py:1-23` exports 8 `define_asset_job` instances; create `scripts/dagster_sensor_job_coverage_lint.py` (~30 LOC)
- [ ] **P1.7** Add `[tasks."lint:dagster:sensor-job-coverage"]` in `mise.toml` pointing at the new lint script
- [ ] **P1.8** Wire BAML `Collector` API at `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:_run_path_baml()` so MLflow observability fires (per A6 verification)
- [ ] **P1.9** Run `dagster asset materialize --select biiep_ocr_ensemble` against a real Ireland LC PDF; confirm `rows_landed > 0`

## Phase 2 — Library upgrade + pattern adoption (10 tasks, ~1 day)

- [ ] **P2.1** Bump CocoIndex pin from `>=1.0.14,<1.0.8,!=1.0.8` to `>=1.0.20,<2.0.0` in `pyproject.toml`
- [ ] **P2.2** Run `bun run cocoindex update --pip` to refresh venv; verify all 196 CocoIndex files AST-parse
- [ ] **P2.3** Add `deps=` parameter to 14 `@coco.fn(memo=True)` sites in `cocoindex_flows/european_nations_cross/{law,education,medicine}_embedding.py` + `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` + `cocoindex_flows/biep_parity/*_factory.py`
- [ ] **P2.4** Add BAML `ClientRegistry` pattern section to `.agents/skills/baml/SKILL.md` §3 with code samples for OCR ensemble primary/fallback chain
- [ ] **P2.5** Add BAML `Collector` API section to `.agents/skills/baml/SKILL.md` §4 with `usage`, `raw_llm_response`, `calls[-1].http_response` examples
- [ ] **P2.6** Verify DLT pin is `>=1.28.1` in `pyproject.toml`; add `[tasks."lint:dlt:nested-hints"]` in `mise.toml` (script: `scripts/lint_dlt_nested_hints.py`, ~40 LOC, fails on `__` in nested_hints path fragments)
- [ ] **P2.7** Create `docs/PANGOLIN_OIDC_CONFIG.md` documenting `Auto Provision Users` + PKCE S256 + `certResolver: letsencrypt` (HTTP-01) + the 4 PocketID endpoint URLs
- [ ] **P2.8** Verify all `compose.yaml` files referencing `bpbradley/locket:infisical` use `>=v0.18.0` or substitute the shim image
- [ ] **P2.9** Create `scripts/lint_locket_version.py` (~30 LOC) that scans `bonneagar/stacks/**/compose.yaml` for `locket:infisical` references and verifies the version pin
- [ ] **P2.10** Add `[tasks."lint:locket-version"]` in `mise.toml` pointing at the new lint script

## Phase 3 — Migrate 15 hardcoded model strings in `meaisinfhoghlaim/models/routing.py` (3 tasks, ~0.5 days)

- [ ] **P3.1** Migrate 6 hardcoded `uccix-mistral-24b` references + 8 hardcoded `gemma-4-26B-A4B` references + 1 hardcoded `molmo2-8b` reference + the final fallback at line 97 to `model_for("text_llm", "irish"|"default"|..., language="ga"|"en"|...)` lookups
- [ ] **P3.2** Update `openspec/specs/drift-remediation/spec.md` to reflect that `meaisinfhoghlaim/process/llm_router.py` was already migrated by the 2026-07-30 change, and that the remaining gap is `models/routing.py`
- [ ] **P3.3** Create `tests/test_routing_model_registry.py` (~30 LOC) verifying all 15 migrated strings resolve via `model_for(...)`

## Phase 4 — Drift cleanup + AGENTS.md rebaseline + Locket version gate (7 tasks, ~0.5 days)

- [ ] **P4.1** Fix 7 stale count claims across `AGENTS.md` (spec count 89→94), `agents/tuatha/AGENTS.md`, `bonneagar/AGENTS.md` (stack count 89→98), `notebooks/AGENTS.md` (notebook count 52→54)
- [ ] **P4.2** Fix 6 outdated `INDEXING_AND_COGNITION.md` numbers (chunks: 257,957; docs: 1,743; MCPs: 15; agents: 15; skills: 162; health-check snippets)
- [ ] **P4.3** Regenerate the 5 missing per-spec AGENTS.md files by running `mise run sync:all` (closes the `repo-hygiene-agent-routing` spec gap)
- [ ] **P4.4** Repair `guides.yml` per `2026-08-13-guides-yml-repair-and-docs-integrations-index-v1` (closes the `INDEXING_AND_COGNITION` `INTEGRATIONS_INDEX` rebuild)
- [ ] **P4.5** Force-push the 33 feat/* branches (#139) — operator action: `git push --force-with-lease origin $(git branch --format='%(refname:short)' | grep '^feat/' | tr '\n' ' ')`
- [ ] **P4.6** Run `mise run lint:drift-docs` — final validation gate (all AGENTS.md number claims match ground truth)
- [ ] **P4.7** Run `mise run lint:skills` — validates all 157 skills have frontmatter

## Phase 5 — Skill consolidation (4 tasks, ~0.5 days)

- [ ] **P5.1** Run `validate_skill_references.py` (the per-spec AGENTS.md cross-reference check)
- [ ] **P5.2** Cognify the 7 most-updated skills into Cognee (per `2026-08-13-skill-consolidation-and-extension-v1`): `baml`, `cocoindex`, `dlt`, `dagster`, `infrastructure-stacks`, `centralized-registry`, `knowledge-sync-loop`
- [ ] **P5.3** Update `.agents/skills/cocoindex/SKILL.md` to reflect `>=1.0.20` + `deps=` pattern + LiveMap + batched writes
- [ ] **P5.4** Re-run `mise run sync:all` to push the per-spec AGENTS.md regeneration

## Phase 6 — Pre-deploy + headroom + branch hygiene (2 tasks, ~0.5 days)

- [ ] **P6.1** Run `scripts/fetch-image-digest.sh` against `ghcr.io/openclaw/openclaw:2026.2.6` and `ghcr.io/openchamber/openchamber:1.0.0` from a host with live GHCR access; update both compose.yaml files to the real SHA256 (#81)
- [ ] **P6.2** Run `scripts/arm1-oci-headroom-check.sh` and decide whether to proceed with `openclaw + openchamber` deploy (#82)

## Phase 7 — Validation + archive (3 tasks, ~30 min)

- [ ] **P7.1** `openspec validate 2026-08-17-hygiene-drift-cleanup-v1 --strict` exits 0
- [ ] **P7.2** Run the full suite: `mise run lint:drift-docs && mise run lint:skills && mise run lint:dagster:sensor-job-coverage && mise run lint:dlt:nested-hints && mise run lint:locket-version && mise run lint:registry`
- [ ] **P7.3** `openspec archive 2026-08-17-hygiene-drift-cleanup-v1 --yes`

## Total: 38 tasks, ~4 days