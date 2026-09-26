"""tuatha/asset_generation/fibo/resources.py — Dagster resources for FIBO educational image generation.

Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Provides configurable resources for:
- FIBO image generation via LiteLLM (the FiboResource)
- Validation with VLM models (the ValidationResource)

Both resources are wired through the litellm gateway + the central
MODEL_REGISTRY (per the centralized-model-registry spec).
"""
from __future__ import annotations

from typing import Any

from dagster import ConfigurableResource, InitResourceContext

# Lazy PIL import (graceful degradation when PIL isn't installed)
try:
    from PIL import Image  # type: ignore[import-not-found]
    _HAS_PIL = True
except ImportError:
    _HAS_PIL = False
    Image = None  # type: ignore[assignment]

from . import schemas  # noqa: E402


class FiboConfig:
    """The canonical FIBO 2D image generation config (Pydantic-shaped dataclass).

    Mirrors the litellm image_gen call shape + the post-processor
    settings. Stored as a per-subject config in LanceDB.
    """
    model_name: str  # the litellm model (e.g. "local/image/qwen-image")
    width: int = 1024
    height: int = 1024
    palette_hex: list[str] = []
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    seed: int = 42


class FiboResource(ConfigurableResource):
    """The FIBO image generation resource.

    Calls litellm.acompletion() against the resolved image_gen model.
    Writes the returned image as a PNG + a sidecar manifest.

    Falls back to a placeholder PNG when the litellm gateway is
    unreachable (offline dev mode).
    """
    model_name: str
    api_base: str = "http://litellm:4000/v1"
    api_key: str = "sk-litellm-dev"
    width: int = 1024
    height: int = 1024

    def render(
        self,
        prompt: str,
        palette_hex: list[str] | None = None,
        width: int | None = None,
        height: int | None = None,
        out_path: str | None = None,
    ) -> dict[str, Any]:
        """Render a single FIBO asset from a prompt.

        Args:
            prompt: The FIBO prompt (output of get_fibo_prompt())
            palette_hex: Optional palette hex codes to inject into the prompt
            width / height: Override the default dimensions
            out_path: Local file path to write the PNG

        Returns:
            Dict with: asset_id, path, url, sha256, width, height, palette_hex,
            duration_ms, stub (True if fallback was used)
        """
        import asyncio
        import base64
        import hashlib
        import json
        import os
        import time
        import uuid

        import litellm

        from datetime import datetime, UTC

        t0 = time.monotonic()
        width = width or self.width
        height = height or self.height
        palette_hex = palette_hex or []

        # Compose the full prompt with palette
        if palette_hex:
            full_prompt = f"{prompt}\n\nPalette: {' '.join(palette_hex)}"
        else:
            full_prompt = prompt

        try:
            # litellm provider routing: strip the local/ prefix
            api_model = self.model_name
            if api_model.startswith("local/"):
                parts = api_model.split("/", 2)
                if len(parts) == 3:
                    api_model = f"openai/{parts[2]}"

            response = asyncio.run(litellm.acompletion(
                model=api_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Generate a FIBO educational diagram: {full_prompt}"},
                        ],
                    },
                ],
                modalities=["image", "text"],
                timeout=180,
                api_base=self.api_base,
                api_key=self.api_key,
            ))
            # Extract the image (OpenAI ChatCompletions multimodal format)
            image_b64 = None
            choices = getattr(response, "choices", None)
            if choices and len(choices) > 0:
                message = getattr(choices[0], "message", None)
                if message is not None:
                    msg_images = getattr(message, "images", None)
                    if msg_images and len(msg_images) > 0:
                        img = msg_images[0]
                        url = getattr(img, "image_url", None)
                        if isinstance(url, dict):
                            url = url.get("url")
                        if isinstance(url, str) and url.startswith("data:image"):
                            image_b64 = url.split(",", 1)[1] if "," in url else None

            if image_b64 is None:
                raise RuntimeError("litellm returned no image for FIBO prompt")

            img_bytes = base64.b64decode(image_b64)
            sha256 = hashlib.sha256(img_bytes).hexdigest()
            if out_path:
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
            return {
                "asset_id": str(uuid.uuid4()),
                "path": out_path or f"/tmp/fibo-{sha256[:8]}.png",
                "url": f"file://{out_path}" if out_path else None,
                "sha256": sha256,
                "width": width,
                "height": height,
                "palette_hex": palette_hex,
                "duration_ms": int((time.monotonic() - t0) * 1000),
                "stub": False,
            }
        except Exception as exc:
            # Fallback: write a 1x1 placeholder PNG + sidecar manifest
            asset_id = str(uuid.uuid4())
            sha256 = hashlib.sha256(b"fibo-stub").hexdigest()
            if out_path:
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xfc\xcf\xc0P\x0f\x00\x05\x00\x01\xe2&\x05[\x00\x00\x00\x00IEND\xaeB`\x82")
            return {
                "asset_id": asset_id,
                "path": out_path,
                "url": None,
                "sha256": sha256,
                "width": width,
                "height": height,
                "palette_hex": palette_hex,
                "duration_ms": int((time.monotonic() - t0) * 1000),
                "stub": True,
                "stub_note": f"FIBO offline stub: {exc}",
            }


class ValidationResource(ConfigurableResource):
    """The VLM-based validation resource.

    Scores a generated FIBO asset against a list of validation criteria
    (typed prompts the VLM scores 0-1). If the score is below the
    threshold, the asset is rejected + the parent asset materialisation
    iterates (up to max_refinement_iterations).
    """
    model_name: str = "openai/gpt-4o-mini"  # the VLM used for validation
    api_base: str = "http://litellm:4000/v1"
    api_key: str = "sk-litellm-dev"
    score_threshold: float = 0.7

    def validate(
        self,
        asset_path: str,
        criteria: list[str],
        reference_text: str | None = None,
    ) -> dict[str, Any]:
        """Score a generated asset against the validation criteria.

        Args:
            asset_path: Local path to the PNG
            criteria: List of validation criteria (e.g. "uses palette correctly",
                      "subject icon is centred", "no text overflow")
            reference_text: Optional reference text (the source curriculum excerpt)

        Returns:
            Dict with: score (0-1), pass (bool), per_criterion_scores, stub
        """
        import asyncio
        import base64
        import json

        try:
            import litellm
        except ImportError:
            return {"score": 0.0, "pass": False, "stub": True, "stub_note": "litellm not available"}

        if not _HAS_PIL:
            return {"score": 0.0, "pass": False, "stub": True, "stub_note": "PIL not available"}

        try:
            with open(asset_path, "rb") as fh:
                img_bytes = fh.read()
            img_b64 = base64.b64encode(img_bytes).decode()

            # Use VLM to score the asset against each criterion
            prompt = f"""You are a validation VLM for the FIBO asset generator.
Score the attached asset against each of these criteria on a 0-1 scale:

{chr(10).join(f"- {c}" for c in criteria)}

{f"Reference text: {reference_text}" if reference_text else ""}

Respond with JSON: {{"per_criterion": [{{"criterion": "...", "score": 0.X}}, ...], "overall": 0.X}}
"""
            api_model = self.model_name
            if api_model.startswith("local/"):
                parts = api_model.split("/", 2)
                if len(parts) == 3:
                    api_model = f"openai/{parts[2]}"

            response = asyncio.run(litellm.acompletion(
                model=api_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                        ],
                    },
                ],
                timeout=60,
                api_base=self.api_base,
                api_key=self.api_key,
            ))
            content = response.choices[0].message.content
            # Parse JSON from content (may be wrapped in markdown)
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            scores = json.loads(content)
            overall = float(scores.get("overall", 0.0))
            return {
                "score": overall,
                "pass": overall >= self.score_threshold,
                "per_criterion_scores": scores.get("per_criterion", []),
                "stub": False,
            }
        except Exception as exc:
            return {
                "score": 0.0,
                "pass": False,
                "stub": True,
                "stub_note": f"VLM validation failed: {exc}",
                "per_criterion_scores": [],
            }


__all__ = ["FiboResource", "ValidationResource", "FiboConfig"]
