# 2026-08-17-biep-v3-bring-up-v1

## Why

The BIEP v3 + VLM/OCR stack is code-complete after the 35-commit
push (`ba76f5ff3` through `33b2de574`) but 14 pending openspec
changes still need to ship. After the `2026-08-17-hygiene-drift-cleanup-v1`
change (Mega-6) archived, three classes of remaining work must land
to bring the BIEP v3 + VLM/OCR stack online:

**Phase 1 — IaC + ops** (12 tasks, ~2 days): commit 6 working-tree files
(litellm config, llama-swap compose, model_registry), reconcile the
storage-infrastructure resource-sync repo namespace, automate
bootstrap Phases 6/6b/7, add 7 Traefik routers + 10 Pangolin
siteResources + 3 site-rebinding UPDATEs (closes the
`edge-routing-and-offline-site-remediation-v1` change), and 2
operator actions (openchamber SHA256, ai-that-works submodule).

**Phase 2 — litellm + llama-swap + BAML stub cleanup** (18 tasks, ~3 days):
the litellm config IS already correct in source per the
`2026-07-29-lakehouse-extensive-hydration-v1` change (Correction #12
from the plan), so Phase 2 is purely `km deploy stack litellm --force` +
`scripts/download_gguf_weights.py` (50 LOC) for 17 GGUF files
(60-80 GB transfer) + llama-swap bring-up + BAML stub cleanup for
the 6 LC subjects (extends the 6/22 already-done) + the
`tests/test_scanned_detector.py` (30 LOC, 4 scenarios).

**Phase 3 — KG population + lakehouse banner validation** (8 tasks,
~2 days): verify Cognee comes up via the unified lakehouse
(`scripts/lakehouse_unified_up.sh`), register 5 per-stage cognify
`defs.yaml` files, activate 8 BRIDGE cross-stage edges + 38
cross-jurisdiction equivalences + 7 ingest sensors, real BAML
prompts for the 2 Gaeilge functions, and process the
`leaving_certificate/` 13 subjects × (EN+GA) PDFs.

**Phase 4 — England + NCCA + 4 regression gates + CopilotKit pin**
(22 tasks, ~2 days): 6 DLT sources for England (3 GCSE + 3 A-Level
boards × ~92 subjects), 6 Dagster asset groups, migrate 8 NCCA
subject specialists from back-compat to new wiring layer, 4 new
regression gates (sensor-job-coverage, litellm-router-fallbacks,
baml-stub-prompts, copilotkit-actions-stubbed), wire MiniMax + Qwen
Cloud token plans into MODEL_REGISTRY, pin CopilotKit >= 1.67.1 +
upgrade ag-ui-strands (per Correction #6), and BAML ClientRegistry +
CocoIndex `deps=` adoption.

This mega-change absorbs the 14 pending openspec changes that gate
BIEP v3 production: `lakehouse-unified-data-plane-v1`,
`bonneagar-infra-remediation-v3`, `edge-routing-and-offline-site-remediation-v1`,
`biiep-v3-jurisdiction-sensor-jobs-v1`, `biiep-v3-orchestration-activation-v1`,
`knowledge-graph-population-activation-v1`, `ocr-vision-activation-completion-v1`,
`token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`,
`baml-extraction-completion-v1`, `copilotkit-action-wiring-v1`,
`england-biiep-pipeline-v1`, `knowledge-graph-population-v1`,
`ocr-vision-activation-v1`, and the 8 NCCA specialists migration
(implicit in `agents/tuatha/wiring.py`).

## Dependencies

`Blocked by: none` (all blockers were resolved by the archived
`2026-08-17-hygiene-drift-cleanup-v1` change: A1+A2 verified, the
3 locket-shim migrations landed, the BAML Collector wiring landed,
the 15 hardcoded strings in `routing.py` migrated to `model_for()`,
the 5 lakehouse deprecation banners were already in place).
`Blocked by (soft): 2026-08-15-knowledge-sync-loop-v1` (Layer 6
sync:dagster will catch any new asset drift)
`Blocked by (soft): 2026-08-15-bonneagar-infra-remediation-v2` (the
Pangolin client-mgmt API + `iac:bootstrap-pangolin-client` /
`iac:sync:clients` commands)
`Affected repos: cianfhoghlaim`

## What Changes

### Phase 1 — IaC + ops (12 tasks, ~2 days)

- Commit 6 files from the working tree: `bonneagar/stacks/litellm/config/config.yaml`
  (11 model-name fixes), `bonneagar/stacks/llama-swap/compose.yaml`
  (image tag + mount path fixes), `meaisinfhoghlaim/models/llama_swap_config.yaml`,
  `bun.lock` + `package.json` (dependency drift).
- Fix `bonneagar/komodo/resource-syncs/storage-infrastructure.toml:14`
  (`repo = "cliste/bonneagar"` → `"cianfhoghlaim/bonneagar"` — closes
  the v7-flatten namespace gap).
- Refactor `bonneagar/iac/commands/bootstrap.ts:140-150` to replace
  the 3 `logWarn("not yet automated")` blocks with real
  `deployKomodoCore() + deployKomodoPeriphery() + deployTinyauth()` calls.
- Add 7 Traefik `Host(` routers to `bonneagar/pangolin/config/traefik/traefik_config.yml`
  for `litellm`, `langfuse`, `vikunja`, `n8n`, `glance`,
  `changedetection`, `paperless`.
- Wire `scripts/check-edge-tls.sh --strict --all` into `iac:health`
  (closes the false-positive health-signal gap).
- 10 Pangolin `siteResources` CREATE calls via `iac:sync:clients` (per
  the Integration API `PUT /org/{orgId}/site-resource`).
- 3 site-rebinding UPDATEs (rebind `infisical`, `openchamber`, `komodo`
  to the live `arm1-oci` site).
- 2 operator actions: update `openchamber/compose.yaml:38` SHA256 to
  the real digest (live GHCR access required), reconcile `ai-that-works`
  submodule pointer to canonical upstream commit.

### Phase 2 — litellm + llama-swap + BAML stub cleanup (18 tasks, ~3 days)

- `km deploy stack litellm --force` (per Correction #12 — the source
  config IS already in the dict form at line 645-647; the deployed
  container is the only thing stale).
- Create `scripts/download_gguf_weights.py` (~50 LOC) that downloads
  the 17 GGUF model files from HuggingFace Hub via the `hf` CLI in
  the priority order defined in `meaisinfhoghlaim/models/llama_swap_config.yaml`
  (gemma-4-26B-A4B first, then qwen3-vl-8b, then qwen3.6-27b-mtp, then
  the 14 specialist / legacy models — resumable, ~60-80 GB transfer).
- Create `scripts/verify_litellm_redeploy.sh` (~30 LOC) that asserts
  the redeployed container has `dict` form fallbacks (closes the
  crash-loop class per dlt-hub/dlt#4247 and the
  `2026-07-29-lakehouse-extensive-hydration-v1` change).
- Bring up `llama-swap`: `cd bonneagar/stacks/llama-swap && docker compose up -d`.
- Complete the BAML stub cleanup: extend the 6/22 already-done
  tasks to all 6 LC subjects × 4 extraction kinds = 24 real prompts.
- Create `tests/test_scanned_detector.py` (~30 LOC, 4 scenarios) per
  the deferred task from the `2026-08-10-ocr-vision-activation-v1` change.

### Phase 3 — KG population + lakehouse banner validation (8 tasks, ~2 days)

- Verify Cognee comes up via the unified lakehouse
  (`scripts/lakehouse_unified_up.sh`) and join the shared
  `lakehouse-postgres` at the `cognee_cianfhoghlaim` database.
- Register 5 per-stage cognify `defs.yaml` files
  (aistear / primary / junior_cycle / senior_cycle / university)
  at `orchestration/defs/3_model_lifecycle/cognify/<stage>/defs.yaml`.
- Activate the 8 BRIDGE cross-stage edges (Aistear↔Primary,
  Primary↔JC, JC↔SC, SC↔University) + 4 lateral equivalences
  (JC SC↔England KS4, SC↔Scotland Higher, etc.).
- Activate the 38 cross-jurisdiction equivalences (the equivalence
  edges connecting Irish 5-stage KG to England / Scotland / Wales /
  NI 5-stage KGs per the `british-isles-education-pipeline-v3` spec).
- Activate the 7 ingest sensors (one per KG stage), each polling
  the upstream registry for new cohorts and triggering cognify.
- Real BAML prompts for `ExtractBilingualLearningOutcome` and
  `ExtractCrossLinguisticGA` via the `gaeilge_lc_client` (routed
  through `uccix-mistral-24b` — the platform's only dedicated
  Irish-language model per the `centralized-model-registry` spec).
- Process `leaving_certificate/` 13 subjects × (EN+GA) PDFs through
  the BIEP v3 5-phase pattern (Ingestion → Materials → Embedding →
  ibis logging → Analytics) using the token-plan text APIs.

### Phase 4 — England + NCCA + 4 regression gates + CopilotKit pin (22 tasks, ~2 days)

- **England DLT sources** (3 + 3 = 6 files): `dlt_sources/british_isles/england/education/gcse/{aqa,ocr,edexcel}_source.py`
  + `dlt_sources/british_isles/england/education/a_level/{aqa,ocr,edexcel}_source.py`.
- **England Dagster asset groups** (2 files): `orchestration/defs/2_materials/england_education/{gcse,a_level}_assets.py`.
- **England misconfig check**: `orchestration/defs/2_materials/england_education/misconfig_check.py`.
- **England seed script**: `scripts/seed_england_pdfs.py` for 92 subjects × 3 boards.
- **Real BAML prompt**: extract `ExtractAQAQualSpec` (the one stub in
  `baml_src/british_isles/england/education/curriculum_syllabus.baml`).
- **8 NCCA specialists migration**: move `gael_agent`, `math_agent`,
  `appm_agent`, `chem_agent`, `comp_agent`, `engl_agent`, `geog_agent`,
  `hist_agent` from the back-compat wiring in `agents/tuatha/wiring.py`
  to the new `CelticAgentOpsComponent` (per the
  `meaisinfhoghlaim-agent-frameworks` spec).
- **4 new regression gates** (each added to `mise.toml` + each with
  a corresponding `scripts/<name>.py`):
  - `lint:dagster:sensor-job-coverage` (already added by Mega-6)
  - `lint:litellm-router-fallbacks` (NEW, ~40 LOC, fails if any
    `router_settings.fallbacks:` is a bare list of strings rather than
    the `{primary: [fallbacks]}` dict form per `2026-07-29-lakehouse-extensive-hydration-v1`)
  - `lint:baml-stub-prompts` (NEW, ~50 LOC, fails if any BAML
    function body is the literal string `"Auto-generated extraction prompt."`
    — closes the 832-of-838 stub class)
  - `lint:copilotkit-actions-stubbed` (NEW, ~40 LOC, fails if any
    CopilotKit action returns `"TBD"` placeholder — closes the 12-of-14 stub class)
- **Token plans into MODEL_REGISTRY**: add `minimax-coding-plan/MiniMax-M3`
  (text_llm/default) + the 4 Qwen Cloud models (qwen3-coder-next,
  qwen3-coder-plus, qwen3-max-2026-01-23, glm-5.1, kimi-k2.6, mimo-v2.5,
  deepseek-v4-flash) per `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`.
- **MINIMAX_API_KEY + QWEN_DASHSCOPE_API_KEY** added to `.infisical.env`.
- **CopilotKit pin** to `@copilotkit/runtime >= 1.67.1` +
  `@copilotkit/react-core >= 1.67.1` + `@copilotkit/react-ui >= 1.67.1` in
  `web/apps/cianfhoghlaim-leaving-cert/package.json` per Correction #6.
- **ag-ui-strands upgrade** alongside the CopilotKit pin (per
  `CopilotKit issue #2946` fixed in v1.63.x).
- **BAML ClientRegistry** adoption: add `ExtractorPrimary` /
  `ExtractorFallback` patterns in `baml_src/clients.baml` for the OCR
  ensemble (per the `baml-schemas` spec added by Mega-6).
- **CocoIndex `deps=` adoption**: update the 14 `@coco.fn(memo=True)`
  sites to declare module-level prompt strings via `deps=`
  (per the `ciianfhoghlaim-cocoindex-v1-migration` spec added by Mega-6).
- **`web/COPILOTKIT_PIN.md`**: NEW canonical doc explaining the
  pin + decision + 1.67.1 migration notes.

## Impact

- Code: ~25 files modified, ~14 files created
- New tasks in `mise.toml`: `lint:litellm-router-fallbacks`,
  `lint:baml-stub-prompts`, `lint:copilotkit-actions-stubbed`
- Spec deltas: 7 specs affected (0 MODIFIED + 13 ADDED across 7 capabilities)
- New scripts: 4 (download_gguf_weights, verify_litellm_redeploy,
  seed_england_pdfs, plus the 3 new lint scripts)
- New tests: 1 (tests/test_scanned_detector.py)
- New docs: 1 (web/COPILOTKIT_PIN.md)
- Models: 17 GGUF files (~60-80 GB) downloaded into stedding/huggingface/gguf/

## Success criteria

1. `openspec validate 2026-08-17-biep-v3-bring-up-v1 --strict` exits 0
2. `km deploy stack litellm --force` + `bash scripts/verify_litellm_redeploy.sh` exits 0
3. `cd bonneagar/stacks/llama-swap && docker compose up -d` brings up the container with 17 model IDs at `curl http://llama-swap:8080/v1/models`
4. `dagster asset materialize --select biiep_ocr_ensemble` returns `rows_landed > 0` against a real Ireland LC PDF
5. `mise run lint:dagster:sensor-job-coverage` exits 0 (all 8 jurisdiction sensors have matching jobs)
6. `mise run lint:litellm-router-fallbacks` exits 0 (no bare-list fallbacks)
7. `mise run lint:baml-stub-prompts` exits 0 (no `"Auto-generated extraction prompt."` strings)
8. `mise run lint:copilotkit-actions-stubbed` exits 0 (no `"TBD"` placeholders)
9. `mise run lint:dlt:nested-hints` exits 0 (no `__` path fragments)
10. `mise run lint:locket-version` exits 0 (no unpinned locket refs)
11. `mise run lint:registry` exits 0 (no hardcoded model strings)
12. `mise run sync:dagster` exits 0 (no asset drift)
13. `openspec archive 2026-08-17-biep-v3-bring-up-v1 --yes` succeeds