"""
Generate the v4 litellm/config/config.yaml from the MODEL_REGISTRY.

Per the 2026-08-15 centralized-model-registry openspec change, this
script reads from the canonical ``MODEL_REGISTRY`` (not just the
legacy ``VISION_MODELS`` / ``TEXT_MODELS`` dicts) and emits a complete
litellm config with one entry per ``ocr_vision`` / ``text_llm``
family entry, plus the v4 aliases (vision, ocr, diagram, gaelic,
irish, math, extract, default).

The legacy ``cianfhoghlaim.ocr.models.VISION_MODELS`` is still
imported for back-compat but the script prefers
``MODEL_REGISTRY.filter(family="ocr_vision")`` so any new entries
added to the registry are picked up automatically.

Usage:
    python scripts/generate_litellm_config.py > cianfhoghlaim/stacks/litellm/config/config.yaml

Exit code 0 on success.
"""

from __future__ import annotations

import os
import sys
import warnings
from io import StringIO

# Ensure the registry is importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

warnings.filterwarnings("ignore")
# NOTE (2026-08-07): was `from cianfhoghlaim.ocr.models import ...` — that
# package does not exist anywhere in this environment (ModuleNotFoundError,
# confirmed: `cianfhoghlaim` isn't pip-installed and there's no local
# `cianfhoghlaim/` package), so this script has been unable to run at all,
# not just unable to emit the M3 chokepoint block. `meaisinfhoghlaim.models
# .registry` is the equivalent, currently-populated module (same 5 symbols,
# 24-entry VISION_MODELS). Left as a narrow import-path fix; the many other
# `cianfhoghlaim.*` imports found repo-wide (cocoindex/, cli.py, etc.) are a
# separate, larger legacy-import cleanup, out of scope here.
from meaisinfhoghlaim.models.registry import (  # noqa: E402
    CLASSICAL_OCR,
    TEXT_MODELS,
    VISION_MODELS,
    ModelBackend,
    ModelCapability,
)

# Per the centralized-model-registry openspec change, the canonical
# source of truth is now ``meaisinfhoghlaim.models.MODEL_REGISTRY``.
# We import it lazily (after the path shim above) so the script
# can still run in minimal container builds where the model_registry
# module isn't installed.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY  # noqa: E402
    _HAS_REGISTRY = True
except Exception:  # noqa: BLE001
    MODEL_REGISTRY = None
    _HAS_REGISTRY = False

# ─── Backend routing per VISION_MODEL.backend ───

# Per-model backend URLs (per cianfhoghlaim/stacks/litellm/config/config.yaml)
BACKEND_URLS = {
    ModelBackend.LLAMASWAP: "http://llama-swap:8080/v1",
    ModelBackend.MLX: "http://mlx-omni:10240/v1",
    ModelBackend.TRANSFORMERS: "http://transformers:5000/v1",
    ModelBackend.LITELLM: None,  # routed through BAML clients, no direct URL
}

BACKEND_API_KEY = "not-needed"  # all local services share this


def render_model_entry(key: str, model) -> str:
    """Render a single litellm model_list entry."""
    api_base = BACKEND_URLS.get(model.backend)
    if api_base is None:
        # LITELLM backend — skip (these are routed through BAML clients)
        return ""

    # Build the litellm model id (use the unsloth_id or upstream_id with org prefix)
    if model.unsloth_id:
        litellm_model = f"openai/{model.unsloth_id.split('/')[-1]}"
    elif model.upstream_id:
        litellm_model = f"openai/{model.upstream_id.split('/')[-1]}"
    else:
        litellm_model = f"openai/{key}"

    # Capabilities. NOTE (2026-08-07): `ModelRegistryEntry` (the canonical
    # meaisinfhoghlaim.models.model_registry.MODEL_REGISTRY class) never
    # had a `.capabilities` field — only the legacy `OCRModel`/`TEXT_MODELS`
    # shim objects do. That made this line an unconditional AttributeError
    # crash for every MODEL_REGISTRY-sourced entry, meaning the
    # `_HAS_REGISTRY = True` code path (the "prefer the centralized
    # registry" path this script's docstring describes) had never actually
    # completed a run. Defaulting to `[]` is a safe, honest fix — this
    # field is descriptive metadata in the output YAML (LiteLLM doesn't
    # enforce it), not something to guess a value for. Deciding whether
    # `ModelRegistryEntry` SHOULD gain a `capabilities` field is a separate,
    # larger design decision, out of scope here.
    model_capabilities = getattr(model, "capabilities", None) or []
    caps = [c.value for c in model_capabilities if c.value != "diagram"]
    if ModelCapability.DIAGRAM in model_capabilities:
        caps.append("diagram")

    # Description
    desc = model.notes[:100] if model.notes else f"{key} (v4)"

    # Timeouts based on size
    timeout = 1800 if "235b" in key or "31B" in key else 1200 if "30b" in key or "26B" in key else 600

    out = StringIO()
    out.write(f"  # ─── {key} ({model.role}) ───\n")
    out.write(f"  - model_name: local/vision/{key}\n")
    out.write(f"    litellm_params:\n")
    out.write(f"      model: {litellm_model}\n")
    out.write(f"      api_base: {api_base}\n")
    out.write(f"      api_key: {BACKEND_API_KEY}\n")
    out.write(f"      timeout: {timeout}\n")
    out.write(f"    model_info:\n")
    out.write(f"      description: \"{desc}\"\n")
    out.write(f"      capabilities: {caps}\n")
    if model.unsloth_id:
        out.write(f"      unsloth_id: \"{model.unsloth_id}\"\n")
    out.write(f"      upstream_id: \"{model.upstream_id}\"\n")
    out.write(f"      tier: paid\n")
    # Same rationale as `capabilities` above: `ModelRegistryEntry` has
    # neither field, so default rather than crash.
    if getattr(model, "arm1_oci_required", False):
        out.write(f"      arm1_oci_only: true\n")
    unsloth_features = getattr(model, "unsloth_features", None) or []
    if "moe_12x" in unsloth_features:
        out.write(f"      moe: true\n")
    if "mtp_speculative" in unsloth_features:
        out.write(f"      mtp_speculative: true\n")
    out.write(f"\n")
    return out.getvalue()


def render_header() -> str:
    """Render the config header (v4 preamble)."""
    return """# =============================================================================
# LITELLM GATEWAY CONFIG — Oideachais / Cianfhoghlaim
# =============================================================================
# v4 (2026-06-29): Generated from `cianfhoghlaim.ocr.models.VISION_MODELS`.
# Source: openspec/changes/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority
#
# 24-entry VISION_MODELS registry + 6 CLASSICAL_OCR + 4 TEXT_MODELS
# Unsloth-first fallback chain (per the v4 spec).
#
# Route topology (every URL is internal Docker DNS):
#   LiteLLM (:4000) ──┬── llama-swap (:8080)   [GGUF Q4_K_M, dynamic swap]
#                     ├── mlx-omni    (:10240) [MLX-format on M-series]
#                     ├── transformers (:5000) [PyTorch transformers]
#                     └── Cloud        (Gemini, GLM, OpenAI, Anthropic, OpenCode Go)
#
# To regenerate: python scripts/generate_litellm_config.py > this file
# =============================================================================

model_list:

"""


def render_aliases() -> str:
    """Render the v4 alias section (vision, ocr, diagram, gaelic, irish, math, extract)."""
    return """  # ===========================================================================
  # v4 ALIASES — use these in client code, not the local/vision/* names
  # ===========================================================================

  - model_name: vision
    litellm_params:
      model: openai/qwen3-vl-8b
      api_base: http://llama-swap:8080/v1
      api_key: not-needed
      timeout: 600
    model_info:
      description: "Alias: vision → Qwen 3-VL 8B (Unsloth GGUF), falls back to Gemma 4 26B-A4B, then to cloud Gemini"
      capabilities: ["vision", "vlm", "alias"]
      tier: paid
      fallback_chain: ["local/vision/qwen3-vl-8b", "local/vision/gemma-4-26B-A4B", "gemini/gemini-2.5-pro"]

  - model_name: ocr
    litellm_params:
      model: openai/qwen3-vl-8b
      api_base: http://llama-swap:8080/v1
      api_key: not-needed
      timeout: 600
    model_info:
      description: "Alias: ocr → Qwen 3-VL 8B (workhorse for syllabus/past-paper OCR), falls back to GLM-4.6V Flash, then olmOCR-2-7B-1025"
      capabilities: ["ocr", "vision", "alias"]
      tier: paid
      fallback_chain: ["local/vision/qwen3-vl-8b", "local/vision/glm-4.6v-flash", "local/vision/olmocr-2-7b-1025"]

  - model_name: diagram
    litellm_params:
      model: openai/molmo2-8b
      api_base: http://transformers:5000/v1
      api_key: not-needed
      timeout: 600
    model_info:
      description: "Alias: diagram → Molmo2-8B (top workhorse for figure pointing), falls back to InternVL3_5-8B"
      capabilities: ["diagram", "grounding", "alias"]
      tier: paid
      fallback_chain: ["local/vision/molmo2-8b", "local/vision/internvl3-8b"]

  - model_name: gaelic
    litellm_params:
      model: openai/gemma-4-26B-A4B-it-GGUF
      api_base: http://llama-swap:8080/v1
      api_key: not-needed
      timeout: 600
    model_info:
      description: "Alias: gaelic → Gemma 4 26B-A4B (6 Celtic languages, M4 default), falls back to Qwen 3-VL 8B"
      capabilities: ["gaelic", "multilingual", "vision", "alias"]
      tier: paid
      fallback_chain: ["local/vision/gemma-4-26B-A4B", "local/vision/qwen3-vl-8b", "local/vision/gemma-4-E4B"]

  - model_name: irish
    litellm_params:
      model: openai/uccix-mistral-24b
      api_base: http://transformers:5000/v1
      api_key: not-needed
      timeout: 600
    model_info:
      description: "Alias: irish → UCCIX-Mistral-24B (modern Irish-language path, Nov 2025), falls back to Gemma 4 26B-A4B"
      capabilities: ["irish", "gaelic", "text", "alias"]
      tier: paid
      fallback_chain: ["local/vision/uccix-mistral-24b", "local/vision/gemma-4-26B-A4B"]

  - model_name: default
    litellm_params:
      model: openai/gemma-4-26B-A4B-it-GGUF
      api_base: http://llama-swap:8080/v1
      api_key: not-needed
      timeout: 600
    model_info:
      description: "Alias: default → Gemma 4 26B-A4B (M4 Max default per v4 spec)"
      capabilities: ["vision", "vlm", "default"]
      tier: paid

  - model_name: math
    litellm_params:
      model: openai/qwen3.6-27B-MTP-GGUF
      api_base: http://llama-swap:8080/v1
      api_key: not-needed
      timeout: 600
    model_info:
      description: "Alias: math → Qwen 3.6 27B MTP (best for marking-scheme post-processing), falls back to Qwen 3.6 35B-A3B MTP, then to GLM-4.6"
      capabilities: ["math", "reasoning", "alias"]
      tier: paid
      fallback_chain: ["local/vision/qwen3.6-27b-mtp", "local/vision/qwen3.6-35b-a3b-mtp", "openai/glm-4.6"]

  - model_name: extract
    litellm_params:
      model: openai/gemma-4-12B
      api_base: http://llama-swap:8080/v1
      api_key: not-needed
      timeout: 600
    model_info:
      description: "Alias: extract → Gemma 4 12B Unified (good for BAML extraction with diagram support)"
      capabilities: ["vision", "vlm", "extraction", "alias"]
      tier: paid
      fallback_chain: ["local/vision/gemma-4-12B", "local/vision/gemma-4-26B-A4B", "openai/glm-4.6"]

  - model_name: embedding-bge-m3
    litellm_params:
      model: openai/text-embedding-3-small
      api_key: not-needed
    model_info:
      description: "Alias: embedding-bge-m3 → 1024-dim multilingual embeddings (for the PDF processing pipeline Stage 5)"
      capabilities: ["embedding", "alias"]
      tier: paid
      fallback_chain: ["openai/text-embedding-3-small", "celtic/embedding/bge-m3"]

"""


def render_text_models() -> str:
    """Render the v4 TEXT_MODELS section (for the agent fleet).

    Per the centralized-model-registry openspec change, prefer the
    ``text_llm`` family from ``MODEL_REGISTRY`` (which subsumes the
    legacy ``TEXT_MODELS`` dict). Falls back to the legacy dict when
    the registry is unavailable.
    """
    out = StringIO()
    out.write("  # =========================================================================\n")
    out.write("  # LOCAL TEXT MODELS (via llama-swap) — for the agent fleet\n")
    out.write("  # =========================================================================\n\n")
    if _HAS_REGISTRY:
        for entry in MODEL_REGISTRY.filter(family="text_llm"):
            # Use the entry as a shim: render_model_entry reads .backend,
            # .unsloth_id, .upstream_id, .capabilities, .role, .notes.
            out.write(render_model_entry(entry.key, entry))
    else:
        for key, model in TEXT_MODELS.items():
            out.write(render_model_entry(key, model))
    return out.getvalue()


def render_router_settings() -> str:
    """Render the router_settings section (preserved from v3).

    Per the 2026-08-08-lakehouse-extensive-hydration-v1 change:
    `fallbacks` used to be a bare list of model-name strings, which
    litellm's `Router.validate_fallbacks()` rejects outright ("Item
    'qwen3-vl-8b' is not a dictionary") -- this crash-looped the whole
    litellm container on every startup (confirmed live via `docker logs
    litellm`), not just the vision route. litellm's real schema requires
    each `fallbacks` entry to be `{primary_model: [fallback_model, ...]}`.
    Fixed here (the generator, the actual source of truth) as well as in
    the currently-checked-in `bonneagar/stacks/litellm/config/config.yaml`
    output, so regenerating the config doesn't reintroduce the bug.
    """
    return """router_settings:
  # Master fallback chain (per the v4 spec + litellm-minimax-vendor-derisking change)
  num_retries: 3
  timeout: 600
  retry_policy: exponential_backoff_retry

  fallbacks:
    - qwen3-vl-8b: [gemma-4-26B-A4B, glm-4.6v-flash, openai/glm-4.6, gemini/gemini-2.5-pro]

  # Vendor-de-risking for MiniMax-M3 (per the litellm-minimax-vendor-derisking change)
  # The `minimax` alias uses 3-key round-robin (OPENCODE_GO_API_KEY_0/1/2)
  # with a 4-tier paid fallback (qwen3.7-max → kimi-k2.6 → glm-4.6)
  # and a final local GGUF floor (qwen3.6-27b-mtp via llama-swap).
  contexts:
    - priority: 0
      content_policy: "irish-curriculum"
      fallbacks:
        - qwen3-vl-8b: [gemma-4-26B-A4B]

litellm_settings:
  drop_params: true
  set_verbose: false
  telemetry: false
  cache: false
  # Per openspec/changes/litellm-minimax-vendor-derisking/:
  # The 3 OpenCode Go slots are rotated via 3 separate env vars
  # (OPENCODE_GO_API_KEY_0, _1, _2). See compose.yaml env section.
"""


def main() -> int:
    out = StringIO()

    # Header
    out.write(render_header())

    # Track which keys have been rendered to avoid duplicates
    rendered_keys: set[str] = set()

    # Per the centralized-model-registry openspec change, prefer the
    # ``ocr_vision`` family from ``MODEL_REGISTRY`` (which subsumes
    # the legacy ``VISION_MODELS`` dict). Falls back to the legacy
    # dict when the registry is unavailable.
    if _HAS_REGISTRY:
        ocr_vision_entries = MODEL_REGISTRY.filter(family="ocr_vision")
    else:
        ocr_vision_entries = [
            # Each VISION_MODELS entry is an OCRModel; ModelRegistryEntry
            # is API-compatible for render_model_entry().
            type("ShimEntry", (), {
                "key": key,
                "backend": model.backend,
                "unsloth_id": model.unsloth_id,
                "upstream_id": model.upstream_id,
                "capabilities": model.capabilities,
                "role": getattr(model, "role", "default"),
                "notes": model.notes,
                "arm1_oci_required": getattr(model, "arm1_oci_required", False),
                "unsloth_features": getattr(model, "unsloth_features", []),
            })
            for key, model in VISION_MODELS.items()
        ]

    # Group by backend
    by_backend: dict[ModelBackend, list[tuple[str, object]]] = {
        ModelBackend.LLAMASWAP: [],
        ModelBackend.MLX: [],
        ModelBackend.TRANSFORMERS: [],
    }
    for entry in ocr_vision_entries:
        # OCR vision entries may have a `backend` of either ModelBackend
        # enum or string; normalize to the enum for the grouping check.
        backend = entry.backend
        if isinstance(backend, str):
            try:
                backend = ModelBackend(backend)
            except ValueError:
                continue
        if backend in by_backend:
            by_backend[backend].append((entry.key, entry))

    # Render each backend section
    backend_titles = {
        ModelBackend.LLAMASWAP: "LOCAL GGUF (via llama-swap :8080) — Unsloth Q4_K_M, dynamic swap",
        ModelBackend.MLX: "LOCAL MLX (via mlx-omni :10240) — Apple Silicon fast path",
        ModelBackend.TRANSFORMERS: "LOCAL TRANSFORMERS (via transformers :5000) — PyTorch + MLX/Apple fallback",
    }
    for backend, items in by_backend.items():
        out.write(f"  # =========================================================================\n")
        out.write(f"  # {backend_titles[backend]}\n")
        out.write(f"  # =========================================================================\n\n")
        for key, model in items:
            out.write(render_model_entry(key, model))
            rendered_keys.add(key)

    # Text models (for the agent fleet) — skip duplicates already rendered
    out.write("  # =========================================================================\n")
    out.write("  # LOCAL TEXT MODELS (via llama-swap) — for the agent fleet\n")
    out.write("  # =========================================================================\n\n")
    if _HAS_REGISTRY:
        for entry in MODEL_REGISTRY.filter(family="text_llm"):
            if entry.key in rendered_keys:
                continue
            out.write(render_model_entry(entry.key, entry))
            rendered_keys.add(entry.key)
    else:
        for key, model in TEXT_MODELS.items():
            if key in rendered_keys:
                continue  # already rendered as a vision model
            out.write(render_model_entry(key, model))
            rendered_keys.add(key)

    # Aliases
    out.write(render_aliases())

    # Router settings
    out.write(render_router_settings())

    # ── Safety check (2026-08-07): this generator does NOT emit the
    # hand-maintained "M3 chokepoint" or "token-plan direct endpoint"
    # sections — render_model_entry() only knows the `local/vision/{key}`
    # naming convention (BACKEND_URLS covers llama-swap/mlx/transformers),
    # not the hosted-API aliasing (`kimi/k2`, `minimax-m3`, `minimax-direct`,
    # `dashscope/qwen3.7-plus`, ...) those sections use. Piping this
    # script's output straight over the committed config.yaml — as its own
    # header comment says to — WILL silently delete both sections. Warn
    # loudly on stderr so `mise run litellm:regenerate > config.yaml`
    # doesn't destroy them without anyone noticing; this is not a fix, only
    # a guard, until render_model_entry() is generalized to also emit the
    # hosted-API naming convention (a real design decision, out of scope
    # for this pass — see the comment on `capabilities` above for what
    # else changed here 2026-08-07).
    _HAND_MAINTAINED_NAMES = (
        "kimi/k2", "glm/5.1", "minimax/m2.5", "mimo/2.5", "deepseek/flash",
        "minimax-m3", "minimax-direct",
        "dashscope/qwen3.7-plus", "dashscope/qwen3-coder-next",
    )
    generated = out.getvalue()
    missing = [
        n for n in _HAND_MAINTAINED_NAMES
        if f"model_name: {n}\n" not in generated
    ]
    if missing:
        print(
            "WARNING: this generator does NOT emit the following "
            "hand-maintained model_list entries, present in the committed "
            f"config.yaml: {missing}. Redirecting this script's output "
            "over config.yaml will DELETE them. Do not run "
            "`mise run litellm:regenerate > config.yaml` until "
            "render_model_entry() is extended to cover hosted-API "
            "aliasing, or manually re-merge these sections back in "
            "after regenerating.",
            file=sys.stderr,
        )

    sys.stdout.write(generated)
    return 0


if __name__ == "__main__":
    sys.exit(main())
