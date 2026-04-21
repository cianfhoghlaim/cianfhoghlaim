"""
OCR Adapter Layer for Multiple Backends.

Provides unified interface for OCR extraction via:
- PaddleOCR (MCP server)
- Docling (REST API)
- Dots.OCR (vLLM OpenAI-compatible)
- Unstract (REST API)

Usage:
    from sruth.oideachas.ocr.adapters import get_adapter, compare_ocr_models

    adapter = get_adapter("paddleocr")
    result = await adapter.process_image(image_bytes)

    # Or compare multiple models
    results = await compare_ocr_models(image_bytes, models=["paddleocr", "docling"])
"""

from __future__ import annotations

import base64
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import httpx

# ============================================================================
# Configuration
# ============================================================================


class OCRBackend(str, Enum):
    """Supported OCR backends."""

    PADDLEOCR = "paddleocr"
    DOCLING = "docling"
    DOTS_OCR = "dots_ocr"
    UNSTRACT = "unstract"


# Backend configurations
OCR_BACKENDS = {
    "paddleocr": {
        "url": os.getenv("PADDLEOCR_URL", "http://localhost:8000"),
        "type": "mcp",
        "name": "PaddleOCR",
    },
    "docling": {
        "url": os.getenv("DOCLING_URL", "http://localhost:5001"),
        "type": "rest",
        "name": "Docling",
    },
    "dots_ocr": {
        "url": os.getenv("DOTS_OCR_URL", "http://localhost:8001"),
        "type": "openai",
        "name": "Dots.OCR",
    },
    "unstract": {
        "url": os.getenv("UNSTRACT_URL", "http://localhost:8002"),
        "type": "rest",
        "name": "Unstract",
    },
}


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class BoundingBox:
    """Bounding box for detected text."""

    x: float
    y: float
    width: float
    height: float
    text: str
    confidence: float


@dataclass
class PageOCRResult:
    """OCR result for a single page."""

    page_number: int
    text: str
    confidence: float
    bounding_boxes: list[BoundingBox] = field(default_factory=list)


@dataclass
class OCRResult:
    """Complete OCR result from any backend."""

    text: str
    confidence: float
    model_id: str
    backend: OCRBackend
    elapsed_seconds: float
    page_count: int = 1
    pages: list[PageOCRResult] = field(default_factory=list)
    bounding_boxes: list[BoundingBox] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "success"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "confidence": self.confidence,
            "model_id": self.model_id,
            "backend": self.backend.value,
            "elapsed_seconds": self.elapsed_seconds,
            "page_count": self.page_count,
            "status": self.status,
            "error": self.error,
        }


# ============================================================================
# Abstract Base Adapter
# ============================================================================


class OCRAdapter(ABC):
    """Abstract base class for OCR adapters."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def process_image(
        self,
        image: bytes | Path,
        prompt: str | None = None,
    ) -> OCRResult:
        """Process a single image and return OCR result."""
        pass

    @abstractmethod
    async def process_pdf(
        self,
        pdf: bytes | Path,
        pages: list[int] | None = None,
    ) -> OCRResult:
        """Process a PDF document and return OCR result."""
        pass

    @property
    @abstractmethod
    def backend(self) -> OCRBackend:
        """Return the backend type."""
        pass


# ============================================================================
# PaddleOCR Adapter (MCP)
# ============================================================================


class PaddleOCRAdapter(OCRAdapter):
    """Adapter for PaddleOCR via MCP server."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.url = self.config.get("url", OCR_BACKENDS["paddleocr"]["url"])

    @property
    def backend(self) -> OCRBackend:
        return OCRBackend.PADDLEOCR

    async def process_image(
        self,
        image: bytes | Path,
        prompt: str | None = None,
    ) -> OCRResult:
        start_time = time.time()

        if isinstance(image, Path):
            image = image.read_bytes()

        try:
            client = await self._get_client()
            image_b64 = base64.b64encode(image).decode()

            # MCP-style request
            response = await client.post(
                f"{self.url}/ocr",
                json={
                    "image": image_b64,
                    "det": True,
                    "rec": True,
                    "cls": True,
                },
            )
            response.raise_for_status()
            result = response.json()

            # Parse PaddleOCR response
            text_lines = []
            boxes = []
            total_conf = 0.0

            for item in result.get("result", []):
                box_coords = item.get("box", [])
                text = item.get("text", "")
                conf = item.get("confidence", 0.0)

                text_lines.append(text)
                total_conf += conf

                if box_coords and len(box_coords) >= 4:
                    boxes.append(BoundingBox(
                        x=box_coords[0][0],
                        y=box_coords[0][1],
                        width=box_coords[2][0] - box_coords[0][0],
                        height=box_coords[2][1] - box_coords[0][1],
                        text=text,
                        confidence=conf,
                    ))

            full_text = "\n".join(text_lines)
            avg_conf = total_conf / len(text_lines) if text_lines else 0.0

            return OCRResult(
                text=full_text,
                confidence=avg_conf,
                model_id="paddleocr-v4",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                bounding_boxes=boxes,
            )

        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                model_id="paddleocr-v4",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )

    async def process_pdf(
        self,
        pdf: bytes | Path,
        pages: list[int] | None = None,
    ) -> OCRResult:
        start_time = time.time()

        if isinstance(pdf, Path):
            pdf = pdf.read_bytes()

        try:
            # Convert PDF to images
            from pdf2image import convert_from_bytes

            images = convert_from_bytes(pdf, dpi=150)

            if pages:
                images = [images[i - 1] for i in pages if 0 < i <= len(images)]

            all_text = []
            all_boxes = []
            total_conf = 0.0
            page_results = []

            for i, img in enumerate(images):
                import io
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                img_bytes = buf.getvalue()

                result = await self.process_image(img_bytes)
                all_text.append(result.text)
                all_boxes.extend(result.bounding_boxes)
                total_conf += result.confidence

                page_results.append(PageOCRResult(
                    page_number=i + 1,
                    text=result.text,
                    confidence=result.confidence,
                    bounding_boxes=result.bounding_boxes,
                ))

            return OCRResult(
                text="\n\n".join(all_text),
                confidence=total_conf / len(images) if images else 0.0,
                model_id="paddleocr-v4",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                page_count=len(images),
                pages=page_results,
                bounding_boxes=all_boxes,
            )

        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                model_id="paddleocr-v4",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )


# ============================================================================
# Docling Adapter (REST)
# ============================================================================


class DoclingAdapter(OCRAdapter):
    """Adapter for Docling document understanding service."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.url = self.config.get("url", OCR_BACKENDS["docling"]["url"])

    @property
    def backend(self) -> OCRBackend:
        return OCRBackend.DOCLING

    async def process_image(
        self,
        image: bytes | Path,
        prompt: str | None = None,
    ) -> OCRResult:
        start_time = time.time()

        if isinstance(image, Path):
            image = image.read_bytes()

        try:
            client = await self._get_client()

            # Docling expects file upload
            files = {"file": ("image.png", image, "image/png")}

            response = await client.post(
                f"{self.url}/convert",
                files=files,
                data={"output_format": "markdown"},
            )
            response.raise_for_status()
            result = response.json()

            text = result.get("markdown", result.get("text", ""))

            return OCRResult(
                text=text,
                confidence=0.9,  # Docling doesn't provide confidence
                model_id="docling-v2",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                metadata={"format": "markdown"},
            )

        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                model_id="docling-v2",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )

    async def process_pdf(
        self,
        pdf: bytes | Path,
        pages: list[int] | None = None,
    ) -> OCRResult:
        start_time = time.time()

        if isinstance(pdf, Path):
            pdf = pdf.read_bytes()

        try:
            client = await self._get_client()

            files = {"file": ("document.pdf", pdf, "application/pdf")}
            data = {"output_format": "markdown"}

            if pages:
                data["pages"] = ",".join(str(p) for p in pages)

            response = await client.post(
                f"{self.url}/convert",
                files=files,
                data=data,
            )
            response.raise_for_status()
            result = response.json()

            text = result.get("markdown", result.get("text", ""))
            page_count = result.get("page_count", 1)

            return OCRResult(
                text=text,
                confidence=0.9,
                model_id="docling-v2",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                page_count=page_count,
                metadata={"format": "markdown"},
            )

        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                model_id="docling-v2",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )


# ============================================================================
# Dots.OCR Adapter (OpenAI-compatible)
# ============================================================================


class DotsOCRAdapter(OCRAdapter):
    """Adapter for Dots.OCR via vLLM OpenAI-compatible API."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.url = self.config.get("url", OCR_BACKENDS["dots_ocr"]["url"])
        self.model = self.config.get("model", "dots-ocr")

    @property
    def backend(self) -> OCRBackend:
        return OCRBackend.DOTS_OCR

    async def process_image(
        self,
        image: bytes | Path,
        prompt: str | None = None,
    ) -> OCRResult:
        start_time = time.time()

        if isinstance(image, Path):
            image = image.read_bytes()

        prompt = prompt or "Extract all text from this image accurately."

        try:
            client = await self._get_client()
            image_b64 = base64.b64encode(image).decode()

            response = await client.post(
                f"{self.url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                                },
                            ],
                        }
                    ],
                    "max_tokens": 4096,
                    "temperature": 0.1,
                },
            )
            response.raise_for_status()
            result = response.json()

            text = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})

            return OCRResult(
                text=text,
                confidence=0.85,
                model_id="dots-ocr",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                metadata={
                    "tokens": usage.get("total_tokens", 0),
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                },
            )

        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                model_id="dots-ocr",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )

    async def process_pdf(
        self,
        pdf: bytes | Path,
        pages: list[int] | None = None,
    ) -> OCRResult:
        # Convert PDF pages to images and process each
        return await self._process_pdf_as_images(pdf, pages)

    async def _process_pdf_as_images(
        self,
        pdf: bytes | Path,
        pages: list[int] | None = None,
    ) -> OCRResult:
        start_time = time.time()

        if isinstance(pdf, Path):
            pdf = pdf.read_bytes()

        try:
            import io

            from pdf2image import convert_from_bytes

            images = convert_from_bytes(pdf, dpi=150)

            if pages:
                images = [images[i - 1] for i in pages if 0 < i <= len(images)]

            all_text = []
            for img in images:
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                result = await self.process_image(buf.getvalue())
                all_text.append(result.text)

            return OCRResult(
                text="\n\n".join(all_text),
                confidence=0.85,
                model_id="dots-ocr",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                page_count=len(images),
            )

        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                model_id="dots-ocr",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )


# ============================================================================
# Unstract Adapter (REST)
# ============================================================================


class UnstractAdapter(OCRAdapter):
    """Adapter for Unstract document extraction service."""

    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.url = self.config.get("url", OCR_BACKENDS["unstract"]["url"])

    @property
    def backend(self) -> OCRBackend:
        return OCRBackend.UNSTRACT

    async def process_image(
        self,
        image: bytes | Path,
        prompt: str | None = None,
    ) -> OCRResult:
        start_time = time.time()

        if isinstance(image, Path):
            image = image.read_bytes()

        try:
            client = await self._get_client()

            files = {"file": ("image.png", image, "image/png")}

            response = await client.post(
                f"{self.url}/extract",
                files=files,
            )
            response.raise_for_status()
            result = response.json()

            text = result.get("text", result.get("content", ""))

            return OCRResult(
                text=text,
                confidence=0.88,
                model_id="unstract-v1",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
            )

        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                model_id="unstract-v1",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )

    async def process_pdf(
        self,
        pdf: bytes | Path,
        pages: list[int] | None = None,
    ) -> OCRResult:
        start_time = time.time()

        if isinstance(pdf, Path):
            pdf = pdf.read_bytes()

        try:
            client = await self._get_client()

            files = {"file": ("document.pdf", pdf, "application/pdf")}

            response = await client.post(
                f"{self.url}/extract",
                files=files,
            )
            response.raise_for_status()
            result = response.json()

            text = result.get("text", result.get("content", ""))
            page_count = result.get("page_count", 1)

            return OCRResult(
                text=text,
                confidence=0.88,
                model_id="unstract-v1",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                page_count=page_count,
            )

        except Exception as e:
            return OCRResult(
                text="",
                confidence=0.0,
                model_id="unstract-v1",
                backend=self.backend,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )


# ============================================================================
# Adapter Registry
# ============================================================================


class OCRAdapterRegistry:
    """Registry for OCR adapters."""

    _adapters: dict[str, type[OCRAdapter]] = {
        "paddleocr": PaddleOCRAdapter,
        "docling": DoclingAdapter,
        "dots_ocr": DotsOCRAdapter,
        "unstract": UnstractAdapter,
    }

    @classmethod
    def get(cls, backend: str) -> OCRAdapter:
        """Get an adapter instance by backend name."""
        adapter_cls = cls._adapters.get(backend)
        if adapter_cls is None:
            raise ValueError(f"Unknown backend: {backend}. Available: {list(cls._adapters.keys())}")
        return adapter_cls(OCR_BACKENDS.get(backend, {}))

    @classmethod
    def register(cls, name: str, adapter_cls: type[OCRAdapter]) -> None:
        """Register a new adapter."""
        cls._adapters[name] = adapter_cls

    @classmethod
    def list_backends(cls) -> list[str]:
        """List available backends."""
        return list(cls._adapters.keys())


def get_adapter(backend: str) -> OCRAdapter:
    """Get an OCR adapter by backend name."""
    return OCRAdapterRegistry.get(backend)


# ============================================================================
# Comparison Functions
# ============================================================================


async def compare_ocr_models(
    image: bytes | Path,
    models: list[str] | None = None,
    prompt: str | None = None,
) -> dict[str, OCRResult]:
    """
    Compare OCR results from multiple models.

    Args:
        image: Image bytes or path
        models: List of backend names (defaults to all available)
        prompt: Optional prompt for vision-based OCR

    Returns:
        Dict mapping model name to OCRResult
    """
    models = models or ["paddleocr", "docling"]
    results: dict[str, OCRResult] = {}

    for model in models:
        try:
            adapter = get_adapter(model)
            result = await adapter.process_image(image, prompt)
            results[model] = result
            await adapter.close()
        except Exception as e:
            results[model] = OCRResult(
                text="",
                confidence=0.0,
                model_id=model,
                backend=OCRBackend(model) if model in [b.value for b in OCRBackend] else OCRBackend.PADDLEOCR,
                elapsed_seconds=0.0,
                status="error",
                error=str(e),
            )

    return results
