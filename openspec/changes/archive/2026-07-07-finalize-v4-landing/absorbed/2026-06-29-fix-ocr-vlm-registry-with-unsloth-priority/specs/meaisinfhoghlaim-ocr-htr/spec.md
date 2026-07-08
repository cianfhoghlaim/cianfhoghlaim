# Spec Delta: meaisinfhoghlaim-ocr-htr

## ADDED Requirements

### Requirement: 20-entry vision model registry with Unsloth-first priority

The system SHALL expose a vision model registry at `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS` with **at least 20 entries** (replacing the legacy 10-entry `OCR_MODELS` + 6-entry `VLM_MODELS`). The registry MUST cover, at minimum, these VLM families and specialist OCR families:

- **Gemma 4** — 4 sizes (E2B, E4B, 12B, 26B-A4B MoE) — **31B removed (19GB marginal on M4 48GB)**
- **GLM-4.6V Flash** — single 9-10B class — **full MoE 107B removed (doesn't fit on M4 48GB)**
- **Qwen 3-VL** — 3 sizes (4B, 8B, 30B-A3B MoE) — **235B-A22B removed (130GB doesn't fit on M4)**
- **Qwen 3.6** — 1 size with MTP speculative decoding (27B MTP) — **35B-A3B MTP removed (22GB marginal)**
- **Qwen 2.5-VL** — kept as legacy
- **DeepSeek-OCR-2** — single 3.4B specialist
- **Granite-Docling** — single 258M specialist
- **olmOCR-2-7B-1025** — single 8.3B specialist
- **Dots-OCR** — single 3.0B layout specialist
- **PaddleOCR-VL** — single 958.6M multilingual OCR specialist
- **Molmo2** — 2 sizes (4B, 8B)
- **InternVL3_5-8B** — single 8.5B
- **Llama 3.2 Vision** — single 11B as legacy
- **Gemma 3** — single 4B as legacy
- **UCCIX** — 3 variants (Llama-3.1-8B, Mistral-24B primary, Llama-2-13B legacy)

The 4 removed models (qwen3-vl-235b-a22b, glm-4.6v-full, qwen3.6-35b-a3b-mtp, gemma-4-31B) are documented in `openspec/changes/deploy-v4-ocr-vlm-on-m4-max/proposal.md` as "too large for M4 48GB; use a smaller alternative".

Each entry MUST have:

- `unsloth_id: str | None` — the `unsloth/...-GGUF` or `unsloth/...-unsloth-bnb-4bit` HF ID (preferred)
- `mlx_id: str | None` — the `mlx-community/...-4bit` HF ID for Apple Silicon
- `upstream_id: str` — the canonical upstream org ID
- `backend: ModelBackend` — one of `litellm`, `mlx`, `transformers`, `llama-swap`
- `capabilities: list[ModelCapability]` — the OCR capabilities
- `unsloth_features: list[str]` — subset of `["dynamic_2_0_gguf", "mtp_speculative", "moe_12x", "imatrix", "fast_inference"]`
- `role: Literal["tier1_heavy", "tier2_medium", "tier3_light", "specialist", "legacy"]`
- `m4_max_48gb_fit: bool`
- `arm1_oci_required: bool`
- `available: bool` — `False` for known-broken or legacy entries
- `notes: str` — provenance + last-verified date

The registry MUST NOT include cloud-API-only models (no OpenAI, no Anthropic, no Ollama). Every entry MUST have at least one local inference path.

The registry MUST have at least 20 entries that all fit on the M4 Max 48 GB unified memory host (per the v4 M4-fit criterion). Larger models (235B, 107B, 22 GB marginal, 19 GB marginal) are not in the v4 registry — they are documented in `openspec/changes/deploy-v4-ocr-vlm-on-m4-max/` as "too large for M4; use a smaller alternative".

#### Scenario: A developer adds a new Gemma 4 size

- **GIVEN** a developer adds a new Gemma 4 size variant to
  `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS`
- **WHEN** the registry is imported
- **THEN** the registry MUST have ≥21 entries
- **AND** the entry MUST have all 11 required fields populated
- **AND** if `unsloth_id` is `None`, the entry MUST include a comment explaining why (gap request status)
- **AND** the entry's `m4_max_48gb_fit` MUST be `True` (per the v4 M4-first policy)

### Requirement: Unsloth-first fallback chain

The system SHALL prefer the Unsloth variant over the upstream org's repo. The `get_optimal_for_m4(model_key)` helper function SHALL return the `unsloth_id` when it exists and the model fits in M4 Max 48 GB; otherwise it SHALL fall back to `mlx_id`, then `upstream_id`.

#### Scenario: M4 Max 48 GB prefers Unsloth GGUF

- **GIVEN** the registry has `gemma-4-26B-A4B` with `unsloth_id="unsloth/gemma-4-26B-A4B-it-GGUF"` (~14 GB)
- **WHEN** `get_optimal_for_m4("gemma-4-26B-A4B")` is called
- **THEN** the helper MUST return `"unsloth/gemma-4-26B-A4B-it-GGUF"`
- **AND** it MUST NOT return the upstream `google/gemma-4-26B-A4B-it` unless the Unsloth variant is missing

### Requirement: 3-tier OCR ladder (heavy / medium / light)

The system SHALL expose a 3-tier OCR ladder via the registry:

- **Tier 1 (heavy, arm1-oci only):** `qwen3-vl-235b-a22b` (~130 GB), `qwen3.6-35b-a3b-mtp` (~22 GB)
- **Tier 2 (medium, M4 Max 48 GB):** `gemma-4-26B-A4B` (14 GB, the M4 default), `qwen3-vl-8b` (5 GB), `gemma-3-4b` (16 GB), `internvl3-8b` (5 GB)
- **Tier 3 (light, mobile / iPad):** `gemma-4-E2B` (3 GB), `qwen3-vl-4b` (3 GB), `glm-4.6v-flash` (6 GB)

#### Scenario: A developer queries the M4 default

- **GIVEN** the registry is loaded
- **WHEN** a developer calls `get_default_for_m4_max()`
- **THEN** the function MUST return `gemma-4-26B-A4B`
- **AND** the returned `OCRModel` MUST have `role="tier2_medium"` and `m4_max_48gb_fit=True`

### Requirement: New DIAGRAM capability for figure detection

The system SHALL add a new `ModelCapability.DIAGRAM = "diagram"` enum value to `ModelBackend` (in `cianfhoghlaim/ocr/models/registry.py`). This capability indicates the model can detect, point to, or extract figure regions in PDF documents (e.g. chemistry diagrams, biology specimens, geography maps). Models tagged with `DIAGRAM` MUST be used by the 6-stage PDF processing pipeline in `oideachais-pdf-processing`.

#### Scenario: A chemistry diagram is extracted

- **GIVEN** a 2024 LC Chemistry paper page 7 with 6 organic-chemistry diagrams
- **WHEN** Stage 2 (diagram detection) of the PDF processing pipeline runs
- **THEN** it MUST dispatch to a model with `ModelCapability.DIAGRAM` (e.g. `granite-docling-258M` or `molmo2-8b`)
- **AND** the 6 diagram bounding boxes MUST be stored in `page_diagrams` table

## MODIFIED Requirements

### Requirement: 10-model 6-backend OCR registry (legacy alias)

The system SHALL preserve the legacy 10-entry `OCR_MODELS` dict at `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py:OCR_MODELS` for backward compatibility, with a deprecation warning logged on import. The new canonical registry is at `cianfhoghlaim/ocr/models/registry.py:VISION_MODELS` (24+ entries per ADDED Requirement above).

#### Scenario: Legacy code still works

- **GIVEN** an old import `from ocr import OCR_MODELS` from `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/__init__.py`
- **WHEN** the legacy module is imported
- **THEN** a `DeprecationWarning` SHALL be logged
- **AND** `OCR_MODELS` SHALL still be importable with the old keys
- **AND** each old key SHALL map to the new VISION_MODELS entry

## REMOVED Requirements

### Requirement: 6 VLM_MODELS dict at vlm_finetune_comparison.py

**Reason:** The 6-entry `VLM_MODELS` dict at `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/vlm_finetune_comparison.py:55` is replaced by the 24+ entry `VISION_MODELS` at the v4 location. The 3 wrong model_id renames in commit `33500d3` (qwen3-vl-7b→qwen2.5-vl-7b, qwen3-vl-30b→qwen2.5-vl-72b, glm-4.6v-flash→glm-4v-9b) are reverted to the real Unsloth IDs verified on 2026-06-29.

**Migration:** Old `vlm_finetune_comparison.py` is moved to `cianfhoghlaim/ocr/models/_previous_versions/vlm_finetune_comparison-v3-legacy.py`; the new `vlm_finetune_comparison.py` re-exports the corrected dict from the v4 registry.
