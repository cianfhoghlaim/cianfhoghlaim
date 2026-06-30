"""English DLT source — Cianfhoghlaim Oideachais.

Reads NCCA Leaving Certificate English + Junior Cycle English PDFs.
2 NCCA levels (OL + HL) + JC.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterator

import dlt

CIANFHOGHLAIM_ROOT = Path(__file__).resolve().parents[3]
ENGL_CORPUS = CIANFHOGHLAIM_ROOT / "leaving_certificate" / "english"


def _pdf_metadata(path: Path) -> dict[str, Any]:
    h = hashlib.sha256()
    size = path.stat().st_size
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return {"path": str(path.relative_to(CIANFHOGHLAIM_ROOT)), "filename": path.name, "sha256": h.hexdigest(), "size_bytes": size, "language": "en"}


@dlt.source(name="english_lc")
def engl_source(language: str | None = None, use_baml: bool = True) -> list[Any]:
    return [_engl_syllabus(language, use_baml), _engl_papers(language, use_baml), _engl_marking_schemes(language, use_baml)]


def _list_pdfs(language: str | None) -> list[Path]:
    out: list[Path] = []
    if not ENGL_CORPUS.exists():
        return out
    out.extend(sorted(ENGL_CORPUS.glob("*.pdf")))
    return out


@dlt.resource(name="engl_syllabus", primary_key=["sha256"])
def _engl_syllabus(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b
    syllabus_pdfs = [p for p in _list_pdfs(language) if "syllabus" in p.name.lower() or "SCSEC" in p.name.upper() or "Specification" in p.name]
    for pdf in syllabus_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "syllabus": None}
            continue
        text = _pdf_to_text(pdf)
        syllabus = b.ExtractLeavingCertSyllabus(text)
        yield {**meta, "syllabus": syllabus.model_dump()}


@dlt.resource(name="engl_past_papers", primary_key=["sha256"])
def _engl_papers(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b
    paper_pdfs = [p for p in _list_pdfs(language) if any(tag in p.name.upper() for tag in ("ALP", "GLP"))]
    for pdf in paper_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "paper": None}
            continue
        text = _pdf_to_text(pdf)
        paper = b.ExtractLeavingCertPastPaper(text)
        yield {**meta, "paper": paper.model_dump()}


@dlt.resource(name="engl_marking_schemes", primary_key=["sha256"])
def _engl_marking_schemes(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b
    for pdf in _list_pdfs(language):
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "marking_scheme": None}
            continue
        text = _pdf_to_text(pdf)
        scheme = b.ExtractLeavingCertMarkingScheme(text)
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