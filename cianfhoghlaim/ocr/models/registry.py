"""
OCR / VLM Model Registry (v4 home, post-2026-06-28 consolidation).

This is the canonical OCR/VLM model registry for the Cianfhoghlaim
platform. Every OCR/VLM call in the lakehouse routes through here.

Key changes from the legacy `_meaisinfhoghlaim_src/model_registry.py`:
- 24-entry `VISION_MODELS` dict (replaces the legacy 10-entry `OCR_MODELS`
  + 6-entry `VLM_MODELS`)
- All entries Unsloth-first: every model has `unsloth_id` → `mlx_id` →
  `upstream_id` fallback chain
- No cloud-API models (no OpenAI, no Anthropic) per user request
- New `ModelCapability.DIAGRAM` enum value for figure detection
  (used by the 6-stage PDF processing pipeline)
- New `role: Literal["tier1_heavy", "tier2_medium", "tier3_light",
  "specialist", "legacy"]` field for the 3-tier ladder
- New `unsloth_features: list[str]` field for Dynamic 2.0 GGUFs,
  MTP speculative decoding, MoE 12x, imatrix

All 24 model_ids were verified live on HuggingFace Hub via the
HF MCP tools on 2026-06-29. See the full audit at
`openspec/research/2026-06-29-ocr-vlm-registry-audit/kcg-ocr-vlm-registry.md`.

Usage:
    from cianfhoghlaim.ocr.models import (
        VISION_MODELS, get_optimal_for_m4, select_ocr_backend
    )

    # List all models
    for key, model in VISION_MODELS.items():
        print(f"{key}: {model.unsloth_id or model.upstream_id}")

    # Get the M4 default
    model = VISION_MODELS[get_default_for_m4_max()]

    # Pick a model for a given PDF
    from pathlib import Path
    selection = select_ocr_backend(Path("syllabus.pdf"))
"""

from __future__ import annotations

import base64
import io
import warnings
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal

import numpy as np

# Re-export back-compat aliases for the legacy module
warnings.warn(
    "Importing from cianfhoghlaim.ocr.models is the v4 home. "
    "The legacy cianfhoghlaim.ocr._meaisinfhoghlaim_src.model_registry "
    "is deprecated and will be removed in v5.",
    DeprecationWarning,
    stacklevel=2,
)


# ─── Enums ───────────────────────────────────────────────────────────────────


class ModelBackend(str, Enum):
    """Supported model backends.

    Note: the v4 registry has DROPPED `OPENAI` and `ANTHROPIC` from
    the canonical backend list. All 24 entries have at least one
    local inference path (Unsloth GGUF, mlx-community, or upstream
    safetensors on M4 Max 48 GB / arm1-oci).
    """

    LITELLM = "litellm"
    MLX = "mlx"
    TRANSFORMERS = "transformers"
    LLAMASWAP = "llama-swap"  # NEW in v4 — Unsloth GGUFs served via llama-swap


class ModelCapability(str, Enum):
    """Model capabilities.

    `DIAGRAM` is NEW in v4 (added 2026-06-29) for the 6-stage PDF
    processing pipeline's figure detection / captioning tasks.
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
    "gemma-4-31B": OCRModel(
        key="gemma-4-31B",
        name="Gemma 4 31B dense (SOTA)",
        unsloth_id="unsloth/gemma-4-31B-it-GGUF",
        mlx_id="mlx-community/gemma-4-31b-it-8bit",
        upstream_id="google/gemma-4-31B-it",
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
        unsloth_features=["fast_inference", "imatrix"],
        role="tier1_heavy",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="32.7B dense, 19GB. Top dense. F-19 SOTA baseline. arm1-oci preferred.",
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
    "glm-4.6v-full": OCRModel(
        key="glm-4.6v-full",
        name="GLM-4.6V full MoE (arm1-oci)",
        unsloth_id="unsloth/GLM-4.6V-GGUF",
        mlx_id=None,
        upstream_id="zai-org/GLM-4.6V",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
            ModelCapability.MATH,
            ModelCapability.REASONING,
            ModelCapability.DIAGRAM,
        ],
        unsloth_features=["moe_12x", "fast_inference", "imatrix"],
        role="tier1_heavy",
        m4_max_48gb_fit=False,
        arm1_oci_required=True,
        available=True,
        max_resolution=(2048, 2048),
        notes="107.7B MoE, 414K downloads. arm1-oci only.",
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
    "qwen3-vl-235b-a22b": OCRModel(
        key="qwen3-vl-235b-a22b",
        name="Qwen 3-VL 235B-A22B MoE (arm1-oci SOTA)",
        unsloth_id="unsloth/Qwen3-VL-235B-A22B-Instruct-GGUF",
        mlx_id=None,
        upstream_id="Qwen/Qwen3-VL-235B-A22B-Instruct",
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
        m4_max_48gb_fit=False,
        arm1_oci_required=True,
        available=True,
        max_resolution=(4096, 4096),
        notes="235.7B MoE / 22B active, ~130GB. arm1-oci SOTA for full NCCA corpus. 6.2M downloads.",
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
    "qwen3.6-35b-a3b-mtp": OCRModel(
        key="qwen3.6-35b-a3b-mtp",
        name="Qwen 3.6 35B-A3B MTP MoE",
        unsloth_id="unsloth/Qwen3.6-35B-A3B-MTP-GGUF",
        mlx_id="unsloth/Qwen3.6-35B-A3B-UD-MLX-4bit",
        upstream_id="Qwen/Qwen3.6-35B-A3B",
        backend=ModelBackend.LLAMASWAP,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.MATH,
            ModelCapability.MULTILINGUAL,
            ModelCapability.GAELIC,
        ],
        unsloth_features=["moe_12x", "mtp_speculative", "fast_inference", "imatrix"],
        role="tier1_heavy",
        m4_max_48gb_fit=True,
        arm1_oci_required=False,
        available=True,
        max_resolution=(2048, 2048),
        notes="35.9B MoE / 3B active, ~22GB. **MTP + MoE**. 778K downloads.",
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
}
# Total: 24 entries (verified live on HF Hub 2026-06-29, Unsloth-only)


# ─── Classical OCR (Docker compose stacks) ──────────────────────────────────


CLASSICAL_OCR: dict[str, dict[str, Any]] = {
    "docling-serve": {
        "stack": "infrastructure/stacks/ocr-classical/docling-serve/",
        "image": "docker.io/ds4sd/docling-serve:latest",
        "port": 5001,
        "notes": "IBM Docling — 258M params, DocTags layout. The 'safety net' when VLM extraction fails.",
    },
    "paddleocr": {
        "stack": "infrastructure/stacks/ocr-classical/paddleocr/",
        "image": "docker.io/paddlepaddle/paddleocr:latest",
        "port": 8888,
        "notes": "PaddlePaddle OCR — multilingual, first-party GGUF.",
    },
    "olmocr": {
        "stack": "infrastructure/stacks/ocr-classical/olmocr/",
        "image": "docker.io/allenai/olmocr:latest",
        "port": 8000,
        "notes": "AllenAI olmOCR — 7B params, math-OCR specialist. The 'specialist' for marking-scheme LaTeX.",
    },
    "tesseract": {
        "stack": "infrastructure/stacks/ocr-classical/tesseract/",
        "image": "docker.io/tesseractshadow/tesseract4re:latest",
        "port": 8889,
        "notes": "Tesseract 4 — clean printed-text baseline.",
    },
    "pylaia": {
        "stack": "infrastructure/stacks/ocr-classical/pylaia/",
        "image": "docker.io/cianhoghlaim/pylaia-irish:latest",
        "port": 7779,
        "notes": "Pylaia HTR — best for historical Irish manuscripts (the Dúchas corpus).",
    },
    "dots-ocr": {
        "stack": "infrastructure/stacks/ocr-classical/dots-ocr/",
        "image": "docker.io/rednote-hilab/dots.ocr-serve:latest",
        "port": 8001,
        "notes": "rednote-hilab Dots-OCR — 3.0B layout specialist (vs the VLM `dots-ocr` key).",
    },
}
# Total: 6 classical OCR stacks (the v4 platform spec says they 'stay separate as Docker compose')


# ─── Text-only Models (for the agent fleet) ────────────────────────────────


TEXT_MODELS: dict[str, OCRModel] = {
    "qwen3.6-27b-mtp": VISION_MODELS["qwen3.6-27b-mtp"],
    "qwen3.6-35b-a3b-mtp": VISION_MODELS["qwen3.6-35b-a3b-mtp"],
    "uccix-mistral-24b": VISION_MODELS["uccix-mistral-24b"],
    "uccix-llama-3.1-8b": VISION_MODELS["uccix-llama-3.1-8b"],
}
# 4 text-only entries (the Qwen 3.6 + UCCIX models)


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
        return [m for m in self.models.values() if m.available and m.arm1_oci_required is False or m.m4_max_48gb_fit]

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


def get_default_for_m4_max() -> str:
    """Return the default model key for the M4 Max 48 GB target.

    Per the v4 spec, the default is `gemma-4-26B-A4B` (MoE, 14GB, 4B active,
    the sweet spot for M4 Max 48 GB unified memory).
    """
    return "gemma-4-26B-A4B"


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
