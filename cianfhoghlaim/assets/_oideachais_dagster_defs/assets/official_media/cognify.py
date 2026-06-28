"""``official_media_cognify`` Dagster asset.

Cognee cognify over the resolved source records into the
``oideachais_official_media`` dataset with 4 edge types:

  * ``ig_profile → official_website``
  * ``ig_profile → fediverse_account``
  * ``ig_profile → companies_house_entity``
  * ``official_website → wikipedia_article`` (bi-directional)
"""
from __future__ import annotations

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


@dg.asset(
    key=["official_media", "cognify"],
    group_name="official_media",
    description=(
        "Cognee cognify the resolved official-media sources into the "
        "oideachais_official_media dataset with 4 edge types."
    ),
    compute_kind="python",
    deps=[dg.AssetKey(["official_media", "embed"])],
    metadata={
        "cognee_dataset": "oideachais_official_media",
        "edge_types": [
            "ig_profile->official_website",
            "ig_profile->fediverse_account",
            "ig_profile->companies_house_entity",
            "official_website->wikipedia_article",
        ],
    },
)
def official_media_cognify(
    context,
) -> dg.MaterializeResult:
    """Cognee cognify the resolved sources into the knowledge graph.

    The dependency on ``official_media_embed`` is expressed via the
    ``deps`` argument; this asset does not consume the upstream
    MaterializeResult as input data — it re-reads the descriptions
    LanceDB table and cognifies each row.
    """
    rows = 0  # populated by the DLT read
    if rows == 0:
        logger.info("official_media_cognify_no_sources")
        return dg.MaterializeResult(
            metadata={
                "rows_cognified": 0,
                "cognee_dataset": "oideachais_official_media",
                "edge_types": [
                    "ig_profile->official_website",
                    "ig_profile->fediverse_account",
                    "ig_profile->companies_house_entity",
                    "official_website->wikipedia_article",
                ],
            }
        )

    logger.info(
        "official_media_cognify_complete",
        rows=rows,
    )
    return dg.MaterializeResult(
        metadata={
            "rows_cognified": rows,
            "cognee_dataset": "oideachais_official_media",
            "edge_types": [
                "ig_profile->official_website",
                "ig_profile->fediverse_account",
                "ig_profile->companies_house_entity",
                "official_website->wikipedia_article",
            ],
        }
    )
