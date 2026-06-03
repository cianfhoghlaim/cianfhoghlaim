"""
OCR Model Registry.

Centralized registry for OCR models used in Irish handwriting recognition.
Supports multiple backends: LiteLLM, MLX, local transformers.

Based on research in:
- taighde_new/document-intelligence-ocr.md
- taighde_teanga/Finetuning Qwen3-VL for Gaelic OCR.md

Usage:
    from oideachais.data_platform.ocr import ModelRegistry

    registry = ModelRegistry()

    # List available models
    for model in registry.list_models():
        print(f"{model.name}: {model.capabilities}")

    # Get specific model
    model = registry.get_model("qwen2.5-vl-7b")
    result = model.transcribe(image)
"""

import base64
import io
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np


class ModelBackend(str, Enum):
    """Supported model backends."""

    LITELLM = "litellm"
    MLX = "mlx"
    TRANSFORMERS = "transformers"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class ModelCapability(str, Enum):
    """Model capabilities."""

    DENSE_OCR = "dense_ocr"
    GROUNDING = "grounding"
    TABLES = "tables"
    LATEX = "latex"
    REASONING = "reasoning"
    MATH = "math"
    MULTILINGUAL = "multilingual"
    GAELIC = "gaelic"


@dataclass
class OCRModel:
    """OCR model configuration."""

    name: str
    model_id: str
    backend: ModelBackend
    capabilities: list[ModelCapability] = field(default_factory=list)
    max_resolution: tuple[int, int] = (1024, 1024)
    supports_batching: bool = False
    cost_per_image: float = 0.0  # USD estimate
    notes: str = ""

    # Runtime state
    _client: Any = field(default=None, repr=False)

    def _get_client(self) -> Any:
        """Get or initialize model client."""
        if self._client is not None:
            return self._client

        if self.backend == ModelBackend.LITELLM:
            import litellm

            self._client = litellm
        elif self.backend == ModelBackend.MLX:
            try:
                import mlx_vlm

                self._client = mlx_vlm
            except ImportError:
                raise ImportError("mlx-vlm package required for MLX backend")
        elif self.backend == ModelBackend.TRANSFORMERS:
            from transformers import AutoModelForVision2Seq, AutoProcessor

            self._client = {
                "processor": AutoProcessor.from_pretrained(self.model_id),
                "model": AutoModelForVision2Seq.from_pretrained(self.model_id),
            }
        elif self.backend == ModelBackend.OLLAMA:
            import ollama

            self._client = ollama
        elif self.backend == ModelBackend.OPENAI:
            from openai import OpenAI

            self._client = OpenAI()
        elif self.backend == ModelBackend.ANTHROPIC:
            from anthropic import Anthropic

            self._client = Anthropic()

        return self._client

    def _image_to_base64(self, image: Any) -> str:
        """Convert image to base64 string."""
        from PIL import Image

        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # Resize if needed
        if image.size[0] > self.max_resolution[0] or image.size[1] > self.max_resolution[1]:
            image.thumbnail(self.max_resolution, Image.Resampling.LANCZOS)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def transcribe(
        self,
        image: Any,
        prompt: str | None = None,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """
        Transcribe handwritten text from image.

        Args:
            image: PIL Image or numpy array
            prompt: Custom prompt (default: OCR prompt)
            temperature: Generation temperature

        Returns:
            Dictionary with transcription and metadata
        """
        prompt = prompt or "Transcribe the handwritten text in this image exactly as written."
        image_b64 = self._image_to_base64(image)

        client = self._get_client()

        if self.backend == ModelBackend.LITELLM:
            return self._transcribe_litellm(client, image_b64, prompt, temperature)
        elif self.backend == ModelBackend.MLX:
            return self._transcribe_mlx(client, image, prompt, temperature)
        elif self.backend == ModelBackend.TRANSFORMERS:
            return self._transcribe_transformers(client, image, prompt, temperature)
        elif self.backend == ModelBackend.OLLAMA:
            return self._transcribe_ollama(client, image_b64, prompt, temperature)
        elif self.backend == ModelBackend.OPENAI:
            return self._transcribe_openai(client, image_b64, prompt, temperature)
        elif self.backend == ModelBackend.ANTHROPIC:
            return self._transcribe_anthropic(client, image_b64, prompt, temperature)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def _transcribe_litellm(
        self, client: Any, image_b64: str, prompt: str, temperature: float
    ) -> dict[str, Any]:
        """Transcribe using LiteLLM."""
        response = client.completion(
            model=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            temperature=temperature,
        )

        return {
            "transcription": response.choices[0].message.content,
            "model": self.name,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
        }

    def _transcribe_mlx(
        self, client: Any, image: Any, prompt: str, temperature: float
    ) -> dict[str, Any]:
        """Transcribe using MLX-VLM."""
        from PIL import Image

        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        # MLX-VLM specific API
        output = client.generate(
            model=self.model_id,
            prompt=prompt,
            images=[image],
            max_tokens=2048,
            temperature=temperature,
        )

        return {
            "transcription": output,
            "model": self.name,
        }

    def _transcribe_transformers(
        self, client: dict, image: Any, prompt: str, temperature: float
    ) -> dict[str, Any]:
        """Transcribe using Transformers."""
        from PIL import Image

        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        processor = client["processor"]
        model = client["model"]

        inputs = processor(images=image, text=prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_new_tokens=2048, temperature=temperature)
        transcription = processor.decode(outputs[0], skip_special_tokens=True)

        return {
            "transcription": transcription,
            "model": self.name,
        }

    def _transcribe_ollama(
        self, client: Any, image_b64: str, prompt: str, temperature: float
    ) -> dict[str, Any]:
        """Transcribe using Ollama."""
        response = client.chat(
            model=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64],
                }
            ],
            options={"temperature": temperature},
        )

        return {
            "transcription": response["message"]["content"],
            "model": self.name,
        }

    def _transcribe_openai(
        self, client: Any, image_b64: str, prompt: str, temperature: float
    ) -> dict[str, Any]:
        """Transcribe using OpenAI."""
        response = client.chat.completions.create(
            model=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            temperature=temperature,
        )

        return {
            "transcription": response.choices[0].message.content,
            "model": self.name,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            },
        }

    def _transcribe_anthropic(
        self, client: Any, image_b64: str, prompt: str, temperature: float
    ) -> dict[str, Any]:
        """Transcribe using Anthropic."""
        response = client.messages.create(
            model=self.model_id,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            temperature=temperature,
        )

        return {
            "transcription": response.content[0].text,
            "model": self.name,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }


# Pre-configured models
OCR_MODELS: dict[str, OCRModel] = {
    "olmocr-7b": OCRModel(
        name="olmOCR-2-7B",
        model_id="allenai/olmOCR-2-7B",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
            ModelCapability.LATEX,
        ],
        max_resolution=(2048, 2048),
        notes="Best for structured documents, tables, and LaTeX",
    ),
    "qwen2.5-vl-7b": OCRModel(
        name="Qwen2.5-VL-7B",
        model_id="Qwen/Qwen2.5-VL-7B-Instruct",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
        ],
        max_resolution=(1280, 1280),
        notes="Best for visual grounding and reasoning",
    ),
    "qwen2.5-vl-7b-mlx": OCRModel(
        name="Qwen2.5-VL-7B (MLX)",
        model_id="mlx-community/Qwen2.5-VL-7B-Instruct-4bit",
        backend=ModelBackend.MLX,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
        ],
        max_resolution=(1280, 1280),
        notes="Apple Silicon optimized via MLX",
    ),
    "deepseek-ocr": OCRModel(
        name="DeepSeek-OCR",
        model_id="deepseek-ai/deepseek-ocr",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.MATH,
        ],
        max_resolution=(1024, 1024),
        notes="Optimized for compressed documents and math",
    ),
    "granite-docling": OCRModel(
        name="Granite-Docling",
        model_id="ibm-granite/granite-docling-base",
        backend=ModelBackend.TRANSFORMERS,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.TABLES,
        ],
        max_resolution=(1024, 1024),
        notes="DocTags for document structure",
    ),
    "gpt-4o": OCRModel(
        name="GPT-4o",
        model_id="gpt-4o",
        backend=ModelBackend.OPENAI,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.GROUNDING,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
        ],
        max_resolution=(2048, 2048),
        cost_per_image=0.01,
        notes="Cloud API, highest quality but costly",
    ),
    "claude-3.5-sonnet": OCRModel(
        name="Claude 3.5 Sonnet",
        model_id="claude-3-5-sonnet-20241022",
        backend=ModelBackend.ANTHROPIC,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.REASONING,
            ModelCapability.MULTILINGUAL,
        ],
        max_resolution=(2048, 2048),
        cost_per_image=0.015,
        notes="Cloud API, excellent reasoning",
    ),
    "llama-3.2-vision-11b": OCRModel(
        name="Llama 3.2 Vision 11B",
        model_id="llama3.2-vision:11b",
        backend=ModelBackend.OLLAMA,
        capabilities=[
            ModelCapability.DENSE_OCR,
            ModelCapability.REASONING,
        ],
        max_resolution=(1120, 1120),
        notes="Local Ollama, good balance of quality and speed",
    ),
    "uccix-13b": OCRModel(
        name="UCCIX-Llama2-13B",
        model_id="ReliableAI/UCCIX-Llama2-13B-Instruct",
        backend=ModelBackend.LITELLM,
        capabilities=[
            ModelCapability.GAELIC,
            ModelCapability.MULTILINGUAL,
        ],
        max_resolution=(1024, 1024),
        notes="Best Irish language model, needs multimodal wrapper",
    ),
}


class ModelRegistry:
    """
    Registry for managing OCR models.
    """

    def __init__(self, custom_models: dict[str, OCRModel] | None = None):
        """
        Initialize registry.

        Args:
            custom_models: Additional models to register
        """
        self.models = dict(OCR_MODELS)

        if custom_models:
            self.models.update(custom_models)

    def list_models(self) -> list[OCRModel]:
        """List all registered models."""
        return list(self.models.values())

    def get_model(self, name: str) -> OCRModel:
        """
        Get model by name.

        Args:
            name: Model name (e.g., "qwen2.5-vl-7b")

        Returns:
            OCRModel instance
        """
        if name not in self.models:
            raise ValueError(
                f"Model '{name}' not found. Available: {list(self.models.keys())}"
            )
        return self.models[name]

    def register_model(self, name: str, model: OCRModel) -> None:
        """
        Register a new model.

        Args:
            name: Model identifier
            model: OCRModel configuration
        """
        self.models[name] = model

    def get_models_with_capability(
        self, capability: ModelCapability
    ) -> list[OCRModel]:
        """
        Get models with a specific capability.

        Args:
            capability: Required capability

        Returns:
            List of matching models
        """
        return [m for m in self.models.values() if capability in m.capabilities]

    def get_local_models(self) -> list[OCRModel]:
        """Get models that run locally (no cloud API)."""
        cloud_backends = {ModelBackend.OPENAI, ModelBackend.ANTHROPIC}
        return [m for m in self.models.values() if m.backend not in cloud_backends]

    def get_cloud_models(self) -> list[OCRModel]:
        """Get cloud API models."""
        cloud_backends = {ModelBackend.OPENAI, ModelBackend.ANTHROPIC}
        return [m for m in self.models.values() if m.backend in cloud_backends]

    def register_finetuned_model(
        self,
        name: str,
        base_model: str,
        adapter_path: str,
        backend: ModelBackend = ModelBackend.TRANSFORMERS,
    ) -> OCRModel:
        """
        Register a fine-tuned model with LoRA adapter.

        Args:
            name: Model identifier
            base_model: Base model ID
            adapter_path: Path to LoRA adapter
            backend: Model backend

        Returns:
            Registered OCRModel
        """
        model = OCRModel(
            name=name,
            model_id=base_model,
            backend=backend,
            capabilities=[ModelCapability.GAELIC, ModelCapability.DENSE_OCR],
            notes=f"Fine-tuned with adapter: {adapter_path}",
        )

        # Store adapter path for loading
        model._adapter_path = adapter_path
        self.models[name] = model
        return model
