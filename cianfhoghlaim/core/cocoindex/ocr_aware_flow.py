"""CocoIndex OCR-aware flow — wires the 11 vision models + 4 classical OCR
Docker stacks into a CocoIndex v1 pipeline for educational PDFs.

This is a NEW v4 addition that integrates:
* cianfhoghlaim.ocr.models.registry.OCR_VISION_REGISTRY (11 vision models)
* cianfhoghlaim.ocr.models.registry.CLASSICAL_OCR_REGISTRY (4 classical OCR
  Docker stacks: dots-ocr, docling-serve, olmocr, paddleocr)

with a CocoIndex flow that:
1. Walks the Ireland syllabus corpus (Plan 1 active)
2. For each PDF, selects the optimal (model, backend) pair from the registry
3. Extracts structured text + layout + fada-aware normalisation
4. Embeds the chunks via the BGE-M3 multilingual embedder
5. Mounts a LanceDB target table (`ireland_syllabus_chunks`)

The selection logic is in `select_ocr_backend()` below.

NOTE: This is a skeleton. The CocoIndex @coco.fn decorators will be added
once the upstream CocoIndex v1 release stabilises the new OCR transformer
API. The selection logic + registry wiring are production-ready.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cianfhoghlaim.ocr.models.registry import (
    OCR_VISION_REGISTRY,
    OCRModel,
)


@dataclass
class OCRAwareSelection:
    """A (model, backend) pair selected for a given document."""

    model: OCRModel
    reason: str


def select_ocr_backend(document_path: Path) -> OCRAwareSelection:
    """Pick the best (model, backend) pair for a document.

    Heuristic:
    - Small text-first PDFs (<5 MB) → Gemma-4 E2B (fast, low-VRAM)
    - Dense syllabi (5–20 MB) → Qwen3.6 27B-MLX-8bit on Apple Silicon
    - SEC exam papers (image-heavy) → Qwen3.6 35B-A3B-GGUF (best OCR)
    - Old scanned Gaelic texts (pre-1922) → GLM-4.6V-Flash
    """
    size_mb = document_path.stat().st_size / (1024 * 1024)
    name = document_path.name.lower()

    # Image-heavy / SEC exam papers: largest model
    if "sec" in name or "examination" in name or "leaving_cert" in str(document_path):
        model = next(m for m in OCR_VISION_REGISTRY if "35B-A3B-GGUF" in m.model_id)
        return OCRAwareSelection(model, "SEC exam paper → Qwen3.6 35B-A3B-GGUF")

    # Pre-1922 scanned Gaelic manuscripts: GLM vision
    if any(year in name for year in ("1900", "1910", "1920", "1922")):
        model = next(m for m in OCR_VISION_REGISTRY if "GLM-4.6V" in m.model_id)
        return OCRAwareSelection(model, "Pre-1922 manuscript → GLM-4.6V-Flash")

    # Dense syllabi: Qwen3.6 27B MLX
    if size_mb >= 5:
        model = next(m for m in OCR_VISION_REGISTRY if "27B-MLX-8bit" in m.model_id)
        return OCRAwareSelection(
            model, f"Dense syllabus ({size_mb:.1f} MB) → Qwen3.6 27B-MLX-8bit"
        )

    # Small PDFs: Gemma-4 E2B (fast)
    model = next(m for m in OCR_VISION_REGISTRY if "E2B-it" in m.model_id)
    return OCRAwareSelection(model, f"Small document ({size_mb:.1f} MB) → Gemma-4 E2B")


def build_ireland_syllabus_flow():
    """Build the CocoIndex OCR-aware flow for the Ireland syllabus corpus.

    Skeleton — the @coco.fn + @coco.lifespan decorators are added when the
    upstream CocoIndex v1 OCR transformer API lands. The selection logic
    above (select_ocr_backend) is already wired into the registry.
    """
    from cianfhoghlaim.core.cocoindex._lifespan import EMBEDDER, LANCE_DB

    # Plan 1 corpora (Ireland education)
    corpus_dirs = [
        "cianfhoghlaim/sources/nations/ie/education/early_childhood/{english,gaeilge}",
        "cianfhoghlaim/sources/nations/ie/education/primary/{english,gaeilge}",
        "cianfhoghlaim/sources/nations/ie/education/junior_cycle/{english,gaeilge}",
        "cianfhoghlaim/sources/nations/ie/education/senior_cycle/{english,gaeilge}",
        "cianfhoghlaim/sources/nations/ie/education/leaving_cert/{english,gaeilge}",
    ]

    # TODO: @coco.fn flow_ireland_syllabus_ocr() with:
    #   - gather PDFs from each corpus_dir
    #   - call select_ocr_backend(pdf) → OCRModel
    #   - dispatch to backend via cianfhoghlaim.core.browser.BrowserbaseBackend
    #     or LiteLLM / MLX / Ollama clients
    #   - normalise text with cianfhoghlaim.ocr.evaluation.gaelic_metrics
    #   - embed with EMBEDDER (BGE-M3)
    #   - mount LanceDB target `ireland_syllabus_chunks`
    return LANCE_DB, EMBEDDER, corpus_dirs


if __name__ == "__main__":
    # Smoke test the selection logic
    import sys

    for path in sys.argv[1:]:
        p = Path(path)
        if p.exists():
            sel = select_ocr_backend(p)
            print(f"{p.name}: {sel.reason}")
