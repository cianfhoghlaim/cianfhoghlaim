"""
cognify — Python asset module for Domain 4.

Wires the 10 cognify functions as Dagster assets:

Cognee integration (7 functions):
1. author_archive_cognify
2. cross_stage_cognify
3. culture_cognify
4. leabharlann_cognify
5. leabharlann_inbox_cognify
6. official_media_cognify
7. site_analysis_cognify

Cross-archive rules (3 files):
1. author_archive_cross_corpus
2. leabharlann_cross_archive
3. leabharlann_inbox_cross_archive

This is the Layer 3 of the 4-layer asset graph (per
.agents/skills/dagster/SKILL.md): knowledge graph construction
via Cognee + 8 cross-stage edge types + 3 leabharlann
cross-archive edge types.

Reference: openspec/specs/oideachais-cognify-knowledge-graph/spec.md
(9 requirements).
"""
from __future__ import annotations

import dagster as dg


def _make_cognify_asset(name: str, module_path: str, fn_name: str) -> dg.AssetsDefinition:
    """Build a Dagster asset for a single cognify function."""
    @dg.asset(
        name=name,
        group_name="cognify",
        compute_kind="cognee",
        description=f"Cognify {name} via Cognee {fn_name}",
    )
    def _asset() -> dg.MaterializeResult:
        import importlib
        mod = importlib.import_module(module_path)
        fn = getattr(mod, fn_name)
        result = fn()
        return dg.MaterializeResult(
            metadata={"pipeline": name, "module": module_path, "fn": fn_name}
        )

    return _asset


# The 7 cognee_integration functions.
cognee_integration_assets = [
    _make_cognify_asset(
        "author_archive_cognify",
        "cianfhoghlaim.cognify.cognee_integration.author_archive_cognify",
        "cognify_author_archive",
    ),
    _make_cognify_asset(
        "cross_stage_cognify",
        "cianfhoghlaim.cognify.cognee_integration.cross_stage_cognify",
        "cognify_cross_stage",
    ),
    _make_cognify_asset(
        "culture_cognify",
        "cianfhoghlaim.cognify.cognee_integration.culture_cognify",
        "cognify_culture",
    ),
    _make_cognify_asset(
        "leabharlann_cognify",
        "cianfhoghlaim.cognify.cognee_integration.leabharlann_cognify",
        "cognify_leabharlann",
    ),
    _make_cognify_asset(
        "leabharlann_inbox_cognify",
        "cianfhoghlaim.cognify.cognee_integration.leabharlann_inbox_cognify",
        "cognify_leabharlann_inbox",
    ),
    _make_cognify_asset(
        "official_media_cognify",
        "cianfhoghlaim.cognify.cognee_integration.official_media_cognify",
        "cognify_official_media",
    ),
    _make_cognify_asset(
        "site_analysis_cognify",
        "cianfhoghlaim.cognify.cognee_integration.site_analysis_cognify",
        "cognify_site_analysis",
    ),
]


# The 3 cross-archive rules functions.
cross_archive_assets = [
    _make_cognify_asset(
        "author_archive_cross_corpus",
        "cianfhoghlaim.cognify.rules.author_archive_cross_corpus",
        "build_cross_corpus_edges",
    ),
    _make_cognify_asset(
        "leabharlann_cross_archive",
        "cianfhoghlaim.cognify.rules.leabharlann_cross_archive",
        "build_leabharlann_cross_archive_edges",
    ),
    _make_cognify_asset(
        "leabharlann_inbox_cross_archive",
        "cianfhoghlaim.cognify.rules.leabharlann_inbox_cross_archive",
        "build_leabharlann_inbox_cross_archive_edges",
    ),
]


cognify_assets = cognee_integration_assets + cross_archive_assets


__all__ = ["cognify_assets"]
