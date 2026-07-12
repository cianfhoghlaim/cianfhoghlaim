"""Gaeilge DLT source — Cianfhoghlaim Oideachais.

Reads the NCCA Leaving Certificate Gaeilge + Junior Cycle Gaeilge PDFs
from `cianfhoghlaim/leaving_certificate/gaeilge/`. Gaeilge has both EN
(uncommon) and GA versions; this source reads both.

3 NCCA levels (FL / OL / HL) plus Junior Cycle.

See:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
    cianfhoghlaim/baml/qpack_gaeilge.baml (the BAML contract)
"""
from __future__ import annotations

import hashlib
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt

CIANFHOGHLAIM_ROOT = Path(__file__).resolve().parents[3]
GAEL_CORPUS = CIANFHOGHLAIM_ROOT / "leaving_certificate" / "gaeilge"


def _pdf_metadata(path: Path) -> dict[str, Any]:
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
        # Gaeilge is primarily in Irish
        "language": "ga" if "Siollabais" in path.name or "IV" in path.name else "ga",
    }


@dlt.source(name="gaeilge_lc")
def gael_source(
    language: str | None = None,
    use_baml: bool = True,
) -> list[Any]:
    if language and language not in {"en", "ga"}:
        raise ValueError(f"language must be 'en' or 'ga', got {language!r}")

    return [
        _gael_syllabus_resource(language, use_baml),
        _gael_syllabus_structure_resource(language, use_baml),
        _gael_past_papers_resource(language, use_baml),
        _gael_marking_schemes_resource(language, use_baml),
        _gael_quest_items_resource(use_baml),
    ]


def _list_pdfs(language: str | None) -> list[Path]:
    out: list[Path] = []
    if not GAEL_CORPUS.exists():
        return out
    for pdf in sorted(GAEL_CORPUS.glob("*.pdf")):
        out.append(pdf)
    return out


@dlt.resource(name="gael_syllabus", primary_key=["sha256"])
def _gael_syllabus_resource(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b

    syllabus_pdfs = [
        p for p in _list_pdfs(language)
        if "syllabus" in p.name.lower() or "Siollabais" in p.name or "SCSEC" in p.name.upper()
    ]
    for pdf in syllabus_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "syllabus": None, "topics_count": 0, "los_count": 0}
            continue
        text = _pdf_to_text(pdf)
        syllabus = b.ExtractCurriculumSyllabus(text)
        yield {
            **meta,
            "syllabus": syllabus.model_dump(),
            "subject": syllabus.subject,
            "year": syllabus.year,
            "topics_count": len(syllabus.topics),
            "los_count": sum(len(t.learning_outcomes) for t in syllabus.topics),
        }


@dlt.resource(name="gael_syllabus_structure", primary_key=["sha256"])
def _gael_syllabus_structure_resource(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b

    syllabus_pdfs = [
        p for p in _list_pdfs(language)
        if "syllabus" in p.name.lower() or "Siollabais" in p.name or "SCSEC" in p.name.upper()
    ]
    for pdf in syllabus_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "structure": None, "level_count": 0}
            continue
        text = _pdf_to_text(pdf)
        structure = b.ExtractSyllabusStructure(text, "Gaeilge", meta["language"])
        yield {
            **meta,
            "structure": structure.model_dump(),
            "level_count": len(structure.level_sections),
        }


@dlt.resource(name="gael_past_papers", primary_key=["sha256"])
def _gael_past_papers_resource(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b

    paper_pdfs = [
        p for p in _list_pdfs(language)
        if any(tag in p.name.upper() for tag in ("ALP", "GLP", "BLP"))
    ]
    for pdf in paper_pdfs:
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "paper": None, "items_count": 0}
            continue
        text = _pdf_to_text(pdf)
        paper = b.ExtractExamPaperLayout(text)
        yield {**meta, "paper": paper.model_dump(), "items_count": len(paper.items) if hasattr(paper, "items") else 0}


@dlt.resource(name="gael_marking_schemes", primary_key=["sha256"])
def _gael_marking_schemes_resource(language: str | None, use_baml: bool) -> Iterator[dict[str, Any]]:
    from cianfhoghlaim.baml_client import b

    for pdf in _list_pdfs(language):
        meta = _pdf_metadata(pdf)
        if not use_baml:
            yield {**meta, "marking_scheme": None, "items_count": 0}
            continue
        text = _pdf_to_text(pdf)
        scheme = b.ExtractMarkingSchemeGuideline(text)
        yield {**meta, "marking_scheme": scheme.model_dump(), "items_count": len(scheme.items) if hasattr(scheme, "items") else 0}


@dlt.resource(name="gael_quest_items", primary_key=["item_id"])
def _gael_quest_items_resource(use_baml: bool) -> Iterator[dict[str, Any]]:
    for row in _gael_past_papers_resource(language=None, use_baml=use_baml):
        paper = row.get("paper")
        if not paper:
            continue
        for item in (paper.get("items") or []):
            yield {
                "item_id": item.get("id"),
                "sha256": row["sha256"],
                "filename": row["filename"],
                "item": item,
            }


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
