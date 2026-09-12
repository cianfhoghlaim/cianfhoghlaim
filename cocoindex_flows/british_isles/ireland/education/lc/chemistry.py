"""cocoindex_flows.british_isles.ireland.education.lc.chemistry
-- the BIEP v3 Leaving Certificate Chemistry CocoIndex v1 App.

Sister module to `mathematics.py` — same R1-R4 contract + same
BAML fallback strategy, parameterised for Chemistry. See
`mathematics.py` for the full module docstring.
"""
from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)


try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb as _coco_lancedb  # type: ignore[import-not-found]
    from cocoindex.resources.file import FileLike  # type: ignore[import-not-found]
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]
    from numpy.typing import NDArray  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:  # pragma: no cover
    logger.warning("cocoindex_v1_not_available_for_chemistry: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    _coco_lancedb = None  # type: ignore[assignment]
    FileLike = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    NDArray = None  # type: ignore[assignment]


from ....._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)

from ._shared import (  # noqa: E402
    baml_available,
    build_subject_fixture,
    chunk_text,
    pure_python_embed,
    python_baml_fallback_extract,
)


_BAML_AVAILABLE: bool = baml_available()

if _BAML_AVAILABLE:
    try:
        from baml_client.baml_client import b  # type: ignore[import-not-found]

        _baml_extract = b.ExtractLCSyllabusChemistry
    except ImportError:  # pragma: no cover
        _baml_extract = None  # type: ignore[assignment]
else:
    _baml_extract = None  # type: ignore[assignment]


def _python_baml_fallback_extract(text: str) -> dict[str, Any]:
    return python_baml_fallback_extract("chemistry", text)


@dataclass
class ChemistryChunk:
    chunk_id: str
    subject: str
    language: str
    level: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]  # type: ignore[valid-type]
    source_url: str
    extracted_topic: str
    extracted_level: str
    extracted_year: str


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_chemistry_file(
        file: "FileLike",  # type: ignore[name-defined]
        subject: str,
        language: str,
        level: str,
        target_table: "_coco_lancedb.TableTarget[ChemistryChunk]",  # type: ignore[name-defined]
    ) -> None:
        text = await file.read_text()
        chunks = chunk_text(text)

        if _baml_extract is not None:
            try:
                extraction = _baml_extract(text=text)
                topic = (extraction.topic or "") if hasattr(extraction, "topic") else ""
                extracted_level = (extraction.level or "") if hasattr(extraction, "level") else ""
                year = (extraction.year or "") if hasattr(extraction, "year") else ""
            except Exception as exc:  # pragma: no cover
                logger.warning("baml_extract_failed_for_chemistry: %s", exc)
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

        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        id_gen = IdGenerator()  # type: ignore[call-arg]

        for chunk_text_str in chunks:
            vec = await embedder.embed(chunk_text_str)  # type: ignore[attr-defined]
            target_table.declare_row(
                row=ChemistryChunk(
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
    async def chemistry_app_main(
        sourcedir: pathlib.Path,
        language: str,
        level: str,
    ) -> None:
        target_table = await _coco_lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB,  # type: ignore[arg-type]
            table_name=f"cianhoghlaim.ireland.leaving_cycle.chemistry.{level}_{language}_chunks",
            table_schema=await _coco_lancedb.TableSchema.from_class(  # type: ignore[union-attr]
                ChemistryChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")

        if not sourcedir.exists():
            logger.warning(
                "chemistry_corpus_dir_not_found",
                language=language, level=level, path=str(sourcedir),
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
            await process_chemistry_file(
                file=record,  # type: ignore[arg-type]
                subject="chemistry",
                language=language,
                level=level,
                target_table=target_table,
            )


if COCOINDEX_AVAILABLE:
    app = coco.App(  # type: ignore[union-attr]
        coco.AppConfig(  # type: ignore[union-attr]
            name="ireland_lc_chemistry_embedding",
        ),
        chemistry_app_main,
        sourcedir=pathlib.Path(
            os.getenv(
                "CIANFHOGHLAIM_LC_CHEMISTRY_ROOT",
                "leaving_certificate/chemistry",
            )
        ),
        language="en",
        level="hl",
    )


async def run_chemistry_subject(
    sourcedir: pathlib.Path,
    language: str = "en",
    level: str = "hl",
    embed_fn=None,
) -> list[dict[str, Any]]:
    """Standalone runner for Chemistry. See mathematics.py for details."""
    if embed_fn is None:
        embed_fn = pure_python_embed

    rows: list[dict[str, Any]] = []
    if sourcedir.exists():
        for fp in sorted(sourcedir.glob("**/*")):
            if fp.is_file() and fp.suffix.lower() in {".pdf", ".txt", ".md"}:
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    text = ""
                if text:
                    rows.append({
                        "filename": fp.name, "text": text, "level": level,
                        "language": language, "source_url": str(fp),
                    })
    if not rows:
        rows = build_subject_fixture("chemistry", num_rows=5)

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
            out.append({
                "chunk_id": f"{row['filename']}#{i}",
                "subject": "chemistry",
                "language": row["language"],
                "level": row["level"],
                "text": chunk,
                "embedding": embedding,
                "source_url": row["source_url"],
                "extracted_topic": ", ".join(fields.get("topic", [])),
                "extracted_level": ", ".join(fields.get("level", [])),
                "extracted_year": ", ".join(fields.get("year", [])),
            })
    return out


__all__ = [
    "ChemistryChunk",
    "process_chemistry_file",
    "chemistry_app_main",
    "app",
    "run_chemistry_subject",
    "COCOINDEX_AVAILABLE",
    "_BAML_AVAILABLE",
]
