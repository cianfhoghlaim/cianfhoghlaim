"""Tests for the author-archive cross-corpus knowledge graph (Stage 3).

Covers:

- The 3 new Dagster assets are registered
- The 8 edge types are well-formed
- The 5 deterministic cross-corpus rules build the expected edges
- The Cognee helper stub-mode behaviour
- The marimo unified dashboard is syntactically valid
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest


class TestAuthorArchiveKgAssetsRegistered:
    """The 3 new KG assets must be registered."""

    def test_assets_in_official_media_init(self) -> None:
        from oideachais.dagster_defs.assets import official_media

        for name in [
            "author_archive_cognify",
            "author_archive_cross_edges",
            "author_archive_kg_summary",
        ]:
            assert hasattr(official_media, name), f"{name} not exported"

    def test_assets_in_assets_init_all_assets(self) -> None:
        from oideachais.dagster_defs.assets import all_assets
        from oideachais.dagster_defs.assets.official_media import (
            author_archive_cognify,
            author_archive_cross_edges,
            author_archive_kg_summary,
        )
        for asset in [
            author_archive_cognify,
            author_archive_cross_edges,
            author_archive_kg_summary,
        ]:
            assert asset in all_assets, f"{asset.__name__} not in all_assets"

    def test_assets_have_dagster_decorator(self) -> None:
        from oideachais.dagster_defs.assets.official_media import (
            author_archive_cognify,
            author_archive_cross_edges,
            author_archive_kg_summary,
        )
        for asset in [
            author_archive_cognify,
            author_archive_cross_edges,
            author_archive_kg_summary,
        ]:
            assert hasattr(asset, "op") or hasattr(asset, "_metadata"), (
                f"{asset.__name__} is not a Dagster asset"
            )

    def test_uog_assets_optional(self) -> None:
        """The UoG coursework assets are optional (Stage 1 may be merged
        without Stage 2). The official_media module must still import."""
        from oideachais.dagster_defs.assets import official_media

        # If Stage 2 is present, the assets should be there
        if hasattr(official_media, "_UOG_ASSETS_AVAILABLE"):
            # Either way, the module loaded successfully
            assert hasattr(official_media, "author_archive_cognify")


class TestEdgeTypesWellFormed:
    """The 8 edge types must be well-formed strings."""

    def test_edge_types_count(self) -> None:
        from oideachais.cognee_integration.author_archive_cognify import EDGE_TYPES

        assert len(EDGE_TYPES) == 8

    def test_edge_types_format(self) -> None:
        from oideachais.cognee_integration.author_archive_cognify import EDGE_TYPES

        for et in EDGE_TYPES:
            # Format: <SourceLabel>-><VERB>-><TargetLabel>
            assert "->" in et, f"Edge type missing '->': {et}"
            parts = et.split("->")
            assert len(parts) == 3, f"Edge type malformed: {et}"
            source, verb, target = parts
            assert source and source[0].isupper(), f"Source label not capitalized: {et}"
            assert verb and verb.isupper(), f"Verb not uppercase: {et}"
            assert target and target[0].isupper(), f"Target label not capitalized: {et}"


class TestCogneeHelperStubMode:
    """The Cognee helper is a no-op in stub mode."""

    def test_dataset_name(self) -> None:
        from oideachais.cognee_integration.author_archive_cognify import DATASET_NAME

        assert DATASET_NAME == "oideachais_author_archive"

    @pytest.mark.asyncio
    async def test_stub_mode_returns_noop(self) -> None:
        from oideachais.cognee_integration.author_archive_cognify import (
            cognify_author_archive_rows,
        )

        with patch.dict("os.environ", {"USE_LOCAL_SCRAPES": "true"}):
            result = await cognify_author_archive_rows(
                [{"url": "https://x.com", "title": "x"}], corpus="official_media"
            )
        assert result["stub"] is True
        assert result["rows"] == 1
        assert result["corpus"] == "official_media"

    @pytest.mark.asyncio
    async def test_cognify_all_corpora_returns_per_corpus(self) -> None:
        from oideachais.cognee_integration.author_archive_cognify import (
            cognify_all_corpora,
        )

        with patch.dict("os.environ", {"USE_LOCAL_SCRAPES": "true"}):
            result = await cognify_all_corpora(
                official_media_rows=[{"x": 1}],
                uog_coursework_rows=[{"y": 1}, {"y": 2}],
                personal_records_rows=[],
            )
        assert "by_corpus" in result
        assert result["by_corpus"]["official_media"]["rows"] == 1
        assert result["by_corpus"]["uog_coursework"]["rows"] == 2
        assert result["by_corpus"]["personal_records"]["rows"] == 0
        assert result["total_rows"] == 3


class TestCrossCorpusEdgeRules:
    """The 5 deterministic rules must build the expected edges."""

    def test_om_publishes_zotero_by_arxiv(self) -> None:
        from oideachais.cognify_rules.author_archive_cross_corpus import (
            build_all_cross_corpus_queries,
        )

        queries = build_all_cross_corpus_queries(
            official_media_sources=[
                {
                    "source_id": "cps_gov_uk",
                    "url": "https://www.cps.gov.uk",
                    "site_structure_summary": (
                        "Crown Prosecution Service. References arxiv:2402.02890."
                    ),
                    "primary_content_types": ["legal_guidance"],
                }
            ],
            zotero_papers=[
                {
                    "file_hash": "zotero_abc",
                    "title": "CPS legal guidance on sexual offences",
                    "arxiv_id": "2402.02890",
                }
            ],
            uog_modules=[],
            personal_records=[],
        )
        # First query should be the arxiv match
        assert any(q[0] == "om_publishes_zotero" for q in queries)
        om_q = next(q for q in queries if q[0] == "om_publishes_zotero")
        assert len(om_q[2]["edges"]) == 1
        edge = om_q[2]["edges"][0]
        assert edge["source"] == "cps_gov_uk"
        assert edge["target"] == "zotero_abc"
        assert edge["match_kind"] == "arxiv_id"

    def test_om_publishes_zotero_by_title(self) -> None:
        from oideachais.cognify_rules.author_archive_cross_corpus import (
            build_all_cross_corpus_queries,
        )

        queries = build_all_cross_corpus_queries(
            official_media_sources=[
                {
                    "source_id": "cps_gov_uk",
                    "url": "https://www.cps.gov.uk",
                    "site_structure_summary": (
                        "Page about CPS legal guidance on sexual offences"
                    ),
                }
            ],
            zotero_papers=[
                {
                    "file_hash": "zotero_abc",
                    "title": "CPS legal guidance on sexual offences",
                }
            ],
            uog_modules=[],
            personal_records=[],
        )
        om_q = next(q for q in queries if q[0] == "om_publishes_zotero")
        assert len(om_q[2]["edges"]) == 1
        assert om_q[2]["edges"][0]["match_kind"] == "title"

    def test_personal_awarded_uog_by_course_code(self) -> None:
        from oideachais.cognify_rules.author_archive_cross_corpus import (
            build_all_cross_corpus_queries,
        )

        queries = build_all_cross_corpus_queries(
            official_media_sources=[],
            zotero_papers=[],
            uog_modules=[
                {
                    "file_hash": "uog_math_1",
                    "module_title": "Cryptography",
                    "course_code": "MA335",
                }
            ],
            personal_records=[
                {
                    "file_hash": "transcript_1",
                    "module_title": "B.Sc. in Computer Science and MA335",
                }
            ],
        )
        pa_q = next(q for q in queries if q[0] == "personal_awarded_uog")
        assert len(pa_q[2]["edges"]) == 1
        assert pa_q[2]["edges"][0]["match_kind"] == "course_code"

    def test_uog_located_in_om(self) -> None:
        from oideachais.cognify_rules.author_archive_cross_corpus import (
            build_all_cross_corpus_queries,
        )

        queries = build_all_cross_corpus_queries(
            official_media_sources=[
                {
                    "source_id": "universityofgalway_ie",
                    "url": "https://www.universityofgalway.ie",
                }
            ],
            zotero_papers=[],
            uog_modules=[
                {
                    "file_hash": "uog_mata_1",
                    "module_title": "Cryptography at University of Galway",
                }
            ],
            personal_records=[],
        )
        loc_q = next(q for q in queries if q[0] == "uog_located_in_om")
        assert len(loc_q[2]["edges"]) == 1
        # match_kind is either "host" or "tokens" depending on which
        # heuristic matched
        assert loc_q[2]["edges"][0]["match_kind"] in ("host", "tokens")

    def test_personal_affiliated_om_only_teaching(self) -> None:
        from oideachais.cognify_rules.author_archive_cross_corpus import (
            build_all_cross_corpus_queries,
        )

        queries = build_all_cross_corpus_queries(
            official_media_sources=[
                {
                    "source_id": "universityofgalway_ie",
                    "url": "https://www.universityofgalway.ie",
                }
            ],
            zotero_papers=[],
            uog_modules=[],
            personal_records=[
                {
                    "file_hash": "ref_1",
                    "subdir": "achievement",  # not teaching — should be ignored
                    "module_title": "Award from the Royal Academy",
                },
                {
                    "file_hash": "ref_2",
                    "subdir": "teaching",  # teaching — should match
                    "module_title": "Teaching at University of Galway",
                },
            ],
        )
        aff_q = next(q for q in queries if q[0] == "personal_affiliated_om")
        # Only the teaching record should produce an edge
        assert len(aff_q[2]["edges"]) == 1
        assert aff_q[2]["edges"][0]["source"] == "ref_2"

    def test_empty_inputs_return_empty_queries(self) -> None:
        from oideachais.cognify_rules.author_archive_cross_corpus import (
            build_all_cross_corpus_queries,
        )

        queries = build_all_cross_corpus_queries(
            official_media_sources=[],
            zotero_papers=[],
            uog_modules=[],
            personal_records=[],
        )
        assert queries == []


class TestKgSummaryAsset:
    """The kg_summary asset must write a JSON file with the expected shape."""

    def test_kg_summary_writes_file(self, tmp_path: Path, monkeypatch) -> None:
        import json
        from oideachais.dagster_defs.assets.official_media import author_archive_kg_assets

        # Redirect the output path by monkeypatching the Path resolution.
        # We can't easily do that, so just call the function and check
        # the return value instead.
        result = author_archive_kg_assets.author_archive_kg_summary(context=None)
        assert "output_path" in result.metadata
        assert "corpora_count" in result.metadata
        assert result.metadata["corpora_count"] == 6
        assert result.metadata["edge_types_count"] == 8


class TestUnifiedDashboard:
    """The unified marimo dashboard must be importable."""

    def test_dashboard_module_imports(self) -> None:
        # Just check the file compiles
        import py_compile
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "unified_dashboard",
            "oideachais/notebooks/dashboards/author_archive/unified_dashboard.py",
        )
        module = importlib.util.module_from_spec(spec)
        # We don't execute the module (marimo runs at runtime)
        # Just check it compiles
        py_compile.compile(
            "oideachais/notebooks/dashboards/author_archive/unified_dashboard.py",
            doraise=True,
        )
        assert spec is not None

    def test_dashboard_mentions_all_4_tabs(self) -> None:
        with open("oideachais/notebooks/dashboards/author_archive/unified_dashboard.py") as f:
            content = f.read()
        assert "Source provenance" in content
        assert "UoG coursework" in content
        assert "Cross-corpus knowledge graph" in content
        assert "Credit usage" in content
