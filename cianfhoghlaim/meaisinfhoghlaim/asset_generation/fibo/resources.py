"""
Dagster resources for FIBO educational image generation.

Provides configurable resources for:
- FIBO image generation via LiteLLM
- Validation with VLM models
"""


from dagster import ConfigurableResource, InitResourceContext
from PIL import Image

from .schemas import FiboConfig


class FiboResource(ConfigurableResource):
    """
    Dagster resource for FIBO educational image generation.

    Uses LiteLLM to generate educational images from structured prompts.
    """

    litellm_api_base: str = "http://localhost:4000"
    model: str = "flux-schnell"
    default_style: str = "digital_illustration"
    timeout: int = 120

    _client = None

    def setup_for_execution(self, context: InitResourceContext) -> None:
        """Initialize HTTP client."""
        import httpx

        self._client = httpx.AsyncClient(
            base_url=self.litellm_api_base,
            timeout=self.timeout,
        )

    @property
    def client(self):
        """Get HTTP client, creating if needed."""
        if self._client is None:
            import httpx

            self._client = httpx.AsyncClient(
                base_url=self.litellm_api_base,
                timeout=self.timeout,
            )
        return self._client

    async def generate(
        self,
        prompt: dict | FiboConfig,
        seed: int | None = None,
        output_path: str | None = None,
        width: int = 512,
        height: int = 512,
    ) -> Image.Image:
        """
        Generate an educational image from FIBO config.

        Args:
            prompt: FIBO configuration dict or FiboConfig object
            seed: Random seed for reproducibility
            output_path: Optional path to save image
            width: Image width
            height: Image height

        Returns:
            Generated PIL Image
        """
        import base64
        import io

        # Convert to text prompt
        if isinstance(prompt, FiboConfig):
            text_prompt = prompt.to_prompt()
        elif isinstance(prompt, dict):
            config = FiboConfig(**prompt)
            text_prompt = config.to_prompt()
        else:
            text_prompt = str(prompt)

        # Add educational context
        text_prompt = f"Educational diagram: {text_prompt}, clear labels, high quality"

        # Build request
        payload = {
            "model": self.model,
            "prompt": text_prompt,
            "size": f"{width}x{height}",
            "n": 1,
            "response_format": "b64_json",
        }

        if seed is not None:
            payload["extra_body"] = {"seed": seed}

        # Call LiteLLM
        response = await self.client.post(
            "/v1/images/generations",
            json=payload,
        )
        response.raise_for_status()

        data = response.json()

        if "data" not in data or len(data["data"]) == 0:
            raise ValueError("No image data in response")

        # Decode image
        image_b64 = data["data"][0].get("b64_json")
        if not image_b64:
            raise ValueError("No base64 image in response")

        image_bytes = base64.b64decode(image_b64)
        image = Image.open(io.BytesIO(image_bytes))

        # Save if path provided
        if output_path:
            image.save(output_path)

        return image

    async def refine(
        self,
        existing_json: dict,
        instruction: str,
    ) -> tuple[Image.Image, dict]:
        """
        Refine an existing image with instruction.

        Args:
            existing_json: Original FIBO config
            instruction: Refinement instruction

        Returns:
            Tuple of (refined image, updated config)
        """
        # Update config with instruction
        updated_config = existing_json.copy()
        original_desc = updated_config.get("detailed_description", "")
        updated_config["detailed_description"] = f"{original_desc}. {instruction}"

        # Generate new image
        image = await self.generate(updated_config)

        return image, updated_config

    def create_educational_prompt(
        self,
        concept: str,
        diagram_type: str,
        subject: str,
        style: str = "digital_illustration",
    ) -> dict:
        """
        Create an educational FIBO prompt configuration.

        Args:
            concept: Educational concept to visualize
            diagram_type: Type of diagram (molecular, process_flow, etc.)
            subject: Subject area (chemistry, biology, etc.)
            style: Visual style

        Returns:
            FIBO configuration dict
        """
        # Subject-specific styling
        subject_styles = {
            "chemistry": {
                "color_palette": ["blue", "green", "white"],
                "style_hints": "molecular structures, chemical bonds, clean scientific illustration",
            },
            "biology": {
                "color_palette": ["green", "blue", "natural"],
                "style_hints": "biological structures, cell diagrams, anatomical illustration",
            },
            "physics": {
                "color_palette": ["blue", "orange", "neutral"],
                "style_hints": "force diagrams, wave patterns, physics illustration",
            },
            "geography": {
                "color_palette": ["earth tones", "blue", "green"],
                "style_hints": "maps, landforms, geographic illustration",
            },
        }

        subject_config = subject_styles.get(subject, {
            "color_palette": ["educational"],
            "style_hints": "clear educational diagram",
        })

        return {
            "title": concept,
            "short_description": f"{diagram_type} diagram of {concept}",
            "detailed_description": f"Educational {diagram_type} showing {concept}. {subject_config['style_hints']}. Clear labels, accurate representation, suitable for students.",
            "style": style,
            "medium": "digital_illustration",
            "color_palette": subject_config["color_palette"],
            "subject_position": "center",
            "background": "clean white",
            "lighting": "soft even",
            "aspect_ratio": "1:1",
            "quality": "high",
            "subject_area": subject,
            "diagram_type": diagram_type,
            "complexity_level": "moderate",
        }


class ValidationResource(ConfigurableResource):
    """
    Dagster resource for validating educational images.

    Uses VLM models to validate generated images against
    curriculum requirements.
    """

    validation_threshold: float = 0.7
    max_refinement_iterations: int = 3
    vlm_model: str = "gpt-4-vision-preview"
    litellm_api_base: str = "http://localhost:4000"

    _client = None

    @property
    def client(self):
        """Get HTTP client."""
        if self._client is None:
            import httpx

            self._client = httpx.AsyncClient(
                base_url=self.litellm_api_base,
                timeout=120,
            )
        return self._client

    async def validate_image(
        self,
        image: Image.Image,
        concept_title: str,
        concept_description: str,
        visual_requirements: dict,
    ) -> dict:
        """
        Validate a generated educational image.

        Args:
            image: Generated PIL Image
            concept_title: Title of the concept
            concept_description: Description of the concept
            visual_requirements: Visual requirements dict

        Returns:
            Validation result with scores and feedback
        """
        import base64
        import io

        try:
            # Convert image to base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            image_b64 = base64.b64encode(buffer.getvalue()).decode()

            # Build validation prompt
            diagram_type = visual_requirements.get("diagram_type", "diagram")
            prompt = f"""Evaluate this educational image for a {diagram_type} about "{concept_title}".

Concept: {concept_description}

Rate the following on a scale of 0-1:
1. Scientific Accuracy: Does the image correctly represent the concept?
2. Educational Clarity: Is the image clear and easy to understand for students?
3. Concept Alignment: Does the image match what was requested?

Also identify any issues that should be corrected.

Respond in JSON format:
{{
    "scores": {{
        "scientific_accuracy": 0.0-1.0,
        "educational_clarity": 0.0-1.0,
        "concept_alignment": 0.0-1.0,
        "overall": 0.0-1.0
    }},
    "issues": ["list of issues if any"],
    "feedback": "brief feedback"
}}"""

            # Call VLM
            response = await self.client.post(
                "/v1/chat/completions",
                json={
                    "model": self.vlm_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{image_b64}"
                                    },
                                },
                            ],
                        }
                    ],
                    "max_tokens": 500,
                },
            )
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse JSON response
            import json

            # Try to extract JSON from response
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # Try to find JSON in the response
                import re

                json_match = re.search(r"\{[\s\S]*\}", content)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {
                        "scores": {"overall": 0.5},
                        "issues": [],
                        "feedback": content,
                    }

            # Determine if passes threshold
            overall = result.get("scores", {}).get("overall", 0)
            result["passes_threshold"] = overall >= self.validation_threshold

            return result

        except Exception as e:
            return {
                "error": str(e),
                "passes_threshold": False,
                "scores": {"overall": 0},
                "issues": [f"Validation error: {e}"],
            }

    async def suggest_refinements(
        self,
        image: Image.Image,
        target_concept: str,
        issues: list[str],
    ) -> list[str]:
        """
        Get refinement suggestions for an image.

        Args:
            image: Current PIL Image
            target_concept: Target concept
            issues: Current issues

        Returns:
            List of refinement suggestions
        """
        if not issues:
            return []

        # Generate suggestions based on issues
        suggestions = []
        for issue in issues:
            if "accuracy" in issue.lower():
                suggestions.append(
                    f"Correct scientific accuracy: {issue}"
                )
            elif "clarity" in issue.lower():
                suggestions.append(
                    f"Improve clarity: {issue}"
                )
            elif "label" in issue.lower():
                suggestions.append(
                    f"Add or fix labels: {issue}"
                )
            else:
                suggestions.append(
                    f"Address: {issue}"
                )

        return suggestions
