# centralized-model-registry Specification

## Purpose
TBD - created by archiving change 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1. Update Purpose after archive.

## Requirements

### Requirement: Single canonical model registry covering all model families

The system SHALL provide a single canonical `MODEL_REGISTRY` dict at
`meaisinfhoghlaim/models/registry.py` covering at minimum the 5 model
families:

1. `ocr_vision` — the existing 22-entry `VISION_MODELS` (becomes a
   subset view via `MODEL_REGISTRY.filter(family="ocr_vision")`)
2. `text_llm` — the 9 M3 chokepoint aliases (`kimi/k2`, `glm/5.1`,
   `minimax/m2.5`, `mimo/2.5`, `deepseek/flash`, `minimax-m3`) + the
   canonical `minimax` opencode provider + the 6 hackathon HF
   Inference fallbacks
3. `embedder` — the 3 sentence-transformer models
   (`BAAI/bge-m3`, `BAAI/bge-large-en-v1.5`, `all-MiniLM-L6-v2`)
4. `rerank` — the 3 rerank providers (jina-reranker-v2-base-multilingual,
   rerank-v3.5, gte-rerank-v2)
5. `image_gen` — the 5 image-gen models (flux2-dev, z-image-turbo,
   qwen-image, sdxl, fibo)
6. `voice` — the 5 voice/ASR/TTS models (whisper-large,
   wav2vec2-irish, chatterbox, aba-tts, ResembleAI/chatterbox)
7. `translation` — the 3 translation models (opus-mt, m2m100, nllb)

Each entry SHALL have at minimum: `key`, `family`, `role`,
`unsloth_id | None`, `mlx_id | None`, `upstream_id`, `backend`,
`available: bool`, `notes`. The `family` and `role` form the
canonical 2-axis key for `resolve(family, role)`.

#### Scenario: MODEL_REGISTRY is queryable by family + role

- **GIVEN** the `MODEL_REGISTRY` at
  `meaisinfhoghlaim/models/registry.py`
- **WHEN** the operator runs
  `python3 -c "from meaisinfhoghlaim.models.registry import MODEL_REGISTRY; print(len(MODEL_REGISTRY))"`
- **THEN** the output is `>= 70` (22 OCR/VLM + 15 text LLM + 3
  embedder + 3 rerank + 5 image-gen + 5 voice + 3 translation + ~14
  legacy/transitional)

#### Scenario: MODEL_REGISTRY.resolve(family, role) returns a model key

- **GIVEN** the `MODEL_REGISTRY` populated with the 5 families
- **WHEN** the operator runs
  `python3 -c "from meaisinfhoghlaim.models.registry import MODEL_REGISTRY; print(MODEL_REGISTRY.resolve('text_llm', 'default'))"`
- **THEN** the output is `"minimax-m3"`
- **AND** `MODEL_REGISTRY.resolve("ocr_vision", "diagram")` returns
  `"molmo2-8b"`
- **AND** `MODEL_REGISTRY.resolve("voice", "tts")` returns
  `"ResembleAI/chatterbox"`

#### Scenario: VISION_MODELS is a subset view

- **GIVEN** the legacy `VISION_MODELS` dict referenced by
  `meaisinfhoghlaim-ocr-htr` and `meaisin-24-ocr-models` specs
- **WHEN** the operator runs
  `python3 -c "from meaisinfhoghlaim.models.registry import VISION_MODELS; print(len(VISION_MODELS))"`
- **THEN** the output is `>= 22`
- **AND** `VISION_MODELS == MODEL_REGISTRY.filter(family="ocr_vision")`
  returns `True`

### Requirement: All LiteLLM + BAML + agent + embedder + image-gen + voice + translation sites consume the registry

The system SHALL NOT contain any hardcoded model string (other than in
the canonical `MODEL_REGISTRY` itself) in any of these directories:

- `agents/` (all sub-packages)
- `baml_src/` (all `.baml` files)
- `notebooks/` (all `.py` files)
- `web/` (all `.ts`/`.tsx` files)
- `orchestration/` (all `.py` files)
- `bonneagar/stacks/litellm/config/` (the LiteLLM config is generated
  from the registry; no hardcoded aliases in comments)

Each consumer SHALL use either:

- `MODEL_REGISTRY.resolve(family, role)` — for single-model lookups
- `MODEL_REGISTRY.resolve(family, role, language)` — for language-specific
  lookups (e.g. `irish` model)
- `MODEL_REGISTRY.filter(family)` — for list-of-models (e.g. embedder
  dropdown)

#### Scenario: Zero hardcoded model strings outside the registry

- **GIVEN** the `MODEL_REGISTRY` populated with the 5 families
- **WHEN** the operator runs `mise run lint:registry`
- **THEN** the output is `Found 0 hardcoded model strings in audited files`
- **AND** the exit code is `0`

#### Scenario: All LiteLLM aliases are generated from MODEL_REGISTRY

- **GIVEN** `scripts/generate_litellm_config.py` reads `MODEL_REGISTRY`
- **WHEN** the operator runs `mise run cic:meaisin:litellm-regenerate`
- **THEN** `bonneagar/stacks/litellm/config/config.yaml` is regenerated
  from `MODEL_REGISTRY`
- **AND** the file contains zero hardcoded alias definitions (no
  `vision:`, `ocr:`, `diagram:`, `gaelic:`, `irish:`, `default:`,
  `math:`, `extract:`, `embedding-bge-m3:` blocks — only
  `local/vision/<key>` entries derived from `MODEL_REGISTRY.filter(
  family="ocr_vision")`)

#### Scenario: All BAML clients reference MODEL_REGISTRY

- **GIVEN** the 27 active BAML clients in `baml_src/clients.baml` (21) +
  `clients_llama_swap.baml` (4) + `clients_ocr_ensemble.baml` (2)
- **WHEN** the operator runs `mise run baml:generate`
- **THEN** every `client<llm>` block references a model key that exists
  in `MODEL_REGISTRY`
- **AND** the 8 commented-out historical clients in
  `clients.baml:15-82` are deleted

#### Scenario: All 12 agents consume MODEL_REGISTRY

- **GIVEN** the 12 agents in `agents/agent_registry.py`
- **WHEN** the operator runs `mise run lint:registry`
- **THEN** every `agent_registry.<key>.litellm_routing_key` resolves
  through `MODEL_REGISTRY.resolve("text_llm", role=<key>)`
- **AND** the 32 hardcoded `gemini-2.0-flash` sites in `agents/adk/*`
  are replaced with `MODEL_REGISTRY.resolve(...)` calls

### Requirement: Registry provides model_for(family, role, language) API + CLI + marimo tab

The system SHALL expose the `MODEL_REGISTRY` through 3 surfaces:

1. **Python API**: `MODEL_REGISTRY.resolve(family, role, language=None)`
   + `MODEL_REGISTRY.filter(family)` at
   `meaisinfhoghlaim/models/registry.py`
2. **CLI**: `bun run cianfhoghlaim models list` (human + JSON output)
   + `models enable <key>` / `models disable <key>` subcommands in
   `scripts/cianfhoghlaim-cli.ts`
3. **Marimo tab**: Tab 1 "Models" in `notebooks/00_control_panel.py`
   (see the `deployment-control-panel` spec) lists every
   `MODEL_REGISTRY` entry by family with toggle on/off

#### Scenario: model_for() Python API works for all families

- **GIVEN** the `MODEL_REGISTRY` populated with the 5 families
- **WHEN** the operator runs
  `python3 -c "from meaisinfhoghlaim.models.registry import MODEL_REGISTRY; assert MODEL_REGISTRY.resolve('text_llm', 'default') == 'minimax-m3'; assert MODEL_REGISTRY.resolve('voice', 'tts') == 'ResembleAI/chatterbox'; assert len(MODEL_REGISTRY.filter('embedder')) >= 3"`
- **THEN** the assertions all pass and the exit code is `0`

#### Scenario: CLI models list prints every entry

- **GIVEN** the `MODEL_REGISTRY` populated with the 5 families
- **WHEN** the operator runs `bun run cianfhoghlaim models list`
- **THEN** the output lists every entry grouped by family (ocr_vision,
  text_llm, embedder, rerank, image_gen, voice, translation)
- **AND** the JSON variant (`bun run cianfhoghlaim models list --json`)
  outputs `[{key, family, role, upstream_id, backend, available}, ...]`

#### Scenario: Marimo Tab 1 lists every MODEL_REGISTRY entry

- **GIVEN** the `notebooks/00_control_panel.py` notebook
- **WHEN** the operator runs `marimo edit notebooks/00_control_panel.py`
  and clicks Tab 1 "Models"
- **THEN** the tab shows a `mo.ui.multiselect` listing every
  `MODEL_REGISTRY` entry by family
- **AND** toggling an entry writes the choice to
  `deployment-choice.yaml` via
  `notebooks/_shared/deployment_choice.py:write_choice()`

### Requirement: Registry is audited on every commit

The system SHALL run `mise run lint:registry` on every commit via a CI
hook (or equivalent) to detect hardcoded model strings in the audited
files. The lint SHALL exit non-zero if any hardcoded model string is
detected that does not exist in `MODEL_REGISTRY`.

#### Scenario: lint:registry detects a hardcoded model string

- **GIVEN** a new Python file at `agents/foo.py` containing
  `model = "gemini-2.0-flash"` (hardcoded, not from `MODEL_REGISTRY`)
- **WHEN** the operator runs `mise run lint:registry`
- **THEN** the output contains `agents/foo.py: hardcoded model string "gemini-2.0-flash" not in MODEL_REGISTRY`
- **AND** the exit code is non-zero

#### Scenario: lint:registry passes when registry is consumed

- **GIVEN** a Python file at `agents/foo.py` containing
  `model = MODEL_REGISTRY.resolve("text_llm", "default")`
- **WHEN** the operator runs `mise run lint:registry`
- **THEN** the output is `Found 0 hardcoded model strings in audited files`
- **AND** the exit code is `0`

#### Scenario: lint:registry is wired into CI

- **GIVEN** the `mise run lint:registry` task
- **WHEN** the operator runs `mise run doctor`
- **THEN** the output includes `lint:registry: OK`
- **AND** the existing CI pipeline (`.github/workflows/`)
  includes a step that runs `mise run lint:registry`

### Requirement: Registry audit is a CI gate

The system SHALL run `mise run lint:registry` in the `.forgejo/workflows/`
CI on every commit. The CI gate SHALL fail any commit that introduces
a hardcoded model string outside the `MODEL_REGISTRY` whitelist
(detected via `scripts/registry_audit.py --strict`).

#### Scenario: hardcoded model string blocks PR

- **GIVEN** a PR adds `LlmAgent(model="custom-llama-3-70b")` to a Python file
- **WHEN** the CI runs `mise run lint:registry`
- **THEN** the audit SHALL flag the hardcoded model string
- **AND** the CI gate SHALL exit non-zero
- **AND** the PR SHALL be blocked from merge

### Requirement: Audit covers all model-using surfaces

The `mise run lint:registry` task SHALL audit every Python file
under `agents/`, `baml_src/`, `notebooks/`, `web/`, `orchestration/`,
`spaces/`, **and** `meaisinfhoghlaim/`. Any hardcoded model string
in any of these directories (not routed through `MODEL_REGISTRY`)
SHALL fail the gate.

#### Scenario: A hardcoded model is added to meaisinfhoghlaim/process/

- **GIVEN** a developer adds `default_model="gpt-4.5-turbo"` to a
  new function in `meaisinfhoghlaim/process/llm_router.py`
- **WHEN** `mise run lint:registry` runs
- **THEN** the audit MUST detect the new hardcoded string
- **AND** the gate MUST exit 1 with a finding like
  `meaisinfhoghlaim/process/llm_router.py:<line>: 'gpt-4.5-turbo'`

#### Scenario: The audit is run against the post-change state

- **GIVEN** the `drift-remediation` change has migrated the 6
  hardcoded models in `meaisinfhoghlaim/` to `model_for(...)` lookups
- **WHEN** `mise run lint:registry` runs
- **THEN** the audit MUST exit 0 with `Found 0 hardcoded model strings in audited files`
- **AND** the `_AUDIT_DIRS` list in `scripts/registry_audit.py`
  MUST include `meaisinfhoghlaim/`

### Requirement: Registry drift watcher notebook

The system MUST publish a registry drift watcher notebook at
`notebooks/14_dev_env_tools_08_registry_drift_watch.py` that:

1. Invokes `scripts/registry_audit.py --json` and parses the
   structured findings (count + file list + matched string).
2. Renders a drift dashboard showing the total drift count + the
   list of offending files + the canonical `MODEL_REGISTRY` entry
   that should replace each finding (if a registry entry exists).
3. Re-runs the audit on every cell re-evaluation so the operator
   can edit a file and see the drift count drop in real time.
4. Includes a CI gate status block that displays whether
   `mise run lint:registry` will pass (drift = 0) or fail
   (drift > 0) and whether the `registry_drift_alert_sensor` will
   fire on the next tick.
5. References the canonical skill (`.agents/skills/centralized-registry/SKILL.md`)
   + the canonical Dagster sensor
   (`orchestration/defs/sync_assets.py:registry_drift_alert_sensor`)
   + the companion explorer notebook (`notebooks/14_dev_env_tools_07_model_registry.py`).

#### Scenario: Operator opens the drift watcher notebook

- **GIVEN** the v1 cascading change has wired the 8 canonical artifacts
- **WHEN** the operator runs `marimo edit notebooks/14_dev_env_tools_08_registry_drift_watch.py`
- **THEN** the notebook shows the current drift count (must be 0)
- **AND** the notebook shows the canonical `MODEL_REGISTRY` entries
  that should replace each finding (if any)
- **AND** the notebook shows the CI gate status (`✓ 0 drift — gate passes`)
- **AND** the notebook's docstring references the centralized-registry skill + the Dagster sensor + the MODEL_REGISTRY explorer

### Requirement: Pre-commit hook blocks drift regressions

The system MUST publish a pre-commit hook that blocks commits that
introduce hardcoded model strings (the missing enforcement layer
that would have caught v1 + v2 regressions at commit time).

The hook MUST:

1. Live in `.pre-commit-config.yaml` as a single `local` repo with a
   `lint-registry` hook (`language: system`, `pass_filenames: false`,
   `always_run: true`, `stages: [pre-commit]`).
2. Invoke `mise run lint:registry` (which calls
   `scripts/registry_audit.py`).
3. Exit non-zero if any hardcoded model name or model ID is found
   in `agents/`, `baml_src/`, `notebooks/`, `web/`,
   `orchestration/`, `spaces/`, or `meaisinfhoghlaim/` that isn't
   routed through `MODEL_REGISTRY`.
4. Be installable via `mise run pre-commit-install` (new task) or
   `pre-commit install` (manual).
5. Be runnable manually via `mise run pre-commit-run` (new task)
   or `pre-commit run --all-files` (manual).
6. Be skippable via `git commit --no-verify` (rare — for emergencies).
7. Be documented in `.agents/skills/centralized-registry/SKILL.md`
   under a `## Pre-commit hook` subsection.

#### Scenario: A developer commits a file with a hardcoded model string

- **GIVEN** the developer has run `mise run pre-commit-install`
- **AND** they edit `agents/foo/bar.py` to add `default_model="gemini-2.0-flash"`
- **WHEN** they run `git commit -m "add agent"`
- **THEN** the pre-commit hook runs `mise run lint:registry`
- **AND** the audit detects the hardcoded string
- **AND** the commit is blocked with a non-zero exit code

#### Scenario: A developer commits a file that uses MODEL_REGISTRY.resolve()

- **GIVEN** the developer has run `mise run pre-commit-install`
- **AND** they edit `agents/foo/bar.py` to add
  `from meaisinfhoghlaim.models import model_for; default = model_for("text_llm", "default")`
- **WHEN** they run `git commit -m "add agent"`
- **THEN** the pre-commit hook runs `mise run lint:registry`
- **AND** the audit reports 0 drift
- **AND** the commit succeeds

### Requirement: Token-plan model entries in MODEL_REGISTRY

The MODEL_REGISTRY SHALL include entries for the 7 paid token-plan
models listed below. The registry file lives at
`meaisinfhoghlaim/models/model_registry.py`.

The entries are:
- `minimax-coding-plan/MiniMax-M3` (text_llm/default) — the MiniMax
  coding plan endpoint at `https://api.minimax.io/anthropic`
  (Anthropic-compatible)
- `qwen3-coder-next` (text_llm/token_plan_coding) — DashScope coding
  specialist
- `qwen3-coder-plus` (text_llm/token_plan_coding_strong) — DashScope
  coding + reasoning
- `qwen3-max-2026-01-23` (text_llm/token_plan_max) — DashScope
  flagship reasoning model
- `glm-5.1` (text_llm/token_plan_glm) — third-party via DashScope
- `kimi-k2.6` (text_llm/token_plan_kimi) — third-party via DashScope
- `mimo-v2.5` (text_llm/token_plan_mimo) — third-party via DashScope
- `deepseek-v4-flash` (text_llm/token_plan_deepseek) — third-party
  via DashScope

Each entry MUST include:
- `provider: openai` (for DashScope OpenAI-compatible endpoint)
- `base_url_env: DASHSCOPE_BASE_URL` (default
  `https://coding.dashscope.aliyuncs.com/v1`)
- `api_key_env: DASHSCOPE_API_KEY` (or `MINIMAX_API_KEY` for MiniMax)

Per the `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
change proposal.

Per the `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
change proposal. Each entry MUST include:
- `provider: "openai"` (for DashScope OpenAI-compatible endpoint)
- `base_url_env: "DASHSCOPE_BASE_URL"` (default `https://coding.dashscope.aliyuncs.com/v1`)
- `api_key_env: "DASHSCOPE_API_KEY"` (or `"MINIMAX_API_KEY"` for MiniMax)

#### Scenario: Token-plan model resolves via model_for

- **WHEN** `model_for("text_llm", "token_plan_coding")` is called
- **THEN** it returns `"qwen3-coder-next"`
- **AND** the BAML client can use this string as a model ID

#### Scenario: Token-plan secrets are hydrated

- **WHEN** `mise run secrets:init` runs
- **THEN** `MINIMAX_API_KEY` and `QWEN_DASHSCOPE_API_KEY` are populated
  in the dev-baile Infisical vault
- **AND** `.env` (hydrated by mise) exposes both keys

### Requirement: registry_audit covers token-plan hardcoded strings

The `mise run lint:registry` gate SHALL fail if any
`agents/`, `baml_src/`, `notebooks/`, `web/`, `orchestration/`,
`spaces/`, or `meaisinfhoghlaim/` file contains a hardcoded token-plan
model string that is not routed through `MODEL_REGISTRY`.

#### Scenario: Developer hardcodes a token-plan model

- **WHEN** a developer adds `model_name = "qwen3-coder-plus"` directly
  in a Python file (without using `model_for(...)`)
- **THEN** `mise run lint:registry` exits 1 with
  `path/to/file.py:<line>: 'qwen3-coder-plus' — route through MODEL_REGISTRY`

### Requirement: Bilingual GA↔EN cross-stage BAML extraction SHALL be added

`baml_src/british_isles/ireland/education/_cross/cross_linguistic.baml` SHALL add `ExtractBilingualLearningOutcome(en_text, ga_text) -> BilingualLearningOutcome` and `ExtractCrossLinguisticGA(ga_text) -> CrossLinguisticConcept` functions with real prompts.

**WHEN** `b.ExtractBilingualLearningOutcome(en_text=..., ga_text=...)` is called with paired LC English + Irish syllabus text
**THEN** it SHALL return `{en_lo_id, ga_lo_id, confidence, source_pairs: [(en_segment, ga_segment)]}`

#### Scenario: Bilingual pair extracted from LC English + Irish chemistry syllabus

- **WHEN** the operator runs `b.ExtractBilingualLearningOutcome(en_text=english_chem_syllabus, ga_text=irish_chem_syllabus)`
- **THEN** the function returns `{en_lo_id: "LC-CHEM-LO-023", ga_lo_id: "LC-CEM-LO-023", confidence: 0.92, source_pairs: [...]}`
- **AND** the result lands in `md:cianfhoghlaim.bilingual_los` table for downstream Graphiti episodes

### Requirement: Cross-stage cognify SHALL create 8 cross-stage edges

The `cross_stage_cognify` asset SHALL execute the 8 hand-coded `EDGE_DEFINITIONS`:
- `AistearPrinciple-BRIDGES_TO->PrimaryLearningOutcome`
- `PrimaryLearningOutcome-PREPARES_FOR->JCLearningOutcome`
- `JCLearningOutcome-PROGRESSES_TO->SCLearningOutcome`
- `SCLearningOutcome-ASSESSED_BY->ExamQuestion`
- `LCSubject-REQUIRED_FOR->CAOCourse`
- `CAOCourse-DELIVERS->Programme`
- `QQIFetAward-LADDERS_INTO->CAOCourse`
- `Apprenticeship-ALTERNATIVE_TO->CAOCourse`

**WHEN** all 5 stage cognify assets complete successfully
**THEN** cross-stage cognify SHALL iterate the 8 EDGE_DEFINITIONS and call BAML `ExtractCrossStageLink(a, b)` to score each pair
**AND** write edges to Cognee dataset `cianfhoghlaim.education.cross_stage` where the BAML score >= 0.5

#### Scenario: AistearPrinciple bridges to PrimaryLearningOutcome via BAML scoring

- **WHEN** the cross-stage cognify runs after `aistear_cognify` + `primary_cognify` complete
- **THEN** for each pair (AistearPrinciple, PrimaryLearningOutcome), `ExtractCrossStageLink(principle, lo)` returns a score
- **AND** if score >= 0.5, a `BRIDGES_TO` edge is written to the cross_stage dataset

### Requirement: Cross-qualification map SHALL be backed by Cognee

The 30 hard-coded equivalences in `meaisinfhoghlaim/alignment/cross_qualification_subject_map.py:81-120` SHALL be migrated to a Cognee dataset `british_isles_equivalences` with provenance from `baml_src/british_isles/_cross/isles_education.baml`. New equivalences SHALL be added for: Scotland Nat 5/Higher/Adv Higher (3), Wales WJEC (1), Northern Ireland CCEA (1), Jersey/Guernsey/Isle of Man (3) — total 38 equivalences.

**WHEN** `CrossJurisdictionDiffer.diff(qual_a, jur_a, qual_b, jur_b)` is called
**THEN** it SHALL query Cognee for the matching equivalence edge
**AND** return the alignment percentage + provenance link to the source BAML extraction

#### Scenario: Ireland chemistry ↔ England chemistry returns 0.80 alignment

- **WHEN** `CrossJurisdictionDiffer.diff("lc", "ireland", "gcse", "england", subject="chemistry")` is called
- **THEN** it queries the Cognee `british_isles_equivalences` dataset for the matching edge
- **AND** returns `{alignment_pct: 0.80, equivalence_id: "lc_chem_gcse_chem_01", notes: "LC is broader"}`

### Requirement: 9 cognee_ingest scripts SHALL be wired as Dagster sensors

Each of `cognee_ingest_{docs,dlt_sources,baml_schemas,skills,agent_definitions,openspec,stacks_catalog,notebooks}.py` SHALL be wrapped as a `@sensor` in `orchestration/defs/3_model_lifecycle/cognify/sensors/` watching the relevant root directory.

**WHEN** any file in `baml_src/*.baml` changes
**THEN** the `cognee_ingest_baml_schemas` sensor SHALL trigger a re-cognify into the `baml_schemas` Cognee dataset

#### Scenario: New BAML function triggers re-cognify

- **WHEN** an operator adds a new `@function` to `baml_src/british_isles/ireland/education/stages/aistear.baml`
- **THEN** the `baml_schemas_sensor` fires within 60s
- **AND** `cognee_ingest_baml_schemas.py` runs against the new schema
- **AND** the `baml_schemas` Cognee dataset is updated

### Requirement: ocr_vision family SHALL be exposed with full pipeline documentation in centralized-registry §11

The `centralized-registry` skill MUST add a `## 11. OCR/VLM
Pipeline` section (after the existing `## 10. The 6
follow-up issues`) that documents the full OCR/VLM surface
for the Cianfhoghlaim platform — at minimum:

1. The 22-entry `VISION_MODELS` subset view of the
   `ocr_vision` family in `MODEL_REGISTRY`, with per-entry
   `key` / `role` / `upstream_id` / `backend`
2. The 6 `CLASSICAL_OCR` backends in
   `meaisinfhoghlaim/models/registry.py:CLASSICAL_OCR`
   (Pylaia + TrOCR + PaddleOCR + Tesseract + dots.ocr + VLM)
3. The BIEP v2 4-path ensemble (`EnsembledExtractor` —
   `baml + unstract + qwen3_vl + gemma4`) at
   `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`,
   including the RAGAS voting pattern and the
   `OCR_WEBHOOK_URL` emission pattern
4. The 7 PDF converters in
   `meaisinfhoghlaim/document_factory/` (`docling`,
   `marker`, `unstructured`, `deepseekocr`, `pymupdf4llm`,
   `curriculum_document`, `pdf_factory`)
5. The 4 alignment methods in
   `meaisinfhoghlaim/alignment/aligner.py` (`VecAlign`,
   `HunAlign`, `GaoisAlign`, `Hybrid`) plus the
   `ColPaliAligner` for manuscript bbox extraction
6. The Irish HTR dataset
   (`meaisinfhoghlaim/datasets/irish_htr_dataset.py`)
7. The M4-Max dispatch helper
   (`select_optimal_for_m4_max()`)
8. The llama-swap GGUF inference path
   (`meaisinfhoghlaim/models/llama_swap_config.yaml`)
9. The BAML `baml_src/clients_ocr_ensemble.baml` patterns
10. The `meaisinfhoghlaim/ocr/` back-compat shim (with
    `DeprecationWarning` documentation — canonical is
    `meaisinfhoghlaim.models`)

The §11 entry MUST be the first CCC result for any agent
query containing "OCR", "VLM", "vision model", or
"document extraction".

#### Scenario: Agent discovers OCR/VLM surface via §11

- **GIVEN** an agent is asked to add or modify an OCR model
  in the Cianfhoghlaim platform
- **WHEN** the agent runs
  `bun run ccc:search "OCR VLM pipeline"` or
  `bun run ccc:search "vision model selection"`
- **THEN** the first CCC result MUST be the
  `centralized-registry` §11 entry
- **AND** §11 MUST include the 22-entry `VISION_MODELS`
  table with `key` / `role` / `upstream_id` / `backend`
  columns
- **AND** §11 MUST include a code sample for the 4-path
  ensemble `EnsembledExtractor` invocation
- **AND** §11 MUST cross-reference
  `meaisinfhoghlaim/README.md` for the deeper sub-package
  docs
- **AND** §11 MUST document the `meaisinfhoghlaim/ocr/`
  back-compat shim `DeprecationWarning` and point at
  `meaisinfhoghlaim.models` as canonical

#### Scenario: Agent uses §11 to pick an OCR model for a new jurisdiction

- **GIVEN** an agent is adding a new BIEP v3 jurisdiction
  pipeline and needs to pick an OCR model
- **WHEN** the agent reads §11 to choose a model
- **THEN** §11 MUST group the 22 `VISION_MODELS` entries
  by role (`default` / `irish` / `bilingual` /
  `scanned_manuscript` / `diagram` / `dense_ocr`)
- **AND** §11 MUST show the M4-Max dispatch helper code
  with a sample invocation returning the recommended
  model for the M4-Max 64GB workload
- **AND** §11 MUST reference
  `meaisinfhoghlaim/models/llama_swap_config.yaml` for
  the local inference configuration
- **AND** §11 MUST reference
  `baml_src/clients_ocr_ensemble.baml` for the
  ensemble client pattern

### Requirement: dlt_sources/DATA_PLATFORM_ROUTER.md SHALL exist as the single router for the 5 per-area AGENTS.md files

A `DATA_PLATFORM_ROUTER.md` file at `dlt_sources/` MUST
serve as the single router for the Cianfhoghlaim data
platform surface. It MUST link to each of the 5 canonical
per-area docs (`dlt_sources/AGENTS.md`, `baml_src/AGENTS.md`,
`cocoindex/AGENTS.md`, `orchestration/AGENTS.md`,
`meaisinfhoghlaim/README.md`) and document the 6 critical
conventions:

1. Always use relative imports within sub-packages
2. Respect the ingestion cache (`USE_LOCAL_SCRAPES=true`)
3. Zero absolute namespaces in data pipelines
4. R1-R4 CocoIndex conformance
5. MODEL_REGISTRY-only (no hardcoded model strings)
6. Factory pattern for N nearly-identical Apps

The router MUST be co-located with the per-area `AGENTS.md`
files (at `dlt_sources/DATA_PLATFORM_ROUTER.md`), NOT in
`.agents/skills/`, so it does not inflate the top-level
skill count.

Each of the 5 per-area docs MUST contain a cross-link back
to `DATA_PLATFORM_ROUTER.md` (verified via
`grep -l "DATA_PLATFORM_ROUTER" <5 files>` returning 5
matches).

#### Scenario: New agent discovers the data platform surface via the router

- **GIVEN** a new agent is asked to add a DLT source for a
  new British Isles education jurisdiction
- **WHEN** the agent searches for "data platform" or
  reads `dlt_sources/AGENTS.md`
- **THEN** the agent finds a link to
  `DATA_PLATFORM_ROUTER.md`
- **AND** the router points at the 5 per-area docs and the
  6 critical conventions
- **AND** the router includes a "I want to add X, where do
  I go?" routing table that the agent can use to find the
  correct sub-package for the task

#### Scenario: Per-area docs cross-link the router

- **GIVEN** the `DATA_PLATFORM_ROUTER.md` file exists at
  `dlt_sources/DATA_PLATFORM_ROUTER.md`
- **WHEN** an operator runs
  `grep -l "DATA_PLATFORM_ROUTER" dlt_sources/AGENTS.md baml_src/AGENTS.md cocoindex/AGENTS.md orchestration/AGENTS.md meaisinfhoghlaim/README.md`
- **THEN** the command returns 5 matches (one per per-area
  doc)
- **AND** each per-area doc has a
  `## Data platform router` section with a 1-line link to
  the router file

### Requirement: INDEXING_AND_COGNITION.md §10 SHALL resolve the ccc CLI vs codebase_indexing v1 App split

The `.agents/skills/INDEXING_AND_COGNITION.md` skill MUST
add a `## 10. Code-search canonical entrypoint` section
(after the existing `## 9. The cianfhoghlaim v4
consolidation`) that provides a single decision matrix
resolving the dual CLI vs v1 App vs graph companion split.

The matrix MUST list at least these 3 surfaces:

1. **CLI** — `bun run ccc:search "<query>"`
   (kept for developer shortcuts; the `ccc` skill carries
   the DEPRECATION NOTICE banner)
2. **Python v1 App** —
   `from cocoindex.codebase_indexing import code_search`
   (the canonical replacement for `ccc search`)
3. **Graph companion** —
   `search_code_graph(file_path=..., node_type=...)`
   (the 7-node / 7-edge code graph; 7 node types: File,
   Function, Class, Method, Module, Interface, Variable;
   7 edge types: CONTAINS, IMPORTS, CALLS, EXTENDS,
   IMPLEMENTS, USES, DEFINES)

Plus the 4 infrastructure companions:
`search_api_endpoints`, `search_filesystem`,
`search_storage`, `search_config`.

#### Scenario: Agent picks the right code-search surface for the task

- **GIVEN** an agent needs to find a specific function in
  the codebase
- **WHEN** the agent reads `INDEXING_AND_COGNITION.md §10`
- **THEN** the matrix MUST recommend the v1 App
  (`code_search(...)`) for pipelines and ad-hoc Python
  use, the CLI (`ccc search`) for one-off terminal
  searches, and the graph companion
  (`search_code_graph(...)`) for code-structure queries
  (e.g. "what calls function X?")
- **AND** the matrix MUST cross-reference
  `cocoindex/AGENTS.md` for the v1 App canonical pattern
- **AND** the matrix MUST cross-reference
  `.agents/skills/ccc/SKILL.md` for the CLI surface
  (with the DEPRECATION NOTICE context)

### Requirement: cocoindex_query_api integration helper

The system SHALL provide a `cocoindex_query_api` integration helper at
`cocoindex/_shared/cocoindex_query_api.py` that exposes every
CocoIndex App as a `search(query, top_k=5) -> List[Chunk]` Python
closure. The closure wraps `lancedb.Table.search` with the canonical
`BAAI/bge-m3` embedder.

The helper replaces the 47 ad-hoc `lancedb.connect(CIANFHOGHLAIM_LANCEDB_URL)`
calls scattered across notebooks, agents, and web apps.

#### Scenario: Every CocoIndex App exposes a search closure

- **GIVEN** the 47 BIEP CocoIndex Apps + the 4 infrastructure CocoIndex Apps (upstream_blog_monitor, upstream_api_surface, docs_skills_consolidation, codebase_indexing)
- **WHEN** the operator runs `python -c "from cocoindex._shared.cocoindex_query_api import get_search; print(get_search('ireland_lc_mathematics_embedding'))"`
- **THEN** the helper returns a callable that runs the canonical
  LanceDB query against the BIEP v3 table
  `cianhoghlaim.education.ireland.lc.mathematics.chunks`

#### Scenario: All 47 ad-hoc lancedb.connect calls are replaced

- **WHEN** `mise run lint:cocoindex-query-api-coverage` runs
- **THEN** all 47 ad-hoc `lancedb.connect(...)` calls MUST be replaced
  with `from cocoindex._shared.cocoindex_query_api import get_search`
- **AND** the lint returns `OK: 47/47 connect calls replaced`
