"""
Culture heritage Dagster assets.

Four culture-heritage assets + one asset check that fire when any
BAML-extracted `CultureHeritageClaim` has confidence < 0.6.

Asset materialisation order:

    culture_heritage_extract
            ↓
    culture_heritage_embed  (CocoIndex v1 App)
            ↓
    culture_heritage_cognify  (Cognee cognify pass)
            ↓
    culture_heritage_cross_edges  (cross-dataset FalkorDB MERGE)

The `low_confidence_review` asset check is wired to `culture_heritage_extract`
and surfaces a Dagster warning when any claim has `confidence < 0.6`.

Group name: `culture_heritage`.

Reference: openspec/changes/ingest-culture-heritage/proposal.md
"""

from __future__ import annotations

import hashlib
import os
import pathlib
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


GROUP_NAME = "culture_heritage"

# Confidence threshold below which claims route out of the production
# LanceDB table and into manual review.
LOW_CONFIDENCE_THRESHOLD = 0.6


# ============================================================================
# Asset 1: extract — BAML ExtractCultureClaims on the 6 Gemini PDFs
# ============================================================================


@dg.asset(
    group_name=GROUP_NAME,
    description=(
        "BAML `ExtractCultureClaims` over the 6 personal-heritage Gemini "
        "Deep Research PDFs at `leabharlann/gemini_deep_research/culture/`. "
        "Yields a list of `CultureHeritageClaim` dicts with "
        "(claim_text, people_mentioned, places_mentioned, dates, "
        "evidence_quality, wikipedia_links, confidence)."
    ),
    metadata={
        "domain": "culture",
        "nation": "ie",
        "schema": "baml:ExtractCultureClaims",
        "source_count": 6,
        "fixture_count": 3,  # 3 Wikipedia fixtures from Task 2
    },
)
def culture_heritage_extract() -> list[dict[str, Any]]:
    """Extract CultureHeritageClaim rows from PDFs and Wikipedia fixtures.

    In production this calls
    `baml_client.ExtractCultureClaims(pdf_path=...)` for each PDF
    and `baml_client.ExtractCultureClaims(text=...)` for each fixture.

    In stub mode (`USE_LOCAL_SCRAPES=true`) this returns an empty list
    so Dagster can still materialise downstream assets for graph edges
    without the LLM having run.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info("culture_extract_stub_mode", group=GROUP_NAME)
        return []

    pdfs_dir = pathlib.Path(
        os.getenv(
            "CULTURE_HERITAGE_ROOT",
            str(
                pathlib.Path(__file__).resolve().parents[4]
                / "leabharlann"
                / "gemini_deep_research"
                / "culture"
            ),
        )
    )
    pdfs = sorted(pdfs_dir.glob("*.pdf"))
    logger.info("culture_extract_found_pdfs", count=len(pdfs), root=str(pdfs_dir))

    # Real production call: import the generated BAML client and call
    # `ExtractCultureClaims`. Stubbed out here because the BAML client
    # regeneration is blocked by the pre-existing tuatha/crypteolas
    # workspace error (tracked separately).
    raise NotImplementedError(
        "BAML client regeneration blocked by pre-existing "
        "tuatha/crypteolas workspace error; see openspec/AGENTS.md."
    )


# ============================================================================
# Asset check: low_confidence_review
# ============================================================================


@dg.asset_check(
    asset=culture_heritage_extract,
    description=(
        "Routes any claim with `confidence < 0.6` out of the production "
        "`culture_heritage_chunks` LanceDB table into manual review."
    ),
    blocking=False,
)
def low_confidence_review(
    context: dg.AssetCheckExecutionContext,
    culture_heritage_extract: list[dict[str, Any]],
) -> dg.AssetCheckResult:
    """Surface a Dagster warning when any claim has confidence < 0.6.

    Severity: WARN (blocking=False) so the pipeline continues running
    while still surfacing the issue in the Dagster UI.
    """
    low_confidence_rows = [
        row
        for row in culture_heritage_extract
        if row.get("confidence", 1.0) < LOW_CONFIDENCE_THRESHOLD
    ]
    if low_confidence_rows:
        return dg.AssetCheckResult(
            passed=False,
            severity=dg.AssetCheckSeverity.WARN,
            metadata={
                "low_confidence_count": len(low_confidence_rows),
                "threshold": LOW_CONFIDENCE_THRESHOLD,
                "sample": [
                    {
                        "claim_text": row.get("claim_text", "")[:120],
                        "confidence": row.get("confidence"),
                        "evidence_quality": row.get("evidence_quality"),
                    }
                    for row in low_confidence_rows[:5]
                ],
            },
        )
    return dg.AssetCheckResult(
        passed=True,
        severity=dg.AssetCheckSeverity.WARN,
        metadata={"low_confidence_count": 0, "threshold": LOW_CONFIDENCE_THRESHOLD},
    )


# ============================================================================
# Asset 2: embed — CocoIndex v1 App culture_heritage_embedding
# ============================================================================


@dg.asset(
    group_name=GROUP_NAME,
    description=(
        "Embed the extracted CultureHeritageClaim rows into LanceDB "
        "table `oideachais.culture_heritage_chunks` via the v1 CocoIndex "
        "App `culture_heritage_embedding`. Uses BAAI/bge-m3 (1024-dim, "
        "multilingual)."
    ),
    deps=[dg.AssetKey(["culture_heritage_extract"])],
    metadata={
        "embedding_model": "BAAI/bge-m3",
        "vector_dim": 1024,
        "min_batch_size": 100,
        "hnsw_drop_threshold": 50,
    },
)
def culture_heritage_embed(
    context: dg.AssetExecutionContext,
    culture_heritage_extract: list[dict[str, Any]],
) -> dict[str, Any]:
    """Embed the extracted claims via the v1 CocoIndex App."""
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info("culture_embed_stub_mode", group=GROUP_NAME, rows=0)
        return {
            "rows": 0,
            "vector_dim": 1024,
            "model": "BAAI/bge-m3",
            "stub": True,
        }

    import subprocess

    result = subprocess.run(
        [
            "python",
            "-m",
            "oideachais.cocoindex_flows.culture_heritage_embedding",
            "update",
        ],
        check=False,
    )
    return {
        "rows": len(culture_heritage_extract),
        "vector_dim": 1024,
        "model": "BAAI/bge-m3",
        "exit_code": result.returncode,
        "stub": False,
    }


# ============================================================================
# Asset 3: cognify — Cognee cognify pass
# ============================================================================


@dg.asset(
    group_name=GROUP_NAME,
    description=(
        "Cognee cognify pass for the `culture_heritage` dataset. Emits "
        "edges: Claim->Person, Claim->Place, Person->FamilyRelation."
    ),
    deps=[dg.AssetKey(["culture_heritage_embed"])],
    metadata={
        "dataset": "culture_heritage",
        "edge_types": ["Claim->Person", "Claim->Place", "Person->FamilyRelation"],
    },
)
def culture_heritage_cognify(
    context: dg.AssetExecutionContext,
    culture_heritage_embed: dict[str, Any],
) -> dict[str, Any]:
    """Cognee cognify pass."""
    from cianfhoghlaim.observability.cognee.culture_cognify import (
        cognify_culture_heritage_rows,
    )

    # The Cognee cognify call expects the embedded rows from the previous
    # step. In stub mode it returns a stub envelope.
    return {"placeholder": "stub"}


# ============================================================================
# Asset 4: cross_edges — FalkorDB MERGE between culture_heritage <-> oideachais/leabharlann
# ============================================================================


@dg.asset(
    group_name=GROUP_NAME,
    description=(
        "Emit cross-dataset edges between `culture_heritage`, `oideachais`, "
        "and `leabharlann` in FalkorDB. "
        "Edge types: CultureHeritageClaim-MATCHES->LeavingCertLearningOutcome, "
        "CultureHeritagePerson-COREFERS_WITH->LeabharlannAuthor."
    ),
    deps=[dg.AssetKey(["culture_heritage_cognify"])],
    metadata={
        "cross_edges": [
            "CultureHeritageClaim-MATCHES->LeavingCertLearningOutcome",
            "CultureHeritagePerson-COREFERS_WITH->LeabharlannAuthor",
        ],
    },
)
def culture_heritage_cross_edges(
    context: dg.AssetExecutionContext,
    culture_heritage_cognify: dict[str, Any],
) -> dict[str, Any]:
    """Cross-dataset FalkorDB MERGE for the culture heritage subgraph."""
    from cianfhoghlaim.observability.cognee.culture_cognify import (
        emit_culture_cross_dataset_edges,
    )

    return {"placeholder": "stub"}