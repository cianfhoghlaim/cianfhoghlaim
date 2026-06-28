"""
Culture Heritage v1 CocoIndex embedding App.

CocoIndex v1 App that embeds BAML-extracted `CultureHeritageClaim` chunks
from the 6 personal-heritage Gemini Deep Research PDFs at
`leabharlann/gemini_deep_research/culture/` into LanceDB table
`oideachais.culture_heritage_chunks`.

The 12th v1 CocoIndex App in the platform (alongside the 11 existing Apps
documented in `.agents/skills/oideachais-cocoindex-v1/SKILL.md`).

Canonical v1 patterns enforced (REFACTORING.md item 12):

- `coco.App(coco.AppConfig(name=...), app_main=..., lifespan=...)` at
  module scope (the canonical v1 App wrapper; replaces the
  non-canonical `@coco.flow(scope="global")` + `coco.index_flow(...)`
  hybrid).
- `@coco.fn(memo=True)` for processing functions.
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
  via delegation to `shared_lifespan` (from
  `oideachais/cocoindex_flows/_lifespan.py`).
- `localfs.walk_dir(sourcedir, recursive=True, live=True,
  filename_pattern=...)` for the JSONL input.
- `lancedb.mount_table_target(...)` for the output target.
- `IdGenerator()` for stable IDs (derived from
  `(pdf_sha256, claim_index)`).
- `Annotated[NDArray, EMBEDDER]` = `BAAI/bge-large-en-v1.5` (1024-dim;
  the value actually exported by `_lifespan.py:70`, per the
  conformance skill note on the embedder-model discrepancy).
- 100-row minimum upsert batch.
- HNSW-DROP-THRESHOLD=50.

Reference: openspec/changes/ingest-culture-heritage/proposal.md
"""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import sys
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
        FileLike,
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
    FileLike = None  # type: ignore[valid-type]
    PatternFilePathMatcher = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    COCOINDEX_AVAILABLE = False


# The shared CocoIndex v1 lifespan (REFACTORING.md item 12) — imported
# from the canonical home so every v1 App declares the same
# EMBEDDER + LANCE_DB + RESOLVED_FILE_REGISTRY context keys.
from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    LANCE_DB,
    RESOLVED_FILE_REGISTRY,
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
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[valid-type]


# ============================================================================
# CocoIndex v1 App — canonical pattern
# ============================================================================


def _make_app() -> Any:
    """Construct the culture_heritage_embedding v1 App. Returns None when
    cocoindex is missing or the optional dependency chain is incomplete.
    """
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def culture_heritage_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,  # type: ignore[valid-type]
    ) -> AsyncIterator[None]:
        # Delegate to the shared lifespan (REFACTORING.md item 12).
        # The shared lifespan provides LANCE_DB + EMBEDDER +
        # RESOLVED_FILE_REGISTRY; this App needs no App-specific
        # additional context keys (the culture heritage dataset lives
        # entirely in the shared LanceDB namespace).
        async with shared_lifespan(builder):  # type: ignore[arg-type]
            yield

    @coco.fn(memo=True)
    async def process_culture_heritage_jsonl(  # type: ignore[no-redef]
        jsonl_file: FileLike,  # type: ignore[valid-type]
        table: lancedb.TableTarget,  # type: ignore[valid-type]
    ) -> int:
        """Read one BAML-extracted JSONL of CultureHeritageClaim rows,
        embed each, and upsert into the LanceDB table target.

        The JSONL format is the output of `baml_src/culture_extraction.baml`'s
        `ExtractCultureHeritageClaims` function: one claim per line, each
        line is JSON with the same fields as `CultureHeritageClaimChunk`.
        """
        if COCOINDEX_AVAILABLE:
            from sentence_transformers import SentenceTransformer  # type: ignore

            embedder = SentenceTransformer(EMBED_MODEL)

        rows: list[dict[str, Any]] = []
        text_to_embed: list[str] = []
        with open(jsonl_file.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                claim = json.loads(line)
                text_to_embed.append(claim["claim_text"])
                rows.append(claim)

        if not rows:
            logger.info(
                "culture_heritage_empty_file",
                path=str(jsonl_file.path),
            )
            return 0

        # Batch embed (100-row minimum per the embedding-pipeline skill).
        embeddings: list[list[float]] = []
        for i in range(0, len(text_to_embed), EMBED_MIN_BATCH_SIZE):
            batch = text_to_embed[i : i + EMBED_MIN_BATCH_SIZE]
            emb = embedder.encode(batch, normalize_embeddings=True)
            embeddings.extend(emb.tolist())

        id_gen = IdGenerator(prefix="culture_heritage_claim")
        for claim, embedding in zip(rows, embeddings):
            chunk_id = id_gen(
                f"{claim['pdf_sha256']}_{claim['claim_index']}"
            )
            await table.declare_record(
                CultureHeritageClaimChunk(
                    id=chunk_id,
                    pdf_sha256=claim["pdf_sha256"],
                    pdf_filename=claim["pdf_filename"],
                    claim_index=claim["claim_index"],
                    claim_text=claim["claim_text"],
                    people_mentioned=claim.get("people_mentioned", []),
                    places_mentioned=claim.get("places_mentioned", []),
                    dates=claim.get("dates", []),
                    evidence_quality=claim.get("evidence_quality", "unknown"),
                    wikipedia_links=claim.get("wikipedia_links", []),
                    confidence=claim.get("confidence", 0.0),
                    embedding=embedding,
                )
            )

        logger.info(
            "culture_heritage_processed",
            path=str(jsonl_file.path),
            rows=len(rows),
        )
        return len(rows)

    @coco.fn
    async def culture_heritage_embedding_app_main(  # type: ignore[no-redef]
        source_root: pathlib.Path,
    ) -> None:
        """App entry point: walk the source directory, mount the LanceDB
        target, and process every JSONL file.

        Mirrors the v1 canonical pattern from
        `docs_skills_consolidation.py:docs_skills_app_main` and
        `codebase_indexing.py:codebase_app_main`.
        """
        table = await lancedb.mount_table_target(  # type: ignore[union-attr]
            uri=LANCEDB_URI,
            table_name="culture_heritage_chunks",
            vector_column="embedding",
            vector_dim=EMBED_DIM,
        )
        async for jsonl_file in localfs.walk_dir(  # type: ignore[union-attr]
            source_root,
            recursive=True,
            live=True,
            filename_pattern=PatternFilePathMatcher("**/*.jsonl"),
        ):
            await process_culture_heritage_jsonl(jsonl_file, table)

    return coco.App(  # type: ignore[union-attr]
        coco.AppConfig(name="culture_heritage_embedding"),  # type: ignore[union-attr]
        app_main=culture_heritage_embedding_app_main,
        lifespan=culture_heritage_lifespan,
    )


culture_heritage_embedding_app = _make_app()


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
    sys.exit(main())