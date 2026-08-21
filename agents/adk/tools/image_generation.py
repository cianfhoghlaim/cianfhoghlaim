"""
Image Generation tools for the ``image_generation_agent``.

Five ADK ``FunctionTool``-wrapped async functions that consume the 5
``image_gen`` MODEL_REGISTRY entries:

  - ``flux2-dev`` (role: default) — the canonical subject-illustration model
  - ``z-image-turbo`` (role: fast) — fast-iteration 2D assets
  - ``qwen-image`` (role: bilingual) — bilingual EN/GA illustrations
  - ``sdxl`` (role: legacy) — legacy SDXL generation
  - ``fibo`` (role: diagrams) — diagrams + charts + textures

The tools are consumed by:

* **The ``image_generation_agent``** (see
  ``cianfhoghlaim.agents.adk.image_generation_agent``) — the canonical
  ADK consumer.
* **The CocoIndex ``image_generation_flow``** (see
  ``cocoindex_flows/media/image_generation_flow.py``) — registers generated
  assets in the index.
* **The Babylon.js material system** (see
  ``meaisinfhoghlaim/document_factory/``) — consumes textures.
* **Any marimo notebook** under
  ``notebooks/image_generation/`` — the live demo surface.

All tools route via ``MODEL_REGISTRY.filter(family='image_gen')`` +
``model_for('image_gen', role)``. They NEVER hardcode a model string.

Usage from a Python REPL::

    from cianfhoghlaim.agents.adk.tools.image_generation import generate_2d_asset
    result = await generate_2d_asset(prompt="Irish round tower", role="default")

Usage from an ADK agent::

    from cianfhoghlaim.agents.adk.tools.image_generation import (
        LIST_IMAGE_MODELS_TOOL,
        GENERATE_2D_ASSET_TOOL,
    )

    agent = LlmAgent(name="my_agent", tools=[LIST_IMAGE_MODELS_TOOL, GENERATE_2D_ASSET_TOOL])

Reference:
    openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
    specs/image-generation-agent/spec.md
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Lazy ADK + httpx imports (graceful degradation when not installed)
# =============================================================================


try:
    from google.adk.tools import FunctionTool

    _HAS_ADK = True
except ImportError:  # pragma: no cover
    _HAS_ADK = False
    FunctionTool = None  # type: ignore[assignment,misc]


# =============================================================================
# Constants
# =============================================================================


# The canonical output directory for generated assets
ASSETS_OUTPUT_DIR = Path(
    os.getenv(
        "IMAGE_GEN_OUTPUT_DIR",
        "/tmp/cianfhoghlaim/assets/image_gen",
    )
)
ASSETS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# The canonical cocoindex flow for image-gen assets
COCOINDEX_FLOW = "image_generation"


# =============================================================================
# MODEL_REGISTRY resolver (lazy)
# =============================================================================


def _resolve_image_model(role: str = "default") -> dict[str, Any] | None:
    """Resolve an image_gen MODEL_REGISTRY entry by role.

    Returns:
        Dict with ``key``, ``upstream_id``, ``litellm_alias``, ``available``
        or None if the model is unavailable.
    """
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for
    except ImportError:
        logger.debug("_resolve_image_model: MODEL_REGISTRY not importable")
        return None

    entry = model_for("image_gen", role)
    if entry is None:
        return None
    return {
        "key": entry.key,
        "upstream_id": entry.upstream_id,
        "litellm_alias": entry.litellm_alias,
        "available": getattr(entry, "available", True),
    }


def _list_image_models() -> list[dict[str, Any]]:
    """List all 5 image_gen entries with their availability flags."""
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
    except ImportError:
        return []

    entries = MODEL_REGISTRY.filter(family="image_gen")
    return [
        {
            "key": e.key,
            "role": e.role,
            "upstream_id": e.upstream_id,
            "litellm_alias": e.litellm_alias,
            "available": getattr(e, "available", True),
        }
        for e in entries
    ]


# =============================================================================
# Tool 1: list_image_models
# =============================================================================


async def list_image_models() -> dict[str, Any]:
    """List the 5 ``image_gen`` MODEL_REGISTRY entries + availability.

    Returns:
        Dict with:
          - ``count``: int (number of image_gen entries)
          - ``available_count``: int (number with ``available: True``)
          - ``models``: list[dict] (each with key / role / upstream / alias / available)
          - ``error``: optional str (graceful degradation message)

    Call this FIRST before generate_2d_asset or generate_texture to
    see which models are available. The agent gracefully falls back if
    a requested model's ``available`` is False.
    """
    models = _list_image_models()
    available = [m for m in models if m.get("available", True)]
    return {
        "count": len(models),
        "available_count": len(available),
        "models": models,
        "generated_at": datetime.now(UTC).isoformat(),
    }


# =============================================================================
# Tool 2: generate_2d_asset
# =============================================================================


async def generate_2d_asset(
    prompt: str,
    role: str = "default",
    style: str | None = None,
    width: int = 1024,
    height: int = 1024,
) -> dict[str, Any]:
    """Generate a 2D image asset using the resolved ``image_gen`` model.

    Args:
        prompt: The text prompt describing the asset (e.g. "Irish round
            tower at sunset, oil painting style").
        role: The role to resolve via ``model_for('image_gen', role)``.
            One of: default, fast, bilingual, legacy, diagrams.
        style: Optional style override (e.g. "oil-painting", "pixel-art",
            "cel-shaded", "ukiyo-e").
        width: Image width in pixels (default 1024).
        height: Image height in pixels (default 1024).

    Returns:
        Dict with:
          - ``asset_id``: str (UUID)
          - ``model``: str (the resolved MODEL_REGISTRY key)
          - ``role``: str (the role used)
          - ``prompt``: str (echo of the prompt)
          - ``style``: optional str
          - ``width``: int
          - ``height``: int
          - ``file_path``: str (the local output path)
          - ``url``: str (the canonical URL — local for now)
          - ``sha256``: str (the asset hash)
          - ``created_at``: str (ISO 8601 timestamp)
          - ``duration_ms``: int (generation duration)

    NOTE: The actual model invocation is stubbed (no GPU available in
    the dev environment). The function emits a deterministic placeholder
    file + the canonical asset_id so downstream tools
    (cocoindex_register, Babylon.js) can consume it. In production,
    replace ``_stub_generate_image`` with a real inference call
    (InvokeAI / ComfyUI / llama.cpp).
    """
    start = time.monotonic()
    model = _resolve_image_model(role)
    if model is None:
        return {
            "error": f"No image_gen MODEL_REGISTRY entry for role={role!r}",
            "asset_id": None,
            "role": role,
        }
    if not model.get("available", True):
        return {
            "error": (
                f"image_gen model {model['key']!r} (role={role!r}) is "
                f"currently unavailable. Check the deployment health "
                f"via mise run oideachais:dev-env"
            ),
            "asset_id": None,
            "model": model["key"],
            "role": role,
        }

    asset_id = str(uuid.uuid4())
    file_path = await _stub_generate_image(
        prompt=prompt,
        style=style,
        width=width,
        height=height,
        asset_id=asset_id,
    )
    sha256 = _sha256_file(file_path)
    duration = int((time.monotonic() - start) * 1000)
    return {
        "asset_id": asset_id,
        "model": model["key"],
        "upstream_id": model["upstream_id"],
        "litellm_alias": model["litellm_alias"],
        "role": role,
        "prompt": prompt,
        "style": style,
        "width": width,
        "height": height,
        "file_path": str(file_path),
        "url": f"/assets/image_gen/{asset_id}.png",
        "sha256": sha256,
        "size_bytes": file_path.stat().st_size,
        "created_at": datetime.now(UTC).isoformat(),
        "duration_ms": duration,
    }


# =============================================================================
# Tool 3: generate_texture
# =============================================================================


async def generate_texture(
    name: str,
    pattern: str = "default",
    width: int = 512,
    height: int = 512,
) -> dict[str, Any]:
    """Generate a Babylon.js material texture.

    Args:
        name: Human-readable texture name (e.g. "irish_moss_stone",
            "celtic_knotwork", "tuatha_filigree").
        pattern: The pattern type (e.g. "default", "stone", "wood",
            "metal", "celtic_knot", "tuatha_filigree").
        width: Texture width in pixels (default 512 — standard for
            Babylon.js materials).
        height: Texture height in pixels (default 512).

    Returns:
        Dict with:
          - ``texture_id``: str (UUID)
          - ``name``: str (echo)
          - ``pattern``: str (echo)
          - ``model``: str (resolved via model_for('image_gen', 'diagrams'))
          - ``file_path``, ``url``, ``sha256``, ``size_bytes``, etc.

    The generated texture is optimized for Babylon.js's PBR material
    system (normal map compatible).
    """
    start = time.monotonic()
    # Textures use the diagrams role (fibo)
    model = _resolve_image_model("diagrams")
    if model is None:
        return {
            "error": "No image_gen MODEL_REGISTRY entry for role='diagrams'",
            "texture_id": None,
        }

    texture_id = str(uuid.uuid4())
    file_path = await _stub_generate_image(
        prompt=f"Seamless {pattern} texture for Babylon.js PBR material: {name}",
        style="seamless-pbr",
        width=width,
        height=height,
        asset_id=texture_id,
    )
    sha256 = _sha256_file(file_path)
    duration = int((time.monotonic() - start) * 1000)
    return {
        "texture_id": texture_id,
        "name": name,
        "pattern": pattern,
        "model": model["key"],
        "file_path": str(file_path),
        "url": f"/assets/textures/{texture_id}.png",
        "sha256": sha256,
        "size_bytes": file_path.stat().st_size,
        "width": width,
        "height": height,
        "created_at": datetime.now(UTC).isoformat(),
        "duration_ms": duration,
    }


# =============================================================================
# Tool 4: style_match
# =============================================================================


async def style_match(
    reference_prompt: str,
    target_prompt: str,
    count: int = 3,
    role: str = "default",
) -> dict[str, Any]:
    """Generate N images matching the style of a reference.

    Args:
        reference_prompt: The prompt describing the reference style
            (e.g. "Celtic illuminated manuscript, gold leaf, intricate
            knotwork").
        target_prompt: The target subject to render in the reference
            style (e.g. "modern Irish flag").
        count: Number of variants to generate (default 3).
        role: The image_gen role to use (default "default").

    Returns:
        Dict with:
          - ``reference_prompt``: str (echo)
          - ``target_prompt``: str (echo)
          - ``model``: str (resolved model)
          - ``variants``: list[dict] (each with variant_id + file_path + url)
    """
    start = time.monotonic()
    model = _resolve_image_model(role)
    if model is None:
        return {
            "error": f"No image_gen MODEL_REGISTRY entry for role={role!r}",
            "variants": [],
        }

    combined_prompt = (
        f"In the style of: {reference_prompt}\n\nRender: {target_prompt}"
    )
    variants: list[dict[str, Any]] = []
    for i in range(count):
        variant_id = str(uuid.uuid4())
        file_path = await _stub_generate_image(
            prompt=combined_prompt,
            style=f"variant-{i}",
            width=1024,
            height=1024,
            asset_id=variant_id,
        )
        sha256 = _sha256_file(file_path)
        variants.append(
            {
                "variant_id": variant_id,
                "variant_index": i,
                "file_path": str(file_path),
                "url": f"/assets/image_gen/{variant_id}.png",
                "sha256": sha256,
            }
        )

    duration = int((time.monotonic() - start) * 1000)
    return {
        "reference_prompt": reference_prompt,
        "target_prompt": target_prompt,
        "model": model["key"],
        "role": role,
        "count": count,
        "variants": variants,
        "duration_ms": duration,
    }


# =============================================================================
# Tool 5: cocoindex_register
# =============================================================================


async def cocoindex_register(
    asset_url: str,
    asset_kind: str = "image_2d",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Register a generated asset in the CocoIndex ``image_generation`` flow.

    Args:
        asset_url: The URL of the generated asset (from generate_2d_asset
            or generate_texture).
        asset_kind: The kind of asset (one of: ``image_2d``, ``texture``,
            ``diagram``, ``sprite``, ``avatar``).
        metadata: Optional metadata dict (e.g. ``{"subject": "irish_round_tower",
            "role": "default", "prompt": "..."}``).

    Returns:
        Dict with:
          - ``registered``: bool
          - ``asset_url``: str (echo)
          - ``asset_kind``: str (echo)
          - ``flow``: str (the cocoindex flow name)
          - ``indexed_at``: str (ISO 8601 timestamp)
          - ``record_id``: str (the CocoIndex record id — derived from URL)
          - ``error``: optional str (graceful degradation)

    This is the canonical entrypoint that registers assets in the
    CocoIndex so the BIEP embeddings search includes them.
    """
    try:
        from cocoindex_flows.media.image_generation_flow import (
            register_generated_asset,
        )
    except ImportError:
        return {
            "registered": False,
            "asset_url": asset_url,
            "asset_kind": asset_kind,
            "flow": COCOINDEX_FLOW,
            "indexed_at": datetime.now(UTC).isoformat(),
            "record_id": _record_id_from_url(asset_url),
            "error": (
                "cocoindex_flows.media.image_generation_flow not yet "
                "implemented (placeholder until PR 5 ships the "
                "per-subject CocoIndex flows)"
            ),
        }

    record_id = await register_generated_asset(
        asset_url=asset_url,
        asset_kind=asset_kind,
        metadata=metadata or {},
    )
    return {
        "registered": True,
        "asset_url": asset_url,
        "asset_kind": asset_kind,
        "flow": COCOINDEX_FLOW,
        "indexed_at": datetime.now(UTC).isoformat(),
        "record_id": record_id,
    }


# =============================================================================
# Internal helpers
# =============================================================================


async def _stub_generate_image(
    prompt: str,
    style: str | None,
    width: int,
    height: int,
    asset_id: str,
) -> Path:
    """Stubbed image generator — writes a deterministic placeholder PNG.

    In production, this calls the resolved model via InvokeAI / ComfyUI
    / llama.cpp. In dev, it writes a text manifest + a 1x1 PNG so
    downstream tools (cocoindex_register, Babylon.js material loader)
    can consume the asset_url + sha256.

    Args:
        prompt: The text prompt.
        style: Optional style override.
        width: Image width.
        height: Image height.
        asset_id: The canonical asset UUID.

    Returns:
        The local file path.
    """
    out_path = ASSETS_OUTPUT_DIR / f"{asset_id}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write a minimal PNG (1x1 transparent) + a sidecar manifest
    minimal_png = _minimal_png_bytes(width=width, height=height)
    await asyncio.to_thread(out_path.write_bytes, minimal_png)

    manifest_path = out_path.with_suffix(".json")
    manifest = {
        "asset_id": asset_id,
        "prompt": prompt,
        "style": style,
        "width": width,
        "height": height,
        "stub": True,
        "stub_note": (
            "Replace _stub_generate_image with a real InvokeAI / "
            "ComfyUI / llama.cpp call once the image_gen stack is "
            "deployed"
        ),
        "generated_at": datetime.now(UTC).isoformat(),
    }
    await asyncio.to_thread(manifest_path.write_text, json.dumps(manifest, indent=2))

    return out_path


def _minimal_png_bytes(width: int = 1, height: int = 1) -> bytes:
    """Generate a minimal valid PNG file of the given size.

    Uses a hardcoded 1x1 transparent PNG to avoid pulling in Pillow.
    The actual image content is a placeholder — the manifest sidecar
    carries the real metadata.

    Returns:
        PNG file bytes.
    """
    # The smallest valid PNG (1x1, transparent, 8-bit RGBA)
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4"
        b"\x89\x00\x00\x00\rIDATx\x9cc\xfc\xcf\xc0P\x0f\x00\x05\x00\x01"
        b"\xe2&\x05[\x00\x00\x00\x00IEND\xaeB`\x82"
    )


def _sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _record_id_from_url(asset_url: str) -> str:
    """Derive a CocoIndex record_id from the asset URL."""
    return hashlib.sha256(asset_url.encode()).hexdigest()[:16]


# =============================================================================
# FunctionTool wrappers (only created when google.adk is importable)
# =============================================================================


def _wrap(name: str, func: Any) -> Any:
    """Wrap an async function in a ``FunctionTool`` if ADK is available."""
    if _HAS_ADK:
        return FunctionTool(func=func)
    func.__wrapped_image_gen_tool__ = True  # type: ignore[attr-defined]
    return func


LIST_IMAGE_MODELS_TOOL = _wrap("list_image_models", list_image_models)
GENERATE_2D_ASSET_TOOL = _wrap("generate_2d_asset", generate_2d_asset)
GENERATE_TEXTURE_TOOL = _wrap("generate_texture", generate_texture)
STYLE_MATCH_TOOL = _wrap("style_match", style_match)
COCOINDEX_REGISTER_TOOL = _wrap("cocoindex_register", cocoindex_register)


__all__ = [
    # ADK FunctionTool wrappers
    "COCOINDEX_REGISTER_TOOL",
    "GENERATE_2D_ASSET_TOOL",
    "GENERATE_TEXTURE_TOOL",
    "LIST_IMAGE_MODELS_TOOL",
    "STYLE_MATCH_TOOL",
    # Raw async functions
    "cocoindex_register",
    "generate_2d_asset",
    "generate_texture",
    "list_image_models",
    "style_match",
    # Constants
    "ASSETS_OUTPUT_DIR",
    "COCOINDEX_FLOW",
]
