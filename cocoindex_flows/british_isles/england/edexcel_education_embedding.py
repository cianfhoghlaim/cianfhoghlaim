"""
England Edexcel (Pearson) CocoIndex v1 Embedding App (BIEP v2 canonical).

Mirrors `england_aqa_education_embedding.py` but for Edexcel. Conforms to
the canonical v1 R1–R4 conformance contract.

Reference: openspec/changes/2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/
"""
from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)

try:
    from cocoindex_flows._shared._lifespan import EMBEDDER, LANCE_DB, shared_lifespan  # type: ignore  # noqa: F401
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]


from .aqa_education_embedding import (  # noqa: E402
    AQA_SUBJECTS as EDEXCEL_SUBJECTS,
    AQA_LEVELS as EDEXCEL_LEVELS,
)
from .aqa_education_embedding import AQAChunk as EdexcelChunk  # type: ignore  # noqa: E402,F401


if COCOINDEX_AVAILABLE:
    app = coco.App(coco.AppConfig(name="england_edexcel_education_embedding"))

    @coco.fn(lifespan=shared_lifespan)
    async def edexcel_qualification_embedding_flow(  # type: ignore[no-redef]
        subject: str,
        qualification_level: str,
        source_pdf: str,
        chunk_text: str,
        topic: str = "",
        ao_id: str = "",
        content_hash: str = "",
    ):
        table_name = f"cianfhoghlaim.england.edexcel.{subject}.{qualification_level}"
        target = lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB, table_name, schema=EdexcelChunk,
        )
        chunk_id = f"edexcel/{subject}/{qualification_level}/{content_hash[:16]}/{ao_id}"
        embedding = await EMBEDDER.embed(chunk_text)  # type: ignore[union-attr]
        yield EdexcelChunk(  # type: ignore[call-arg]
            chunk_id=chunk_id, board="edexcel", subject=subject,
            qualification_level=qualification_level, topic=topic,
            assessment_objective_id=ao_id, text=chunk_text,
            source_pdf=source_pdf, content_hash=content_hash, embedding=embedding,
        )
else:
    app = None  # type: ignore[assignment]

    async def edexcel_qualification_embedding_flow(*args, **kwargs):  # type: ignore[no-redef]
        if False:
            yield EdexcelChunk(  # type: ignore[call-arg]
                chunk_id="", board="", subject="", qualification_level="",
                topic="", assessment_objective_id="", text="", source_pdf="",
                content_hash="", embedding=None,  # type: ignore[arg-type]
            )


__all__: list[str] = [
    "EDEXCEL_SUBJECTS", "EDEXCEL_LEVELS", "EdexcelChunk",
    "edexcel_qualification_embedding_flow", "app",
]
