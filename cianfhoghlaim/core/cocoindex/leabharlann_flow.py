"""CocoIndex leabharlann flow — filesystem + Zotero pipeline for the
personal-archive corpus (6 subdirs × 216 docs).

This is a NEW v4 addition that consolidates the 3 v1 CocoIndex Apps
(`leabharlann_books_embedding`, `leabharlann_zotero_embedding`,
`leabharlann_takeout_embedding`) into a single filesystem-source flow.

The 6 subdirs are all Plan 1 ACTIVE:
* aigne/ (12 docs — AI / ML papers)
* gaeilge/ (45 docs — Irish-language texts)
* gemini_deep_research/ (11 docs — Gemini deep-research outputs)
* mata/ (20 docs — mathematics / statistics)
* ollscoil_na_gaillimhe/ (8 docs — University of Galway coursework)
* zotero/ (120 docs — Zotero library)

The flow:
1. Walks each subdir for PDFs / EPUBs / Markdown
2. Extracts text via OCR (11 vision + 4 classical via ocr_aware_flow.py)
3. Splits via tree-sitter chunking (per-file-type aware)
4. Embeds via BGE-M3 multilingual
5. Mounts the LanceDB target `leabharlann_chunks`

NOTE: Skeleton — the @coco.fn decorators land when CocoIndex v1 stabilises.
The selection logic + registry wiring are production-ready.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LeabharlannCorpus:
    """One leabharlann subdir with metadata."""

    slug: str  # matches dir name under cianfhoghlaim/leabharlann/<slug>/
    label_ga: str  # Irish label
    label_en: str
    expected_doc_count: int
    primary_languages: tuple[str, ...]  # ISO 639-1 codes
    source_format_priority: tuple[str, ...]  # which extensions to prefer
    notes: str = ""


# The 6 leabharlann subdirs (Plan 1 active)
LEABHARLANN_CORPORA: tuple[LeabharlannCorpus, ...] = (
    LeabharlannCorpus(
        slug="aigne",
        label_ga="Aigne",
        label_en="AI / ML papers",
        expected_doc_count=12,
        primary_languages=("en",),
        source_format_priority=("pdf", "md", "txt"),
        notes="AI/ML research papers; English-first; arXiv-style.",
    ),
    LeabharlannCorpus(
        slug="gaeilge",
        label_ga="Gaeilge",
        label_en="Irish-language texts",
        expected_doc_count=45,
        primary_languages=("ga", "en"),
        source_format_priority=("pdf", "epub", "md"),
        notes="Irish-language texts; primary Plan 1 corpus for OCR eval.",
    ),
    LeabharlannCorpus(
        slug="gemini_deep_research",
        label_ga="Taighde domhain Gemini",
        label_en="Gemini deep-research outputs",
        expected_doc_count=11,
        primary_languages=("en",),
        source_format_priority=("md", "pdf", "txt"),
        notes="Gemini deep-research markdown reports; long-form.",
    ),
    LeabharlannCorpus(
        slug="mata",
        label_ga="Mata",
        label_en="Mathematics",
        expected_doc_count=20,
        primary_languages=("en", "ga"),
        source_format_priority=("pdf", "md", "txt"),
        notes="Mathematics + statistics textbooks; heavy equations.",
    ),
    LeabharlannCorpus(
        slug="ollscoil_na_gaillimhe",
        label_ga="Ollscoil na Gaillimhe",
        label_en="University of Galway coursework",
        expected_doc_count=8,
        primary_languages=("en", "ga"),
        source_format_priority=("pdf", "docx", "md"),
        notes="UoG MSc in AI coursework (2026-2027).",
    ),
    LeabharlannCorpus(
        slug="zotero",
        label_ga="Zotero",
        label_en="Zotero library",
        expected_doc_count=120,
        primary_languages=("en", "ga", "cy", "gd"),
        source_format_priority=("pdf", "epub"),
        notes="Largest subdir; mixed academic papers across Celtic + global.",
    ),
)


def discover_documents(corpus: LeabharlannCorpus,
                       root: Path = Path("cianfhoghlaim/leabharlann")) -> list[Path]:
    """Walk a corpus subdir and return all documents in priority order."""
    subdir = root / corpus.slug
    if not subdir.exists():
        return []
    docs: list[Path] = []
    for ext in corpus.source_format_priority:
        docs.extend(sorted(subdir.rglob(f"*.{ext}")))
    return docs


def build_leabharlann_flow():
    """Build the CocoIndex leabharlann flow.

    Skeleton — the @coco.fn + @coco.lifespan decorators are added when
    CocoIndex v1 stabilises. The discovery logic + registry wiring are
    production-ready.
    """
    from cianfhoghlaim.core.cocoindex._lifespan import EMBEDDER, LANCE_DB

    docs_by_corpus: dict[str, list[Path]] = {}
    for corpus in LEABHARLANN_CORPORA:
        docs_by_corpus[corpus.slug] = discover_documents(corpus)

    # TODO: @coco.fn flow_leabharlann() with:
    #   - for each (corpus, doc) pair, call select_ocr_backend(doc) → OCRModel
    #   - dispatch OCR via ocr_aware_flow + cianfhoghlaim.core.browser backends
    #   - normalise text via cianfhoghlaim.ocr.evaluation.gaelic_metrics
    #   - chunk via cianfhoghlaim.libraries.codeolas.chunking
    #   - embed via EMBEDDER (BGE-M3)
    #   - mount LanceDB target `leabharlann_chunks`
    return LANCE_DB, EMBEDDER, docs_by_corpus


def expected_total_documents() -> int:
    """Return the expected total document count (216 docs across 6 subdirs)."""
    return sum(c.expected_doc_count for c in LEABHARLANN_CORPORA)


if __name__ == "__main__":
    import sys

    discovered = sum(len(discover_documents(c)) for c in LEABHARLANN_CORPORA)
    expected = expected_total_documents()
    print(
        f"leabharlann: discovered {discovered} docs across "
        f"{len(LEABHARLANN_CORPORA)} subdirs (expected {expected})"
    )
    if discovered != expected:
        print(
            f"WARNING: discovered {discovered} != expected {expected}",
            file=sys.stderr,
        )
        sys.exit(1)
