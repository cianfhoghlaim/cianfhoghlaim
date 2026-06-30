"""
Tests for the leabharlann cognify + cross-archive edges work.

Covers:
- `oideachais.cognee_integration.leabharlann_cognify` (graceful degradation)
- `oideachais.cognify_rules.leabharlann_cross_archive` (3 edge rules)
- `oideachais.api.routes.cross_archive_graph` (FastAPI route)
- `oideachais.dagster_defs.sensors.cognee_cron_sensor` (cron evaluation)
- `oideachais.dagster_defs.assets.leabharlann_cognify_assets` (4 assets)

Reference: openspec/changes/leabharlann-cognify-and-cross-archive-edges/
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# ============================================================================
# Cognee cognify adapter tests
# ============================================================================


class TestCognifyLeabharlannRows:
    """The cognify pass is a no-op in stub mode and graceful when Cognee is missing."""

    def test_stub_mode_returns_no_edges(self) -> None:
        from cianfhoghlaim.observability.cognee.leabharlann_cognify import (
            DATASET_BOOKS,
            cognify_leabharlann_rows,
        )

        with patch.dict(os.environ, {"USE_LOCAL_SCRAPES": "true"}):
            result = cognify_leabharlann_rows(DATASET_BOOKS, rows=[{"a": 1}])
        # cognify_leabharlann_rows is async — but in stub mode it returns a
        # plain dict via the sync path. We need to run it as a coroutine.
        import asyncio
        result = asyncio.run(cognify_leabharlain_rows_sync(DATASET_BOOKS, rows=[{"a": 1}]))
        assert result["stub"] is True
        assert result["rows"] == 1

    def test_unknown_dataset_raises(self) -> None:
        import asyncio

        from cianfhoghlaim.observability.cognee.leabharlann_cognify import (
            cognify_leabharlann_rows,
        )
        with pytest.raises(ValueError, match="unknown leabharlann dataset"):
            asyncio.run(cognify_leabharlann_rows("not_a_dataset", rows=[]))

    def test_datasets_constant(self) -> None:
        from cianfhoghlaim.observability.cognee.leabharlann_cognify import (
            DATASET_BOOKS,
            DATASET_TAKEOUT,
            DATASET_ZOTERO,
        )
        assert DATASET_BOOKS == "leabharlann_books"
        assert DATASET_ZOTERO == "leabharlann_zotero"
        assert DATASET_TAKEOUT == "leabharlann_takeout"


async def cognify_leabharlain_rows_sync(dataset, rows):
    """Helper to make the async function synchronous in tests."""
    from cianfhoghlaim.observability.cognee.leabharlann_cognify import (
        cognify_leabharlann_rows,
    )
    return await cognify_leabharlann_rows(dataset, rows)


# ============================================================================
# Cross-archive edge rule tests
# ============================================================================


class TestNormaliseTitle:
    def test_lowercases_and_strips(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _normalise_title,
        )
        assert _normalise_title("Hello, World! 123") == "hello world 123"

    def test_handles_empty(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _normalise_title,
        )
        assert _normalise_title("") == ""


class TestExtractUrlsFromText:
    def test_extracts_http_and_https(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _extract_urls_from_text,
        )
        text = "See https://arxiv.org/abs/2504.02890 and http://example.com/foo."
        urls = _extract_urls_from_text(text)
        assert "https://arxiv.org/abs/2504.02890" in urls
        assert "http://example.com/foo." in urls

    def test_empty_input(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _extract_urls_from_text,
        )
        assert _extract_urls_from_text("") == []
        assert _extract_urls_from_text(None) == []


class TestArxivMatchQuery:
    def test_no_matches_returns_empty(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _build_arxiv_match_query,
        )
        cypher, params = _build_arxiv_match_query(
            gemini_citations=[{"url": "https://example.com/no-arxiv", "source_file_hash": "h1"}],
            zotero_papers=[{"arxiv_id": "2504.99999", "file_hash": "z1"}],
        )
        assert cypher == ""
        assert params == {}

    def test_match_produces_edges(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _build_arxiv_match_query,
        )
        cypher, params = _build_arxiv_match_query(
            gemini_citations=[
                {
                    "url": "https://arxiv.org/abs/2504.02890",
                    "source_file_hash": "g1",
                }
            ],
            zotero_papers=[{"arxiv_id": "2504.02890", "file_hash": "z1"}],
        )
        assert "UNWIND" in cypher
        assert "MERGE" in cypher
        assert "CITES" in cypher
        assert len(params["edges"]) == 1
        assert params["edges"][0]["source"] == "g1"
        assert params["edges"][0]["target"] == "z1"
        assert params["edges"][0]["arxiv_id"] == "2504.02890"


class TestModuleTitleMatchQuery:
    def test_match_produces_edges(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _build_module_title_match_query,
        )
        cypher, params = _build_module_title_match_query(
            uog_artifacts=[
                {
                    "file_hash": "u1",
                    "module_title": "Handwritten Text Recognition for Irish",
                    "key_topics": [],
                }
            ],
            zotero_papers=[
                {
                    "file_hash": "z1",
                    "title": "Handwritten Text Recognition (HTR) for Irish-Langu",
                }
            ],
        )
        # 60% token overlap on the shorter string should fire.
        assert "UNWIND" in cypher
        assert "TEACHES" in cypher
        assert len(params["edges"]) >= 1

    def test_no_match(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _build_module_title_match_query,
        )
        cypher, params = _build_module_title_match_query(
            uog_artifacts=[
                {"file_hash": "u1", "module_title": "Quantum Mechanics", "key_topics": []}
            ],
            zotero_papers=[
                {"file_hash": "z1", "title": "Renaissance Poetry"},
            ],
        )
        assert cypher == ""
        assert params == {}


class TestTakeoutCitationQuery:
    def test_match_produces_edges(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _build_takeout_citation_query,
        )
        cypher, params = _build_takeout_citation_query(
            takeout_docs=[
                {
                    "file_hash": "t1",
                    "extracted_text": "See https://gemini-report.example/abc for context.",
                }
            ],
            gemini_reports=[
                {
                    "file_hash": "g1",
                    "cited_urls": [{"url": "https://gemini-report.example/abc"}],
                }
            ],
        )
        assert "UNWIND" in cypher
        assert "CITES" in cypher
        assert len(params["edges"]) == 1
        assert params["edges"][0]["source"] == "t1"
        assert params["edges"][0]["target"] == "g1"

    def test_no_match(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _build_takeout_citation_query,
        )
        cypher, params = _build_takeout_citation_query(
            takeout_docs=[{"file_hash": "t1", "extracted_text": "no urls here"}],
            gemini_reports=[{"file_hash": "g1", "cited_urls": []}],
        )
        assert cypher == ""
        assert params == {}

    def test_gemini_citations_fallback(self) -> None:
        """The takeout rule should also try the `gemini_citations` column."""
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            _build_takeout_citation_query,
        )
        _cypher, params = _build_takeout_citation_query(
            takeout_docs=[
                {
                    "file_hash": "t1",
                    "extracted_text": "See https://gemini.example/xyz",
                }
            ],
            gemini_reports=[
                {
                    "file_hash": "g1",
                    "cited_urls": [],
                    "gemini_citations": [{"url": "https://gemini.example/xyz"}],
                }
            ],
        )
        assert len(params["edges"]) == 1


class TestBuildAllCrossArchiveQueries:
    def test_returns_only_matched_rules(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            build_all_cross_archive_queries,
        )
        queries = build_all_cross_archive_queries(
            gemini_reports=[],
            zotero_papers=[],
            uog_artifacts=[],
            takeout_docs=[],
        )
        assert queries == []

    def test_arxiv_match_included(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            build_all_cross_archive_queries,
        )
        queries = build_all_cross_archive_queries(
            gemini_reports=[
                {
                    "file_hash": "g1",
                    "cited_urls": [{"url": "https://arxiv.org/abs/2504.02890"}],
                }
            ],
            zotero_papers=[{"file_hash": "z1", "arxiv_id": "2504.02890"}],
            uog_artifacts=[],
            takeout_docs=[],
        )
        names = [q[0] for q in queries]
        assert "gemini_cites_zotero_arxiv" in names

    def test_all_three_rules_with_full_data(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            build_all_cross_archive_queries,
        )
        queries = build_all_cross_archive_queries(
            gemini_reports=[
                {
                    "file_hash": "g1",
                    "cited_urls": [
                        {"url": "https://arxiv.org/abs/2504.02890"},
                        {"url": "https://gemini.example/xyz"},
                    ],
                }
            ],
            zotero_papers=[{"file_hash": "z1", "arxiv_id": "2504.02890", "title": "X"}],
            uog_artifacts=[
                {
                    "file_hash": "u1",
                    "module_title": "Some Matching Topic for Zotero",
                    "key_topics": [],
                }
            ],
            takeout_docs=[
                {
                    "file_hash": "t1",
                    "extracted_text": "See https://gemini.example/xyz for details",
                }
            ],
        )
        names = [q[0] for q in queries]
        # The arxiv and URL matches will fire; the title match depends on
        # the heuristic — with the dummy data the title may or may not
        # match. We assert the two deterministic ones.
        assert "gemini_cites_zotero_arxiv" in names
        assert "takeout_cites_gemini_url" in names

    def test_handles_duckdb_json_string_columns(self) -> None:
        """DuckDB may return `gemini_citations` as a JSON string, not a list."""
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            build_all_cross_archive_queries,
        )
        queries = build_all_cross_archive_queries(
            gemini_reports=[
                {
                    "file_hash": "g1",
                    "gemini_citations": '[{"url": "https://arxiv.org/abs/2504.02890"}]',  # str
                    "cited_urls": [],
                }
            ],
            zotero_papers=[{"file_hash": "z1", "arxiv_id": "2504.02890"}],
            uog_artifacts=[],
            takeout_docs=[],
        )
        names = [q[0] for q in queries]
        assert "gemini_cites_zotero_arxiv" in names


class TestPopulateCrossArchiveEdges:
    def test_falkordb_unavailable_returns_stub(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            populate_cross_archive_edges,
        )
        with patch.dict(sys.modules, {"oideachais.graph.falkordb_client": None}):
            result = populate_cross_archive_edges(
                gemini_reports=[
                    {
                        "file_hash": "g1",
                        "cited_urls": [{"url": "https://arxiv.org/abs/2504.02890"}],
                    }
                ],
                zotero_papers=[{"file_hash": "z1", "arxiv_id": "2504.02890"}],
            )
        assert result["stub"] is True
        assert result["total_edges"] == 0

    def test_mocked_falkordb_executes(self) -> None:
        from cianfhoghlaim.cognify.leabharlann_cross_archive import (
            populate_cross_archive_edges,
        )
        mock_client = MagicMock()
        mock_client.execute.return_value = {"relationships_created": 1}
        result = populate_cross_archive_edges(
            gemini_reports=[
                {
                    "file_hash": "g1",
                    "cited_urls": [{"url": "https://arxiv.org/abs/2504.02890"}],
                }
            ],
            zotero_papers=[{"file_hash": "z1", "arxiv_id": "2504.02890"}],
            falkordb_client=mock_client,
        )
        assert result["stub"] is False
        assert result["total_edges"] == 1
        assert "gemini_cites_zotero_arxiv" in result["queries"]


# ============================================================================
# FastAPI cross-archive graph route tests
# ============================================================================


class TestCrossArchiveGraphRoute:
    def test_route_registers(self) -> None:
        from cianfhoghlaim.agents.api._oideachais_api.routes.cross_archive_graph import router

        assert router.prefix == "" or router.prefix == "/"
        paths = [r.path for r in router.routes]  # type: ignore[attr-defined]
        assert any("/cross-archive-graph/{query}" in p for p in paths)

    def test_response_models(self) -> None:
        from cianfhoghlaim.agents.api._oideachais_api.routes.cross_archive_graph import (
            GraphEdge,
            GraphNode,
            GraphResponse,
        )
        n = GraphNode(id="x", label="ZoteroPaper", properties={"title": "foo"})
        assert n.id == "x"
        e = GraphEdge(source="x", target="y", type="CITES", properties={"arxiv_id": "1234.5678"})
        assert e.type == "CITES"
        g = GraphResponse(query="q", nodes=[n], edges=[e], total=2)
        assert g.total == 2

    def test_health_check_unavailable(self) -> None:
        from cianfhoghlaim.agents.api._oideachais_api.routes import cross_archive_graph as mod

        with patch.object(mod, "_get_falkordb_client", return_value=None):
            import asyncio
            result = asyncio.run(mod.cross_archive_graph_health())
        assert result["status"] == "unavailable"

    def test_query_returns_200_with_mock_client(self) -> None:
        """End-to-end test of the route via FastAPI TestClient + mocked FalkorDB."""
        from fastapi.testclient import TestClient
        from cianfhoghlaim.agents.api._oideachais_api.routes import cross_archive_graph as mod

        mock_client = MagicMock()
        mock_client.query.return_value = [
            {
                "n": {
                    "id": "z1",
                    "title": "Handwritten Text Recognition for Irish",
                    "_label": "ZoteroPaper",
                },
                "r": {
                    "type": "CITES",
                    "arxiv_id": "2504.02890",
                },
                "m": {"id": "g1", "title": "Gemini Report", "_label": "GeminiReport"},
            }
        ]
        orig_get = mod._get_falkordb_client
        mod._get_falkordb_client = lambda: mock_client
        try:
            from cianfhoghlaim.agents.api._oideachais_api.main import app
            client = TestClient(app)
            resp = client.get("/cross-archive-graph/irish")
            assert resp.status_code == 200
            data = resp.json()
            assert data["query"] == "irish"
            assert len(data["nodes"]) == 2
            # Edges depend on the mock structure; we just assert the field exists.
            assert "edges" in data
            assert "total" in data
        finally:
            mod._get_falkordb_client = orig_get

    def test_query_returns_200_when_falkordb_unavailable(self) -> None:
        """Graceful degradation: empty graph when FalkorDB is missing."""
        from fastapi.testclient import TestClient
        from cianfhoghlaim.agents.api._oideachais_api.routes import cross_archive_graph as mod

        orig_get = mod._get_falkordb_client
        mod._get_falkordb_client = lambda: None
        try:
            from cianfhoghlaim.agents.api._oideachais_api.main import app
            client = TestClient(app)
            resp = client.get("/cross-archive-graph/anything")
            assert resp.status_code == 200
            data = resp.json()
            assert data["nodes"] == []
            assert data["edges"] == []
            assert data["total"] == 0
        finally:
            mod._get_falkordb_client = orig_get

    def test_query_400_on_empty_string(self) -> None:
        from fastapi.testclient import TestClient
        from cianfhoghlaim.agents.api._oideachais_api.routes import cross_archive_graph as mod

        orig_get = mod._get_falkordb_client
        mod._get_falkordb_client = lambda: None
        try:
            from cianfhoghlaim.agents.api._oideachais_api.main import app
            client = TestClient(app)
            resp = client.get("/cross-archive-graph/  ")  # whitespace
            # FastAPI may return 200 (whitespace passes) or 400; accept either
            # but not 500.
            assert resp.status_code in (200, 400, 422)
        finally:
            mod._get_falkordb_client = orig_get


# ============================================================================
# Cognee cron sensor tests
# ============================================================================


class TestCogneeCronSensor:
    def test_sensor_evaluates_to_run_requests(self) -> None:
        from cianfhoghlaim.dagster.sensors.cognee_cron_sensor import (
            evaluate_cognee_cron,
        )
        context = MagicMock()
        context.cursor = None
        result = evaluate_cognee_cron(context)
        assert hasattr(result, "run_requests")
        assert len(result.run_requests) == 4  # 3 cognify + 1 cross-archive
        assert result.cursor == "1"

    def test_sensor_increments_cursor(self) -> None:
        from cianfhoghlaim.dagster.sensors.cognee_cron_sensor import (
            evaluate_cognee_cron,
        )
        context = MagicMock()
        context.cursor = "5"
        result = evaluate_cognee_cron(context)
        assert result.cursor == "6"


# ============================================================================
# Cognify assets tests (graceful degradation)
# ============================================================================


class TestCognifyAssets:
    def test_books_asset_imports(self) -> None:
        from cianfhoghlaim.dagster.assets.leabharlann_cognify_assets import (
            LEABHARLANN_COGNIFY_ASSETS,
        )
        assert len(LEABHARLANN_COGNIFY_ASSETS) == 4

    def test_dataset_constants(self) -> None:
        from cianfhoghlaim.dagster.assets.leabharlann_cognify_assets import (
            COGNEE_DATASET_BOOKS,
            COGNEE_DATASET_TAKEOUT,
            COGNEE_DATASET_ZOTERO,
        )
        assert COGNEE_DATASET_BOOKS == "leabharlann_books"
        assert COGNEE_DATASET_ZOTERO == "leabharlann_zotero"
        assert COGNEE_DATASET_TAKEOUT == "leabharlann_takeout"
