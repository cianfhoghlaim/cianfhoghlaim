"""cocoindex_flows.british_isles.ireland.education.lc.geography
-- the BIEP v3 Leaving Certificate Geography CocoIndex v1 App.
Sister module to `mathematics.py`.
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
    logger.warning("cocoindex_v1_not_available_for_geography: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    _coco_lancedb = None  # type: ignore[assignment]
    FileLike = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    NDArray = None  # type: ignore[assignment]


from ....._shared._lifespan import (  # noqa: E402
    EMBEDDER, LANCE_DB, shared_lifespan,
)
from ._shared import (  # noqa: E402
    baml_available, build_subject_fixture, chunk_text,
    pure_python_embed, python_baml_fallback_extract,
)

_BAML_AVAILABLE: bool = baml_available()
if _BAML_AVAILABLE:
    try:
        from baml_client.baml_client import b  # type: ignore[import-not-found]
        _baml_extract = b.ExtractLCSyllabusGeography
    except ImportError:
        _baml_extract = None  # type: ignore[assignment]
else:
    _baml_extract = None  # type: ignore[assignment]


def _python_baml_fallback_extract(text: str) -> dict[str, Any]:
    return python_baml_fallback_extract("geography", text)


@dataclass
class GeographyChunk:
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
    async def process_geography_file(
        file: "FileLike", subject: str, language: str, level: str,
        target_table: "_coco_lancedb.TableTarget[GeographyChunk]",
    ) -> None:
        text = await file.read_text()
        chunks = chunk_text(text)
        if _baml_extract is not None:
            try:
                extraction = _baml_extract(text=text)
                topic = (extraction.topic or "") if hasattr(extraction, "topic") else ""
                extracted_level = (extraction.level or "") if hasattr(extraction, "level") else ""
                year = (extraction.year or "") if hasattr(extraction, "year") else ""
            except Exception as exc:
                logger.warning("baml_extract_failed_for_geography: %s", exc)
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
        embedder = await coco.use_context(EMBEDDER)
        id_gen = IdGenerator()
        for chunk_text_str in chunks:
            vec = await embedder.embed(chunk_text_str)
            target_table.declare_row(
                row=GeographyChunk(
                    chunk_id=await id_gen.next_id(chunk_text_str),
                    subject=subject, language=language, level=level,
                    text=chunk_text_str, embedding=vec,
                    source_url=str(file.file_path),
                    extracted_topic=topic, extracted_level=extracted_level,
                    extracted_year=year,
                ),
            )

    @coco.fn
    async def geography_app_main(
        sourcedir: pathlib.Path, language: str, level: str,
    ) -> None:
        target_table = await _coco_lancedb.mount_table_target(
            LANCE_DB,
            table_name=f"cianhoghlaim.ireland.leaving_cycle.geography.{level}_{language}_chunks",
            table_schema=await _coco_lancedb.TableSchema.from_class(
                GeographyChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        if not sourcedir.exists():
            logger.warning("geography_corpus_dir_not_found", language=language, level=level, path=str(sourcedir))
            return
        from cocoindex.connectors import localfs as _coco_localfs
        files = _coco_localfs.walk_dir(sourcedir, recursive=True, path_matcher=None, live=True)
        async for record in files.items():
            file_path = pathlib.PurePath(record["path"])
            if not (str(file_path).lower().endswith(".pdf") or str(file_path).lower().endswith(".txt") or str(file_path).lower().endswith(".md")):
                continue
            await process_geography_file(file=record, subject="geography", language=language, level=level, target_table=target_table)


if COCOINDEX_AVAILABLE:
    app = coco.App(
        coco.AppConfig(name="ireland_lc_geography_embedding"),
        geography_app_main,
        sourcedir=pathlib.Path(os.getenv("CIANFHOGHLAIM_LC_GEOGRAPHY_ROOT", "leaving_certificate/geography")),
        language="en", level="hl",
    )


async def run_geography_subject(
    sourcedir: pathlib.Path, language: str = "en", level: str = "hl", embed_fn=None,
) -> list[dict[str, Any]]:
    if embed_fn is None:
        embed_fn = pure_python_embed
    rows: list = []
    if sourcedir.exists():
        for fp in sorted(sourcedir.glob("**/*")):
            if fp.is_file() and fp.suffix.lower() in {".pdf", ".txt", ".md"}:
                try:
                    text = fp.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    text = ""
                if text:
                    rows.append({"filename": fp.name, "text": text, "level": level, "language": language, "source_url": str(fp)})
    if not rows:
        rows = build_subject_fixture("geography", num_rows=5)
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
                "subject": "geography", "language": row["language"], "level": row["level"],
                "text": chunk, "embedding": embedding, "source_url": row["source_url"],
                "extracted_topic": ", ".join(fields.get("topic", [])),
                "extracted_level": ", ".join(fields.get("level", [])),
                "extracted_year": ", ".join(fields.get("year", [])),
            })
    return out


__all__ = ["GeographyChunk", "process_geography_file", "geography_app_main", "app", "run_geography_subject", "COCOINDEX_AVAILABLE", "_BAML_AVAILABLE"]
