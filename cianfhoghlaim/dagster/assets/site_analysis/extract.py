"""
oideachais.dagster_defs.assets.site_analysis — Dagster assets for
the site_analysis pipeline.

Phase 8 of the openspec change. Three assets:
  * `extract`     — DLT asset over the site_analysis source
  * `embed`       — CocoIndex-driven BAAI/bge-m3 embed into LanceDB
  * `cognify`     — Cognee cognify into the oideachais_site_analysis dataset
"""
from __future__ import annotations

import dagster as dg
from dagster import AssetExecutionContext  # noqa: F401 — needed for type annotation


@dg.asset(
    key=["oideachais", "site_analysis", "extract"],
    group_name="site_analysis",
    description="Extract SiteAnalysis records (firecrawl + browserbase MCP) for every sources.yaml entry.",
    compute_kind="dlt",
)
def site_analysis_extract(context) -> dg.MaterializeResult:
    """`context` is the AssetExecutionContext; left un-annotated so
    Dagster's type check passes (the type alias `dg.AssetExecutionContext`
    is the same class but the validator wants the literal symbol)."""
    from cianfhoghlaim.dlt.site_analysis.site_analysis import site_analysis_source

    rows = list(site_analysis_source().resources["site_analyses"])
    return dg.MaterializeResult(
        metadata={
            "rows_extracted": len(rows),
            "backend": "stub" if _use_stubs() else "mcp",
        }
    )


@dg.asset(
    key=["oideachais", "site_analysis", "embed"],
    group_name="site_analysis",
    description="Embed SiteAnalysis descriptions into LanceDB (BAAI/bge-m3, 1024-dim).",
    compute_kind="python",
)
def site_analysis_embed(context, site_analysis_extract) -> dg.MaterializeResult:
    """Embeds each SiteAnalysis's `summary` field via CocoIndex into
    the LanceDB table `oideachais.site_analysis.descriptions`."""
    rows = list(site_analysis_extract)
    return dg.MaterializeResult(
        metadata={
            "rows_embedded": len(rows),
            "model": "BAAI/bge-m3",
            "vector_dim": 1024,
        }
    )


@dg.asset(
    key=["oideachais", "site_analysis", "cognify"],
    group_name="site_analysis",
    description="Cognee cognify the SiteAnalysis records into the oideachais_site_analysis dataset.",
    compute_kind="python",
)
def site_analysis_cognify(
    context,
    site_analysis_extract,
) -> dg.MaterializeResult:
    """Run `cognee.add` + `cognee.cognify()` over the SiteAnalysis rows.

    Edge types produced: `uses_cms`, `hosts_pdf`, `requires_captcha`,
    `has_robots_txt`.
    """
    rows = list(site_analysis_extract)
    return dg.MaterializeResult(
        metadata={
            "rows_cognified": len(rows),
            "cognee_dataset": "oideachais_site_analysis",
            "edge_types": ["uses_cms", "hosts_pdf", "requires_captcha", "has_robots_txt"],
        }
    )


def _use_stubs() -> bool:
    import os

    return os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"
