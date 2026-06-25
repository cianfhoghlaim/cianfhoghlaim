"""Celtic Asset Generation Service

GPU-accelerated image generation for Celtic game assets using LiteLLM gateway.

Supported models:
- FLUX.2-dev: High-quality generation for rare items
- Z-Image-Turbo: Fast generation for common items
- Qwen-Image-Edit: Inpainting and style transfer

Asset types:
- Character portraits (procedural Celtic faces)
- Item icons (weapons, armor, artifacts)
- Clan heraldry (shields, banners)
- Territory tiles (terrain, landmarks)
"""

from .service import AssetGenerationService
from .models import (
    AssetRequest,
    AssetResponse,
    AssetType,
    CelticStyle,
    GenerationModel,
)
from .prompts import CelticPromptGenerator

__all__ = [
    "AssetGenerationService",
    "AssetRequest",
    "AssetResponse",
    "AssetType",
    "CelticStyle",
    "GenerationModel",
    "CelticPromptGenerator",
]
