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

