"""
LC Subject v1 CocoIndex Embedding App (BIEP v1 canonical — parameterised).

Embeds the NCCA Leaving Certificate syllabuses, exam papers, and
marking schemes into LanceDB for **all 6 BIEP v1 LC subjects** via a
single parameterised CocoIndex v1 App.

The 7 deprecated per-subject files (chemistry_embedding.py,
mathematics_embedding.py, etc.) have been collapsed into this single
flow per the 2026-07-25-cocoindex-per-subject-dedup-v1 change.

R1–R4 v1 conformance contract:
- R1 — `from .._shared._lifespan import shared_lifespan` (delegates to the
  shared lifespan in `_lifespan.py`)
- R2 — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- R3 — `app = coco.App(coco.AppConfig(name="lc_subject_embedding"))`
  at module scope
- R4 — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim) per the BIEP v1 spec.
LanceDB table: `cianfhoghlaim.lc.<subject>.<level>_<language>` — preserves
the exact asset key shape from the deprecated per-subject files.

The 6 LC subjects (per `lc_subject_config.yaml`):
  mathematics, chemistry, geography, english, gaeilge, computer_science

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/changes/2026-07-25-cocoindex-per-subject-dedup-v1/
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


from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# ----------------------------------------------------------------------------
# Configuration (driven by `lc_subject_config.yaml`)
# ----------------------------------------------------------------------------

import yaml  # type: ignore[import-not-found]

_DEFAULT_ROOT = pathlib.Path(
    pathlib.Path(__file__).resolve().parents[2]
    / "leaving_certificate"
)

_CONFIG_PATH = pathlib.Path(
    os.getenv(
        "CIANFHOGHLAIM_LC_SUBJECT_CONFIG",
        str(pathlib.Path(__file__).resolve().parent / "lc_subject_config.yaml"),
    )
)


def _load_subject_config() -> list[dict[str, str]]:
    """Load the canonical 6 LC subjects from `lc_subject_config.yaml`.

    Returns a list of {subject, dagster_asset_key} dicts.
    Falls back to the canonical 6 BIEP v1 subjects if the YAML is missing.
    """
    fallback = [
        {"subject": "mathematics", "dagster_asset_key": "lc_mathematics_embedding"},
        {"subject": "chemistry", "dagster_asset_key": "lc_chemistry_embedding"},
        {"subject": "geography", "dagster_asset_key": "lc_geography_embedding"},
        {"subject": "english", "dagster_asset_key": "lc_english_embedding"},
        {"subject": "gaeilge", "dagster_asset_key": "lc_gaeilge_embedding"},
        {"subject": "computer_science", "dagster_asset_key": "lc_computer_science_embedding"},
    ]
    if not _CONFIG_PATH.exists():
        logger.warning(
            "lc_subject_config_missing_using_fallback",
            path=str(_CONFIG_PATH),
        )
        return fallback
    try:
        with open(_CONFIG_PATH) as f:
            cfg = yaml.safe_load(f)
        if not cfg or "subjects" not in cfg:
            return fallback
        return list(cfg["subjects"])
    except Exception as e:
        logger.warning("lc_subject_config_parse_error: %s", e)
        return fallback


SUBJECTS_CONFIG: list[dict[str, str]] = _load_subject_config()
"""The canonical 6 LC subjects driven by `lc_subject_config.yaml`."""


def _subject_root(subject: str) -> pathlib.Path:
    """Return the canonical corpus root for one LC subject."""
    return pathlib.Path(
        os.getenv(
            f"CIANFHOGHLAIM_{subject.upper()}_ROOT",
            str(_DEFAULT_ROOT / subject),
        )
    )


# ----------------------------------------------------------------------------
# Generic chunk dataclass (parameterised by subject)
# ----------------------------------------------------------------------------

@dataclass
class SubjectChunk:
    """One chunked + embedded paragraph from any LC subject PDF.

    The ``subject`` field is parameterised — every row carries the subject
    slug so a single LanceDB table per (subject, level, language) carries
    the per-subject provenance.
    """

    chunk_id: str
    subject: str
    level: str
    language: str
    filename: str
    chunk_index: int
    text: str
    embedding: Annotated[NDArray, EMBEDDER]


# ----------------------------------------------------------------------------
# CocoIndex v1 R1–R4 contract (parameterised flow)
# ----------------------------------------------------------------------------

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
    async def process_lc_subject_pdf(
        file_path: pathlib.PurePath,
        text: str,
        subject: str,
        level: str,
        language: str,
        target_table: lancedb.TableTarget[SubjectChunk],  # type: ignore[type-var]
    ) -> None:
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        filename = file_path.name
        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            vec = await embedder.embed(chunk)  # type: ignore[attr-defined]
            target_table.declare_row(
                row=SubjectChunk(
                    chunk_id=f"{file_path}#{i}",
                    subject=subject,
                    level=level,
                    language=language,
                    filename=filename,
                    chunk_index=i,
                    text=chunk,
                    embedding=vec,
                )
            )

    @coco.fn
    async def lc_subject_app_main(
        subject: str,
        sourcedir: pathlib.Path,
        level: str,
        language: str,
    ) -> None:
        """Embed one LC subject's corpus into the per-subject LanceDB table."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=f"cianfhoghlaim.lc.{subject}.{level}_{language}",
            table_schema=await lancedb.TableSchema.from_class(
                SubjectChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")

        if not sourcedir.exists():
            logger.warning(
                "lc_subject_corpus_dir_not_found",
                subject=subject,
                path=str(sourcedir),
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
            await process_lc_subject_pdf(
                file_path, text, subject, level, language, target_table
            )

    @coco.fn
    async def lc_subject_embedding_app(
        subject: str,
        level: str = "hl",
        language: str = "en",
    ) -> None:
        """Top-level entry: drive one subject's full materialisation."""
        sourcedir = _subject_root(subject)
        await lc_subject_app_main(subject, sourcedir, level, language)

    # R3 — `app = coco.App(coco.AppConfig(name=...))` at module scope.
    # Default to mathematics (the canonical first subject).
    app = coco.App(
        coco.AppConfig(name="lc_subject_embedding"),
        lc_subject_embedding_app,
        subject="mathematics",
        level="hl",
        language="en",
    )


async def query_lc_subject(
    subject: str,
    query: str,
    level: str = "hl",
    language: str = "en",
    top_k: int = 5,
) -> list[dict]:
    """Semantic search over one LC subject's LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        raise RuntimeError("cocoindex is not installed")

    from cianfhoghlaim.lancedb.search import semantic_search

    return await semantic_search(
        table=f"cianfhoghlaim.lc.{subject}.{level}_{language}",
        query=query,
        top_k=top_k,
    )


__all__ = [
    "SUBJECTS_CONFIG",
    "SubjectChunk",
    "app",
    "query_lc_subject",
    "lc_subject_embedding_app",
    "lc_subject_app_main",
    "process_lc_subject_pdf",
]