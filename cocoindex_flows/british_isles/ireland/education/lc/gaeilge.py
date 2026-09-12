"""cocoindex_flows.british_isles.ireland.education.lc.gaeilge
-- the BIEP v3 Leaving Certificate Gaeilge CocoIndex v1 App.

Irish-language only (no `en` variant per the BIEP v3 spec — the
canonical Gaeilge table is `cianhoghlaim.lc.gaeilge.hl_ga`).
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
    logger.warning("cocoindex_v1_not_available_for_gaeilge: %s", e)
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
        _baml_extract = b.ExtractLCSyllabusGaeilge
    except ImportError:
        _baml_extract = None
else:
    _baml_extract = None


def _python_baml_fallback_extract(text: str) -> dict[str, Any]:
    return python_baml_fallback_extract("gaeilge", text)


@dataclass
class GaeilgeChunk:
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
    async def process_gaeilge_file(
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
                logger.warning("baml_extract_failed_for_gaeilge: %s", exc)
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
                row=GaeilgeChunk(
                    chunk_id=await id_gen.next_id(chunk_text_str),
                    subject=subject, language=language, level=level,
                    text=chunk_text_str, embedding=vec,
                    source_url=str(file.file_path),
                    extracted_topic=topic, extracted_level=extracted_level,
                    extracted_year=year,
                ),
            )

    @coco.fn
    async def gaeilge_app_main(sourcedir, language, level):
        target_table = await _coco_lancedb.mount_table_target(
            LANCE_DB,
            table_name=f"cianhoghlaim.ireland.leaving_cycle.gaeilge.{level}_{language}_chunks",
            table_schema=await _coco_lancedb.TableSchema.from_class(
                GaeilgeChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        if not sourcedir.exists():
            logger.warning("gaeilge_corpus_dir_not_found", language=language, level=level, path=str(sourcedir))
            return
        from cocoindex.connectors import localfs as _coco_localfs
        files = _coco_localfs.walk_dir(sourcedir, recursive=True, path_matcher=None, live=True)
        async for record in files.items():
            file_path = pathlib.PurePath(record["path"])
            if not (str(file_path).lower().endswith(".pdf") or str(file_path).lower().endswith(".txt") or str(file_path).lower().endswith(".md")):
                continue
            await process_gaeilge_file(file=record, subject="gaeilge", language=language, level=level, target_table=target_table)


if COCOINDEX_AVAILABLE:
    app = coco.App(
        coco.AppConfig(name="ireland_lc_gaeilge_embedding"),
        gaeilge_app_main,
        sourcedir=pathlib.Path(os.getenv("CIANFHOGHLAIM_LC_GAEILGE_ROOT", "leaving_certificate/gaeilge")),
        language="ga", level="hl",
    )


async def run_gaeilge_subject(sourcedir, language="ga", level="hl", embed_fn=None):
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
        rows = build_subject_fixture("gaeilge", num_rows=5)
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
                "subject": "gaeilge", "language": row["language"], "level": row["level"],
                "text": chunk, "embedding": embedding, "source_url": row["source_url"],
                "extracted_topic": ", ".join(fields.get("topic", [])),
                "extracted_level": ", ".join(fields.get("level", [])),
                "extracted_year": ", ".join(fields.get("year", [])),
            })
    return out


__all__ = ["GaeilgeChunk", "process_gaeilge_file", "gaeilge_app_main", "app", "run_gaeilge_subject", "COCOINDEX_AVAILABLE", "_BAML_AVAILABLE"]
