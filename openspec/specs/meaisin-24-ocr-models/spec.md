# meaisin-24-ocr-models Capability

## Purpose

`meaisin-24-ocr-models` is the per-OCR/VLM model contract for the
meaisinfhoghlaim v5 umbrella. It documents the canonical 24-model
registry structure, the per-model BAML Extract function contract, the
per-model 2-axis partition, the per-model asset check, the per-model
MotherDuck Dive + Flight, and the per-model ChangeDetection.io monitor
for the 24 OCR/VLM models in the v4 registry.

The 24 OCR/VLM models across 4 backends are:

- **LITELLM** (1 entry: uccix-llama2-13b) — proxied via `litellm.cianfhoghlaim.ie:4000`
- **MLX** (4 entries: granite-docling-258M, dots-ocr, deepseek-ocr-2, gemma-4-E2B) — Apple Silicon MLX
- **TRANSFORMERS** (6 entries: deepseek-ocr-2, olmocr-2-7b-1025, molmo2-4b, molmo2-8b, uccix-mistral-24b, uccix-llama-3.1-8b) — Python inline
- **LLAMASWAP** (13 entries: the Unsloth GGUF family) — served via `llama-swap` at `ghcr.io/mostlygeek/llama-swap:v166`
## Requirements
### Requirement: 24-model v4 registry structure

The system SHALL provide a canonical 24-entry `VISION_MODELS` dict
in `meaisinfhoghlaim/models/registry.py` with the canonical structure:

```python
OCRModel(
    key: str,             # canonical model identifier
    name: str,            # display name
    unsloth_id: str | None,  # preferred Unsloth GGUF ID
    mlx_id: str | None,      # Apple Silicon MLX ID
    upstream_id: str,        # canonical upstream org HF ID
    backend: ModelBackend,    # litellm | mlx | transformers | llama-swap
    capabilities: list[ModelCapability],  # 9 capabilities
    unsloth_features: list[str],
    role: ModelRole,         # tier1 | tier2 | tier3
    m4_max_48gb_fit: bool,
    arm1_oci_required: bool,
    available: bool,
    max_resolution: tuple[int, int],
    notes: str,
)
```

The 24 keys are: `deepseek-ocr-2`, `docling-serve`, `dots-ocr`,
`gemma-3-4b`, `glm-4.6v-flash`, `internvl3-8b`, `llama-3.2-vision-11b`,
`molmo2-4b`, `molmo2-8b`, `olmocr-2-7b-1025`, `paddleocr-vl-1.6`,
`qwen3-vl-30b-a3b`, `qwen3-vl-4b`, `qwen3-vl-8b`, `qwen3.6-27b-mtp`,
`uccix-llama-3.1-8b`, `uccix-llama2-13b`, `uccix-mistral-24b`,
`unstract-api`, + 5 more entries (LlamaSwap Unsloth GGUF family).

#### Scenario: 24-model registry present

- **WHEN** the operator runs `python3 -c "from meaisinfhoghlaim.models.registry import VISION_MODELS; print(len(VISION_MODELS))"`
- **THEN** the output is `>= 24`

### Requirement: Per-model BAML Extract function contract

The system SHALL provide a canonical BAML `Extract*` function per
model. The function takes `(pdf_text, model_key)` and returns a
canonical model extraction Pydantic type.

#### Scenario: Per-model BAML Extract function callable

- **WHEN** the operator runs `python3 -c "from baml_client import b; print(b.Extract<Model>(pdf_text='test', model_key='<model>'))"`
- **THEN** the function returns a valid Pydantic type

### Requirement: Per-model 2-axis scope × model partition

The system SHALL partition every per-model Dagster asset on the
canonical 2-axis partition:

- **Scope axis**: `meaisin_ocr_vlm_<model_key>`
- **Model axis**: integer version (e.g. `v4`) or `undated`

#### Scenario: Per-model partition

- **WHEN** the `ocr_model_<key>_documents_ingested` asset materialises
- **THEN** the partition key is `(scope="meaisin_ocr_vlm_<model_key>", model="v4")`

### Requirement: Per-model 3 asset checks

The system SHALL provide 3 asset checks per model:

- `ocr_model_<key>_ingested_check` — the model is in the registry
- `ocr_model_<key>_extractions_ragas_check` — the RAGAS score >= 0.70
- `ocr_model_<key>_embeddings_check` — the model is embedded in the registry

#### Scenario: Per-model asset check passing

- **WHEN** the `ocr_model_<key>_ingested_check` runs
- **THEN** it returns `passed=True` with the metadata `{"model_key": "<key>", "available": True}`

### Requirement: Per-model MotherDuck Dive + Flight

The system SHALL provide 1 MotherDuck Dive + 1 MotherDuck Flight per
model. The Dive reads from `md:cianfhoghlaim.education.meaisin.models.registry`
and the Flight calls the meaisin v5 entrypoint script.

#### Scenario: Per-model MotherDuck Dive

- **WHEN** the operator opens the MotherDuck Dive `meaisin_ocr_registry_dive`
- **THEN** the Dive shows 24 rows (one per model)

### Requirement: Per-model ChangeDetection.io monitor

The system SHALL provide 1 ChangeDetection.io monitor per model. The
monitors are at `bonneagar/stacks/changedetection/monitors/meaisin_<model_key>.yaml`.

#### Scenario: Per-model ChangeDetection monitor

- **WHEN** the operator opens `bonneagar/stacks/changedetection/monitors/meaisin_<model_key>.yaml`
- **THEN** the monitor has the canonical structure

### Requirement: Per-model mise task entrypoint

The system SHALL provide 1 canonical mise task per model:
- `meaisin:ocr:test:<model_key>` — runs the 4-path OCR ensemble + the OCR evaluation harness + the 24-model registry audit

The 24 mise tasks are added to `mise.toml` via the meaisin v5
operator surface (Phase 1 of the 7-phase plan).

#### Scenario: Per-model mise task

- **WHEN** the operator runs `mise run meaisin:ocr:test:deepseek-ocr-2`
- **THEN** the script runs 3 steps (4-path ensemble + OCR eval + registry audit)

### Requirement: Per-model snake_case file naming

The system SHALL enforce the canonical per-model snake_case file naming
convention:

```text
s3://garage/cianfhoghlaim/meaisin/ocr/<model_key>/<year>/<model_key>__<year>__<sha256_8>.json
```

#### Scenario: Per-model filename validation

- **WHEN** the operator runs `mise run meaisin:v3:status`
- **THEN** the status script verifies the 24-model registry covers all 24 keys

### Requirement: 24-model OCR/VLM registry is a subset view of MODEL_REGISTRY

The system SHALL expose the existing 22-entry `VISION_MODELS` as a
subset view of the new `MODEL_REGISTRY` via
`MODEL_REGISTRY.filter(family="ocr_vision")`. The 24-model 2-axis
partition (scope × model) MUST be preserved.

#### Scenario: VISION_MODELS is a subset view

- **GIVEN** the new `MODEL_REGISTRY` at
  `meaisinfhoghlaim/models/registry.py`
- **WHEN** the operator runs
  `python3 -c "from meaisinfhoghlaim.models.registry import VISION_MODELS, MODEL_REGISTRY; assert VISION_MODELS == MODEL_REGISTRY.filter(family='ocr_vision')"`
- **THEN** the assertion passes and the exit code is `0`

#### Scenario: 2-axis partition is preserved

- **GIVEN** the existing 24-model 2-axis partition (scope × model)
- **WHEN** the `ocr_model_<key>_documents_ingested` asset materialises
- **THEN** the partition key is `(scope="meaisin_ocr_vlm_<model_key>",
  model="v4")` (unchanged from the existing contract)

### Requirement: meaisin-24-ocr-models MUST consume MODEL_REGISTRY.filter(family="ocr_vision")

The system SHALL update `openspec/specs/meaisin-24-ocr-models/spec.md`
to reference `MODEL_REGISTRY.filter(family="ocr_vision")` rather than
the legacy `VISION_MODELS` direct reference. The 24-model 4-backend
contract (LITELLM / MLX / TRANSFORMERS / LLAMASWAP) MUST be preserved.

#### Scenario: meaisin-24-ocr-models references MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated (52 entries / 7 families)
- **WHEN** the operator reads `openspec/specs/meaisin-24-ocr-models/spec.md`
- **THEN** the spec references `MODEL_REGISTRY.filter(family="ocr_vision")` for the 24-model list
- **AND** the 24-model 4-backend contract is preserved

#### Scenario: meaisin-24-ocr-models connects to the centralized-registry skill

- **GIVEN** the `centralized-registry` skill at `.agents/skills/centralized-registry/SKILL.md`
- **WHEN** a subagent needs to add a new OCR/VLM model
- **THEN** the skill's `model_for("ocr_vision", role)` API is the canonical entry point
- **AND** the 24-model registry is a subset view of the unified `MODEL_REGISTRY`

## Cross-references

- `meaisin-v3-operator-surface` — the umbrella operator surface
- `meaisinfhoghlaim-platform` — the umbrella platform spec
- `meaisinfhoghlaim-ocr-htr` — the OCR + HTR capability
- `meaisinfhoghlaim-agent-frameworks` — the 12-agent framework spec
- `multimodal-code-and-media-intel` — the multimodal capability
- `openspec/changes/2026-07-17-fix-phantom-agents-and-ocr-backend-list-v1/` — the v5 fix
- `openspec/changes/2026-07-17-restore-ocr-python-package-v1/` — the v5 restore
- `openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/` — the v5 England AQA
- `openspec/changes/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/` — the v5 ensemble
- `meaisinfhoghlaim/models/registry.py` — the 24-model v4 registry (canonical home)
- `scripts/meaisin_ocr_htr_tests/ocr_model_<key>_extract.py` — the 24 per-model entrypoint scripts
- `motherduck/dives/meaisin_ocr_registry_dive.py` — the canonical registry Dive
- `docs/agents/meaisin-v3-systematic-download.md` — the canonical newcomer guide
