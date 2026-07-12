"""CocoIndex leabharlann v1 App — filesystem pipeline for the
personal-archive corpus (6 subdirs × 216 docs).

Consolidates the 3 v1 CocoIndex Apps (leabharlann_books_embedding,
leabharlann_zotero_embedding, leabharlann_takeout_embedding) into a
single filesystem-source flow that walks the 6 leabharlann subdirs
and mounts a shared `leabharlann_chunks` LanceDB table.

The 6 subdirs are all Plan 1 ACTIVE:
* aigne/ (12 docs — AI / ML papers)
* gaeilge/ (45 docs — Irish-language texts)
* gemini_deep_research/ (11 docs — Gemini deep-research outputs)
* mata/ (20 docs — mathematics / statistics)
* ollscoil_na_gaillimhe/ (8 docs — University of Galway coursework)
* zotero/ (120 docs — Zotero library)

The flow:
1. Walks each subdir for PDFs / EPUBs / Markdown
2. Chunks via RecursiveSplitter (markdown-aware)
3. Embeds via BGE-M3 multilingual
4. Mounts the LanceDB target `leabharlann_chunks`

Migrated from the original skeleton (which had no `coco.App(...)` at
module scope) to the canonical v1 pattern (R1–R4 conformance contract)
by the `2026-07-09-cocoindex-v1-remaining-apps-v1` change.

- **R1** — `from ._lifespan import shared_lifespan`
- **R2** — `leabharlann_flow_app = coco.App(coco.AppConfig(name=...))`
- **R3** — `lancedb.mount_table_target(LANCE_DB, ...)`
- **R4** — `target_table.declare_vector_index(column="embedding")`
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import structlog
from numpy.typing import NDArray

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.connectors import localfs  # type: ignore[import-not-found]
    from cocoindex.ops.text import RecursiveSplitter  # type: ignore[import-not-found]
    from cocoindex.resources.file import (  # type: ignore[import-not-found]
        FileLike,
        PatternFilePathMatcher,
    )

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    RecursiveSplitter = None  # type: ignore[assignment]
    FileLike = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]


# R1: shared lifespan + canonical ContextKeys.
from ._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


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


# ============================================================================
# Row schema
# ============================================================================

if COCOINDEX_AVAILABLE:

    @dataclass
    class LeabharlannChunk:
        """One chunked + embedded paragraph from a leabharlann doc."""

        chunk_id: str
        corpus_slug: str
        filename: str
        chunk_index: int
        text: str
        embedding: Annotated[NDArray, EMBEDDER]


# ============================================================================
# v1 App: LeabharlannFlow (consolidated filesystem pipeline)
# ============================================================================

if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_leabharlann_chunk(
        chunk_text: str,
        corpus_slug: str,
        filename: str,
        chunk_index: int,
        target_table: lancedb.TableTarget[LeabharlannChunk],  # type: ignore[type-var]
    ) -> None:
        """Process one chunk into a LanceDB row."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        vec = await embedder.embed(chunk_text)  # type: ignore[attr-defined]
        chunk_id = f"{corpus_slug}::{filename}::{chunk_index}"
        target_table.declare_row(
            row=LeabharlannChunk(
                chunk_id=chunk_id,
                corpus_slug=corpus_slug,
                filename=filename,
                chunk_index=chunk_index,
                text=chunk_text,
                embedding=vec,
            )
        )

    @coco.fn
    async def leabharlann_flow_app_main(corpus_root: Path) -> None:
        """Leabharlann v1 App entry point: walks the 6 subdirs + embeds each doc."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="leabharlann_chunks",
            table_schema=await lancedb.TableSchema.from_class(
                LeabharlannChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")

        for corpus in LEABHARLANN_CORPORA:
            corpus_dir = corpus_root / corpus.slug
            if not corpus_dir.exists():
                logger.warning(
                    "leabharlann_corpus_missing",
                    corpus=corpus.slug,
                    path=str(corpus_dir),
                )
                continue

            files = localfs.walk_dir(  # type: ignore[union-attr]
                corpus_dir,
                recursive=True,
                path_matcher=PatternFilePathMatcher(
                    included_patterns=[
                        "*.pdf", "*.md", "*.txt", "*.epub", "*.docx",
                    ],
                ),
                live=True,
            )
            splitter = RecursiveSplitter()  # type: ignore[call-arg]
            async for record in files.items():
                file_path = Path(record["path"])
                filename = file_path.name
                text = ""
                try:
                    if str(file_path).lower().endswith(".pdf"):
                        import fitz  # PyMuPDF
                        doc = fitz.open(str(file_path))
                        text = "\n".join(page.get_text() for page in doc)
                        doc.close()
                    else:
                        text = file_path.read_text(encoding="utf-8", errors="replace")
                except Exception as e:  # noqa: BLE001
                    logger.warning(
                        "leabharlann_file_read_failed",
                        file=str(file_path),
                        error=str(e),
                    )
                    continue
                if not text.strip():
                    continue
                chunks = splitter.split(  # type: ignore[union-attr]
                    text,
                    chunk_size=1000,
                    chunk_overlap=200,
                    language="markdown",
                )
                for i, chunk in enumerate(chunks):
                    chunk_text = chunk.text if hasattr(chunk, "text") else str(chunk)
                    await process_leabharlann_chunk(
                        chunk_text,
                        corpus.slug,
                        filename,
                        i,
                        target_table,
                    )

    leabharlann_flow_app = coco.App(
        coco.AppConfig(name="LeabharlannFlow"),
        leabharlann_flow_app_main,
        corpus_root=Path("cianfhoghlaim/leabharlann"),
    )


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