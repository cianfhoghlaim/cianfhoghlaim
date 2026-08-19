"""
Government Circulars v1 CocoIndex Embedding App (BIEP v1 — the 7th v1 App).

Embeds the BAML-extracted `gov.ie` education circulars into
LanceDB for semantic search.

This is the cross-cutting ingestion surface — DES / NCCA / SEC /
DoE (NI) circulars from `gov.ie/en/circulars` +
`gov.ie/ga/ciorcláin`, extracted via BAML
`ExtractCircular` (`baml/education/lc_extraction/circular_extraction.baml`)
and embedded here.

R1–R4 v1 conformance contract per `_lifespan.py`:
- R1 — `from .._shared._lifespan import shared_lifespan`
- R2 — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- R3 — `app = coco.App(coco.AppConfig(name=...))` at module scope
- R4 — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim, supports Irish + English).
LanceDB table: `cianfhoghlaim.government.circulars.<dept>_<year>_<language>`.

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
"""

from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass
from typing import Annotated

import structlog
from numpy.typing import NDArray

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.connectors import localfs  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]


# R1 — delegate to the shared lifespan in _lifespan.py
from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# ============================================================================
# Configuration
# ============================================================================

# The BAML-extracted circulars land in DuckLake, but the source
# PDFs live in `leaving_certificate/government_circulars/<dept>/<year>/<lang>/`.
# The PDF dir layout mirrors the LanceDB table suffix.
DEFAULT_GOV_CIRCULARS_ROOT = pathlib.Path(
    os.getenv(
        "CIANFHOGHLAIM_GOV_CIRCULARS_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[2]
            / "leaving_certificate"
            / "government_circulars"
        ),
    )
)

GOV_DEPTS: tuple[str, ...] = ("DES", "NCCA", "SEC", "DOE_NI")


# ============================================================================
# Row schema
# ============================================================================

if COCOINDEX_AVAILABLE:

    @dataclass
    class GovCircularChunk:
        """One chunked + embedded paragraph from a gov.ie circular PDF."""

        chunk_id: str
        circular_id: str
        dept: str
        subject_area: str
        year: int
        language: str
        title: str
        filename: str
        chunk_index: int
        text: str
        embedding: Annotated[NDArray, EMBEDDER]


# ============================================================================
# v1 App: GovernmentCircularsEmbedding
# ============================================================================

if COCOINDEX_AVAILABLE:

    def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        chunks: list[str] = []
        if not text:
            return chunks
        step = chunk_size - overlap
        for i in range(0, len(text), step):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
            if i + chunk_size >= len(text):
                break
        return chunks

    @coco.fn(memo=True)
    async def process_gov_circular_pdf(
        file_path: pathlib.PurePath,
        text: str,
        dept: str,
        year: int,
        language: str,
        target_table: lancedb.TableTarget[GovCircularChunk],  # type: ignore[type-var]
    ) -> None:
        """Process one gov.ie circular PDF into chunked + embedded rows."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        filename = file_path.name
        chunks = _chunk_text(text)
        # The circular_id is derived from the filename + dept + year
        circular_id = f"{dept}-{year}-{filename.replace('.pdf', '')}"
        for i, chunk in enumerate(chunks):
            vec = await embedder.embed(chunk)  # type: ignore[attr-defined]
            target_table.declare_row(
                row=GovCircularChunk(
                    chunk_id=f"{file_path}#{i}",
                    circular_id=circular_id,
                    dept=dept,
                    subject_area="GENERAL",  # refined by BAML `ExtractCircular`
                    year=year,
                    language=language,
                    title=filename,  # BAML overwrites with proper title
                    filename=filename,
                    chunk_index=i,
                    text=chunk,
                    embedding=vec,
                )
            )

    @coco.fn
    async def government_circulars_app_main(
        sourcedir: pathlib.Path,
        dept: str,
        year: int,
        language: str,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=f"cianfhoghlaim.government.circulars.{dept.lower()}_{year}_{language}",
            table_schema=await lancedb.TableSchema.from_class(
                GovCircularChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")

        if not sourcedir.exists():
            logger.warning(
                "gov_circulars_corpus_dir_not_found",
                path=str(sourcedir),
                dept=dept,
                year=year,
                language=language,
            )
            return

        files = localfs.walk_dir(  # type: ignore[attr-defined]
            sourcedir, recursive=True, path_matcher=None, live=True
        )
        async for record in files.items():
            file_path = pathlib.PurePath(record["path"])
            if not str(file_path).lower().endswith(".pdf"):
                continue
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(str(file_path))
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
            except ImportError:
                logger.warning("pymupdf_not_available", file=str(file_path))
                continue
            await process_gov_circular_pdf(
                file_path, text, dept, year, language, target_table
            )

    app = coco.App(
        coco.AppConfig(name="GovernmentCircularsEmbedding"),
        government_circulars_app_main,
        sourcedir=DEFAULT_GOV_CIRCULARS_ROOT,
        dept="DES",
        year=2024,
        language="en",
    )


# ============================================================================
# Ad-hoc query helper
# ============================================================================


async def query_government_circulars(
    query: str,
    dept: str = "DES",
    year: int = 2024,
    language: str = "en",
    top_k: int = 5,
) -> list[dict]:
    """Semantic search over the gov.ie circulars LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        raise RuntimeError("cocoindex is not installed")

    from cianfhoghlaim.lancedb.search import semantic_search

    return await semantic_search(
        table=f"cianfhoghlaim.government.circulars.{dept.lower()}_{year}_{language}",
        query=query,
        top_k=top_k,
    )
