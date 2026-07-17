"""Root PDFs v1 CocoIndex Embedding App.

Embeds the extracted content from the 5 NCCA root-level programme PDFs
into LanceDB. The 5 tables are:
  - cianfhoghlaim.lc.root.key_competencies.<lang>
  - cianfhoghlaim.lc.root.online_learning.<lang>
  - cianfhoghlaim.lc.root.certification.<lang>
  - cianfhoghlaim.lc.root.scr_advisory.<lang>
  - cianfhoghlaim.lc.root.programme_statement.<lang>

Follows the canonical v1 pattern from `leabharlann_embedding.py` and
`_lifespan.py`:
  - `@coco.fn` for processing functions
  - `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
  - `localfs.walk_dir(sourcedir, recursive=True, ...)` for input
  - `lancedb.mount_table_target(...)` for output
  - `IdGenerator()` for stable IDs
  - BGE-M3 multilingual 1024-dim embeddings

Per `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/
ncca-leaving-cert-root-pdfs/spec.md` Requirement R3.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
from collections.abc import AsyncIterator
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco
    from cocoindex.connectors import lancedb, localfs
    from cocoindex.ops.sentence_transformers import (
        SentenceTransformerEmbedder,
    )
    from cocoindex.resources.id import IdGenerator

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None
    lancedb = None
    localfs = None
    SentenceTransformerEmbedder = None
    IdGenerator = None


# The shared CocoIndex v1 lifespan
from ._lifespan import (  # noqa: E402
    LANCE_DB,
    EMBEDDER,
    RESOLVED_FILE_REGISTRY,
    lifespan,
)

# The 5 NCCA root-level PDFs and their target tables
_ROOT_PDFS = (
    ("key_competencies", "NCCAKeyCompetency"),
    ("online_learning", "PedagogySet"),
    ("certification", "CertGuidance"),
    ("scr_advisory", "ExaminerCommentary"),
    ("programme_statement", "AimsExpectations"),
)


# The v1 App for the root PDFs
if COCOINDEX_AVAILABLE:
    app = coco.App(
        name="root_pdfs_embedding",
        description="Embeds the 5 NCCA root-level programme PDFs into LanceDB",
    )

    @coco.lifespan
    async def root_pdfs_lifespan() -> AsyncIterator[None]:
        """Delegate to the shared _lifespan.py."""
        async with lifespan():
            yield

    for table_slug, baml_type in _ROOT_PDFS:
        @coco.fn
        def process_root_pdf(
            content_key: Annotated[str, coco.ResolvedKey],
            content: Annotated[dict, coco.source_files],
        ) -> Annotated[dict, lancedb.target_fields]:
            """Process one extracted PDF into a LanceDB row."""
            return {
                "id": IdGenerator().from_content(content_key),
                "content": str(content),
                "metadata": {
                    "table_slug": table_slug,
                    "baml_type": baml_type,
                    "extracted_at": os.environ.get("CIANFHOGHLAIM_BUILD_TIME", ""),
                },
            }

        @app.target(
            name=f"cianfhoghlaim.lc.root.{table_slug}",
            fields={
                "id": str,
                "content": str,
                "metadata": dict,
            },
        )
        def root_pdf_table(
            embedder: Annotated[Any, EMBEDDER],
            lance_db: Annotated[Any, LANCE_DB],
        ) -> lancedb.TableTarget:
            target_table = lancedb.TableTarget(
                db=lance_db,
                table_name=f"cianfhoghlaim.lc.root.{table_slug}",
                embedding=embedder.embedding(),
            )
            target_table.declare_vector_index(column="embedding")  # R4
            return target_table
else:
    app = None
    logger.warning("root_pdfs_embedding_app_disabled: cocoindex_not_available")


async def update_all_root_pdfs_async() -> None:
    """Update all 5 root PDF tables in the CocoIndex v1 App."""
    if not COCOINDEX_AVAILABLE or app is None:
        logger.warning("root_pdfs_embedding_update_skipped: cocoindex_not_available")
        return

    async def _run_update() -> None:
        logger.info("root_pdfs_embedding_update_started")
        try:
            await app.update()
            logger.info("root_pdfs_embedding_update_complete")
        except Exception as e:
            logger.error("root_pdfs_embedding_update_failed: %s", e)
            raise

    await _run_update()


def update_all_root_pdfs() -> None:
    """Synchronous entry point used by Dagster assets."""
    asyncio.run(update_all_root_pdfs_async())


if __name__ == "__main__":
    update_all_root_pdfs()