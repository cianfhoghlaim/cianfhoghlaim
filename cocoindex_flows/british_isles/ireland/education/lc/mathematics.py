"""cocoindex_flows.british_isles.ireland.education.lc.mathematics
-- the BIEP v3 Leaving Certificate Mathematics CocoIndex v1 App.

The single canonical CocoIndex v1 App for the Ireland Leaving
Certificate Mathematics syllabus, exam papers, and marking
schemes (BIEP v3 M1 milestone, Mathematics × EN + GA = 2
cohorts).

This module is one of the 6 per-subject modules under
`cocoindex_flows/british_isles/ireland/education/lc/`. The
shared scaffolding (subject config + BAML fallback + chunker +
embedder substitute) lives in `_shared.py` — see that file for
the cross-subject plumbing.

BIEP v3 contract (R1-R4):
- R1: imports `shared_lifespan` + `LANCE_DB` + `EMBEDDER` from
  `....._shared._lifespan`
- R2: declares 0 new ContextKeys (re-uses LANCE_DB / EMBEDDER)
- R3: `app = coco.App(coco.AppConfig(name=...))` at module scope
- R4: 2 × `@coco.fn(...)` decorators (process + main)

BAML status
-----------
The `baml_client.baml_client` module is currently unavailable
(`baml-cli generate --from baml_src` fails on duplicate class
definitions in `baml_src/_shared/templates/`). The
`_BAML_AVAILABLE` constant is `False` until that defect is
remediated. Until then, `process_mathematics_file` falls back
to `_python_baml_fallback_extract` (which uses keyword/regex
patterns calibrated for the LC Mathematics corpus).

End-to-end test
---------------
`tests/biep_parity_lc/test_mathematics.py` exercises the full
load → embed → store → query pipeline against a 3-row fixture
(HL/OL/FL snippets), using the pure-Python embedder substitute.
"""
from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)


# ----------------------------------------------------------------------------
# CocoIndex availability probe (defects #1 fixed — cocoindex 1.0.20 from PyPI)
# ----------------------------------------------------------------------------

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb as _coco_lancedb  # type: ignore[import-not-found]
    from cocoindex.resources.file import FileLike  # type: ignore[import-not-found]
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]
    from numpy.typing import NDArray  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available_for_mathematics: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    _coco_lancedb = None  # type: ignore[assignment]
    FileLike = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    NDArray = None  # type: ignore[assignment]


# ----------------------------------------------------------------------------
# R1: import shared_lifespan + LANCE_DB + EMBEDDER from _shared._lifespan
# ----------------------------------------------------------------------------

from ....._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)

from ._shared import (  # noqa: E402
    DEFAULT_EMBED_DIM,
    baml_available,
    build_subject_fixture,
    chunk_text,
    pure_python_embed,
    python_baml_fallback_extract,
)


# ----------------------------------------------------------------------------
# BAML probe (defect #3 — currently unavailable)
# ----------------------------------------------------------------------------

_BAML_AVAILABLE: bool = baml_available()
"""True iff `from baml_client.baml_client import b` succeeds.

Per the kcg-runtime-inert-layers memory, this is currently False
because `baml-cli generate --from baml_src` fails on duplicate
class definitions in `baml_src/_shared/templates/`. Once that
defect is fixed and the client regenerates, this becomes True
and `process_mathematics_file` automatically picks up the BAML
path (the `_python_baml_fallback_extract` call remains as a
final safety net).
"""

if _BAML_AVAILABLE:
    try:
        from baml_client.baml_client import b  # type: ignore[import-not-found]

        _baml_extract = b.ExtractLCSyllabusMathematics
    except ImportError:  # pragma: no cover - defensive
        _baml_extract = None  # type: ignore[assignment]
else:
    _baml_extract = None  # type: ignore[assignment]


def _python_baml_fallback_extract(text: str) -> dict[str, Any]:
    """Per-subject Python BAML fallback for Mathematics.

    Thin wrapper around `python_baml_fallback_extract("mathematics", text)`
    that lives in `_shared.py` — see that file for the keyword
    pattern dictionary. Kept here so the per-subject module is
    self-contained.
    """
    return python_baml_fallback_extract("mathematics", text)


# ----------------------------------------------------------------------------
# Per-subject chunk dataclass (R3 + R4)
# ----------------------------------------------------------------------------

@dataclass
class MathematicsChunk:
    """One chunked + embedded paragraph from an Ireland LC Mathematics PDF."""

    chunk_id: str
    subject: str
    language: str
    level: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]  # type: ignore[valid-type]
    source_url: str
    extracted_topic: str  # from the BAML fallback (or empty)
    extracted_level: str  # from the BAML fallback (or empty)
    extracted_year: str   # from the BAML fallback (or empty)


# ----------------------------------------------------------------------------
# CocoIndex v1 process + main functions
# ----------------------------------------------------------------------------

if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_mathematics_file(
        file: "FileLike",  # type: ignore[name-defined]
        subject: str,
        language: str,
        level: str,
        target_table: "_coco_lancedb.TableTarget[MathematicsChunk]",  # type: ignore[name-defined]
    ) -> None:
        """Embed one Ireland LC Mathematics PDF into the LanceDB table.

        Per-subject processor:
        - Reads the file as text
        - Splits into ~2 KB chunks (200-byte overlap)
        - Calls the BAML extraction function on the full text
          (or falls back to the Python regex extraction)
        - Embeds each chunk via the shared BGE-M3 1024-d embedder
        - Declares one row per chunk to the target table
        """
        text = await file.read_text()
        chunks = chunk_text(text)

        # BAML extraction (or Python fallback)
        if _baml_extract is not None:
            try:
                extraction = _baml_extract(text=text)
                topic = (extraction.topic or "") if hasattr(extraction, "topic") else ""
                extracted_level = (
                    (extraction.level or "") if hasattr(extraction, "level") else ""
                )
                year = (extraction.year or "") if hasattr(extraction, "year") else ""
            except Exception as exc:  # pragma: no cover - BAML runtime errors
                logger.warning("baml_extract_failed_for_mathematics: %s", exc)
                fb = _python_baml_fallback_extract(text)
                fields = fb["fields"]
                topic = ", ".join(fields.get("topic", []))
                extracted_level = ", ".join(fields.get("level", []))
                year = ", ".join(fields.get("year", []))
        else:
            fb = _python_baml_fallback_extract(text)
            fields = fb["fields"]
            topic = ", ".join(fields.get("topic", []))
            extracted_level = ", ".join(fields.get("level", []))
            year = ", ".join(fields.get("year", []))

        # Embed each chunk
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        id_gen = IdGenerator()  # type: ignore[call-arg]

        for chunk_text_str in chunks:
            vec = await embedder.embed(chunk_text_str)  # type: ignore[attr-defined]
            target_table.declare_row(
                row=MathematicsChunk(
                    chunk_id=await id_gen.next_id(chunk_text_str),
                    subject=subject,
                    language=language,
                    level=level,
                    text=chunk_text_str,
                    embedding=vec,
                    source_url=str(file.file_path),
                    extracted_topic=topic,
                    extracted_level=extracted_level,
                    extracted_year=year,
                ),
            )

    @coco.fn
    async def mathematics_app_main(
        sourcedir: pathlib.Path,
        language: str,
        level: str,
    ) -> None:
        """Top-level entry: drive one Mathematics cohort's materialisation.

        The canonical table name follows the BIEP v3 namespace:
          `cianhoghlaim.ireland.leaving_cycle.mathematics.<level>_<lang>_chunks`

        The canonical source dir follows the BIEP v3 convention:
          `leaving_certificate/mathematics/<lang>/` (relative to the
          repo root)
        """
        target_table = await _coco_lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB,  # type: ignore[arg-type]
            table_name=f"cianhoghlaim.ireland.leaving_cycle.mathematics.{level}_{language}_chunks",
            table_schema=await _coco_lancedb.TableSchema.from_class(  # type: ignore[union-attr]
                MathematicsChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")

        if not sourcedir.exists():
            logger.warning(
                "mathematics_corpus_dir_not_found",
                language=language,
                level=level,
                path=str(sourcedir),
            )
            return

        from cocoindex.connectors import localfs as _coco_localfs  # type: ignore[import-not-found]

        files = _coco_localfs.walk_dir(  # type: ignore[attr-defined]
            sourcedir, recursive=True, path_matcher=None, live=True
        )
        async for record in files.items():
            file_path = pathlib.PurePath(record["path"])
            if not (
                str(file_path).lower().endswith(".pdf")
                or str(file_path).lower().endswith(".txt")
                or str(file_path).lower().endswith(".md")
            ):
                continue
            await process_mathematics_file(
                file=record,  # type: ignore[arg-type]
                subject="mathematics",
                language=language,
                level=level,
                target_table=target_table,
            )


# ----------------------------------------------------------------------------
# R3: app at module scope
# ----------------------------------------------------------------------------

if COCOINDEX_AVAILABLE:
    app = coco.App(  # type: ignore[union-attr]
        coco.AppConfig(  # type: ignore[union-attr]
            name="ireland_lc_mathematics_embedding",
        ),
        mathematics_app_main,
        sourcedir=pathlib.Path(
            os.getenv(
                "CIANFHOGHLAIM_LC_MATHEMATICS_ROOT",
                "leaving_certificate/mathematics",
            )
        ),
        language="en",
        level="hl",
    )


# ----------------------------------------------------------------------------
# Standalone runner (test hook)
# ----------------------------------------------------------------------------

async def run_mathematics_subject(
    sourcedir: pathlib.Path,
    language: str = "en",
    level: str = "hl",
    embed_fn=None,
) -> list[dict[str, Any]]:
    """Standalone runner for Mathematics that exercises the full pipeline.

    This is the test hook: it does NOT require a live LanceDB
    connection. Instead, it:
    1. Reads the source dir (or accepts an in-memory fixture list)
    2. Runs the BAML extraction (or fallback)
    3. Computes the embeddings (via `embed_fn`, defaulting to the
       pure-Python substitute)
    4. Returns the rows as a list of dicts (not declared to LanceDB)

    Used by `tests/biep_parity_lc/test_mathematics.py` to verify
    the load → embed → store (in-memory) → query round-trip.
    """
    from ._shared import build_subject_fixture

    if embed_fn is None:
        embed_fn = pure_python_embed

    # Build the source rows: prefer the file system; fall back to fixture
    rows: list[dict[str, Any]] = []
    if sourcedir.exists():
        for fp in sorted(sourcedir.glob("**/*")):
            if fp.is_file() and fp.suffix.lower() in {".pdf", ".txt", ".md"}:
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    text = ""
                if text:
                    rows.append(
                        {
                            "filename": fp.name,
                            "text": text,
                            "level": level,
                            "language": language,
                            "source_url": str(fp),
                        }
                    )
    # If the sourcedir was missing OR empty, fall back to the in-tree fixture
    if not rows:
        rows = build_subject_fixture("mathematics", num_rows=5)

    out: list[dict[str, Any]] = []
    for row in rows:
        text = row["text"]
        if not text:
            continue
        chunks = chunk_text(text)
        fb = _python_baml_fallback_extract(text)
        fields = fb["fields"]
        for i, chunk in enumerate(chunks):
            embedding = embed_fn(chunk)
            out.append(
                {
                    "chunk_id": f"{row['filename']}#{i}",
                    "subject": "mathematics",
                    "language": row["language"],
                    "level": row["level"],
                    "text": chunk,
                    "embedding": embedding,
                    "source_url": row["source_url"],
                    "extracted_topic": ", ".join(fields.get("topic", [])),
                    "extracted_level": ", ".join(fields.get("level", [])),
                    "extracted_year": ", ".join(fields.get("year", [])),
                }
            )
    return out


__all__ = [
    "MathematicsChunk",
    "process_mathematics_file",
    "mathematics_app_main",
    "app",
    "run_mathematics_subject",
    "COCOINDEX_AVAILABLE",
    "_BAML_AVAILABLE",
]
