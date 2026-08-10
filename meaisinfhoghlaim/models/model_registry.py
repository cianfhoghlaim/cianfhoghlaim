"""
Unified model registry for the Cianfhoghlaim platform (post-`centralized-model-registry` change, 2026-08-15).

The single source of truth for **all** AI / agentic / LLM / VLM / OCR /
embedder / reranker / image-gen / voice / translation model choices
across the platform. This module extends the existing 22-entry
`VISION_MODELS` (in `meaisinfhoghlaim.models.registry`) to cover the
other 4 model families:

1. ``ocr_vision`` — the existing 22-entry ``VISION_MODELS`` (subset view)
2. ``text_llm`` — the 9 LiteLLM M3 chokepoint aliases + agent defaults
3. ``embedder`` — the 3 sentence-transformer models (BGE-M3 + BGE-large + MiniLM)
4. ``rerank`` — the 3 rerank providers (Jina + Cohere + Aliyun)
5. ``image_gen`` — the 5 image-gen models (flux2-dev + z-image-turbo + qwen-image + sdxl + fibo)
6. ``voice`` — the 5 voice/ASR/TTS models (whisper-large + wav2vec2-irish + chatterbox + aba-tts)
7. ``translation`` — the 3 translation models (opus-mt + m2m100 + nllb)

The canonical API is the 2-axis key (family, role) for families where a
single "the" model per role genuinely makes sense:

    MODEL_REGISTRY.resolve("text_llm", "default")           # -> "minimax-m3"
    MODEL_REGISTRY.resolve("voice", "tts")                 # -> "ResembleAI/chatterbox"
    MODEL_REGISTRY.filter(family="embedder")                # -> list of 3 entries

Per the lakehouse-multi-subject-multi-model-rollout change,
`ocr_vision` is the one family where `resolve(family, role)` is NOT the
right tool — the platform's actual goal there is comparing multiple
models against the same input (cost/quality benchmarking), not
resolving a single "the" model. Use `filter()` for `ocr_vision`:

    MODEL_REGISTRY.filter(family="ocr_vision", available=True)
    # -> every real candidate model, each with full metadata (backend,
    #    litellm_alias, tier, notes, ...), for running a comparison
    #    across all of them rather than picking one.

This module is the canonical home for the
`centralized-model-registry` openspec capability. The legacy
``meaisinfhoghlaim.models.registry.VISION_MODELS`` remains a subset
view via ``MODEL_REGISTRY.filter(family="ocr_vision")`` — no
breaking change.

Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Iterable, Literal

# Re-export the existing 22-entry VISION_MODELS so they remain
# importable from this module too (the canonical home for the unified
# MODEL_REGISTRY).
from meaisinfhoghlaim.models.registry import (
    CLASSICAL_OCR,
    TEXT_MODELS,
    VISION_MODELS,
    ModelBackend,
    OCRModel,
)

# ─── Model families + roles ────────────────────────────────────────────────


ModelFamily = Literal[
    "ocr_vision",
    "text_llm",
    "embedder",
    "rerank",
    "image_gen",
    "voice",
    "translation",
]


ModelRole = str  # Free-form within each family (e.g. "default", "diagram",
                 # "tts", "strong", "fast"). Each family has its own
                 # canonical role vocabulary documented in the family
                 # section below.


# ─── The unified entry dataclass ───────────────────────────────────────────


@dataclass
class ModelRegistryEntry:
    """A single entry in the unified `MODEL_REGISTRY`.

    Attributes:
        key: Canonical model identifier (e.g. ``"minimax-m3"``,
            ``"BAAI/bge-m3"``, ``"qwen3-vl-8b"``). Unique within the
            registry.
        family: One of the 7 ``ModelFamily`` literals.
        role: Free-form string within the family
            (e.g. ``"default"``, ``"diagram"``, ``"tts"``).
        display_name: Human-readable name for UI surfaces.
        unsloth_id: The Unsloth GGUF ID if available (None otherwise).
        mlx_id: The MLX-community GGUF ID if available.
        upstream_id: The canonical upstream HF ID.
        backend: The runtime backend
            (LITELLM / MLX / TRANSFORMERS / LLAMASWAP / DOCLING /
            UNSTRACT for OCR; HF / OPENAI / LOCAL for text_llm; etc.).
        available: Whether the model is currently available in this
            deployment. False for deprecated entries
            (e.g. ``uccix-llama2-13b``).
        litellm_alias: The LiteLLM alias for this model
            (e.g. ``"minimax-m3"``, ``"local/vision/qwen3-vl-8b"``).
            None if not routed via LiteLLM.
        env_var: Environment variable name to override the model name
            at runtime (e.g. ``"OPENCODE_GO_MODEL"``).
        notes: Free-form documentation.
        languages: Languages this model is specialized for (None =
            language-agnostic).
        tier: Free-form descriptive grouping (e.g. the original OCRModel
            tier: ``"tier1_heavy"`` / ``"tier2_medium"`` / ``"tier3_light"``
            / ``"specialist"`` / ``"legacy"``). Purely descriptive
            metadata, distinct from `role` -- per the
            lakehouse-multi-subject-multi-model-rollout change,
            `ocr_vision` entries no longer collapse this grouping into
            `role` (that caused 15 silent `resolve(family, role)`
            collisions, e.g. 9 different OCR models all claiming
            `role="specialist"`, since `resolve()`'s single-winner
            semantics are wrong for a family the platform wants to
            compare across, not arbitrate a single "the" model for).
    """

    key: str
    family: ModelFamily
    role: str
    display_name: str
    unsloth_id: str | None
    mlx_id: str | None
    upstream_id: str
    backend: str
    available: bool
    litellm_alias: str | None = None
    env_var: str | None = None
    notes: str = ""
    languages: list[str] | None = None
    tier: str | None = None


# ─── The 5 model families ──────────────────────────────────────────────────


# 1. ocr_vision — pull from the existing VISION_MODELS dict
def _ocr_vision_entries() -> dict[str, ModelRegistryEntry]:
    """Project the 24-entry VISION_MODELS into ModelRegistryEntry form.

    Per the lakehouse-multi-subject-multi-model-rollout change: `role`
    used to be derived from OCRModel's tier field (tier1_heavy ->
    "primary", tier2_medium -> "default", etc.), collapsing 24 distinct
    models into only 5 buckets -- confirmed live this caused 15 silent
    `(family, role)` collisions (e.g. 9 different models all claiming
    `role="specialist"`, first-registered winning, the rest permanently
    unreachable via `resolve()`). That's the wrong tool for this family:
    the platform's actual goal for `ocr_vision` is comparing multiple
    models against the same input (cost/quality benchmarking), not
    having `resolve()` arbitrarily pick a single "the" model per role.

    Fix: `role` is now the model's own unique `key` (so `resolve(
    "ocr_vision", <any-key>)` degrades to a harmless, always-correct
    keyed lookup -- no collisions possible, since keys are already
    unique). The original tier grouping is preserved as purely
    descriptive metadata on the new `tier` field instead. Real
    model-comparison code should use `MODEL_REGISTRY.filter(
    family="ocr_vision", available=True)` to get every real candidate
    with full metadata, not `resolve()`, which was never the right tool
    for "give me several models to compare."

    Other families (text_llm, embedder, rerank, image_gen, voice,
    translation) are untouched -- their `resolve(family, role)`
    single-winner semantics are correct for genuinely-interchangeable
    "give me the default/strong/fast model for this family" use cases.
    """
    entries: dict[str, ModelRegistryEntry] = {}
    for vkey, vmodel in VISION_MODELS.items():
        # vmodel.role is a Literal[...] string (not an enum), so we
        # read it as a plain string.
        role_str = getattr(vmodel, "role", "specialist")
        if hasattr(role_str, "value"):  # backwards-compat if it's an enum
            role_str = role_str.value
        # Preserve the original tier grouping as descriptive metadata
        # only -- no longer used as the resolve() lookup key.
        tier_map = {
            "tier1_heavy": "primary",
            "tier2_medium": "default",
            "tier3_light": "lightweight",
            "specialist": "specialist",
            "legacy": "legacy",
        }
        tier = tier_map.get(role_str, role_str)
        # vmodel.backend is a ModelBackend enum OR a string
        backend_raw = getattr(vmodel, "backend", "unknown")
        backend_val = backend_raw.value if hasattr(backend_raw, "value") else str(backend_raw)
        entries[vkey] = ModelRegistryEntry(
            key=vkey,
            family="ocr_vision",
            role=vkey,  # unique per model -- see docstring for why
            display_name=getattr(vmodel, "name", vkey),
            unsloth_id=getattr(vmodel, "unsloth_id", None),
            mlx_id=getattr(vmodel, "mlx_id", None),
            upstream_id=getattr(vmodel, "upstream_id", vkey),
            backend=backend_val,
            available=getattr(vmodel, "available", True),
            litellm_alias=f"local/vision/{vkey}" if getattr(vmodel, "available", True) else None,
            notes=getattr(vmodel, "notes", ""),
            tier=tier,
        )
    return entries


# 2. text_llm — the LiteLLM M3 chokepoint + agent defaults + text-only
#    re-exports of VISION_MODELS
def _text_llm_entries() -> dict[str, ModelRegistryEntry]:
    entries: dict[str, ModelRegistryEntry] = {
        # The 5 M3 chokepoint keywords
        "kimi-k2.6": ModelRegistryEntry(
            key="kimi-k2.6",
            family="text_llm",
            role="kimi",
            display_name="Kimi K2.6 (M3 chokepoint)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="kimi-k2.6",
            backend="opencode_go",
            available=True,
            litellm_alias="kimi/k2",
            env_var="KIMI_K2_MODEL",
            notes="M3 chokepoint: Kimi K2.6 via OpenCode Go API.",
        ),
        "glm-5.1": ModelRegistryEntry(
            key="glm-5.1",
            family="text_llm",
            role="glm",
            display_name="GLM 5.1 (M3 chokepoint)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="glm-5.1",
            backend="opencode_go",
            available=True,
            litellm_alias="glm/5.1",
            env_var="GLM_5_MODEL",
            notes="M3 chokepoint: GLM 5.1 via OpenCode Go API.",
        ),
        "minimax-m2.5": ModelRegistryEntry(
            key="minimax-m2.5",
            family="text_llm",
            role="m2",
            display_name="minimax M2.5 (M3 chokepoint)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="minimax-m2.5",
            backend="opencode_go",
            available=True,
            litellm_alias="minimax/m2.5",
            env_var="MINIMAX_M2_MODEL",
            notes="M3 chokepoint: minimax M2.5 via OpenCode Go API.",
        ),
        "mimo-v2.5": ModelRegistryEntry(
            key="mimo-v2.5",
            family="text_llm",
            role="mimo",
            display_name="MiMo v2.5 (M3 chokepoint)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="mimo-v2.5",
            backend="opencode_go",
            available=True,
            litellm_alias="mimo/2.5",
            env_var="MIMO_MODEL",
            notes="M3 chokepoint: MiMo v2.5 via OpenCode Go API.",
        ),
        "deepseek-v4-flash": ModelRegistryEntry(
            key="deepseek-v4-flash",
            family="text_llm",
            role="deepseek",
            display_name="DeepSeek V4 Flash (M3 chokepoint)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="deepseek-v4-flash",
            backend="opencode_go",
            available=True,
            litellm_alias="deepseek/flash",
            env_var="DEEPSEEK_MODEL",
            notes="M3 chokepoint: DeepSeek V4 Flash via OpenCode Go API.",
        ),
        "minimax-m3": ModelRegistryEntry(
            key="minimax-m3",
            family="text_llm",
            role="default",
            display_name="minimax M3 (canonical plan alias)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="minimax-m3",
            backend="opencode_go",
            available=True,
            litellm_alias="minimax-m3",
            env_var="MINIMAX_BASE_URL",
            notes=(
                "Canonical M3 plan alias used by openclaw/openchamber/hermes. "
                "This is the default model for the 12-agent fleet (the "
                "12 agents in agents/agent_registry.py)."
            ),
        ),
        # ── Qwen token plan (Qwen Cloud, served via DashScope) ──
        # Per openspec/changes/2026-08-06-token-plan-apis-lc-doc-pipeline-
        # and-edge-tls-remediation-v1/specs/centralized-model-registry/spec.md.
        # backend="dashscope" is a direct hosted-API call to DashScope's
        # OpenAI-compatible endpoint (mirrors the "anthropic" / "openai" /
        # "google" hosted-API backend convention used below) — NOT
        # "opencode_go" (that's the OpenCode Zen gateway used by minimax-m3
        # and the M3 chokepoint keywords) and NOT "llama-swap" (that's the
        # local GGUF path used by qwen3.6-27b-mtp just below). The base URL
        # is env-driven via DASHSCOPE_BASE_URL — never hardcoded here.
        "qwen3.7-plus": ModelRegistryEntry(
            key="qwen3.7-plus",
            family="text_llm",
            role="token_plan_primary",
            display_name="Qwen 3.7 Plus (DashScope token plan, primary)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="qwen/qwen3.7-plus",
            backend="dashscope",
            available=True,
            litellm_alias="dashscope/qwen3.7-plus",
            env_var="DASHSCOPE_API_KEY",
            notes=(
                "Qwen Cloud token-plan primary text model, served via "
                "DashScope's OpenAI-compatible endpoint "
                "({DASHSCOPE_BASE_URL}, currently "
                "https://coding.dashscope.aliyuncs.com/v1). Used as the "
                "secondary cross-check client (alongside minimax-m3) for "
                "the lc6 BAML extraction functions "
                "(ExtractCurriculumSyllabus, ExtractExamPaperLayout, "
                "ExtractMarkingSchemeGuideline, ExtractCrossLinguisticConcept). "
                "See baml_src/clients.baml `ExtractQwenCrossCheck`."
            ),
        ),
        "qwen3-coder-next": ModelRegistryEntry(
            key="qwen3-coder-next",
            family="text_llm",
            role="token_plan_coding",
            display_name="Qwen3 Coder Next (DashScope token plan, coding)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="qwen/qwen3-coder-next",
            backend="dashscope",
            available=True,
            litellm_alias="dashscope/qwen3-coder-next",
            env_var="DASHSCOPE_API_KEY",
            notes=(
                "Qwen Cloud token-plan coding model, served via DashScope's "
                "OpenAI-compatible endpoint ({DASHSCOPE_BASE_URL}). Used by "
                "the opencode `qwen` provider (opencode.json) for coding-"
                "agent tasks; not currently wired into a BAML client."
            ),
        ),
        "qwen3.6-27b-mtp": ModelRegistryEntry(
            key="qwen3.6-27b-mtp",
            family="text_llm",
            role="strong",
            display_name="Qwen 3.6 27B MTP (local GGUF)",
            unsloth_id="unsloth/Qwen3.6-27B-MTP-GGUF",
            mlx_id=None,
            upstream_id="Qwen/Qwen3.6-27B",
            backend="llama-swap",
            available=True,
            litellm_alias="local/vision/qwen3.6-27b-mtp",
            env_var=None,
            notes=(
                "Local GGUF served via llama-swap. Used by LlamaSwapReasoningClient "
                "(qwen3.6-27b-mtp) in baml_src/clients_llama_swap.baml. Also "
                "doubles as the 'strong' text-only model on the agent fleet."
            ),
        ),
        "uccix-mistral-24b": ModelRegistryEntry(
            key="uccix-mistral-24b",
            family="text_llm",
            role="irish",
            display_name="UCCIX Mistral 24B (Modern Irish path)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="ReliableAI/UCCIX-Mistral-24B",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            languages=["ga"],
            notes=(
                "Modern Irish-language text model (transformers-backed). "
                "Used by the agent fleet when language='ga' (replaces the "
                "deprecated uccix-llama2-13b)."
            ),
        ),
        "uccix-llama-3.1-8b": ModelRegistryEntry(
            key="uccix-llama-3.1-8b",
            family="text_llm",
            role="irish_fast",
            display_name="UCCIX Llama 3.1 8B (Irish fast path)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="ReliableAI/UCCIX-Llama-3.1-8B",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            languages=["ga"],
            notes=(
                "Fast Irish-language text model (transformers-backed). "
                "Used when language='ga' and a faster response is needed."
            ),
        ),
        "uccix-llama2-13b": ModelRegistryEntry(
            key="uccix-llama2-13b",
            family="text_llm",
            role="irish_legacy",
            display_name="UCCIX Llama2 13B (DEPRECATED)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="ReliableAI/UCCIX-Llama2-13B-Instruct",
            backend="litellm",
            available=False,
            litellm_alias=None,
            env_var=None,
            languages=["ga"],
            notes=(
                "DEPRECATED 2026-08-15. Was in agents/adk/tuatha_config.py:25 "
                "but the canonical registry marks it available=False. "
                "Migrate to uccix-mistral-24b or uccix-llama-3.1-8b."
            ),
        ),
        "claude-sonnet-4-20250514": ModelRegistryEntry(
            key="claude-sonnet-4-20250514",
            family="text_llm",
            role="long_context",
            display_name="Claude Sonnet 4 (long-context)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="anthropic/claude-sonnet-4-20250514",
            backend="anthropic",
            available=True,
            litellm_alias="anthropic/claude-sonnet-4-20250514",
            env_var="ANTHROPIC_API_KEY",
            notes=(
                "Long-context Anthropic model used by agents/letta_client.py. "
                "Requires ANTHROPIC_API_KEY in .infisical.env."
            ),
        ),
        "gpt-4o-mini": ModelRegistryEntry(
            key="gpt-4o-mini",
            family="text_llm",
            role="fast",
            display_name="GPT-4o-mini (fast)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="openai/gpt-4o-mini",
            backend="openai",
            available=True,
            litellm_alias="openai/gpt-4o-mini",
            env_var="OPENAI_API_KEY",
            notes=(
                "Fast OpenAI model used by the HITL agent. Requires "
                "OPENAI_API_KEY in .infisical.env."
            ),
        ),
        "gemini-2.5-pro": ModelRegistryEntry(
            key="gemini-2.5-pro",
            family="text_llm",
            role="strong_hosted",
            display_name="Gemini 2.5 Pro (Google ADK strong)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="google/gemini-2.5-pro",
            backend="google",
            available=True,
            litellm_alias="gemini/gemini-2.5-pro",
            env_var="GOOGLE_API_KEY",
            notes=(
                "Strong Google model used by the email_triage_agent. "
                "Requires GOOGLE_API_KEY in .infisical.env. Role was "
                "originally 'strong', duplicating qwen3.6-27b-mtp's role — "
                "since resolve() is a first-match linear scan, that made "
                "this entry permanently unreachable via resolve('text_llm', "
                "'strong'), which always returned qwen3.6-27b-mtp instead "
                "(that entry's own notes confirm this was the intended "
                "'strong' default for the agent fleet, so it keeps the "
                "role). Renamed to 'strong_hosted' (2026-08-07) so this "
                "entry is independently resolvable for callers who "
                "specifically want a hosted API model with no local-GGUF "
                "dependency, without changing existing resolve('text_llm', "
                "'strong') behavior."
            ),
        ),
        "email_triage_gemini_2_5_pro": ModelRegistryEntry(
            key="email_triage_gemini_2_5_pro",
            family="text_llm",
            role="email_triage_strong",
            display_name="Gemini 2.5 Pro (disambiguated email_triage_strong)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="google/gemini-2.5-pro",
            backend="google",
            available=True,
            litellm_alias="gemini/gemini-2.5-pro",
            env_var="EMAIL_TRIAGE_MODEL",
            notes=(
                "Disambiguated lookup for the email_triage_agent "
                "(`agents/adk/email_triage_agent.py:_email_triage_model`). "
                "The 2-key disambiguation was needed because the "
                "existing `text_llm/strong` role is the local Qwen "
                "3.6 27B MTP path (no Google API key required); the "
                "email_triage agent needs the Google path explicitly."
            ),
        ),
        "unsloth/gemma-3-4b-it-GGUF": ModelRegistryEntry(
            key="unsloth/gemma-3-4b-it-GGUF",
            family="text_llm",
            role="pdf_review_suggestion",
            display_name="Gemma 3 4B (Unsloth GGUF, pdf-review ZeroGPU)",
            unsloth_id="unsloth/gemma-3-4b-it-GGUF",
            mlx_id=None,
            upstream_id="google/gemma-3-4b-it",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var="SUGGESTION_MODEL",
            notes=(
                "ZeroGPU inference for the pdf-review Space "
                "(`spaces/oideachais-pdf-review/app.py:39`). 4 GB GGUF; "
                "runs inside the @spaces.GPU worker boundary."
            ),
        ),
        "unsloth/gemma-4-26B-A4B-it-GGUF": ModelRegistryEntry(
            key="unsloth/gemma-4-26B-A4B-it-GGUF",
            family="text_llm",
            role="pdf_review_explanation",
            display_name="Gemma 4 26B-A4B (Unsloth GGUF, pdf-review ZeroGPU)",
            unsloth_id="unsloth/gemma-4-26B-A4B-it-GGUF",
            mlx_id=None,
            upstream_id="google/gemma-4-26B-A4B-it",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var="EXPLANATION_MODEL",
            notes=(
                "ZeroGPU inference for the pdf-review Space "
                "(`spaces/oideachais-pdf-review/app.py:40`). 14 GB MoE; "
                "requires ZeroGPU large sizing per HuggingFace Spaces spec."
            ),
        ),
        # The 3 hackathon fallback roles — used by the hand-rolled HF
        # Inference chain in `spaces/_common/baml_client.py:69-71` when
        # the LiteLLM gateway is unreachable. Historical hardcoded HF
        # IDs preserved verbatim; consumers should migrate to the
        # canonical LiteLLM path in production.
        "Qwen/Qwen2.5-7B-Instruct": ModelRegistryEntry(
            key="Qwen/Qwen2.5-7B-Instruct",
            family="text_llm",
            role="hackathon_primary",
            display_name="Qwen 2.5 7B (hackathon HF primary)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="Qwen/Qwen2.5-7B-Instruct",
            backend="hf_inference",
            available=True,
            litellm_alias=None,
            env_var="HACKATHON_PRIMARY_MODEL",
            notes=(
                "Hand-rolled HF Inference primary in the 2026-06 hackathon "
                "chain (`spaces/_common/baml_client.py:69`). "
                "Used only when the LiteLLM gateway is unreachable."
            ),
        ),
        "meta-llama/Llama-3.1-8B-Instruct": ModelRegistryEntry(
            key="meta-llama/Llama-3.1-8B-Instruct",
            family="text_llm",
            role="hackathon_fallback_1",
            display_name="Llama 3.1 8B (hackathon HF fallback 1)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="meta-llama/Llama-3.1-8B-Instruct",
            backend="hf_inference",
            available=True,
            litellm_alias=None,
            env_var="HACKATHON_FALLBACK_1_MODEL",
            notes=(
                "Hand-rolled HF Inference fallback 1 in the 2026-06 hackathon "
                "chain (`spaces/_common/baml_client.py:70`)."
            ),
        ),
        "google/gemma-2-9b-it": ModelRegistryEntry(
            key="google/gemma-2-9b-it",
            family="text_llm",
            role="hackathon_fallback_2",
            display_name="Gemma 2 9B IT (hackathon HF fallback 2)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="google/gemma-2-9b-it",
            backend="hf_inference",
            available=True,
            litellm_alias=None,
            env_var="HACKATHON_FALLBACK_2_MODEL",
            notes=(
                "Hand-rolled HF Inference fallback 2 in the 2026-06 hackathon "
                "chain (`spaces/_common/baml_client.py:71`)."
            ),
        ),
    }
    return entries


# 3. embedder — the 3 sentence-transformer models
def _embedder_entries() -> dict[str, ModelRegistryEntry]:
    return {
        "BAAI/bge-m3": ModelRegistryEntry(
            key="BAAI/bge-m3",
            family="embedder",
            role="default",
            display_name="BGE-M3 (1024-d, canonical embedder)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="BAAI/bge-m3",
            backend="sentence-transformers",
            available=True,
            litellm_alias="embedding-bge-m3",
            env_var="CIANFHOGHLAIM_EMBED_MODEL",
            notes=(
                "Canonical 1024-d embedder. Used by cocoindex/_shared/_lifespan.py "
                "and shared across all CocoIndex v1 Apps. Default."
            ),
        ),
        "BAAI/bge-large-en-v1.5": ModelRegistryEntry(
            key="BAAI/bge-large-en-v1.5",
            family="embedder",
            role="english_only",
            display_name="BGE-large-en-v1.5 (1024-d, English only)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="BAAI/bge-large-en-v1.5",
            backend="sentence-transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            notes=(
                "English-only embedder. Optional choice for English-only corpora. "
                "Listed in notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py "
                "embedder dropdown."
            ),
        ),
        "all-MiniLM-L6-v2": ModelRegistryEntry(
            key="all-MiniLM-L6-v2",
            family="embedder",
            role="lightweight",
            display_name="MiniLM-L6-v2 (384-d, lightweight)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="sentence-transformers/all-MiniLM-L6-v2",
            backend="sentence-transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            notes=(
                "Lightweight 384-d embedder. Faster inference than BGE-M3. "
                "Listed in notebooks/16_speedrun_mmo_01_mission_control.py "
                "embedder dropdown."
            ),
        ),
    }


# 4. rerank — the 3 rerank providers
def _rerank_entries() -> dict[str, ModelRegistryEntry]:
    return {
        "jina-reranker-v2-base-multilingual": ModelRegistryEntry(
            key="jina-reranker-v2-base-multilingual",
            family="rerank",
            role="default",
            display_name="Jina Reranker v2 (multilingual)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="jinaai/jina-reranker-v2-base-multilingual",
            backend="jina",
            available=True,
            litellm_alias=None,
            env_var="RERANK_PROVIDER",
            notes=(
                "Canonical rerank provider (default). Configurable via "
                "RERANK_PROVIDER env var (jina | cohere | aliyun)."
            ),
        ),
        "rerank-v3.5": ModelRegistryEntry(
            key="rerank-v3.5",
            family="rerank",
            role="cohere",
            display_name="Cohere Rerank v3.5",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="cohere/rerank-v3.5",
            backend="cohere",
            available=True,
            litellm_alias=None,
            env_var="RERANK_PROVIDER",
            notes="Cohere rerank provider (alternative to Jina).",
        ),
        "gte-rerank-v2": ModelRegistryEntry(
            key="gte-rerank-v2",
            family="rerank",
            role="aliyun",
            display_name="Aliyun GTE Rerank v2",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="Alibaba-NLP/gte-rerank-v2",
            backend="aliyun",
            available=True,
            litellm_alias=None,
            env_var="RERANK_PROVIDER",
            notes="Aliyun GTE rerank provider (alternative to Jina).",
        ),
    }


# 5. image_gen — the 5 image-gen models
def _image_gen_entries() -> dict[str, ModelRegistryEntry]:
    return {
        "local/image/flux2-dev": ModelRegistryEntry(
            key="local/image/flux2-dev",
            family="image_gen",
            role="flux",
            display_name="Flux2-Dev (local image gen)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="black-forest-labs/FLUX.2-dev",
            backend="local",
            available=True,
            litellm_alias="local/image/flux2-dev",
            env_var=None,
            notes="Flux2-Dev local image generation.",
        ),
        "local/image/z-image-turbo": ModelRegistryEntry(
            key="local/image/z-image-turbo",
            family="image_gen",
            role="z_image",
            display_name="Z-Image-Turbo (local image gen)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="stabilityai/z-image-turbo",
            backend="local",
            available=True,
            litellm_alias="local/image/z-image-turbo",
            env_var=None,
            notes="Z-Image-Turbo local image generation (fast variant).",
        ),
        "local/image/qwen-image": ModelRegistryEntry(
            key="local/image/qwen-image",
            family="image_gen",
            role="qwen",
            display_name="Qwen-Image (local image gen)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="Qwen/Qwen-Image",
            backend="local",
            available=True,
            litellm_alias="local/image/qwen-image",
            env_var=None,
            notes="Qwen-Image local image generation.",
        ),
        "local/image/sdxl": ModelRegistryEntry(
            key="local/image/sdxl",
            family="image_gen",
            role="sdxl",
            display_name="SDXL (local image gen)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="stabilityai/stable-diffusion-xl-base-1.0",
            backend="local",
            available=True,
            litellm_alias="local/image/sdxl",
            env_var=None,
            notes="SDXL local image generation (legacy).",
        ),
        "local/image/fibo": ModelRegistryEntry(
            key="local/image/fibo",
            family="image_gen",
            role="fibo",
            display_name="FIBO (local image gen)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="fibonet/fibo",
            backend="local",
            available=True,
            litellm_alias="local/image/fibo",
            env_var=None,
            notes="FIBO local image generation (legacy curriculum asset).",
        ),
    }


# 6. voice — the 5 voice/ASR/TTS models
def _voice_entries() -> dict[str, ModelRegistryEntry]:
    return {
        "whisper-large": ModelRegistryEntry(
            key="whisper-large",
            family="voice",
            role="asr",
            display_name="Whisper Large (ASR, multilingual)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="openai/whisper-large-v3",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            notes="Whisper Large ASR for English + 99 langs.",
        ),
        "wav2vec2-irish": ModelRegistryEntry(
            key="wav2vec2-irish",
            family="voice",
            role="asr_irish",
            display_name="wav2vec2-Irish (ASR, ga)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="cianchek/wav2vec2-large-xlsr-irish",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            languages=["ga"],
            notes="wav2vec2-Irish ASR specialist (Celtic-language path).",
        ),
        "chatterbox": ModelRegistryEntry(
            key="chatterbox",
            family="voice",
            role="tts",
            display_name="Chatterbox (TTS)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="ResembleAI/chatterbox",
            backend="local",
            available=True,
            litellm_alias=None,
            env_var=None,
            notes=(
                "Chatterbox TTS. Default for Irish + English voice synthesis. "
                "Used by agents/api/_oideachais_api/services/chatterbox.py."
            ),
        ),
        "aba-tts": ModelRegistryEntry(
            key="aba-tts",
            family="voice",
            role="tts_irish",
            display_name="ABA-TTS (Irish TTS)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="cianchek/aba-tts",
            backend="local",
            available=True,
            litellm_alias=None,
            env_var=None,
            languages=["ga"],
            notes="ABA-TTS specialist for high-quality Irish TTS.",
        ),
        "ResembleAI/chatterbox": ModelRegistryEntry(
            key="ResembleAI/chatterbox",
            family="voice",
            role="tts_legacy",
            display_name="Chatterbox (legacy full path)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="ResembleAI/chatterbox",
            backend="local",
            available=True,
            litellm_alias=None,
            env_var=None,
            notes=(
                "DEPRECATED 2026-08-15: legacy full-path HF ID. Migrated "
                "consumers to the short key `chatterbox`."
            ),
        ),
    }


# 7. translation — the 3 translation models
def _translation_entries() -> dict[str, ModelRegistryEntry]:
    return {
        "opus-mt": ModelRegistryEntry(
            key="opus-mt",
            family="translation",
            role="default",
            display_name="Helsinki-NLP/OPUS-MT (per-pair template)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="Helsinki-NLP/opus-mt-{src}-{tgt}",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            notes=(
                "Per-language-pair translation template. Interpolates "
                "src + tgt into the model ID at runtime."
            ),
        ),
        "m2m100": ModelRegistryEntry(
            key="m2m100",
            family="translation",
            role="multilingual",
            display_name="M2M-100 (multilingual)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="facebook/m2m100_418M",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            notes="M2M-100 multilingual translation.",
        ),
        "nllb": ModelRegistryEntry(
            key="nllb",
            family="translation",
            role="strong_multilingual",
            display_name="NLLB-200 (strong multilingual)",
            unsloth_id=None,
            mlx_id=None,
            upstream_id="facebook/nllb-200-distilled-600M",
            backend="transformers",
            available=True,
            litellm_alias=None,
            env_var=None,
            notes="NLLB-200 distilled multilingual translation (strong).",
        ),
    }


# ─── The unified registry ──────────────────────────────────────────────────


class _ModelRegistry:
    """The unified model registry.

    Holds all 5 model families (~70 entries) keyed by ``ModelRegistryEntry.key``.
    Provides the canonical `resolve(family, role)` + `filter(family)` API.
    """

    def __init__(self) -> None:
        self._entries: dict[str, ModelRegistryEntry] = {}
        # Populate from each family's contribution
        for fam in (
            _ocr_vision_entries(),
            _text_llm_entries(),
            _embedder_entries(),
            _rerank_entries(),
            _image_gen_entries(),
            _voice_entries(),
            _translation_entries(),
        ):
            self._entries.update(fam)
        self._warn_on_duplicate_roles()

    def _warn_on_duplicate_roles(self) -> None:
        """Log a warning for any (family, role) claimed by >1 entry.

        `resolve()` is a first-match linear scan over insertion order, so a
        silent duplicate makes one entry permanently unreachable via
        `resolve()` (it's still reachable by key). This doesn't raise —
        some duplication may be intentional (e.g. a deprecated entry kept
        for `filter()` visibility) — but it makes the collision visible
        instead of a mystery, unlike the `strong` role duplicate found
        2026-08-07 (qwen3.6-27b-mtp vs. gemini-2.5-pro) that shadowed
        gemini-2.5-pro from every `resolve("text_llm", "strong")` caller
        with no warning at all.
        """
        import logging

        seen: dict[tuple[str, str], str] = {}
        for entry in self._entries.values():
            fr = (entry.family, entry.role)
            if fr in seen:
                logging.getLogger(__name__).warning(
                    "model_registry_duplicate_role",
                    extra={
                        "family": entry.family,
                        "role": entry.role,
                        "shadowed_key": seen[fr],
                        "winning_key": entry.key,
                    },
                )
            else:
                seen[fr] = entry.key

    # ── Iteration / inspection ──

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries.values())

    def __contains__(self, key: str) -> bool:
        return key in self._entries

    def __getitem__(self, key: str) -> ModelRegistryEntry:
        return self._entries[key]

    def get(self, key: str, default: Any = None) -> ModelRegistryEntry | None:
        return self._entries.get(key, default)

    def entries(self) -> list[ModelRegistryEntry]:
        """Return all entries as a list."""
        return list(self._entries.values())

    def keys(self) -> Iterable[str]:
        return self._entries.keys()

    def values(self) -> Iterable[ModelRegistryEntry]:
        return self._entries.values()

    def items(self):
        return self._entries.items()

    # ── Family/role queries ──

    def filter(
        self,
        family: ModelFamily | None = None,
        *,
        role: str | None = None,
        available: bool | None = None,
    ) -> list[ModelRegistryEntry]:
        """Filter entries by family + role + availability.

        Examples:
            MODEL_REGISTRY.filter(family="embedder")
            MODEL_REGISTRY.filter(family="text_llm", role="strong")
            MODEL_REGISTRY.filter(family="ocr_vision", available=True)
        """
        results: list[ModelRegistryEntry] = []
        for entry in self._entries.values():
            if family is not None and entry.family != family:
                continue
            if role is not None and entry.role != role:
                continue
            if available is not None and entry.available != available:
                continue
            results.append(entry)
        return sorted(results, key=lambda e: (e.family, e.role, e.key))

    def resolve(
        self,
        family: ModelFamily,
        role: str,
        *,
        language: str | None = None,
    ) -> str:
        """Resolve a single model key for the given (family, role).

        Args:
            family: One of the 7 ModelFamily literals.
            role: Free-form role string within the family.
            language: Optional 2-letter language code (e.g. ``"ga"``).
                If supplied and a language-specialized entry exists,
                returns the language-specialized model. Otherwise
                returns the language-agnostic entry.

        Returns:
            The canonical model key (e.g. ``"minimax-m3"``,
            ``"molmo2-8b"``, ``"ResembleAI/chatterbox"``).

        Raises:
            KeyError: if no entry matches the (family, role) tuple.
        """
        # First try: language-specialized match
        if language is not None:
            for entry in self._entries.values():
                if (
                    entry.family == family
                    and entry.role == role
                    and entry.languages is not None
                    and language in entry.languages
                ):
                    return entry.key

        # Second try: language-agnostic match
        for entry in self._entries.values():
            if (
                entry.family == family
                and entry.role == role
                and (entry.languages is None or language is None)
            ):
                return entry.key

        raise KeyError(
            f"No entry in MODEL_REGISTRY matches (family={family!r}, "
            f"role={role!r}, language={language!r}). Available roles "
            f"for family={family!r}: "
            f"{sorted({e.role for e in self.filter(family=family)})}"
        )

    # ── Pretty-printing for the control-panel notebook + CLI ──

    def summary(self) -> dict[str, Any]:
        """Return a summary dict for dashboards (by-family counts)."""
        counts: dict[str, int] = {}
        for entry in self._entries.values():
            counts[entry.family] = counts.get(entry.family, 0) + 1
        return {
            "total": len(self._entries),
            "by_family": counts,
            "available": sum(1 for e in self._entries.values() if e.available),
            "deprecated": sum(1 for e in self._entries.values() if not e.available),
        }


# ─── Singleton + module-level API ──────────────────────────────────────────

MODEL_REGISTRY = _ModelRegistry()


# Module-level helpers (so consumers can do `model_for(...)` rather than
# `MODEL_REGISTRY.resolve(...)`).
def model_for(
    family: ModelFamily,
    role: str,
    *,
    language: str | None = None,
) -> str:
    """Resolve a single model key for the given (family, role).

    Convenience wrapper around ``MODEL_REGISTRY.resolve(...)``.
    Returns the canonical model key as a string.
    """
    return MODEL_REGISTRY.resolve(family, role, language=language)


def filter_models(
    family: ModelFamily | None = None,
    *,
    role: str | None = None,
    available: bool | None = None,
) -> list[ModelRegistryEntry]:
    """Filter entries by family + role + availability.

    Convenience wrapper around ``MODEL_REGISTRY.filter(...)``.
    """
    return MODEL_REGISTRY.filter(family, role=role, available=available)


# ─── Legacy back-compat ────────────────────────────────────────────────────

# Re-export the legacy VISION_MODELS so existing imports continue
# to work. New code should use MODEL_REGISTRY.filter(family="ocr_vision").
__all__ = [
    "MODEL_REGISTRY",
    "ModelRegistryEntry",
    "ModelFamily",
    "ModelRole",
    "filter_models",
    "model_for",
    "VISION_MODELS",
    "TEXT_MODELS",
    "CLASSICAL_OCR",
]
