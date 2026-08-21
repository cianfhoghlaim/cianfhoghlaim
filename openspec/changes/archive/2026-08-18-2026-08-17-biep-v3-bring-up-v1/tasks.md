# Tasks: 2026-08-17-biep-v3-bring-up-v1

## Phase 1 — IaC + ops (12 tasks, ~2 days)

- [ ] **P1.1** Commit `bonneagar/stacks/litellm/config/config.yaml` (11 model-name fixes from the working tree)
- [ ] **P1.2** Commit `bonneagar/stacks/llama-swap/compose.yaml` (image tag `:cpu` + mount path fixes from the working tree)
- [ ] **P1.3** Commit `meaisinfhoghlaim/models/llama_swap_config.yaml` (upstream alias mapping from the working tree)
- [ ] **P1.4** Commit `bun.lock` + `package.json` (dependency drift from the working tree)
- [ ] **P1.5** Fix `bonneagar/komodo/resource-syncs/storage-infrastructure.toml:14` (`repo = "cliste/bonneagar"` → `"cianfhoghlaim/bonneagar"`)
- [ ] **P1.6** Refactor `bonneagar/iac/commands/bootstrap.ts:140-150` to replace 3 `logWarn("not yet automated")` blocks with real `deployKomodoCore() + deployKomodoPeriphery() + deployTinyauth()` calls
- [ ] **P1.7** Add 7 Traefik `Host(` routers to `bonneagar/pangolin/config/traefik/traefik_config.yml` for `litellm`, `langfuse`, `vikunja`, `n8n`, `glance`, `changedetection`, `paperless`
- [ ] **P1.8** Wire `scripts/check-edge-tls.sh --strict --all` into `iac:health` (closes the false-positive health-signal gap)
- [ ] **P1.9** 10 Pangolin `siteResources` CREATE calls via `iac:sync:clients` (per `PUT /org/{orgId}/site-resource`)
- [ ] **P1.10** 3 site-rebinding UPDATEs (rebind `infisical`, `openchamber`, `komodo` to the live `arm1-oci` site)
- [ ] **P1.11** Operator action: update `openchamber/compose.yaml:38` SHA256 to the real digest (live GHCR access required)
- [ ] **P1.12** Operator action: reconcile `ai-that-works` submodule pointer to canonical upstream commit

## Phase 2 — litellm + llama-swap + BAML stub cleanup (18 tasks, ~3 days)

- [ ] **P2.1** Run `km deploy stack litellm --force` (per Correction #12 — config is already correct in source)
- [ ] **P2.2** Create `scripts/download_gguf_weights.py` (~50 LOC) that downloads 17 GGUF files from HF Hub in the priority order from `meaisinfhoghlaim/models/llama_swap_config.yaml` (gemma-4-26B-A4B first, then qwen3-vl-8b, then qwen3.6-27b-mtp, then 14 specialist/legacy models — ~60-80 GB transfer, resumable)
- [ ] **P2.3** Run `python scripts/download_gguf_weights.py` (downloads 17 GGUF files into `stedding/huggingface/gguf/`)
- [ ] **P2.4** Verify `ls -lah stedding/huggingface/gguf/ | wc -l` returns 17 + header row (i.e., 18 lines)
- [ ] **P2.5** Create `scripts/verify_litellm_redeploy.sh` (~30 LOC) that asserts the redeployed container has the dict-form fallbacks (closes the crash-loop class)
- [ ] **P2.6** Run `bash scripts/verify_litellm_redeploy.sh` after the litellm redeploy
- [ ] **P2.7** Bring up llama-swap: `cd bonneagar/stacks/llama-swap && docker compose up -d`
- [ ] **P2.8** Verify `curl http://llama-swap:8080/v1/models` returns 17 model IDs
- [ ] **P2.9** Verify `docker logs litellm | grep -E "Router|fallback"` shows no `Router.validate_fallbacks` errors (per the 5-min LiteLLM diagnostic gate from Correction #4)
- [ ] **P2.10** Complete BAML stub cleanup for 6 LC subjects (extend the 6/22 already-done tasks) — real prompts for `ExtractChemSyllabus` (already done) + `ExtractMathSyllabus` + `ExtractGeoSyllabus` + `ExtractGaeilgeSyllabus` + `ExtractEnSyllabus` + `ExtractCompSciSyllabus`
- [ ] **P2.11** Complete BAML stub cleanup for 18 LC × 4 extraction kinds = 24 more real prompts (exam_paper, marking_scheme, diagram, cross_linguistic)
- [ ] **P2.12** Verify `baml-cli generate --from baml_src` regenerates the 14 BAML client files
- [ ] **P2.13** Create `tests/test_scanned_detector.py` (~30 LOC, 4 scenarios) per the deferred task from the `2026-08-10-ocr-vision-activation-v1` change
- [ ] **P2.14** Run `pytest tests/test_scanned_detector.py` exits 0
- [ ] **P2.15** Create `mise.toml` task `lint:litellm-router-fallbacks` (NEW, ~40 LOC script)
- [ ] **P2.16** Create `mise.toml` task `lint:baml-stub-prompts` (NEW, ~50 LOC script)
- [ ] **P2.17** Create `mise.toml` task `lint:copilotkit-actions-stubbed` (NEW, ~40 LOC script)
- [ ] **P2.18** Run `dagster asset materialize --select biiep_ocr_ensemble` against a real Ireland LC PDF; confirm `rows_landed > 0`

## Phase 3 — KG population + lakehouse banner validation (8 tasks, ~2 days)

- [ ] **P3.1** Verify Cognee comes up via the unified lakehouse (`bash scripts/lakehouse_unified_up.sh`)
- [ ] **P3.2** Create 5 per-stage cognify `defs.yaml` files at `orchestration/defs/3_model_lifecycle/cognify/{aistear,primary,junior_cycle,senior_cycle,university}/defs.yaml`
- [ ] **P3.3** Activate 8 BRIDGE cross-stage edges + 4 lateral equivalences (JC SC↔England KS4, SC↔Scotland Higher, etc.) in `orchestration/defs/sensors/kcg_cognify_cross_stage_sensor.py`
- [ ] **P3.4** Activate 38 cross-jurisdiction equivalences in `orchestration/defs/sensors/biiep_jurisdiction_bridge_sensor.py`
- [ ] **P3.5** Activate 7 ingest sensors (one per KG stage) — each polling the upstream registry for new cohorts and triggering cognify
- [ ] **P3.6** Real BAML prompts for `ExtractBilingualLearningOutcome` and `ExtractCrossLinguisticGA` in `baml_src/british_isles/ireland/education/lc_extraction/gaeilge_extraction.baml` via the `gaeilge_lc_client` (routed through `uccix-mistral-24b`)
- [ ] **P3.7** Process `leaving_certificate/` 13 subjects × (EN+GA) PDFs through the BIEP v3 5-phase pattern
- [ ] **P3.8** Verify `md:cianfhoghlaim.lc_extract` contains rows for all 13 leaving_certificate subjects × (EN+GA)

## Phase 4 — England + NCCA + 4 regression gates + CopilotKit pin (22 tasks, ~2 days)

- [ ] **P4.1** Create 3 DLT sources: `dlt_sources/british_isles/england/education/gcse/{aqa,ocr,edexcel}_source.py`
- [ ] **P4.2** Create 3 DLT sources: `dlt_sources/british_isles/england/education/a_level/{aqa,ocr,edexcel}_source.py`
- [ ] **P4.3** Create `dlt_sources/british_isles/england/education/__init__.py` (re-exports 6 sources)
- [ ] **P4.4** Create `orchestration/defs/2_materials/england_education/{gcse,a_level}_assets.py` (2 asset group files)
- [ ] **P4.5** Create `orchestration/defs/2_materials/england_education/misconfig_check.py` (cross-board coverage check)
- [ ] **P4.6** Create `scripts/seed_england_pdfs.py` (seed script for 92 subjects × 3 boards)
- [ ] **P4.7** Real BAML prompt for `ExtractAQAQualSpec` in `baml_src/british_isles/england/education/curriculum_syllabus.baml` (the one stub)
- [ ] **P4.8** Update `orchestration/definitions.py` to load the 6 new asset groups
- [ ] **P4.9** Migrate 8 NCCA subject specialists (`gael_agent`, `math_agent`, `appm_agent`, `chem_agent`, `comp_agent`, `engl_agent`, `geog_agent`, `hist_agent`) from `agents/tuatha/wiring.py` back-compat to new `CelticAgentOpsComponent` wiring layer
- [ ] **P4.10** Add `minimax-coding-plan/MiniMax-M3` to `MODEL_REGISTRY` (text_llm/default)
- [ ] **P4.11** Add 4 Qwen Cloud models (`qwen3-coder-next`, `qwen3-coder-plus`, `qwen3-max-2026-01-23`, `glm-5.1`) to `MODEL_REGISTRY`
- [ ] **P4.12** Add `kimi-k2.6`, `mimo-v2.5`, `deepseek-v4-flash` to `MODEL_REGISTRY`
- [ ] **P4.13** Add `MINIMAX_API_KEY` + `QWEN_DASHSCOPE_API_KEY` to `.infisical.env`
- [ ] **P4.14** Update `web/apps/cianfhoghlaim-leaving-cert/package.json` — pin `@copilotkit/runtime >= 1.67.1` + `@copilotkit/react-core >= 1.67.1` + `@copilotkit/react-ui >= 1.67.1`
- [ ] **P4.15** Upgrade `ag-ui-strands` alongside the CopilotKit pin (per `CopilotKit issue #2946` fixed in v1.63.x)
- [ ] **P4.16** Create `web/COPILOTKIT_PIN.md` — NEW canonical doc explaining the pin + decision + 1.67.1 migration notes
- [ ] **P4.17** Add BAML `ExtractorPrimary` + `ExtractorFallback` ClientRegistry patterns in `baml_src/clients.baml` for the OCR ensemble (per the `baml-schemas` spec)
- [ ] **P4.18** Update 14 `@coco.fn(memo=True)` sites in `cocoindex_flows/european_nations_cross/*_embedding.py` + `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` to use `deps=` for module-level prompt strings (per the `ciianfhoghlaim-cocoindex-v1-migration` spec)
- [ ] **P4.19** Run `bun run cocoindex update --pip` to refresh CocoIndex venv to >=1.0.20; verify all 196 CocoIndex files AST-parse
- [ ] **P4.20** Add 4 new regression gates to `mise.toml` (`lint:litellm-router-fallbacks`, `lint:baml-stub-prompts`, `lint:copilotkit-actions-stubbed`, plus the existing `lint:dagster:sensor-job-coverage`)
- [ ] **P4.21** Run `pytest tests/test_routing_model_registry.py` + the 4 new regression gates — all pass
- [ ] **P4.22** Run `mise run sync:dagster` — Layer 6 drift check exits 0

## Phase 5 — Validation + archive (5 tasks, ~30 min)

- [ ] **P5.1** `openspec validate 2026-08-17-biep-v3-bring-up-v1 --strict` exits 0
- [ ] **P5.2** Run the full suite: `mise run lint:dagster:sensor-job-coverage && mise run lint:dlt:nested-hints && mise run lint:locket-version && mise run lint:litellm-router-fallbacks && mise run lint:baml-stub-prompts && mise run lint:copilotkit-actions-stubbed && mise run lint:registry && pytest tests/`
- [ ] **P5.3** Verify `curl http://llama-swap:8080/v1/models` returns 17 model IDs
- [ ] **P5.4** Verify `dagster asset materialize --select biiep_ocr_ensemble` returns `rows_landed > 0`
- [ ] **P5.5** `openspec archive 2026-08-17-biep-v3-bring-up-v1 --yes`

## Total: 65 tasks, ~7-8 days