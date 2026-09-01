"""Tests for the VLM processing wrapper.

Reference: dlt_sources/british_isles/ireland/education/university/
            exam_papers/uog_exam_vlm.py
"""

from __future__ import annotations

from dlt_sources.education.ireland.british_isles.university.exam_papers.uog_exam_vlm import (
    UOG_VLM_MODEL_REGISTRY,
    UoGExamVLMConfig,
    pdf_to_images,
    run_thesis_eval,
    run_vlm_eval,
)


def test_vlm_registry_lists_exactly_four_models():
    assert len(UOG_VLM_MODEL_REGISTRY) == 4
    model_ids = {m for m, *_ in UOG_VLM_MODEL_REGISTRY}
    assert {"glm-4.6v-flash", "qwen3-vl-7b", "olmocr-2-7b", "gemma-3-9b-it"}.issubset(model_ids)


def test_vlm_config_reads_from_env(monkeypatch):
    monkeypatch.setenv("UOG_VLM_MODEL", "qwen3-vl-7b")
    monkeypatch.setenv("UOG_VLM_DPI", "300")
    monkeypatch.setenv("UOG_VLM_MAX_PAGES", "12")
    cfg = UoGExamVLMConfig.from_env()
    assert cfg.model == "qwen3-vl-7b"
    assert cfg.dpi == 300
    assert cfg.max_pages == 12


def test_pdf_to_images_returns_empty_when_pymupdf_missing(monkeypatch, uog_fake_pdf):
    """GIVEN PyMuPDF is NOT installed (the common CI scenario)
    WHEN pdf_to_images is called
    THEN it returns [] without raising."""
    # Force a re-import with the module absent.
    import sys

    monkeypatch.setitem(sys.modules, "pymupdf", None)
    monkeypatch.setitem(sys.modules, "fitz", None)
    try:
        images = pdf_to_images(uog_fake_pdf)
    finally:
        monkeypatch.undo()
    assert images == []


def test_run_vlm_eval_returns_skip_when_baml_client_missing(monkeypatch, uog_fake_pdf):
    """GIVEN the baml_client has not been generated
    WHEN run_vlm_eval is called
    THEN it returns a `baml_client_missing` row, not raise."""
    # Hide baml_client.
    import sys

    monkeypatch.setitem(sys.modules, "baml_client", None)
    # Force pdf_to_images to return something.
    monkeypatch.setattr(
        "dlt_sources.education.ireland.british_isles.university.exam_papers.uog_exam_vlm.pdf_to_images",
        lambda *_, **__: [b"%PNG-fake"],
    )
    result = run_vlm_eval(uog_fake_pdf, module_code="CT516", academic_year=2023)
    assert result["status"] == "baml_client_missing"
    assert result["module_code"] == "CT516"


def test_run_thesis_eval_emits_one_row_per_model_per_paper(monkeypatch, tmp_path):
    """Given 2 papers and 4 models, the eval emits 8 rows."""
    pdf1 = tmp_path / "CT516_2023_autumn_paper.pdf"
    pdf1.write_bytes(b"%PDF-1.4\n%fake 1\n%%EOF\n")
    pdf2 = tmp_path / "MA335_2023_autumn_paper.pdf"
    pdf2.write_bytes(b"%PDF-1.4\n%fake 2\n%%EOF\n")

    module_codes = {pdf1: "CT516", pdf2: "MA335"}
    years = {pdf1: 2023, pdf2: 2023}

    monkeypatch.setattr(
        "dlt_sources.education.ireland.british_isles.university.exam_papers.uog_exam_vlm.run_vlm_eval",
        lambda pdf, **kwargs: {
            "status": "no_images",
            "module_code": kwargs["module_code"],
            "academic_year": kwargs["academic_year"],
            "page_count": 0,
        },
    )

    rows = run_thesis_eval([pdf1, pdf2], module_codes, years)
    assert len(rows) == 8  # 2 papers x 4 models
    models_seen = {r.model for r in rows}
    assert models_seen == {"glm-4.6v-flash", "qwen3-vl-7b", "olmocr-2-7b", "gemma-3-9b-it"}
