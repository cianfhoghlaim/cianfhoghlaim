"""VLM Extraction Resource for LiteLLM-based document extraction.

Provides vision-language model extraction via LiteLLM router:
- Qwen3-VL (32 language OCR, structured JSON output)
- Gemini 3 Flash (1M context for long documents)
- GLM-4.6V (function-calling extraction)

Model Selection:
- OCR: Qwen3-VL > OLMOcr2-7B > Granite-Docling (fallback chain)
- Vision: Qwen3-VL > GLM-4.6V > Gemma-27B-IT (fallback chain)
- Extract: Gemini-2.5-Flash > Gemini-2.5-Pro > Claude-Sonnet-4 (fallback chain)

Usage:
    @asset(resource_defs={"vlm": vlm_resource()})
    async def extract_document(vlm: VLMExtractionResource):
        # Extract text from scanned page
        text = await vlm.extract_text(page_image)

        # Extract structured data
        data = await vlm.extract_structured(
            page_images,
            schema={"title": "str", "sections": "list[str]"},
        )
        return data
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from typing import Any, Literal

import dagster as dg
import structlog

try:
    from pydantic import Field
except ImportError:
    from dagster import Field

logger = structlog.get_logger(__name__)


@dataclass
class ExtractionResult:
    """Result of VLM extraction."""

    text: str
    model_used: str
    tokens_used: int
    metadata: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: str | None = None


@dataclass
class StructuredExtractionResult:
    """Result of structured VLM extraction."""

    data: dict[str, Any]
    model_used: str
    tokens_used: int
    schema_validated: bool = True
    success: bool = True
    error: str | None = None


class VLMExtractionResource(dg.ConfigurableResource):
    """VLM-based extraction using LiteLLM router.

    Provides extraction capabilities via multiple VLM models with
    automatic fallback chains.

    Model Aliases (configured in LiteLLM):
    - "ocr": local/ocr/olmocr2-7b (MLX server)
    - "vision": local/vision/qwen3-vl (llama-swap)
    - "document": local/document/granite-docling (MLX server)
    - "extract": litellm/gemini-2.5-flash (Cloud API)

    Example:
        @asset(resource_defs={"vlm": vlm_resource()})
        async def ocr_pages(vlm: VLMExtractionResource, page_images):
            texts = []
            for img in page_images:
                text = await vlm.extract_text(img)
                texts.append(text.text)
            return texts
    """

    # LiteLLM configuration
    litellm_base_url: str = Field(
        default_factory=lambda: os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
        description="LiteLLM proxy base URL",
    )

    litellm_api_key: str = Field(
        default_factory=lambda: os.getenv("LITELLM_API_KEY", ""),
        description="LiteLLM API key (if required)",
    )

    # Model selection
    ocr_model: str = Field(
        default="ocr",
        description="Model alias for OCR tasks",
    )

    vision_model: str = Field(
        default="vision",
        description="Model alias for general vision tasks",
    )

    extract_model: str = Field(
        default="extract",
        description="Model alias for structured extraction",
    )

    # Fallback configuration
    enable_fallback: bool = Field(
        default=True,
        description="Enable automatic model fallback on errors",
    )

    # OCR fallback chain (Qwen3-VL → OLMOcr2 → Granite-Docling)
    ocr_fallback_chain: list[str] = Field(
        default_factory=lambda: ["ocr", "vision", "document"],
        description="OCR model fallback chain",
    )

    # Vision fallback chain (Qwen3-VL → GLM-4.6V → Gemma)
    vision_fallback_chain: list[str] = Field(
        default_factory=lambda: ["vision", "glm-4.6v", "gemma-27b"],
        description="Vision model fallback chain",
    )

    # Extract fallback chain (Gemini → Claude)
    extract_fallback_chain: list[str] = Field(
        default_factory=lambda: ["extract", "gemini-2.5-pro", "claude-sonnet-4"],
        description="Extraction model fallback chain",
    )

    # Request configuration
    max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for response",
    )

    temperature: float = Field(
        default=0.0,
        description="Temperature for extraction (0 for deterministic)",
    )

    timeout: float = Field(
        default=120.0,
        description="Request timeout in seconds",
    )

    async def _call_model(
        self,
        model: str,
        messages: list[dict[str, Any]],
        response_format: dict[str, Any] | None = None,
    ) -> tuple[str, int]:
        """Make a LiteLLM call to a specific model.

        Args:
            model: Model name or alias
            messages: Chat messages
            response_format: Optional JSON schema for structured output

        Returns:
            Tuple of (response_text, tokens_used)

        Raises:
            Exception: If model call fails
        """
        try:
            import litellm
        except ImportError:
            raise ImportError("litellm not installed. Install: pip install litellm")

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "api_base": self.litellm_base_url,
        }

        if self.litellm_api_key:
            kwargs["api_key"] = self.litellm_api_key

        if response_format:
            kwargs["response_format"] = response_format

        response = await litellm.acompletion(**kwargs)

        text = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0

        return text, tokens

    async def _call_with_fallback(
        self,
        fallback_chain: list[str],
        messages: list[dict[str, Any]],
        response_format: dict[str, Any] | None = None,
    ) -> tuple[str, str, int]:
        """Call models with fallback chain.

        Args:
            fallback_chain: List of model names to try
            messages: Chat messages
            response_format: Optional JSON schema

        Returns:
            Tuple of (response_text, model_used, tokens_used)

        Raises:
            Exception: If all models in chain fail
        """
        last_error = None

        for model in fallback_chain:
            try:
                text, tokens = await self._call_model(model, messages, response_format)
                logger.info(
                    "vlm_call_success",
                    model=model,
                    tokens=tokens,
                )
                return text, model, tokens

            except Exception as e:
                logger.warning(
                    "vlm_call_failed",
                    model=model,
                    error=str(e),
                    next_model=fallback_chain[fallback_chain.index(model) + 1]
                    if fallback_chain.index(model) + 1 < len(fallback_chain)
                    else "none",
                )
                last_error = e

                if not self.enable_fallback:
                    break

        raise last_error or RuntimeError("All models in fallback chain failed")

    def _encode_image(
        self,
        image_bytes: bytes,
        format: str = "PNG",
    ) -> str:
        """Encode image bytes as data URL."""
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime = f"image/{format.lower()}"
        return f"data:{mime};base64,{b64}"

    async def extract_text(
        self,
        image_bytes: bytes,
        image_format: str = "PNG",
        instruction: str | None = None,
        model: str | None = None,
    ) -> ExtractionResult:
        """Extract text from an image using OCR.

        Args:
            image_bytes: Image content
            image_format: Image format (PNG, JPEG)
            instruction: Custom OCR instruction
            model: Specific model to use (overrides ocr_model)

        Returns:
            ExtractionResult with extracted text
        """
        image_url = self._encode_image(image_bytes, image_format)

        prompt = instruction or (
            "Extract all text from this document page. "
            "Preserve the structure and formatting as much as possible. "
            "Include headings, paragraphs, lists, and table data."
        )

        messages = [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }]

        try:
            if model:
                text, tokens = await self._call_model(model, messages)
                model_used = model
            else:
                text, model_used, tokens = await self._call_with_fallback(
                    self.ocr_fallback_chain,
                    messages,
                )

            return ExtractionResult(
                text=text,
                model_used=model_used,
                tokens_used=tokens,
                success=True,
            )

        except Exception as e:
            logger.error("text_extraction_failed", error=str(e))
            return ExtractionResult(
                text="",
                model_used="none",
                tokens_used=0,
                success=False,
                error=str(e),
            )

    async def extract_table(
        self,
        image_bytes: bytes,
        image_format: str = "PNG",
        model: str | None = None,
    ) -> ExtractionResult:
        """Extract table data from an image.

        Uses VLM to extract tabular data in structured format.

        Args:
            image_bytes: Image containing table
            image_format: Image format
            model: Specific model to use

        Returns:
            ExtractionResult with table data as markdown or JSON
        """
        instruction = (
            "Extract the table from this image. "
            "Return the data as a markdown table with headers. "
            "If there are merged cells, indicate the span. "
            "Preserve all numeric values exactly as shown."
        )

        return await self.extract_text(
            image_bytes,
            image_format,
            instruction=instruction,
            model=model,
        )

    async def extract_formula(
        self,
        image_bytes: bytes,
        image_format: str = "PNG",
        model: str | None = None,
    ) -> ExtractionResult:
        """Extract mathematical formulas as LaTeX.

        Args:
            image_bytes: Image containing formula
            image_format: Image format
            model: Specific model to use

        Returns:
            ExtractionResult with LaTeX formula
        """
        instruction = (
            "Extract the mathematical formula or equation from this image. "
            "Return the formula as valid LaTeX code. "
            "Use proper LaTeX syntax including \\frac, \\sqrt, \\sum, etc."
        )

        return await self.extract_text(
            image_bytes,
            image_format,
            instruction=instruction,
            model=model,
        )

    async def extract_structured(
        self,
        image_bytes: bytes | list[bytes],
        schema: dict[str, Any],
        image_format: str = "PNG",
        instruction: str | None = None,
        model: str | None = None,
    ) -> StructuredExtractionResult:
        """Extract structured data according to schema.

        Supports multi-page extraction for long documents (Gemini 1M context).

        Args:
            image_bytes: Single image or list of page images
            schema: JSON schema for extraction
            image_format: Image format
            instruction: Custom extraction instruction
            model: Specific model to use (overrides extract_model)

        Returns:
            StructuredExtractionResult with extracted data
        """
        import json

        # Handle single or multiple images
        images = image_bytes if isinstance(image_bytes, list) else [image_bytes]

        # Build content with all images
        content = []

        prompt = instruction or (
            f"Extract information from this document according to the following schema:\n"
            f"{json.dumps(schema, indent=2)}\n\n"
            f"Return a valid JSON object matching the schema."
        )
        content.append({"type": "text", "text": prompt})

        for i, img in enumerate(images):
            image_url = self._encode_image(img, image_format)
            content.append({
                "type": "image_url",
                "image_url": {"url": image_url},
            })

        messages = [{"role": "user", "content": content}]

        # Use JSON mode if available
        response_format = {"type": "json_object"}

        try:
            if model:
                text, tokens = await self._call_model(model, messages, response_format)
                model_used = model
            else:
                text, model_used, tokens = await self._call_with_fallback(
                    self.extract_fallback_chain,
                    messages,
                    response_format,
                )

            # Parse JSON response
            try:
                data = json.loads(text)
                schema_validated = True
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    schema_validated = True
                else:
                    data = {"raw_text": text}
                    schema_validated = False

            return StructuredExtractionResult(
                data=data,
                model_used=model_used,
                tokens_used=tokens,
                schema_validated=schema_validated,
                success=True,
            )

        except Exception as e:
            logger.error("structured_extraction_failed", error=str(e))
            return StructuredExtractionResult(
                data={},
                model_used="none",
                tokens_used=0,
                schema_validated=False,
                success=False,
                error=str(e),
            )

    async def classify_document(
        self,
        image_bytes: bytes,
        categories: list[str],
        image_format: str = "PNG",
        model: str | None = None,
    ) -> tuple[str, float]:
        """Classify a document page into categories.

        Args:
            image_bytes: Document page image
            categories: List of possible categories
            image_format: Image format
            model: Specific model to use

        Returns:
            Tuple of (category, confidence)
        """
        import json

        instruction = (
            f"Classify this document into one of the following categories:\n"
            f"{json.dumps(categories)}\n\n"
            f"Return a JSON object with 'category' and 'confidence' (0-1) fields."
        )

        result = await self.extract_structured(
            image_bytes,
            schema={"category": "str", "confidence": "float"},
            image_format=image_format,
            instruction=instruction,
            model=model,
        )

        if result.success and "category" in result.data:
            return result.data["category"], result.data.get("confidence", 1.0)

        return "unknown", 0.0

    async def describe_image(
        self,
        image_bytes: bytes,
        image_format: str = "PNG",
        detail_level: Literal["brief", "detailed", "comprehensive"] = "detailed",
        model: str | None = None,
    ) -> ExtractionResult:
        """Generate a description of an image.

        Args:
            image_bytes: Image content
            image_format: Image format
            detail_level: Level of detail in description
            model: Specific model to use

        Returns:
            ExtractionResult with image description
        """
        prompts = {
            "brief": "Briefly describe what is shown in this image in 1-2 sentences.",
            "detailed": "Describe this image in detail, including all visible elements, text, and layout.",
            "comprehensive": (
                "Provide a comprehensive analysis of this image including: "
                "1) What is shown 2) Any text content 3) Layout and structure "
                "4) Purpose or context 5) Any notable details"
            ),
        }

        return await self.extract_text(
            image_bytes,
            image_format,
            instruction=prompts[detail_level],
            model=model or self.vision_model,
        )


# Resource factory function
def vlm_resource(**kwargs) -> VLMExtractionResource:
    """Factory for VLM extraction resource.

    Usage:
        @asset(resource_defs={"vlm": vlm_resource()})
        async def my_asset(vlm: VLMExtractionResource):
            result = await vlm.extract_text(image_bytes)
            return result.text
    """
    return VLMExtractionResource(**kwargs)
