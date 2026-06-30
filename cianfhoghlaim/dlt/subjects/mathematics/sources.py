"""Mathematics DLT source — Cianfhoghlaim Oideachais.

Reads the 7 NCCA Leaving Certificate Mathematics PDFs from
`cianfhoghlaim/leaving_certificate/mathematics/{en,ga}/` and yields 6
dlt resources per the BAML schema in
`cianfhoghlaim/baml/qpack_mathematics.baml`:

1. math_syllabus — the LeavingCertSyllabus BAML output (topics + LOs)
2. math_syllabus_structure — the SyllabusStructure BAML output
   (level sections, chapter counts, page ranges)
3. math_past_papers — the LeavingCertPastPaper BAML output
4. math_marking_schemes — the LeavingCertMarkingScheme BAML output
5. math_alp_items — the Higher-level (ALP) question items
6. math_glp_items — the Ordinary-level (GLP) question items

The source is **fully local** — it reads from the downloaded PDFs in
`cianfhoghlaim/leaving_certificate/` and does NOT scrape the web.
This is the v1 of the Mathematics pipeline; the web-scraping
fallback is documented in `openspec/changes/ncca-leaving-cert-syllabi-corpus/`
but is not used here because the PDFs are already on disk.

Usage:
    from cianfhoghlaim.dlt.subjects.mathematics import math_source
    pipeline = dlt.pipeline(pipeline_name="math_pipeline", destination=...)
    load_info = pipeline.run(math_source())

See:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
    .agents/skills/cianfhoghlaim-mmo/SKILL.md (the new canonical skill)
    cianfhoghlaim/baml/qpack_mathematics.baml (the BAML contract)
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Iterator

import dlt

# Canonical paths
CIANFHOGHLAIM_ROOT = Path(__file__).resolve().parents[3]
MATH_CORPUS = CIANFHOGHLAIM_ROOT / "leaving_certificate" / "mathematics"
MATH_CORPUS_EN = MATH_CORPUS / "en"
MATH_CORPUS_GA = MATH_CORPUS / "ga"


def _pdf_metadata(path: Path) -> dict[str, Any]:
    """Compute SHA-256 + size + filename metadata for a PDF."""
    h = hashlib.sha256()
    size = path.stat().st_size
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return {
        "path": str(path.relative_to(CIANFHOGHLAIM_ROOT)),
        "filename": path.name,
        "sha256": h.hexdigest(),
        "size_bytes": size,
        "language": "ga" if "_ga" in path.name.lower() or "siollabais" in path.name.lower() else "en",
    }


@dlt.source(name="mathematics_lc")
def math_source(
    language: str | None = None,
    level: str | None = None,
    use_baml: bool = True,
) -> list[Any]:
    """Yield 6 dlt resources for the NCCA Leaving Certificate Mathematics corpus.

    Args:
        language: 'en', 'ga', or None for both
        level: 'hl', 'ol', 'fl', or None for all
        use_baml: if True, invoke the BAML extraction client; if False,
            yield only the raw PDF metadata (useful for dry-run / smoke tests)

    Returns:
        A list of 6 dlt resources
    """
    if language and language not in {"en", "ga"}:
        raise ValueError(f"language must be 'en' or 'ga', got {language!r}")
    if level and level not in {"hl", "ol", "fl"}:
        raise ValueError(f"level must be 'hl', 'ol', or 'fl', got {level!r}")

    resources = [
        _math_syllabus_resource(language, level, use_baml),
        _math_syllabus_structure_resource(language, level, use_baml),
        _math_past_papers_resource(language, level, use_baml),
        _math_marking_schemes_resource(language, level, use_baml),
        _math_alp_items_resource(use_baml),
        _math_glp_items_resource(use_baml),
    ]
    return resources


def _list_pdfs(language: str | None, level: str | None = None) -> list[Path]:
    """List Mathematics PDFs matching the language + level filters."""
    langs = ["en", "ga"] if language is None else [language]
    out: list[Path] = []
    for lang in langs:
        corpus_dir = MATH_CORPUS_EN if lang == "en" else MATH_CORPUS_GA
        if not corpus_dir.exists():
            continue
        for pdf in sorted(corpus_dir.glob("*.pdf")):
            if level:
                # Heuristic: "ALP" = HL, "GLP" = OL, "BLP" = Foundation, "SCSEC" = syllabus/spec
                ll = pdf.name.upper()
                if level == "hl" and "ALP" not in ll and "SC" not in ll:
                    continue
                if level == "ol" and "GLP" not in ll and "SC" not in ll:
                    continue
                if level == "fl" and "BLP" not in ll and "SC" not in ll:
                    continue
            out.append(pdf)
    return out


@dlt.resource(name="math_syllabus", primary_key=["sha256"])
def _math_syllabus_resource(
    language: str | None, level: str | None, use_baml: bool
) -> Iterator[dict[str, Any]]:
    """Yield one row per syllabus PDF with BAML-extracted topics + LOs."""
    from cianfhoghlaim.baml_client import b  # type: ignore

    syllabus_pdfs = [p for p in _list_pdfs(language, level) if "syllabus" in p.name.lower() or "SCSEC" in p.name.upper()]

    for pdf in syllabus_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "syllabus": None, "topics_count": 0, "los_count": 0}
            continue

        # Read the PDF text (PyMuPDF or pdfplumber — whichever is on the venv)
        text = _pdf_to_text(pdf)
        syllabus = b.ExtractLeavingCertSyllabus(text)
        yield {
            **meta,
            "syllabus": syllabus.model_dump(),
            "subject": syllabus.subject,
            "year": syllabus.year,
            "topics_count": len(syllabus.topics),
            "los_count": sum(len(t.learning_outcomes) for t in syllabus.topics),
        }


@dlt.resource(name="math_syllabus_structure", primary_key=["sha256"])
def _math_syllabus_structure_resource(
    language: str | None, level: str | None, use_baml: bool
) -> Iterator[dict[str, Any]]:
    """Yield one row per syllabus PDF with BAML-extracted level sections."""
    from cianfhoghlaim.baml_client import b  # type: ignore

    syllabus_pdfs = [p for p in _list_pdfs(language, level) if "syllabus" in p.name.lower() or "SCSEC" in p.name.upper()]

    for pdf in syllabus_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "structure": None, "level_count": 0}
            continue

        text = _pdf_to_text(pdf)
        structure = b.ExtractSyllabusStructure(text, "Mathematics", meta["language"])
        yield {
            **meta,
            "structure": structure.model_dump(),
            "level_count": len(structure.level_sections),
        }


@dlt.resource(name="math_past_papers", primary_key=["sha256"])
def _math_past_papers_resource(
    language: str | None, level: str | None, use_baml: bool
) -> Iterator[dict[str, Any]]:
    """Yield one row per past-paper PDF."""
    from cianfhoghlaim.baml_client import b  # type: ignore

    paper_pdfs = [
        p for p in _list_pdfs(language, level)
        if any(tag in p.name.upper() for tag in ("ALP", "GLP", "BLP"))
    ]

    for pdf in paper_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "paper": None, "items_count": 0}
            continue

        text = _pdf_to_text(pdf)
        paper = b.ExtractLeavingCertPastPaper(text)
        yield {
            **meta,
            "paper": paper.model_dump(),
            "items_count": len(paper.items) if hasattr(paper, "items") else 0,
        }


@dlt.resource(name="math_marking_schemes", primary_key=["sha256"])
def _math_marking_schemes_resource(
    language: str | None, level: str | None, use_baml: bool
) -> Iterator[dict[str, Any]]:
    """Yield one row per marking-scheme PDF (NCCA publishes alongside papers)."""
    from cianfhoghlaim.baml_client import b  # type: ignore

    # Marking schemes are typically co-located with past papers
    for pdf in _list_pdfs(language, level):
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "marking_scheme": None, "items_count": 0}
            continue

        text = _pdf_to_text(pdf)
        scheme = b.ExtractLeavingCertMarkingScheme(text)
        yield {
            **meta,
            "marking_scheme": scheme.model_dump(),
            "items_count": len(scheme.items) if hasattr(scheme, "items") else 0,
        }


@dlt.resource(name="math_alp_items", primary_key=["item_id"])
def _math_alp_items_resource(use_baml: bool) -> Iterator[dict[str, Any]]:
    """Yield one row per HL (ALP) question item across all past papers."""
    for row in _math_past_papers_resource(language="en", level="hl", use_baml=use_baml):
        paper = row.get("paper")
        if not paper:
            continue
        for item in (paper.get("items") or []):
            yield {
                "item_id": item.get("id"),
                "sha256": row["sha256"],
                "filename": row["filename"],
                "level": "hl",
                "item": item,
            }


@dlt.resource(name="math_glp_items", primary_key=["item_id"])
def _math_glp_items_resource(use_baml: bool) -> Iterator[dict[str, Any]]:
    """Yield one row per OL (GLP) question item across all past papers."""
    for row in _math_past_papers_resource(language="en", level="ol", use_baml=use_baml):
        paper = row.get("paper")
        if not paper:
            continue
        for item in (paper.get("items") or []):
            yield {
                "item_id": item.get("id"),
                "sha256": row["sha256"],
                "filename": row["filename"],
                "level": "ol",
                "item": item,
            }


def _pdf_to_text(pdf: Path) -> str:
    """Extract text from a PDF. Tries PyMuPDF first, falls back to pdfplumber."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(pdf))
        return "\n".join(page.get_text() for page in doc)
    except ImportError:
        try:
            import pdfplumber

            with pdfplumber.open(str(pdf)) as pdf_doc:
                return "\n".join(page.extract_text() or "" for page in pdf_doc.pages)
        except ImportError:
            raise RuntimeError(
                "Neither PyMuPDF nor pdfplumber is installed. "
                "Install one with `uv add pymupdf` or `uv add pdfplumber`."
            )