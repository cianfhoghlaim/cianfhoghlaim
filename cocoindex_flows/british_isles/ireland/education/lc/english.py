"""cocoindex_flows.british_isles.ireland.education.lc.english
-- the BIEP v3 Leaving Certificate English CocoIndex v1 App.
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
    import cocoindex as coco
    from cocoindex.connectors import lancedb as _coco_lancedb
    from cocoindex.resources.file import FileLike
    from cocoindex.resources.id import IdGenerator
    from numpy.typing import NDArray
    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available_for_english: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None
    _coco_lancedb = None
    FileLike = None
    IdGenerator = None
    NDArray = None


from ....._shared._lifespan import EMBEDDER, LANCE_DB, shared_lifespan
from ._shared import (
    baml_available, build_subject_fixture, chunk_text,
    pure_python_embed, python_baml_fallback_extract,
)

_BAML_AVAILABLE: bool = baml_available()
if _BAML_AVAILABLE:
    try:
        from baml_client.baml_client import b
        _baml_extract = b.ExtractLCSyllabusEnglish
    except ImportError:
        _baml_extract = None
else:
    _baml_extract = None


def _python_baml_fallback_extract(text: str) -> dict[str, Any]:
    return python_baml_fallback_extract("english", text)


@dataclass
class EnglishChunk:
    chunk_id: str
    subject: str
    language: str
    level: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]
    source_url: str
    extracted_topic: str
    extracted_level: str
    extracted_year: str


if COCOINDEX_AVAILABLE:
    @coco.fn(memo=True)
    async def process_english_file(
        file, subject, language, level, target_table,
    ):
        text = await file.read_text()
        chunks = chunk_text(text)
        if _baml_extract is not None:
            try:
                extraction = _baml_extract(text=text)
                topic = (extraction.topic or "") if hasattr(extraction, "topic") else ""
                extracted_level = (extraction.level or "") if hasattr(extraction, "level") else ""
                year = (extraction.year or "") if hasattr(extraction, "year") else ""
            except Exception as exc:
                logger.warning("baml_extract_failed_for_english: %s", exc)
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
                row=EnglishChunk(
                    chunk_id=await id_gen.next_id(chunk_text_str),
                    subject=subject, language=language, level=level,
                    text=chunk_text_str, embedding=vec,
                    source_url=str(file.file_path),
                    extracted_topic=topic, extracted_level=extracted_level,
                    extracted_year=year,
                ),
            )

    @coco.fn
    async def english_app_main(sourcedir, language, level):
        target_table = await _coco_lancedb.mount_table_target(
            LANCE_DB,
            table_name=f"cianhoghlaim.ireland.leaving_cycle.english.{level}_{language}_chunks",
            table_schema=await _coco_lancedb.TableSchema.from_class(
                EnglishChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        if not sourcedir.exists():
            logger.warning("english_corpus_dir_not_found", language=language, level=level, path=str(sourcedir))
            return
        from cocoindex.connectors import localfs as _coco_localfs
        files = _coco_localfs.walk_dir(sourcedir, recursive=True, path_matcher=None, live=True)
        async for record in files.items():
            file_path = pathlib.PurePath(record["path"])
            if not (str(file_path).lower().endswith(".pdf") or str(file_path).lower().endswith(".txt") or str(file_path).lower().endswith(".md")):
                continue
            await process_english_file(file=record, subject="english", language=language, level=level, target_table=target_table)


if COCOINDEX_AVAILABLE:
    app = coco.App(
        coco.AppConfig(name="ireland_lc_english_embedding"),
        english_app_main,
        sourcedir=pathlib.Path(os.getenv("CIANFHOGHLAIM_LC_ENGLISH_ROOT", "leaving_certificate/english")),
        language="en", level="hl",
    )


async def run_english_subject(sourcedir, language="en", level="hl", embed_fn=None):
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
        rows = build_subject_fixture("english", num_rows=5)
    out = []
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
                "subject": "english", "language": row["language"], "level": row["level"],
                "text": chunk, "embedding": embedding, "source_url": row["source_url"],
                "extracted_topic": ", ".join(fields.get("topic", [])),
                "extracted_level": ", ".join(fields.get("level", [])),
                "extracted_year": ", ".join(fields.get("year", [])),
            })
    return out


__all__ = ["EnglishChunk", "process_english_file", "english_app_main", "app", "run_english_subject", "COCOINDEX_AVAILABLE", "_BAML_AVAILABLE"]
