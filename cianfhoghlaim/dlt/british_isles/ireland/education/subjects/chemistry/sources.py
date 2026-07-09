"""Chemistry DLT source — Cianfhoghlaim Oideachais.

Reads the NCCA Leaving Certificate Chemistry PDFs from
`cianfhoghlaim/leaving_certificate/chemistry/en/`. 2 NCCA levels (OL + HL).
"""
from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt

CIANFHOGHLAIM_ROOT = Path(__file__).resolve().parents[3]
CHEM_CORPUS = CIANFHOGHLAIM_ROOT / "leaving_certificate" / "chemistry"


def _pdf_metadata(path: Path) -> dict[str, Any]:
    h = hashlib.sha256()
    size = path.stat().st_size
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return {"path": str(path.relative_to(CIANFHOGHLAIM_ROOT)), "filename": path.name, "sha256": h.hexdigest(), "size_bytes": size, "language": "en"}


@dlt.source(name="chemistry_lc")
def chem_source(language: str | None = None, use_baml: bool = True) -> list[Any]:
    return [_chem_syllabus(language, use_baml), _chem_papers(language, use_baml), _chem_marking_schemes(language, use_baml)]


def _list_pdfs(language: str | None) -> list[Path]:
    out: list[Path] = []
    for lang in (["en", "ga"] if language is None else [language]):
        corpus_dir = CHEM_CORPUS / lang
        if corpus_dir.exists():
            out.extend(sorted(corpus_dir.glob("*.pdf")))
    return out


@dlt.resource(name="chem_syllabus", primary_key=["sha256"])
def _chem_syllabus(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b
    syllabus_pdfs = [p for p in _list_pdfs(language) if "syllabus" in p.name.lower() or "SCSEC" in p.name.upper() or "Specification" in p.name]
    for pdf in syllabus_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "syllabus": None}
            continue
        text = _pdf_to_text(pdf)
        syllabus = b.ExtractCurriculumSyllabus(text)
        yield {**meta, "syllabus": syllabus.model_dump(), "topics_count": len(syllabus.topics)}


@dlt.resource(name="chem_past_papers", primary_key=["sha256"])
def _chem_papers(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b
    paper_pdfs = [p for p in _list_pdfs(language) if any(tag in p.name.upper() for tag in ("ALP", "GLP"))]
    for pdf in paper_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "paper": None}
            continue
        text = _pdf_to_text(pdf)
        paper = b.ExtractExamPaperLayout(text)
        yield {**meta, "paper": paper.model_dump()}


@dlt.resource(name="chem_marking_schemes", primary_key=["sha256"])
def _chem_marking_schemes(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b
    for pdf in _list_pdfs(language):
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "marking_scheme": None}
            continue
        text = _pdf_to_text(pdf)
        scheme = b.ExtractMarkingSchemeGuideline(text)
        yield {**meta, "marking_scheme": scheme.model_dump()}


def _pdf_to_text(pdf: Path) -> str:
    try:
        import fitz
        doc = fitz.open(str(pdf))
        return "\n".join(page.get_text() for page in doc)
    except ImportError:
        try:
            import pdfplumber
            with pdfplumber.open(str(pdf)) as pdf_doc:
                return "\n".join(page.extract_text() or "" for page in pdf_doc.pages)
        except ImportError:
            raise RuntimeError("Install PyMuPDF or pdfplumber")
