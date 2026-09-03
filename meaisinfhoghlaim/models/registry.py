"""
OCR / VLM Model Registry (v4 canonical home, post-2026-06-28 consolidation).

This is the **canonical** OCR/VLM model registry for the Cianfhoghlaim
platform. Every OCR/VLM call in the lakehouse routes through here. Per
the v4 platform spec (`openspec/specs/meaisinfhoghlaim-platform/spec.md`
line 685), the canonical home for the registry is
`cianfhoghlaim/meaisinfhoghlaim/models/registry.py`.

History:
- Pre-v4: `sruth/oideachais/_oideachais_src/vlm_finetune_comparison.py` (current: `meaisinfhoghlaim/training/training/unsloth_trainer.py`)
  (the legacy single `VLM_MODELS` dict) +
  `sruth/oideachais/_meaisinfhoghlaim_src/model_registry.py` (current: `meaisinfhoghlaim/models/registry.py:VISION_MODELS`) (the
  separate `OCR_MODELS` dict).
- 2026-06-28 (v4 consolidation): the two dicts were collapsed into a
  single 20-entry `VISION_MODELS` at
  `cianfhoghlaim/meaisinfhoghlaim/models/registry.py` and the
  `_meaisinfhoghlaim_src` directory was removed.
- 2026-07-08 (this change — `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority`):
  the canonical home was moved to `cianfhoghlaim/meaisinfhoghlaim/ocr/models/registry.py`
  and the outer `meaisinfhoghlaim/models/` became a back-compat shim.
- 2026-07-12 (this change — the post-compaction consolidation):
  the canonical home moves BACK to `cianfhoghlaim/meaisinfhoghlaim/models/registry.py`
  (the outer `models/` directory per the v4 platform convention). The inner
  `cianfhoghlaim/meaisinfhoghlaim/ocr/models/registry.py` is now a back-compat
  re-export shim that emits a DeprecationWarning on import.

Key design points:
- 20-entry `VISION_MODELS` dict (Unsloth-first fallback chain:
  `unsloth_id` → `mlx_id` → `upstream_id`). 22 unique keys after the
  `gemma-4-E2B` MLX + LLAMASWAP twins are counted separately.
- No cloud-API models (no OpenAI, no Anthropic) per the 2026-06-29 audit.
- New `ModelCapability.DIAGRAM` enum value for figure detection
  (used by the 6-stage PDF processing pipeline).
- New `role: Literal["tier1_heavy", "tier2_medium", "tier3_light",
  "specialist", "legacy"]` field for the 3-tier ladder.
- New `unsloth_features: list[str]` field for Dynamic 2.0 GGUFs,
  MTP speculative decoding, MoE 12x, imatrix.
- 6-entry `CLASSICAL_OCR` Docker registry (Pylaia, TrOCR, PaddleOCR,
  Tesseract, dots-ocr, VLM).
- 3-entry `TEXT_MODELS` dict for the agent fleet (Qwen 3.6 27B MTP +
  UCCIX-Mistral-24B + UCCIX-Llama-3.1-8B).

All 22 unique model_ids were verified live on HuggingFace Hub via the
HF MCP tools on 2026-06-29. See the full audit at
`openspec/research/2026-06-29-ocr-vlm-registry-audit/kcg-ocr-vlm-registry.md`.

Usage:
    from cianfhoghlaim.ocr.models.registry import (
        VISION_MODELS, get_optimal_for_m4, select_ocr_backend,
        ClassicalOCRStack, all_classical_stacks, all_models,
    )

    # List all vision models
    for key, model in VISION_MODELS.items():
        print(f"{key}: {model.unsloth_id or model.upstream_id}")

    # Get the M4 default
    model = VISION_MODELS[select_optimal_for_m4_max()]

    # Pick a model for a given PDF
    from pathlib import Path
    selection = select_ocr_backend(Path("syllabus.pdf"))

    # Iterate all vision models + all classical stacks for the eval harness
    for model in all_models():
        ...
    for stack in all_classical_stacks():
        ...
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

# No DeprecationWarning is emitted at the v4 canonical home
# (`cianfhoghlaim.ocr.models.registry`). The legacy
# `cianfhoghlaim.meaisinfhoghlaim.models` shim (and the deeper
# `cianfhoghlaim.ocr._meaisinfhoghlaim_src.model_registry` legacy
# path) is the only place that emits a DeprecationWarning.


# ─── Enums ───────────────────────────────────────────────────────────────────


class ModelBackend(str, Enum):
    """Supported model backends.

    Note: the v4 registry has DROPPED `OPENAI` and `ANTHROPIC` from
    the canonical backend list. The v5 (BIEP v2) registry extends the
    backend list from 4 to **6** by adding `DOCLING` (the IBM Docling
    HTTP REST API at :5001) and `UNSTRACT` (the Unstract REST API at
    :8000). All 26 entries have at least one local-or-rest inference
    path (Unsloth GGUF, mlx-community, IBM Docling, Unstract workflow,
    or upstream safetensors on M4 Max 48 GB / arm1-oci).

    Reference: openspec/changes/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/

    Reference: openspec/changes/2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1/
    (adds `UNSLOTH` for the 20 new catalog entries served via the
    Unsloth Studio headless endpoint — see `bonneagar/stacks/unsloth-serve/`).
    """

    LITELLM = "litellm"
    MLX = "mlx"
    TRANSFORMERS = "transformers"
    LLAMASWAP = "llama-swap"  # NEW in v4 — Unsloth GGUFs served via llama-swap
    DOCLING = "docling"        # NEW in v5 (BIEP v2) — IBM Docling HTTP REST API
    UNSTRACT = "unstract"      # NEW in v5 (BIEP v2) — Unstract Prompt Studio workflow
    UNSLOTH = "unsloth"        # NEW in v6 (Unsloth v5 integration) — Unsloth Studio :8889 OpenAI/Anthropic endpoint


class ModelCapability(str, Enum):
    """Model capabilities.

    `DIAGRAM` is NEW in v4 (added 2026-06-29) for the 6-stage PDF
    processing pipeline's figure detection / captioning tasks.

    `UNISTRUCT_WORKFLOW` + `DOCLING_LAYOUT` are NEW in v5 (BIEP v2)
    for the per-path OCR/VLM ensemble (Change 3).

    Reference: openspec/changes/2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/
    """

    DENSE_OCR = "dense_ocr"
    GROUNDING = "grounding"
    TABLES = "tables"
    LATEX = "latex"
    REASONING = "reasoning"
    MATH = "math"
    MULTILINGUAL = "multilingual"
    GAELIC = "gaelic"
    DIAGRAM = "diagram"  # NEW in v4
    DOCLING_LAYOUT = "docling_layout"     # NEW in v5 — IBM Docling DocTags XML
    UNISTRUCT_WORKFLOW = "unstract_workflow"  # NEW in v5 — Unstract Prompt Studio workflow


# Back-compat aliases for legacy code
MODEL_BACKEND = ModelBackend
MODEL_CAPABILITY = ModelCapability


ModelRole = Literal["tier1_heavy", "tier2_medium", "tier3_light", "specialist", "legacy"]


# ─── Dataclass ───────────────────────────────────────────────────────────────


@dataclass
class OCRModel:
    """OCR model configuration (v4 schema).

    New in v4 (vs the legacy OCRModel):
    - `unsloth_id`: the preferred Unsloth GGUF / bnb-4bit HF ID
    - `mlx_id`: the Apple-Silicon MLX HF ID
    - `upstream_id`: the canonical upstream org HF ID
    - `unsloth_features`: list of Unsloth-specific features
      (subset of `["dynamic_2_0_gguf", "mtp_speculative", "moe_12x",
      "imatrix", "fast_inference"]`)
    - `role`: tier classification for the 3-tier ladder
    - `m4_max_48gb_fit`: True if the model fits in 48 GB unified memory
    - `arm1_oci_required`: True if the model only runs on arm1-oci
    - `available`: False for known-broken or legacy entries
    """

    # Identity
    key: str
    name: str

    # Inference IDs (Unsloth-first fallback chain)
    unsloth_id: str | None = None
    mlx_id: str | None = None
    upstream_id: str = ""

    # Backend + capabilities
    backend: ModelBackend = ModelBackend.LLAMASWAP
    capabilities: list[ModelCapability] = field(default_factory=list)

    # v4 metadata
    unsloth_features: list[str] = field(default_factory=list)
    role: ModelRole = "specialist"
    m4_max_48gb_fit: bool = True
    arm1_oci_required: bool = False
    available: bool = True

    # Operational metadata
    max_resolution: tuple[int, int] = (1280, 1280)
    notes: str = ""

    # Runtime state (private)
    _client: Any = field(default=None, repr=False)

    @property
    def model_id(self) -> str:
        """The canonical model_id for backward compatibility.

        Prefers `unsloth_id`, then `mlx_id`, then `upstream_id`.
        """
        return self.unsloth_id or self.mlx_id or self.upstream_id

    def get_optimal_id(self) -> str:
        """Return the optimal HF ID for the M4 Max 48 GB target."""
        return get_optimal_for_m4_id(self)


# ─── Vision Models (24 entries, Unsloth-first) ──────────────────────────────


VISION_MODELS: dict[str, OCRModel] = {
    # ─── Gemma 4 (Google, Mar/Jun 2026) — TIER-1 default family ───
    "gemma-4-E2B": OCRModel(
        key="gemma-4-E2B",
        name="Gemma 4 E2B (edge)",
        unsloth_id="unsloth/gemma-4-E2B-it-GGUF",
        mlx_id="mlx-community/gemma-4-e2b-it-4bit",
        upstream_id="google/gemma-4-E2B-it",
        backend=ModelBackend.MLX,
        capabilities=[
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.DENSE_OCR,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="tier3_light",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1024, 1024),
        notes="5.1B, 3GB, 6 Celtic languages. Edge / Tuatha in-game. Released 2026-06-03.",
    ),
    "gemma-4-E4B": OCRModel(
        key="gemma-4-E4B",
        name="Gemma 4 E4B (browser)",
        unsloth_id="unsloth/gemma-4-E4B-it-GGUF",
        mlx_id=None,  # GAP
        upstream_id="google/gemma-4-E4B-it",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.DENSE_OCR,
            ModelCapability.REASONING,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="tier3_light",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1024, 1024),
        notes="8B, 5GB, 6 Celtic languages. Best mid-size VLM.",
    ),
    "gemma-4-12B": OCRModel(
        key="gemma-4-12B",
        name="Gemma 4 12B Unified",
        unsloth_id="unsloth/gemma-4-12b-it-GGUF",
        mlx_id="mlx-community/gemma-4-12B-it-8bit",
        upstream_id="google/gemma-4-12B-it",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.DENSE_OCR,
            ModelCapability.REASONING,
            ModelCapability.LATEX,
            ModelCapability.MATH,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="tier2_medium",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="12B, 7GB, gemma4_unified arch. Crosses the 'thinking' threshold.",
    ),
    "gemma-4-26B-A4B": OCRModel(
        key="gemma-4-26B-A4B",
        name="Gemma 4 26B-A4B MoE (M4 default)",
        unsloth_id="unsloth/gemma-4-26B-A4B-it-GGUF",
        mlx_id="mlx-community/gemma-4-26b-a4b-it-4bit",
        upstream_id="google/gemma-4-26B-A4B-it",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.DENSE_OCR,
            ModelCapability.REASONING,
            ModelCapability.LATEX,
            ModelCapability.MATH,
            ModelCapability.DIAGRAM,
            ModelCapability.TABLES,
        ],
        unsloth_features=["moe_12x", "fast_inference", "imatrix"],
        role="tier2_medium",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="26.5B MoE / 4B active, 14GB. **M4 Max default**. 30.5M downloads. **Diagram-aware for PDF processing**.",
     ),
    # ─── GLM-4.6V Flash (zai-org, Dec 2025) — fast / low-cost ───
    "glm-4.6v-flash": OCRModel(
        key="glm-4.6v-flash",
        name="GLM-4.6V Flash (Z.ai)",
        unsloth_id="unsloth/GLM-4.6V-Flash-GGUF",
        mlx_id="mlx-community/GLM-4.6V-Flash-4bit",
        upstream_id="zai-org/GLM-4.6V-Flash",
        backend=ModelBackend.MLX,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="tier2_medium",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="10.3B, 6GB, 128k context. Fast / low-cost. 746K downloads. **Diagram-aware** for marking-scheme figures.",
    ),
    # ─── Qwen 3-VL (Alibaba, Oct 2025) — PRIMARY WORKHORSE ───
    "qwen3-vl-4b": OCRModel(
        key="qwen3-vl-4b",
        name="Qwen 3-VL 4B (mobile)",
        unsloth_id="unsloth/Qwen3-VL-4B-Instruct-GGUF",
        mlx_id="mlx-community/Qwen3-VL-4B-Instruct-8bit",
        upstream_id="Qwen/Qwen3-VL-4B-Instruct",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.TABLES,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="tier3_light",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="4.4B, 3GB, 119 languages (Irish explicit), 256K context. Sweet spot for mobile.",
    ),
    "qwen3-vl-8b": OCRModel(
        key="qwen3-vl-8b",
        name="Qwen 3-VL 8B (workhorse)",
        unsloth_id="unsloth/Qwen3-VL-8B-Instruct-GGUF",
        mlx_id="mlx-community/Qwen3-VL-8B-Instruct-4bit",
        upstream_id="Qwen/Qwen3-VL-8B-Instruct",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
            ModelCapability.MATH,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="tier2_medium",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="8.8B, 5GB, 256K context, 256-token frame absorption. **Workhorse for syllabus/past-paper PDF processing**. 39M downloads.",
    ),
    "qwen3-vl-30b-a3b": OCRModel(
        key="qwen3-vl-30b-a3b",
        name="Qwen 3-VL 30B-A3B MoE (Modal burst)",
        unsloth_id="unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF",
        mlx_id="mlx-community/Qwen3-VL-30B-A3B-Instruct-4bit",
        upstream_id="Qwen/Qwen3-VL-30B-A3B-Instruct",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
            ModelCapability.MATH,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=["moe_12x", "fast_inference", "imatrix"],
        role="tier1_heavy",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="31.1B MoE / 3B active, 18GB. Modal A100 burst for full-year exam corpora. 16.1M downloads.",
    ),
    # ─── Qwen 3.6 (Alibaba, Apr 2026) — MTP speculative decoding ───
    "qwen3.6-27b-mtp": OCRModel(
        key="qwen3.6-27b-mtp",
        name="Qwen 3.6 27B MTP",
        unsloth_id="unsloth/Qwen3.6-27B-MTP-GGUF",
        mlx_id="unsloth/Qwen3.6-27B-UD-MLX-4bit",
        upstream_id="Qwen/Qwen3.6-27B",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.MATH,
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
        ],
        unsloth_features=["mtp_speculative", "fast_inference", "imatrix"],
        role="tier1_heavy",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="27.8B dense, ~16GB, **MTP speculative decoding**. Text-only but used for marking-scheme text post-processing. 1.8M downloads.",
    ),
    # ─── DeepSeek-OCR-2 (Feb 2026) — specialist OCR ───
    "deepseek-ocr-2": OCRModel(
        key="deepseek-ocr-2",
        name="DeepSeek-OCR-2 (compressed-doc specialist)",
        unsloth_id="unsloth/DeepSeek-OCR-2",
        mlx_id="mlx-community/DeepSeek-OCR-bf16",
        upstream_id="deepseek-ai/DeepSeek-OCR-2",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.MATH,
            ModelCapability.TABLES,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1024, 1024),
        notes="3.4B, deepseek_vl_v2 arch. Compressed-document specialist. 9.4M downloads. **Used for formula OCR in marking schemes**.",
    ),
    # ─── olmOCR-2-7B-1025 (Oct 2025) — allenai specialist ───
    "olmocr-2-7b-1025": OCRModel(
        key="olmocr-2-7b-1025",
        name="olmOCR-2-7B-1025 (allenai specialist)",
        unsloth_id=None,
        mlx_id=None,
        upstream_id="allenai/olmOCR-2-7B-1025",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
            ModelCapability.MATH,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="8.3B, base=Qwen2.5-VL-7B-Instruct. allenai specialist. 1.1M downloads.",
    ),
    # ─── Granite-Docling (Sep 2025) — tiny doc-structure specialist ───
    "granite-docling-258M": OCRModel(
        key="granite-docling-258M",
        name="Granite-Docling 258M (DocTags)",
        unsloth_id=None,
        mlx_id="ibm-granite/granite-docling-258M-mlx",
        upstream_id="ibm-granite/granite-docling-258M",
        backend=ModelBackend.MLX,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1024, 1024),
        notes="258M, idefics3 arch. Tiny — fits on phone. 2.0M downloads. **DocTags = figure/table/heading detection** for syllabus chunking.",
    ),
    # ─── UCCIX — Irish-language model (Nov 2025) ───
    "uccix-mistral-24b": OCRModel(
        key="uccix-mistral-24b",
        name="UCCIX-Mistral-24B (modern Irish-language path)",
        unsloth_id=None,  # GAP — request from Unsloth
        mlx_id=None,
        upstream_id="ReliableAI/UCCIX-Mistral-24B",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.GAELIC,
            ModelCapability.MULTILINGUAL,
            ModelCapability.REASONING,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="24.1B, mistral3 arch, en+ga. **Modern Irish-language path**. Nov 2025.",
    ),
    "uccix-llama-3.1-8b": OCRModel(
        key="uccix-llama-3.1-8b",
        name="UCCIX-Llama-3.1-8B (smaller Irish alt)",
        unsloth_id=None,
        mlx_id=None,
        upstream_id="ReliableAI/UCCIX-Llama-3.1-8B",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.GAELIC,
            ModelCapability.MULTILINGUAL,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="8B, Llama 3.1. Smaller alt. Mar 2025.",
    ),
    "uccix-llama2-13b": OCRModel(
        key="uccix-llama2-13b",
        name="UCCIX-Llama2-13B (DEPRECATED)",
        unsloth_id=None,
        mlx_id=None,
        upstream_id="ReliableAI/UCCIX-Llama2-13B-Instruct",
        backend=ModelBackend.LITELLM,
        capabilities=[
            ModelCapability.GAELIC,
            ModelCapability.MULTILINGUAL,
        ],
        unsloth_features=[],
        role="legacy",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=False,  # DEPRECATED — Llama 2
        max_resolution=(1024, 1024),
        notes="13.1B, Llama 2 (DEPRECATED). Gated. Use Mistral-24B or Llama-3.1-8B.",
    ),
    # ─── Dots-OCR (Oct 2025) — layout specialist ───
    "dots-ocr": OCRModel(
        key="dots-ocr",
        name="Dots-OCR (layout specialist)",
        unsloth_id=None,
        mlx_id="mlx-community/dots.ocr-4bit",
        upstream_id="rednote-hilab/dots.ocr",
        backend=ModelBackend.MLX,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
            ModelCapability.MULTILINGUAL,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="3.0B, dots_ocr arch. Layout specialist. 5.2M downloads. **Detects figure regions in past papers**.",
    ),
    # ─── PaddleOCR-VL (Jun 2026) — multilingual OCR specialist ───
    "paddleocr-vl-1.6": OCRModel(
        key="paddleocr-vl-1.6",
        name="PaddleOCR-VL 1.6 (multilingual)",
        unsloth_id=None,
        mlx_id=None,
        upstream_id="PaddlePaddle/PaddleOCR-VL-1.6-GGUF",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.MULTILINGUAL,
            ModelCapability.TABLES,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1024, 1024),
        notes="958.6M, paddleocr_vl arch, ERNIE 4.5 0.3B base. First-party GGUF. 611K downloads. **Multilingual syllabus fallback**.",
    ),
    # ─── Molmo2 (Jan 2026) — document VQA specialist ───
    "molmo2-4b": OCRModel(
        key="molmo2-4b",
        name="Molmo2 4B (document VQA)",
        unsloth_id=None,
        mlx_id=None,
        upstream_id="allenai/Molmo2-4B",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="4.9B, molmo2 arch. Document VQA + diagram pointing. 261K downloads.",
    ),
    "molmo2-8b": OCRModel(
        key="molmo2-8b",
        name="Molmo2 8B (top workhorse for syllabus diagrams)",
        unsloth_id=None,
        mlx_id=None,
        upstream_id="allenai/Molmo2-8B",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="8.7B, molmo2 arch, base=Qwen3-8B. **Top workhorse for syllabus diagram pointing**. 2.7M downloads.",
    ),
    # ─── InternVL3_5-8B (Aug 2025) — document understanding specialist ───
    "internvl3-8b": OCRModel(
        key="internvl3-8b",
        name="InternVL3_5-8B (document understanding)",
        unsloth_id="unsloth/InternVL3-8B-GGUF",
        mlx_id=None,
        upstream_id="OpenGVLab/InternVL3_5-8B",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
            ModelCapability.TABLES,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="tier2_medium",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="8.5B, internvl_chat arch. 688K downloads. **2D layout understanding for marking-scheme diagrams**.",
    ),
    # ─── Llama 3.2 Vision (Dec 2024) — legacy ───
    "llama-3.2-vision-11b": OCRModel(
        key="llama-3.2-vision-11b",
        name="Llama 3.2 Vision 11B (legacy)",
        unsloth_id="unsloth/Llama-3.2-11B-Vision-Instruct-unsloth-bnb-4bit",
        mlx_id=None,
        upstream_id="meta-llama/Llama-3.2-11B-Vision-Instruct",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.REASONING,
        ],
        unsloth_features=["dynamic_2_0_gguf", "fast_inference"],
        role="legacy",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1120, 1120),
        notes="10.7B, mllama arch, gated. Legacy — prefer Qwen 3VL 8B.",
    ),
    # ─── Gemma 3 (Mar 2025) — legacy, kept for back-compat ───
    "gemma-3-4b": OCRModel(
        key="gemma-3-4b",
        name="Gemma 3 4B (legacy Celtic)",
        unsloth_id="unsloth/gemma-3-4b-it-GGUF",
        mlx_id=None,
        upstream_id="google/gemma-3-4b-it",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="legacy",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="4B. 6 Celtic languages. Legacy — prefer Gemma 4 E4B.",
    ),

    # ─── v6 (Unsloth v5 integration) — added 2026-08-21 ───
    # 4 new ocr_vision entries from the Unsloth catalog (per the 2026-08-21
    # openspec change). All served via the unsloth-serve stack at :8889
    # (Unsloth Studio headless OpenAI/Anthropic-compatible endpoint).
    "qwen3-vl-8b-instruct": OCRModel(
        key="qwen3-vl-8b-instruct",
        name="Qwen 3-VL 8B Instruct (Unsloth Studio, replacement)",
        unsloth_id="unsloth/Qwen3-VL-8B-Instruct-GGUF",
        mlx_id=None,
        upstream_id="Qwen/Qwen3-VL-8B-Instruct",
        backend=ModelBackend.UNSLOTH,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.TABLES,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
        ],
        unsloth_features=["dynamic_3_0_gguf", "fast_inference", "imatrix"],
        role="tier2_medium",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="8B Instruct, Qwen3-VL arch. Served via unsloth-serve. 256K context (extends to 1M). Replaces qwen3-vl-8b via llama-swap as the v6 default.",
    ),
    "qwen3-vl-32b-instruct": OCRModel(
        key="qwen3-vl-32b-instruct",
        name="Qwen 3-VL 32B Instruct (Unsloth Studio, strong)",
        unsloth_id="unsloth/Qwen3-VL-32B-Instruct-GGUF",
        mlx_id=None,
        upstream_id="Qwen/Qwen3-VL-32B-Instruct",
        backend=ModelBackend.UNSLOTH,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
        ],
        unsloth_features=["dynamic_3_0_gguf", "fast_inference", "imatrix"],
        role="tier1_heavy",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="32B dense Instruct, Qwen3-VL arch. Strong tier. 256K context. Unsloth Dynamic 3.0 GGUF.",
    ),
    "glm-4.6v-flash": OCRModel(
        key="glm-4.6v-flash",
        name="GLM-4.6V-Flash (Unsloth Studio, fast)",
        unsloth_id="unsloth/GLM-4.6V-Flash-GGUF",
        mlx_id=None,
        upstream_id="zai-org/GLM-4.6V-Flash",
        backend=ModelBackend.UNSLOTH,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.MULTILINGUAL,
            ModelCapability.TABLES,
        ],
        unsloth_features=["fast_inference", "imatrix"],
        role="tier3_light",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(1280, 1280),
        notes="GLM-4.6V-Flash (zai-org, Dec 2025). Fast / low-cost VLM. Served via unsloth-serve.",
    ),
    "deepseek-ocr-2": OCRModel(
        key="deepseek-ocr-2",
        name="DeepSeek-OCR 2 (Unsloth Studio, OCR specialist)",
        unsloth_id="unsloth/DeepSeek-OCR-2-GGUF",
        mlx_id=None,
        upstream_id="deepseek-ai/DeepSeek-OCR-2",
        backend=ModelBackend.UNSLOTH,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.DIAGRAM,
            ModelCapability.TABLES,
        ],
        unsloth_features=["dynamic_3_0_gguf", "fast_inference", "imatrix"],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="DeepSeek-OCR 2 (deepseek-ai, 2026). Layout specialist with grounding. Served via unsloth-serve.",
    ),

    # ─── v5 (BIEP v2) — Unstract API + Docling HTTP API (added 2026-07-22) ───
    "unstract-api": OCRModel(
        key="unstract-api",
        name="Unstract REST API (Prompt Studio workflow)",
        unsloth_id=None,
        mlx_id=None,
        upstream_id="unstract/api:v0.177.7",   # The Unstract backend HTTP API
        backend=ModelBackend.UNSTRACT,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
            ModelCapability.MULTILINGUAL,
            ModelCapability.UNISTRUCT_WORKFLOW,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes=(
            "v5 NEW: Unstract Prompt Studio workflow via the Unstract HTTP API "
            "at :8000. Path 2 of the BIEP v2 4-path ensemble. Non-engineers author "
            "extraction prompts in Prompt Studio; the BAML `Unstract` client "
            "calls this endpoint per the `ensembled_extraction.baml` input contract."
        ),
    ),
    "docling-serve": OCRModel(
        key="docling-serve",
        name="IBM Docling HTTP REST API (DocTags XML)",
        unsloth_id=None,
        mlx_id=None,
        upstream_id="ghcr.io/ds4sd/docling-serve:v0.4.0",  # The Docling HTTP API image
        backend=ModelBackend.DOCLING,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
            ModelCapability.DIAGRAM,
            ModelCapability.DOCLING_LAYOUT,
        ],
        unsloth_features=[],
        role="specialist",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes=(
            "v5 NEW: IBM Docling 258M DocTags XML layout specialist via the "
            "docling-serve HTTP REST API at :5001. The 'safety net' first "
            "stage of the BIEP v2 4-path ensemble. Returns structured "
            "DocTags XML preserving tables / figures / equations."
        ),
    ),
}
# Total: 26 entries (24 v4 + 2 v5 BIEP v2 entrants)
# Verified live on HF Hub 2026-06-29 for the original 24; the 2 v5
# entries (unstract-api, docling-serve) are the Unstract + Docling HTTP
# APIs from the bonneagar stacks (no HF model ID).


# ─── Classical OCR (Docker compose stacks) ──────────────────────────────────


CLASSICAL_OCR: dict[str, dict[str, Any]] = {
    "docling-serve": {
        "stack": "bonneagar/stacks/ocr-classical/docling-serve/",
        "image": "docker.io/ds4sd/docling-serve:latest",
        "port": 5001,
        "notes": "IBM Docling — 258M params, DocTags layout. The 'safety net' when VLM extraction fails.",
    },
    "paddleocr": {
        "stack": "bonneagar/stacks/ocr-classical/paddleocr/",
        "image": "docker.io/paddlepaddle/paddleocr:latest",
        "port": 8888,
        "notes": "PaddlePaddle OCR — multilingual, first-party GGUF.",
    },
    "tesseract": {
        "stack": "bonneagar/stacks/ocr-classical/tesseract/",
        "image": "docker.io/tesseractshadow/tesseract4re:latest",
        "port": 8889,
        "notes": "Tesseract 4 — clean printed-text baseline.",
    },
    "tesseract-shadow": {
        "stack": "bonneagar/stacks/ocr-classical/tesseract-shadow/",
        "image": "docker.io/tesseractshadow/tesseract4re:latest-shadow",
        "port": 8890,
        "notes": "Tesseract 4 shadow variant — second independent tesseract deployment for A/B comparison + drift detection.",
    },
    "unstract": {
        "stack": "bonneagar/stacks/ocr-classical/unstract/",
        "image": "docker.io/unstract/api:latest",
        "port": 8002,
        "notes": "Unstract — no-code LLM-powered document extraction (prompts-based). Best for unstructured PDFs and schema-driven extraction.",
    },
    "dots-ocr": {
        "stack": "bonneagar/stacks/ocr-classical/dots-ocr/",
        "image": "docker.io/rednote-hilab/dots.ocr-serve:latest",
        "port": 8001,
        "notes": "rednote-hilab Dots-OCR — 3.0B layout specialist (vs the VLM `dots-ocr` key).",
    },
}
# Total: 6 classical OCR stacks (the canonical user-cited 6 backends:
# docling-serve + paddleocr + dots-ocr + unstract + tesseract + tesseract-shadow).
# Replaces the legacy 6 (which included olmocr + pylaia). Pylaia remains
# available as a Dúchas HTR specialist via the `tuatha_root_agent`
# (see `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` for the canonical
# stack list and migration notes).


# ─── Text-only Models (for the agent fleet) ────────────────────────────────


TEXT_MODELS: dict[str, OCRModel] = {
    "qwen3.6-27b-mtp": VISION_MODELS["qwen3.6-27b-mtp"],
    "uccix-mistral-24b": VISION_MODELS["uccix-mistral-24b"],
    "uccix-llama-3.1-8b": VISION_MODELS["uccix-llama-3.1-8b"],
}
# 3 text-only entries (the Qwen 3.6 27B + UCCIX models — qwen3.6-35b-a3b-mtp removed: marginal on M4 48GB)


# ─── Registry helpers ───────────────────────────────────────────────────────


class ModelRegistry:
    """Registry for managing OCR models (v4)."""

    def __init__(self, custom_models: dict[str, OCRModel] | None = None):
        """Initialize registry.

        Args:
            custom_models: Additional models to register (overrides the
                v4 VISION_MODELS dict on a per-key basis)
        """
        self.models: dict[str, OCRModel] = dict(VISION_MODELS)
        if custom_models:
            self.models.update(custom_models)

    def list_models(self) -> list[OCRModel]:
        """List all registered models."""
        return list(self.models.values())

    def get_model(self, name: str) -> OCRModel:
        """Get model by key (e.g. 'qwen3-vl-8b')."""
        if name not in self.models:
            raise ValueError(
                f"Model '{name}' not found. Available: {sorted(self.models.keys())}"
            )
        return self.models[name]

    def register_model(self, name: str, model: OCRModel) -> None:
        """Register a new model."""
        self.models[name] = model

    def get_models_with_capability(self, capability: ModelCapability) -> list[OCRModel]:
        """Get models with a specific capability (e.g. DIAGRAM)."""
        return [m for m in self.models.values() if capability in m.capabilities]

    def get_local_models(self) -> list[OCRModel]:
        """Get models that run locally (no cloud API)."""
        return [m for m in self.models.values() if (m.available and m.arm1_oci_required is False) or m.m4_max_48gb_fit]

    def get_legacy_models(self) -> list[OCRModel]:
        """Get legacy / deprecated models."""
        return [m for m in self.models.values() if not m.available or m.role == "legacy"]


def get_optimal_for_m4_id(model: OCRModel) -> str:
    """Return the optimal HF ID for the M4 Max 48 GB target.

    Priority: unsloth_id > mlx_id > upstream_id.
    Falls back to upstream if neither Unsloth nor MLX is available.
    """
    if model.m4_max_48gb_fit and model.unsloth_id:
        return model.unsloth_id
    if model.mlx_id:
        return model.mlx_id
    return model.upstream_id


def get_optimal_for_m4(model_key: str) -> str:
    """Convenience wrapper: get the optimal HF ID for a model by key."""
    if model_key not in VISION_MODELS:
        raise KeyError(
            f"Model '{model_key}' not in VISION_MODELS. "
            f"Available: {sorted(VISION_MODELS.keys())}"
        )
    return get_optimal_for_m4_id(VISION_MODELS[model_key])


def select_optimal_for_m4_max() -> str:
    """Return the optimal default model key for the M4 Max 48 GB target.

    Per the v4 spec, the default is `gemma-4-26B-A4B` (MoE, 14GB, 4B active,
    the sweet spot for M4 Max 48 GB unified memory).

    This is the canonical helper used by the 8 NCCA subject agents
    (`agents/tuatha/<slug>_agent.py`) and the ADK `root_agent`
    (`cianfhoghlaim/agents/adk/root_agent.py`). The legacy name
    `get_default_for_m4_max()` is preserved as a deprecated back-compat
    alias (see below).
    """
    return "gemma-4-26B-A4B"


def get_default_for_m4_max() -> str:
    """Deprecated back-compat alias for `select_optimal_for_m4_max()`.

    Use `select_optimal_for_m4_max()` instead. This alias will be removed
    in v5 of the registry.
    """
    import warnings

    warnings.warn(
        "get_default_for_m4_max() is deprecated; use select_optimal_for_m4_max() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return select_optimal_for_m4_max()


@dataclass
class OCRAwareSelection:
    """A (model, backend) pair selected for a given document."""

    model: OCRModel
    reason: str


def select_ocr_backend(
    document_path: Path,
    page_count: int | None = None,
    image_density: float | None = None,
) -> OCRAwareSelection:
    """Pick the best (model, backend) pair for a document.

    Heuristic (extended in v4):
    - Small text-first PDFs (<5 MB) → `gemma-4-E2B` (MLX, fast)
    - Dense syllabi (5–20 MB) → `gemma-4-26B-A4B` (llama-swap, MoE)
    - SEC exam papers (image-heavy) → `qwen3-vl-8b` (llama-swap)
    - Old scanned Gaelic texts (pre-1922) → `glm-4.6v-flash` (MLX)
    - Marking-scheme image-heavy → `molmo2-8b` (transformers)
    - New: page count >10 → prefer `qwen3-vl-8b`
    - New: high image density → `molmo2-8b` (for diagram pointing)
    """
    size_mb = document_path.stat().st_size / (1024 * 1024)
    name = document_path.name.lower()

    # Marking-scheme image-heavy: Molmo2-8B
    if "marking" in name or "scheme" in name or (
        image_density is not None and image_density > 0.5
    ):
        return OCRAwareSelection(
            VISION_MODELS["molmo2-8b"],
            "Marking scheme / high image density → Molmo2-8B (transformers)",
        )

    # SEC exam papers: image-heavy
    if "sec" in name or "examination" in name or "leaving_cert" in str(document_path):
        return OCRAwareSelection(
            VISION_MODELS["qwen3-vl-8b"],
            "SEC exam paper → Qwen 3-VL 8B (llama-swap)",
        )

    # Pre-1922 scanned Gaelic manuscripts
    if any(year in name for year in ("1900", "1910", "1920", "1922")):
        return OCRAwareSelection(
            VISION_MODELS["glm-4.6v-flash"],
            "Pre-1922 manuscript → GLM-4.6V Flash (MLX)",
        )

    # Multi-page > 10 pages: prefer Qwen 3-VL 8B
    if page_count is not None and page_count > 10:
        return OCRAwareSelection(
            VISION_MODELS["qwen3-vl-8b"],
            f"Multi-page ({page_count} pages) → Qwen 3-VL 8B (llama-swap)",
        )

    # Dense syllabi: Gemma 4 26B-A4B
    if size_mb >= 5:
        return OCRAwareSelection(
            VISION_MODELS["gemma-4-26B-A4B"],
            f"Dense syllabus ({size_mb:.1f} MB) → Gemma 4 26B-A4B (llama-swap)",
        )

    # Small PDFs: Gemma 4 E2B
    return OCRAwareSelection(
        VISION_MODELS["gemma-4-E2B"],
        f"Small document ({size_mb:.1f} MB) → Gemma 4 E2B (MLX)",
    )


# ─── Classical-OCR stack helpers (used by `compare.py`) ─────────────────────


@dataclass
class ClassicalOCRStack:
    """A single classical OCR Docker stack.

    The v4 spec keeps the 6 classical OCR stacks separate from the
    `VISION_MODELS` dict (which is vision-LLM only). They live at
    `bonneagar/stacks/ocr-classical/{stack}/` and are exposed
    through the `CLASSICAL_OCR` dict.
    """

    stack_name: str
    docker_image: str
    port: int
    notes: str = ""
    stack_path: str = ""


def all_classical_stacks() -> list[ClassicalOCRStack]:
    """Iterate all classical OCR Docker stacks (the 6 v4 entries)."""
    return [
        ClassicalOCRStack(
            stack_name=name,
            docker_image=info["image"],
            port=info["port"],
            notes=info.get("notes", ""),
            stack_path=info.get("stack", ""),
        )
        for name, info in CLASSICAL_OCR.items()
    ]


def all_models() -> list[OCRModel]:
    """Iterate all vision models in the v4 `VISION_MODELS` dict.

    Equivalent to `list(VISION_MODELS.values())` but exposed as a
    named helper for clarity at call sites (e.g. the eval harness
    in `cianfhoghlaim/ocr/evaluation/compare.py`).
    """
    return list(VISION_MODELS.values())
