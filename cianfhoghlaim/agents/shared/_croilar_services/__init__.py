"""Services for Artwork Processing.

Vision analysis and image generation services using LiteLLM
as a gateway to local and cloud models.

Services:
    - VisionService: Analyze artwork with vision models
    - ImageGenerationService: Generate artwork with InvokeAI
    - StyleAnalyzer: Extract visual style for generation

Usage:
    from services import VisionService, ImageGenerationService

    vision = VisionService()
    analysis = await vision.analyze_artwork(image_bytes)

    generator = ImageGenerationService()
    new_artwork = await generator.generate(
        prompt="album cover",
        style_reference=style_analysis
    )
"""

from services.image_generation import (
    GeneratedImage,
    ImageGenerationService,
    generate_artwork,
)
from services.vision import (
    ArtworkAnalysis,
    StyleAnalysis,
    VisionService,
    analyze_artwork,
)

__all__ = [
    "ArtworkAnalysis",
    "GeneratedImage",
    "ImageGenerationService",
    "StyleAnalysis",
    "VisionService",
    "analyze_artwork",
    "generate_artwork",
]
