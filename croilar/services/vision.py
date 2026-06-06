"""Vision Analysis Service.

Analyzes album artwork using vision-language models via LiteLLM.
Extracts style characteristics, mood, colors, and composition
for use in style transfer and generation.

Models (in fallback order):
    1. local/vision/qwen3-vl - Best quality, 30B VLM
    2. local/vision/glm-4.6v-flash - Fast with function calling
    3. local/vision/moondream2 - Lightweight (1.8B)
    4. gemini-1.5-pro - Cloud fallback

Usage:
    from services.vision import VisionService, analyze_artwork

    # Async API
    service = VisionService()
    analysis = await service.analyze_artwork(image_bytes)

    # Convenience function
    analysis = await analyze_artwork(image_path)
"""

import base64
import io
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import httpx
from PIL import Image

# LiteLLM configuration
LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000")
LITELLM_API_KEY = os.environ.get("LITELLM_API_KEY", "sk-1234")

# Model preferences (fallback chain)
VISION_MODELS = [
    "local/vision/qwen3-vl",
    "local/vision/glm-4.6v-flash",
    "local/vision/moondream2",
    "gemini-1.5-pro",
]


class ArtStyle(str, Enum):
    """Visual art style categories."""

    ABSTRACT = "abstract"
    PHOTOGRAPHIC = "photographic"
    ILLUSTRATED = "illustrated"
    MINIMALIST = "minimalist"
    PSYCHEDELIC = "psychedelic"
    GEOMETRIC = "geometric"
    SURREAL = "surreal"
    COLLAGE = "collage"
    TYPOGRAPHIC = "typographic"
    GRADIENT = "gradient"
    RETRO = "retro"
    FUTURISTIC = "futuristic"
    ORGANIC = "organic"
    GLITCH = "glitch"
    THREE_D = "3d"


class MoodCategory(str, Enum):
    """Mood/emotional categories."""

    ENERGETIC = "energetic"
    CALM = "calm"
    DARK = "dark"
    UPLIFTING = "uplifting"
    MELANCHOLIC = "melancholic"
    MYSTERIOUS = "mysterious"
    DREAMY = "dreamy"
    AGGRESSIVE = "aggressive"
    NOSTALGIC = "nostalgic"
    ETHEREAL = "ethereal"


@dataclass
class StyleAnalysis:
    """Detailed visual style analysis."""

    primary_style: str = ""
    secondary_styles: list[str] = field(default_factory=list)
    color_scheme: str = ""  # e.g., "monochromatic", "complementary", "analogous"
    dominant_colors: list[str] = field(default_factory=list)
    accent_colors: list[str] = field(default_factory=list)
    mood: str = ""
    mood_keywords: list[str] = field(default_factory=list)
    composition: str = ""  # e.g., "centered", "rule_of_thirds", "asymmetric"
    visual_weight: str = ""  # e.g., "heavy", "light", "balanced"
    texture: str = ""  # e.g., "smooth", "grainy", "textured"
    lighting: str = ""  # e.g., "bright", "dark", "high_contrast"
    depth: str = ""  # e.g., "flat", "layered", "3d"
    movement: str = ""  # e.g., "static", "dynamic", "flowing"


@dataclass
class ArtworkAnalysis:
    """Complete artwork analysis result."""

    description: str = ""
    style: StyleAnalysis | None = None
    genre_associations: list[str] = field(default_factory=list)
    visual_elements: list[str] = field(default_factory=list)
    text_detected: str = ""
    subjects: list[str] = field(default_factory=list)
    influences: list[str] = field(default_factory=list)
    generation_prompt: str = ""
    raw_response: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "style": vars(self.style) if self.style else None,
            "genre_associations": self.genre_associations,
            "visual_elements": self.visual_elements,
            "text_detected": self.text_detected,
            "subjects": self.subjects,
            "influences": self.influences,
            "generation_prompt": self.generation_prompt,
        }


class VisionService:
    """Vision analysis service using LiteLLM."""

    def __init__(
        self,
        api_url: str = LITELLM_URL,
        api_key: str = LITELLM_API_KEY,
        preferred_model: str | None = None,
    ):
        """Initialize vision service.

        Args:
            api_url: LiteLLM gateway URL
            api_key: API key for LiteLLM
            preferred_model: Override default model selection
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.preferred_model = preferred_model
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _encode_image(self, image_bytes: bytes) -> str:
        """Encode image bytes to base64 data URL.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Base64 data URL string
        """
        # Detect format
        img = Image.open(io.BytesIO(image_bytes))
        mime_type = f"image/{img.format.lower()}" if img.format else "image/jpeg"

        b64 = base64.b64encode(image_bytes).decode("utf-8")
        return f"data:{mime_type};base64,{b64}"

    async def _call_vision_model(
        self,
        image_data: str,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Call vision model via LiteLLM.

        Args:
            image_data: Base64 data URL
            prompt: Analysis prompt
            model: Model to use (defaults to fallback chain)

        Returns:
            Model response
        """
        if not self._client:
            self._client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120.0,
            )

        models_to_try = [model] if model else VISION_MODELS

        last_error = None
        for current_model in models_to_try:
            try:
                response = await self._client.post(
                    f"{self.api_url}/v1/chat/completions",
                    json={
                        "model": current_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": image_data},
                                    },
                                ],
                            }
                        ],
                        "max_tokens": 2000,
                    },
                )

                if response.status_code == 200:
                    return response.json()

                last_error = f"HTTP {response.status_code}: {response.text}"

            except Exception as e:
                last_error = str(e)
                continue

        raise Exception(f"All vision models failed. Last error: {last_error}")

    async def analyze_artwork(
        self,
        image_bytes: bytes,
        detailed: bool = True,
    ) -> ArtworkAnalysis:
        """Analyze album artwork.

        Args:
            image_bytes: Raw image bytes
            detailed: Include detailed style analysis

        Returns:
            ArtworkAnalysis with extracted information
        """
        image_data = self._encode_image(image_bytes)

        # Build analysis prompt
        if detailed:
            prompt = """Analyze this album artwork in detail. Provide a JSON response with:

{
    "description": "2-3 sentence description of the artwork",
    "style": {
        "primary_style": "main visual style (abstract, photographic, illustrated, minimalist, etc.)",
        "secondary_styles": ["list", "of", "secondary", "styles"],
        "color_scheme": "color harmony type (monochromatic, complementary, analogous, triadic)",
        "dominant_colors": ["list", "of", "hex", "colors"],
        "accent_colors": ["list", "of", "accent", "hex", "colors"],
        "mood": "primary emotional mood",
        "mood_keywords": ["mood", "keywords"],
        "composition": "composition type (centered, rule_of_thirds, asymmetric, etc.)",
        "visual_weight": "heavy, light, or balanced",
        "texture": "texture quality (smooth, grainy, textured, etc.)",
        "lighting": "lighting style (bright, dark, high_contrast, etc.)",
        "depth": "depth perception (flat, layered, 3d)",
        "movement": "sense of movement (static, dynamic, flowing)"
    },
    "genre_associations": ["electronic", "ambient", "dnb", "etc."],
    "visual_elements": ["key", "visual", "elements"],
    "text_detected": "any text visible in the artwork",
    "subjects": ["main", "subjects", "or", "motifs"],
    "influences": ["artistic", "influences", "or", "movements"],
    "generation_prompt": "A detailed prompt that could recreate this style for image generation"
}

Respond with valid JSON only."""
        else:
            prompt = """Briefly describe this album artwork and identify:
1. Visual style (abstract, photographic, illustrated, etc.)
2. Main colors
3. Mood/atmosphere
4. Genre associations

Keep response concise."""

        response = await self._call_vision_model(
            image_data,
            prompt,
            model=self.preferred_model,
        )

        # Parse response
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")

        analysis = ArtworkAnalysis(raw_response=response)

        if detailed:
            try:
                # Extract JSON from response
                json_str = content
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0]

                data = json.loads(json_str.strip())

                analysis.description = data.get("description", "")
                analysis.genre_associations = data.get("genre_associations", [])
                analysis.visual_elements = data.get("visual_elements", [])
                analysis.text_detected = data.get("text_detected", "")
                analysis.subjects = data.get("subjects", [])
                analysis.influences = data.get("influences", [])
                analysis.generation_prompt = data.get("generation_prompt", "")

                if "style" in data:
                    style_data = data["style"]
                    analysis.style = StyleAnalysis(
                        primary_style=style_data.get("primary_style", ""),
                        secondary_styles=style_data.get("secondary_styles", []),
                        color_scheme=style_data.get("color_scheme", ""),
                        dominant_colors=style_data.get("dominant_colors", []),
                        accent_colors=style_data.get("accent_colors", []),
                        mood=style_data.get("mood", ""),
                        mood_keywords=style_data.get("mood_keywords", []),
                        composition=style_data.get("composition", ""),
                        visual_weight=style_data.get("visual_weight", ""),
                        texture=style_data.get("texture", ""),
                        lighting=style_data.get("lighting", ""),
                        depth=style_data.get("depth", ""),
                        movement=style_data.get("movement", ""),
                    )

            except json.JSONDecodeError:
                # If JSON parsing fails, use content as description
                analysis.description = content
        else:
            analysis.description = content

        return analysis

    async def extract_style_prompt(self, image_bytes: bytes) -> str:
        """Extract a generation prompt that captures the artwork's style.

        Useful for style transfer to new artwork.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Detailed prompt for image generation
        """
        image_data = self._encode_image(image_bytes)

        prompt = """Analyze this album artwork and create a detailed prompt for an AI image generator
that would recreate this visual style for a new, different artwork.

Focus on:
- Color palette and color relationships
- Artistic style and technique
- Mood and atmosphere
- Composition principles
- Texture and material qualities
- Lighting and contrast

Output ONLY the generation prompt, no explanation. Make it detailed and specific.
Start with the main subject/style, then add modifiers."""

        response = await self._call_vision_model(
            image_data,
            prompt,
            model=self.preferred_model,
        )

        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip()

    async def compare_artworks(
        self,
        image1_bytes: bytes,
        image2_bytes: bytes,
    ) -> dict[str, Any]:
        """Compare two artworks for style similarity.

        Args:
            image1_bytes: First image bytes
            image2_bytes: Second image bytes

        Returns:
            Comparison analysis
        """
        # This would require multi-image support
        # For now, analyze both separately and compare
        analysis1 = await self.analyze_artwork(image1_bytes, detailed=True)
        analysis2 = await self.analyze_artwork(image2_bytes, detailed=True)

        # Calculate style overlap
        styles1 = set(
            [analysis1.style.primary_style] + (analysis1.style.secondary_styles if analysis1.style else [])
        )
        styles2 = set(
            [analysis2.style.primary_style] + (analysis2.style.secondary_styles if analysis2.style else [])
        )
        style_overlap = len(styles1 & styles2) / max(len(styles1 | styles2), 1)

        moods1 = set(analysis1.style.mood_keywords if analysis1.style else [])
        moods2 = set(analysis2.style.mood_keywords if analysis2.style else [])
        mood_overlap = len(moods1 & moods2) / max(len(moods1 | moods2), 1)

        return {
            "style_similarity": style_overlap,
            "mood_similarity": mood_overlap,
            "shared_styles": list(styles1 & styles2),
            "shared_moods": list(moods1 & moods2),
            "analysis1": analysis1.to_dict(),
            "analysis2": analysis2.to_dict(),
        }


async def analyze_artwork(
    image_source: str | bytes,
    detailed: bool = True,
) -> ArtworkAnalysis:
    """Convenience function to analyze artwork.

    Args:
        image_source: Path to image file or raw bytes
        detailed: Include detailed style analysis

    Returns:
        ArtworkAnalysis
    """
    if isinstance(image_source, str):
        with open(image_source, "rb") as f:
            image_bytes = f.read()
    else:
        image_bytes = image_source

    async with VisionService() as service:
        return await service.analyze_artwork(image_bytes, detailed)


if __name__ == "__main__":
    import asyncio
    import sys

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python vision.py <image_path>")
            sys.exit(1)

        image_path = sys.argv[1]
        analysis = await analyze_artwork(image_path)

        print(f"Description: {analysis.description}")
        if analysis.style:
            print(f"Style: {analysis.style.primary_style}")
            print(f"Mood: {analysis.style.mood}")
            print(f"Colors: {', '.join(analysis.style.dominant_colors)}")
        print(f"Genres: {', '.join(analysis.genre_associations)}")
        print(f"Generation prompt: {analysis.generation_prompt}")

    asyncio.run(main())
