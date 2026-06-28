"""Image Generation Service.

Generates album artwork using local image models via InvokeAI.
Supports style transfer, variations, and guided generation.

Models (in fallback order):
    1. FLUX.2-dev - Highest quality, slower
    2. Z-Image-Turbo - Fast, good quality
    3. Qwen-Image - Complex text rendering
    4. SDXL - Reliable fallback
    5. Fibo - Lightweight MLX

Usage:
    from services.image_generation import ImageGenerationService, generate_artwork

    # Async API
    service = ImageGenerationService()
    result = await service.generate(
        prompt="abstract album cover with geometric shapes",
        style_reference=style_analysis,
        size=(1024, 1024),
    )

    # Save result
    result.save("output.png")

    # Convenience function
    result = await generate_artwork(prompt, style="abstract", genre="electronic")
"""

import base64
import io
import os
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import httpx
from PIL import Image

# InvokeAI configuration
INVOKEAI_URL = os.environ.get("INVOKEAI_URL", "http://localhost:9090")
LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000")
LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY", "sk-1234")

# Model preferences (fallback chain)
IMAGE_MODELS = [
    "local/image/flux2-dev",
    "local/image/z-image-turbo",
    "local/image/qwen-image",
    "local/image/sdxl",
    "local/image/fibo",
]


class ImageSize(StrEnum):
    """Standard image sizes."""

    SQUARE_512 = "512x512"
    SQUARE_768 = "768x768"
    SQUARE_1024 = "1024x1024"
    PORTRAIT_768 = "768x1024"
    LANDSCAPE_1024 = "1024x768"
    WIDE_1536 = "1536x768"


class ArtworkStyle(StrEnum):
    """Predefined artwork styles with prompt modifiers."""

    ABSTRACT = "abstract art, non-representational, geometric shapes, flowing forms"
    MINIMALIST = "minimalist design, clean lines, simple shapes, negative space"
    PHOTOGRAPHIC = "photorealistic, high detail, professional photography"
    ILLUSTRATED = "digital illustration, artistic, stylized, hand-drawn feel"
    PSYCHEDELIC = "psychedelic art, vibrant colors, surreal, trippy patterns"
    GEOMETRIC = "geometric patterns, mathematical, symmetrical, precise shapes"
    SURREAL = "surrealist art, dreamlike, unexpected combinations, Salvador Dali inspired"
    COLLAGE = "collage style, mixed media, layered elements, cut-out aesthetic"
    GRADIENT = "gradient design, smooth color transitions, ombre, color blending"
    RETRO = "retro design, vintage aesthetic, 80s/90s vibes, nostalgic"
    FUTURISTIC = "futuristic design, sci-fi aesthetic, cyberpunk, neon accents"
    ORGANIC = "organic shapes, natural forms, fluid, nature-inspired"
    GLITCH = "glitch art, digital distortion, corrupted data aesthetic, VHS"
    NEON = "neon lights, glowing, dark background, synthwave aesthetic"


class MusicGenreStyle(StrEnum):
    """Music genre-specific style modifiers."""

    ELECTRONIC = "electronic music aesthetic, digital, synthesized, club visuals"
    AMBIENT = "ambient atmosphere, ethereal, soft, floating, peaceful"
    DNB = "drum and bass energy, dynamic, fast-moving, urban"
    LIQUID = "liquid drum and bass, smooth, flowing water, calming"
    TECHNO = "techno aesthetic, industrial, mechanical, dark warehouse"
    HOUSE = "house music vibes, uplifting, colorful, dance"
    CHILLOUT = "chillout atmosphere, relaxed, sunset colors, lounge"
    JAZZ = "jazz aesthetic, vintage, sophisticated, warm tones"
    CLASSICAL = "classical music elegance, orchestral, refined, timeless"


@dataclass
class GeneratedImage:
    """Result of image generation."""

    image_bytes: bytes
    prompt: str
    model: str
    width: int
    height: int
    seed: int = 0
    guidance_scale: float = 7.5
    steps: int = 20
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def image(self) -> Image.Image:
        """Get PIL Image object."""
        return Image.open(io.BytesIO(self.image_bytes))

    def save(self, path: str, format: str = "PNG") -> None:
        """Save image to file.

        Args:
            path: Output file path
            format: Image format (PNG, JPEG, WEBP)
        """
        self.image.save(path, format=format)

    def to_base64(self) -> str:
        """Get base64-encoded image.

        Returns:
            Base64 string
        """
        return base64.b64encode(self.image_bytes).decode("utf-8")

    def to_data_url(self) -> str:
        """Get data URL for embedding.

        Returns:
            Data URL string
        """
        img = self.image
        mime = f"image/{img.format.lower()}" if img.format else "image/png"
        return f"data:{mime};base64,{self.to_base64()}"


class ImageGenerationService:
    """Image generation service using InvokeAI via LiteLLM."""

    def __init__(
        self,
        api_url: str = LITELLM_URL,
        api_key: str = LITELLM_API_KEY,
        invokeai_url: str = INVOKEAI_URL,
        preferred_model: str | None = None,
    ):
        """Initialize image generation service.

        Args:
            api_url: LiteLLM gateway URL
            api_key: API key for LiteLLM
            invokeai_url: Direct InvokeAI URL (for advanced features)
            preferred_model: Override default model selection
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.invokeai_url = invokeai_url.rstrip("/")
        self.preferred_model = preferred_model
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=300.0,  # Image generation can be slow
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _call_image_model(
        self,
        prompt: str,
        size: tuple[int, int] = (1024, 1024),
        model: str | None = None,
        negative_prompt: str = "",
        guidance_scale: float = 7.5,
        steps: int = 20,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Call image generation model via LiteLLM.

        Args:
            prompt: Generation prompt
            size: Image dimensions (width, height)
            model: Model to use
            negative_prompt: What to avoid
            guidance_scale: CFG scale
            steps: Inference steps
            seed: Random seed for reproducibility

        Returns:
            API response with generated image
        """
        if not self._client:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=300.0,
            )

        models_to_try = [model] if model else IMAGE_MODELS

        last_error = None
        for current_model in models_to_try:
            try:
                # Use OpenAI images/generations endpoint format
                # LiteLLM routes this to InvokeAI
                payload = {
                    "model": current_model,
                    "prompt": prompt,
                    "size": f"{size[0]}x{size[1]}",
                    "n": 1,
                    "response_format": "b64_json",
                }

                # Add optional parameters if supported
                if negative_prompt:
                    payload["negative_prompt"] = negative_prompt
                if seed is not None:
                    payload["seed"] = seed

                response = await self._client.post(
                    f"{self.api_url}/v1/images/generations",
                    json=payload,
                )

                if response.status_code == 200:
                    return response.json()

                last_error = f"HTTP {response.status_code}: {response.text}"

            except Exception as e:
                last_error = str(e)
                continue

        raise Exception(f"All image models failed. Last error: {last_error}")

    def _build_prompt(
        self,
        base_prompt: str,
        style: ArtworkStyle | str | None = None,
        genre: MusicGenreStyle | str | None = None,
        style_reference: Any = None,  # StyleAnalysis from vision service
        additional_modifiers: list[str] | None = None,
    ) -> str:
        """Build complete generation prompt.

        Args:
            base_prompt: Core subject/concept
            style: Artwork style preset or custom
            genre: Music genre style preset
            style_reference: Analysis from VisionService for style transfer
            additional_modifiers: Extra prompt terms

        Returns:
            Complete prompt string
        """
        parts = [base_prompt]

        # Add style preset
        if isinstance(style, ArtworkStyle):
            parts.append(style.value)
        elif isinstance(style, str) and style:
            parts.append(style)

        # Add genre style
        if isinstance(genre, MusicGenreStyle):
            parts.append(genre.value)
        elif isinstance(genre, str) and genre:
            parts.append(f"{genre} music aesthetic")

        # Add style reference from vision analysis
        if style_reference:
            if hasattr(style_reference, "generation_prompt") and style_reference.generation_prompt:
                parts.append(style_reference.generation_prompt)
            elif hasattr(style_reference, "style") and style_reference.style:
                style = style_reference.style
                if style.primary_style:
                    parts.append(f"{style.primary_style} style")
                if style.mood:
                    parts.append(f"{style.mood} mood")
                if style.dominant_colors:
                    colors = ", ".join(style.dominant_colors[:3])
                    parts.append(f"color palette: {colors}")
                if style.texture:
                    parts.append(f"{style.texture} texture")
                if style.lighting:
                    parts.append(f"{style.lighting} lighting")

        # Add quality modifiers
        parts.extend([
            "album cover artwork",
            "high quality",
            "detailed",
            "professional design",
        ])

        # Add custom modifiers
        if additional_modifiers:
            parts.extend(additional_modifiers)

        return ", ".join(parts)

    def _default_negative_prompt(self) -> str:
        """Get default negative prompt for artwork generation."""
        return (
            "text, watermark, signature, logo, words, letters, "
            "blurry, low quality, pixelated, distorted, "
            "cropped, out of frame, disfigured, "
            "ugly, bad anatomy, bad proportions"
        )

    async def generate(
        self,
        prompt: str,
        style: ArtworkStyle | str | None = None,
        genre: MusicGenreStyle | str | None = None,
        style_reference: Any = None,
        size: tuple[int, int] | ImageSize = ImageSize.SQUARE_1024,
        negative_prompt: str | None = None,
        guidance_scale: float = 7.5,
        steps: int = 20,
        seed: int | None = None,
        model: str | None = None,
    ) -> GeneratedImage:
        """Generate album artwork.

        Args:
            prompt: Base prompt describing the artwork
            style: Artwork style preset or custom string
            genre: Music genre style preset
            style_reference: Analysis from VisionService for style transfer
            size: Image dimensions or preset
            negative_prompt: What to avoid (uses default if None)
            guidance_scale: CFG scale (higher = more prompt adherence)
            steps: Inference steps (more = higher quality, slower)
            seed: Random seed for reproducibility
            model: Override model selection

        Returns:
            GeneratedImage with result
        """
        # Parse size
        if isinstance(size, ImageSize):
            w, h = map(int, size.value.split("x"))
        else:
            w, h = size

        # Build full prompt
        full_prompt = self._build_prompt(
            prompt, style, genre, style_reference
        )

        # Get negative prompt
        neg_prompt = negative_prompt if negative_prompt is not None else self._default_negative_prompt()

        # Call model
        response = await self._call_image_model(
            prompt=full_prompt,
            size=(w, h),
            model=model or self.preferred_model,
            negative_prompt=neg_prompt,
            guidance_scale=guidance_scale,
            steps=steps,
            seed=seed,
        )

        # Parse response
        data = response.get("data", [{}])[0]
        b64_image = data.get("b64_json", "")

        if not b64_image:
            raise Exception("No image data in response")

        image_bytes = base64.b64decode(b64_image)

        return GeneratedImage(
            image_bytes=image_bytes,
            prompt=full_prompt,
            model=model or self.preferred_model or IMAGE_MODELS[0],
            width=w,
            height=h,
            seed=seed or 0,
            guidance_scale=guidance_scale,
            steps=steps,
            metadata={
                "negative_prompt": neg_prompt,
                "style": style.value if isinstance(style, ArtworkStyle) else style,
                "genre": genre.value if isinstance(genre, MusicGenreStyle) else genre,
            },
        )

    async def generate_variations(
        self,
        image_bytes: bytes,
        prompt: str | None = None,
        num_variations: int = 4,
        strength: float = 0.7,
        **kwargs,
    ) -> list[GeneratedImage]:
        """Generate variations of an existing artwork.

        Args:
            image_bytes: Source image
            prompt: Optional prompt to guide variations
            num_variations: Number of variations to generate
            strength: How much to change (0.0-1.0, higher = more change)
            **kwargs: Additional parameters for generate()

        Returns:
            List of GeneratedImage variations
        """
        # This would use img2img endpoint in InvokeAI
        # For now, generate new images with similar prompts
        variations = []

        for i in range(num_variations):
            seed = kwargs.pop("seed", None)
            if seed is None:
                import random
                seed = random.randint(0, 2**32 - 1)

            result = await self.generate(
                prompt=prompt or "album cover variation",
                seed=seed + i,
                **kwargs,
            )
            variations.append(result)

        return variations

    async def style_transfer(
        self,
        content_prompt: str,
        style_image_bytes: bytes,
        style_strength: float = 0.75,
        **kwargs,
    ) -> GeneratedImage:
        """Generate artwork with style from reference image.

        Args:
            content_prompt: What to generate
            style_image_bytes: Reference image for style
            style_strength: How closely to follow style (0.0-1.0)
            **kwargs: Additional generation parameters

        Returns:
            GeneratedImage with transferred style
        """
        # Analyze style image first
        from services.vision import VisionService

        async with VisionService() as vision:
            style_analysis = await vision.analyze_artwork(style_image_bytes)

        # Generate with style reference
        return await self.generate(
            prompt=content_prompt,
            style_reference=style_analysis,
            guidance_scale=kwargs.pop("guidance_scale", 7.5 + (style_strength * 5)),
            **kwargs,
        )


async def generate_artwork(
    prompt: str,
    style: ArtworkStyle | str | None = None,
    genre: MusicGenreStyle | str | None = None,
    size: tuple[int, int] | ImageSize = ImageSize.SQUARE_1024,
    **kwargs,
) -> GeneratedImage:
    """Convenience function to generate artwork.

    Args:
        prompt: Base prompt
        style: Artwork style
        genre: Music genre style
        size: Image dimensions
        **kwargs: Additional parameters

    Returns:
        GeneratedImage
    """
    async with ImageGenerationService() as service:
        return await service.generate(
            prompt=prompt,
            style=style,
            genre=genre,
            size=size,
            **kwargs,
        )


if __name__ == "__main__":
    import asyncio
    import sys

    async def main():
        prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "abstract album cover"

        print(f"Generating: {prompt}")
        result = await generate_artwork(
            prompt=prompt,
            style=ArtworkStyle.ABSTRACT,
            genre=MusicGenreStyle.ELECTRONIC,
        )

        output_path = "generated_artwork.png"
        result.save(output_path)
        print(f"Saved to {output_path}")
        print(f"Full prompt: {result.prompt}")

    asyncio.run(main())
