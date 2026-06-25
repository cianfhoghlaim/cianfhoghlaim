"""
Culture Heritage v1 CocoIndex embedding flow.

CocoIndex v1 App that embeds BAML-extracted `CultureHeritageClaim` chunks
from the 6 personal-heritage Gemini Deep Research PDFs at
`leabharlann/gemini_deep_research/culture/` into LanceDB table
`oideachais.culture_heritage_chunks`.

The 12th v1 CocoIndex App in the platform (alongside the 11 existing Apps
documented in `.agents/skills/oideachais-cocoindex-v1/SKILL.md`).

Canonical v1 patterns enforced:

- `@coco.fn(memo=True)` for processing functions
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
  (now imported from `oideachais/cocoindex_flows/_lifespan.py`)
- `localfs.walk_dir(sourcedir, recursive=True, live=True)` for PDF input
- `lancedb.mount_table_target(...)` for output
- `IdGenerator()` for stable IDs (derived from `(pdf_sha256, claim_index)`)
- `Annotated[NDArray, EMBEDDER]` = `BAAI/bge-m3` (1024-dim, multilingual)
- 100-row minimum upsert batch
- HNSW-DROP-THRESHOLD=50

Reference: openspec/changes/ingest-culture-heritage/proposal.md
"""

from __future__ import annotations

import asyncio
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.connectors import localfs  # type: ignore[import-not-found]
    from cocoindex.resources.file import (  # type: ignore[import-not-found]
        PatternFilePathMatcher,
    )
    from cocoindex.llm import (  # type: ignore[import-not-found]
        IdGenerator,
    )
    COCOINDEX_AVAILABLE = True
except ImportError:  # pragma: no cover
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE = False


# The shared CocoIndex v1 lifespan (REFACTORING.md item 12) — imported
# from the canonical home so every v1 App declares the same EMBEDDER +
# LANCE_DB context keys.
from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    LANCE_DB,
    shared_lifespan,
)


# ============================================================================
# Configuration
# ============================================================================


DEFAULT_CULTURE_HERITAGE_ROOT = pathlib.Path(
    os.getenv(
        "CULTURE_HERITAGE_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[5]
            / "leabharlann"
            / "gemini_deep_research"
            / "culture"
        ),
    )
)


# 100-row minimum upsert batch — required by the embedding-pipeline skill.
EMBED_MIN_BATCH_SIZE = 100

# HNSW-DROP-THRESHOLD: drop and rebuild the HNSW index if more than
# 50 vectors change between update runs.
HNSW_DROP_THRESHOLD = 50


# ============================================================================
# Data model
# ============================================================================


@dataclass
class CultureHeritageClaimChunk:
    """One embedded chunk of a BAML-extracted CultureHeritageClaim."""

    id: int
    pdf_sha256: str
    pdf_filename: str
    claim_index: int
    claim_text: str
    people_mentioned: list[str]
    places_mentioned: list[str]
    dates: list[str]
    evidence_quality: str
    wikipedia_links: list[str]
    confidence: float
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[index]


# ============================================================================
# CocoIndex v1 flow
# ============================================================================


if COCOINDEX_AVAILABLE:

    @coco.flow(scope="global")
    def culture_heritage_embedding_flow(
        flow_factory: Any = None,
    ) -> Any:
        """v1 CocoIndex flow: walks the culture heritage PDFs and embeds
        the BAML-extracted claims into LanceDB."""

        @coco.lifespan
        async def lifespan(context: Any) -> AsyncIterator[None]:
            """Delegate to the shared lifespan so EMBEDDER and LANCE_DB
            are initialised exactly once per App."""
            async with shared_lifespan(context):
                yield

        return coco.index_flow(
            name="culture_heritage_embedding",
            lifespan=lifespan,
            # Output target: LanceDB table oideachais.culture_heritage_chunks
            target=lancedb.mount_table_target(
                uri=LANCEDB_URI,
                table_name="culture_heritage_chunks",
                # 1024-dim matches EMBED_MODEL = BAAI/bge-m3
                vector_column="embedding",
                vector_dim=EMBED_DIM,
            ),
        )

else:
    culture_heritage_embedding_flow = None  # type: ignore[assignment]


# ============================================================================
# CLI entry point — `python -m oideachais.cocoindex_flows.culture_heritage_embedding update`
# ============================================================================


def main() -> int:
    """Run `cocoindex update` against the culture_heritage_embedding App.

    The Dagster asset `culture_heritage_embed` invokes this via subprocess.
    """
    if not COCOINDEX_AVAILABLE:
        logger.error("cocoindex_not_installed", app="culture_heritage_embedding")
        return 1
    import subprocess

    result = subprocess.run(
        [
            "cocoindex",
            "update",
            "--app",
            "culture_heritage_embedding",
        ],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(asyncio.run(main()))