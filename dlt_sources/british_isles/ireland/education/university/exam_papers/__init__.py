"""UoG exam-papers pipeline package.

Wraps the authenticated University of Galway past-exam-paper
corpus through BAML extraction and CocoIndex embeddings. Exports the
canonical entry points:

  - `uog_exam_papers_source` (DLT source, 5 resources)
  - `uog_exam_assets`         (Dagster asset list, 5 assets)
  - `UoGExamScraper`          (Playwright helper at the scraper layer)
  - `UoGSsoConfig`            (secrets + storage paths)
  - `UoGExamVLMConfig`        (VLM registry for the thesis evaluator)
"""

from __future__ import annotations

from .uog_exam_assets import (
    GROUP_NAME,
    uog_exam_assets,
    uog_exam_login_health,
    uog_exam_los_map,
    uog_exam_module_discovery,
    uog_exam_papers_download,
    uog_exam_papers_ocr_extract,
)
from .uog_exam_papers_source import (
    V1_SCHOOL_WHITELIST,
    all_schools_source,
    computer_science_source,
    msc_ai_source,
    uog_exam_papers_source,
)
from .uog_exam_vlm import (
    UOG_VLM_MODEL_REGISTRY,
    ThesisEvalRow,
    UoGExamVLMConfig,
    pdf_to_images,
    run_thesis_eval,
    run_vlm_eval,
)

__all__ = [
    "GROUP_NAME",
    # VLM evaluation
    "UOG_VLM_MODEL_REGISTRY",
    "V1_SCHOOL_WHITELIST",
    "ThesisEvalRow",
    "UoGExamVLMConfig",
    "all_schools_source",
    "computer_science_source",
    "msc_ai_source",
    "pdf_to_images",
    "run_thesis_eval",
    "run_vlm_eval",
    # Dagster assets
    "uog_exam_assets",
    "uog_exam_login_health",
    "uog_exam_los_map",
    "uog_exam_module_discovery",
    "uog_exam_papers_download",
    "uog_exam_papers_ocr_extract",
    # DLT source
    "uog_exam_papers_source",
]
