"""UniversityOfficialDocVLMExtractor.

Mirrors `UoGExamVLMConfig` (in `dlt_sources/.../uog_exam_vlm.py`)
but targets the **public-side** official documents surface: every
UoG / NUI / Students' Union / British Isles university document
that flows through the Stage-0 audit + Stage-1 collector +
Stage-2 BAML extraction.

The same VLM registry (GLM-4.6V Flash + Qwen3-VL-7B + olmOCR-2-7B
+ Gemma-3) is reused, but the extraction prompt is tuned for the
official-doc schema rather than the exam-paper schema.

Reference: openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
            design/cianext-uog-stage-0-firecrawl-agent.md
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# Re-use the 4-VLM model registry + PDF→PNG helper from the
# exam_papers VLM module. The import is wrapped in a try/except so
# the file remains a valid standalone target for tests that don't
# need sruth_browser on sys.path.
try:
    from dlt_sources.education.ireland.british_isles.university.exam_papers.uog_exam_vlm import (  # type: ignore
        UOG_VLM_MODEL_REGISTRY,
        pdf_to_images,
    )
    from dlt_sources.education.ireland.british_isles.university.exam_papers.uog_exam_vlm import (
        run_vlm_eval as run_exam_vlm_eval,
    )
except ImportError:  # pragma: no cover
    UOG_VLM_MODEL_REGISTRY = ()
    pdf_to_images = None  # type: ignore
    run_exam_vlm_eval = None  # type: ignore


@dataclass
class UniversityOfficialDocVLMConfig:
    """VLM config for the official-doc extraction (public side)."""

    model: str = "glm-4.6v-flash"
    dpi: int = 150  # official docs are typically scanned at lower DPI
    max_pages: int = 30
    timeout_seconds: float = 60.0
    output_schema: str = "UoGOfficialDocument"
    mlflow_experiment: str = "cianfhoghlaim_official_docs_vlm"
    extract_en_alias: str = "extract-en"

    @classmethod
    def from_env(cls) -> UniversityOfficialDocVLMConfig:
        import os

        return cls(
            model=os.environ.get("UOG_OFFICIAL_DOCS_VLM_MODEL", "glm-4.6v-flash"),
            dpi=int(os.environ.get("UOG_OFFICIAL_DOCS_VLM_DPI", "150")),
            max_pages=int(
                os.environ.get("UOG_OFFICIAL_DOCS_VLM_MAX_PAGES", "30")
            ),
            mlflow_experiment=os.environ.get(
                "UOG_OFFICIAL_DOCS_VLM_MLFLOW_EXPERIMENT",
                "cianfhoghlaim_official_docs_vlm",
            ),
        )


def run_official_doc_vlm_eval(
    pdf_path: Path,
    *,
    document_id: str,
    config: UniversityOfficialDocVLMConfig | None = None,
) -> dict[str, Any]:
    """Run one VLM extraction of an official-doc PDF.

    Returns the BAML JSON dict plus a `meta` block. Returns
    `{"status": "no_images"}` if PyMuPDF is missing — never
    raises so the upstream Dagster asset keeps going.
    """
    cfg = config or UniversityOfficialDocVLMConfig.from_env()
    images = pdf_to_images(pdf_path, dpi=cfg.dpi, max_pages=cfg.max_pages) if pdf_to_images else []
    if not images:
        return {
            "status": "no_images",
            "document_id": document_id,
            "config": cfg.__dict__,
        }
    try:
        from baml_client import b as _baml_b  # type: ignore
    except ImportError:
        return {
            "status": "baml_client_missing",
            "document_id": document_id,
            "hint": "Run `baml generate` first.",
        }
    try:
        result = _baml_b.ExtractUoGOfficialDocument(
            prompt=_bytes_to_data_url(images[0]),
            source_url=str(pdf_path),
        )
        return {
            "status": "ok",
            "document_id": document_id,
            "model": cfg.model,
            "dpi": cfg.dpi,
            "page_count": len(images),
            "official_document": (
                result.model_dump() if hasattr(result, "model_dump") else result
            ),
        }
    except Exception as exc:
        logger.warning(
            "official_doc_vlm_failed",
            model=cfg.model,
            document_id=document_id,
            error=str(exc),
        )
        return {
            "status": "error",
            "document_id": document_id,
            "model": cfg.model,
            "error": str(exc),
        }


def _bytes_to_data_url(image_bytes: bytes, mime: str = "image/png") -> str:
    import base64

    b64 = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{b64}"


@dataclass
class OfficialDocEvalRow:
    """One row in the 4-VLM thesis comparison."""

    document_id: str
    model: str
    status: str
    document_type: str = "OTHER"
    confidence: float = 0.0
    title: str = ""
    page_count: int = 0
    elapsed_ms: float = 0.0

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "model": self.model,
            "status": self.status,
            "document_type": self.document_type,
            "title": self.title,
            "page_count": self.page_count,
            "confidence": self.confidence,
            "elapsed_ms": self.elapsed_ms,
        }


def run_thesis_official_docs_eval(
    gold_set: list[Path],
    document_ids: dict[Path, str],
    *,
    models: tuple[str, ...] = tuple(m for m, *_ in UOG_VLM_MODEL_REGISTRY),
) -> list[OfficialDocEvalRow]:
    """Run the 4-VLM comparison on the official-doc gold set.

    Mirrors `run_thesis_eval` (the exam-paper sibling).
    """
    out: list[OfficialDocEvalRow] = []
    if not UOG_VLM_MODEL_REGISTRY:
        return out
    for pdf_path in gold_set:
        document_id = document_ids.get(pdf_path, pdf_path.stem)
        for model_name in models:
            cfg = UniversityOfficialDocVLMConfig(
                model=model_name,
                mlflow_experiment="cianfhoghlaim_official_docs_vlm",
            )
            t0 = time.perf_counter()
            result = run_official_doc_vlm_eval(
                pdf_path, document_id=document_id, config=cfg
            )
            elapsed = (time.perf_counter() - t0) * 1000.0
            official_doc = result.get("official_document") or {}
            out.append(
                OfficialDocEvalRow(
                    document_id=document_id,
                    model=model_name,
                    status=result.get("status", "unknown"),
                    document_type=official_doc.get("document_type", "OTHER")
                    if isinstance(official_doc, dict)
                    else "OTHER",
                    title=official_doc.get("title", "")
                    if isinstance(official_doc, dict)
                    else "",
                    confidence=float(
                        official_doc.get("confidence", 0.0) or 0.0
                    )
                    if isinstance(official_doc, dict)
                    else 0.0,
                    page_count=result.get("page_count", 0),
                    elapsed_ms=round(elapsed, 2),
                )
            )
    return out


__all__ = [
    "OfficialDocEvalRow",
    "UniversityOfficialDocVLMConfig",
    "run_official_doc_vlm_eval",
    "run_thesis_official_docs_eval",
]
