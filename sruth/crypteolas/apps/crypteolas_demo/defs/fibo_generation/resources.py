"""
Dagster resources for FIBO image generation.

Provides configurable resources for:
- FIBO MLX generator
- Validation with Qwen3-VL
"""

from typing import Optional

from dagster import ConfigurableResource, InitResourceContext
from PIL import Image


class FiboResource(ConfigurableResource):
    """
    Dagster resource for FIBO image generation.

    Provides FIBO model for JSON-native educational image generation
    with generate, refine, and inspire modes.
    """

    model_path: str = "briaai/FIBO"
    device: str = "mps"
    vlm_mode: str = "gemini"

    _generator = None

    def setup_for_execution(self, context: InitResourceContext) -> None:
        """Initialize FIBO generator."""
        from ...models.fibo_mlx import FiboMLXGenerator
        self._generator = FiboMLXGenerator(
            model_path=self.model_path,
            device=self.device,
            vlm_mode=self.vlm_mode,
        )

    @property
    def generator(self):
        """Get the FIBO generator."""
        if self._generator is None:
            from ...models.fibo_mlx import FiboMLXGenerator
            self._generator = FiboMLXGenerator(
                model_path=self.model_path,
                device=self.device,
                vlm_mode=self.vlm_mode,
            )
        return self._generator

    async def generate(
        self,
        prompt: dict,
        seed: Optional[int] = None,
        output_path: Optional[str] = None,
    ) -> Image.Image:
        """Generate an image from FIBO JSON prompt."""
        return await self.generator.generate(
            prompt=prompt,
            seed=seed,
            output_path=output_path,
        )

    async def refine(
        self,
        existing_json: dict,
        instruction: str,
    ) -> tuple[Image.Image, dict]:
        """Refine an existing image with instruction."""
        return await self.generator.refine(
            existing_json=existing_json,
            instruction=instruction,
        )

    def create_educational_prompt(
        self,
        concept: str,
        diagram_type: str,
        subject: str,
        style: str = "digital_illustration",
    ) -> dict:
        """Create an educational FIBO prompt."""
        return self.generator.create_educational_prompt(
            concept=concept,
            diagram_type=diagram_type,
            subject=subject,
            style=style,
        )


class ValidationResource(ConfigurableResource):
    """
    Dagster resource for image validation.

    Combines Qwen3-VL and BAML for validating generated
    educational images against curriculum requirements.
    """

    validation_threshold: float = 0.7
    max_refinement_iterations: int = 3

    async def validate_image(
        self,
        image: Image.Image,
        concept_title: str,
        concept_description: str,
        visual_requirements: dict,
    ) -> dict:
        """
        Validate a generated image.

        Returns validation result with scores and feedback.
        """
        try:
            from ...models.qwen_vlm import get_qwen_client

            client = get_qwen_client()
            result = await client.validate_educational_image(
                generated_image=image,
                concept_title=concept_title,
                concept_description=concept_description,
                visual_requirements=visual_requirements,
            )

            # Determine if passes threshold
            overall = result.get("scores", {}).get("overall", 0)
            result["passes_threshold"] = overall >= self.validation_threshold

            return result

        except Exception as e:
            return {
                "error": str(e),
                "passes_threshold": False,
                "scores": {"overall": 0},
            }

    async def suggest_refinements(
        self,
        image: Image.Image,
        target_concept: str,
        issues: list[str],
    ) -> list[str]:
        """Get refinement suggestions for an image."""
        try:
            from ...models.qwen_vlm import get_qwen_client

            client = get_qwen_client()
            return await client.suggest_refinements(
                image=image,
                target_concept=target_concept,
                current_issues=issues,
            )

        except Exception as e:
            return [f"Error getting suggestions: {e}"]
