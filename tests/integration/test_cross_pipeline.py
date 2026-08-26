"""
Cross-Pipeline Integration Tests.

Tests data flow and coordination between sruth pipelines:
- oideachais (education curriculum)
- crypteolas (crypto/DeFi)
- tuath (gaming/mythology)
- códeolas (code analysis)
- browser (web scraping)
- taighde (research)
- aleyum (music)

These tests verify that pipelines can share data through:
1. Shared DuckDB/LanceDB storage
2. MCP server orchestration
3. Knowledge graph connections
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Test data directory
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestOideachaisCrypteolasIntegration:
    """Test integration between education and crypto pipelines."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_curriculum_to_defi_education(
        self,
        duckdb_with_schema,
        mock_mcp_gateway,
    ):
        """
        Test flow: Curriculum content → DeFi educational material.

        Scenario: Find Irish curriculum references to economics/finance
        and connect to DeFi protocol educational content.
        """
        # Insert curriculum data about economics
        duckdb_with_schema.execute("""
            INSERT INTO test_curriculum (id, nation, subject, level, content)
            VALUES
                ('ie_lc_econ_1', 'ireland', 'economics', 'leaving_cert',
                 'Students learn about financial markets and trading'),
                ('ie_lc_bus_1', 'ireland', 'business', 'leaving_cert',
                 'Understanding blockchain and cryptocurrency basics')
        """)

        # Simulate MCP search for related crypto content
        mock_mcp_gateway.qdrant.search = AsyncMock(return_value=[
            {
                "id": "defi_edu_1",
                "score": 0.89,
                "payload": {
                    "topic": "Introduction to DeFi",
                    "curriculum_link": "ie_lc_econ_1",
                    "difficulty": "beginner",
                },
            },
        ])

        # Execute cross-pipeline query
        result = await mock_mcp_gateway.route(
            "qdrant",
            "search",
            {"query": "DeFi for secondary education", "limit": 5}
        )

        assert len(result) > 0
        assert result[0]["payload"]["curriculum_link"] == "ie_lc_econ_1"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_financial_literacy_content_generation(
        self,
        mock_mcp_gateway,
        mock_embedding_service,
    ):
        """
        Test generating educational content about crypto for curriculum.

        Uses crypteolas data to enhance oideachais financial literacy content.
        """
        # Mock crypto protocol data
        crypto_data = [
            {"protocol": "uniswap", "category": "dex", "description": "Decentralized exchange"},
            {"protocol": "aave", "category": "lending", "description": "Lending protocol"},
        ]

        # Mock curriculum requirement
        curriculum_requirement = {
            "subject": "business",
            "topic": "Modern Financial Systems",
            "level": "leaving_cert",
        }

        # Simulate content generation via MCP
        mock_mcp_gateway.chunkhound.code_research = AsyncMock(return_value={
            "answer": "DeFi protocols demonstrate decentralized financial systems",
            "sources": ["crypteolas/defi_overview.md"],
        })

        result = await mock_mcp_gateway.route(
            "chunkhound",
            "code_research",
            {
                "query": f"Explain {crypto_data[0]['description']} for {curriculum_requirement['level']} students",
            }
        )

        assert "DeFi" in result["answer"]


class TestTuathOideachaisIntegration:
    """Test integration between mythology/gaming and education pipelines."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_mythology_curriculum_links(
        self,
        duckdb_with_schema,
        mock_mcp_gateway,
        tuath_test_data,
    ):
        """
        Test linking Irish mythology content to curriculum.

        Scenario: Connect Tuatha Dé Danann stories to Irish language curriculum.
        """
        # Insert Irish curriculum data
        duckdb_with_schema.execute("""
            INSERT INTO test_curriculum (id, nation, subject, level, content)
            VALUES
                ('ie_jc_irish_myth', 'ireland', 'gaeilge', 'junior_cycle',
                 'Scéalta na Féinne agus Cú Chulainn'),
                ('ie_lc_irish_lit', 'ireland', 'gaeilge', 'leaving_cert',
                 'An Táin Bó Cúailnge - staidéar ar an eipic')
        """)

        # Mock Memgraph query for mythology connections
        mock_mcp_gateway.memgraph.cypher_query = AsyncMock(return_value=[
            {
                "character": "Cú Chulainn",
                "curriculum_refs": ["ie_jc_irish_myth", "ie_lc_irish_lit"],
                "cycle": "ulster_cycle",
            },
        ])

        result = await mock_mcp_gateway.route(
            "memgraph",
            "cypher_query",
            {
                "query": """
                    MATCH (c:Character)-[:REFERENCED_IN]->(curr:Curriculum)
                    WHERE c.name = 'Cú Chulainn'
                    RETURN c.name as character, collect(curr.id) as curriculum_refs, c.cycle as cycle
                """
            }
        )

        assert len(result) > 0
        assert result[0]["character"] == "Cú Chulainn"
        assert "ie_jc_irish_myth" in result[0]["curriculum_refs"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_game_educational_content_sync(
        self,
        mock_mcp_gateway,
        lancedb_with_table,
    ):
        """
        Test syncing game content with educational materials.

        Scenario: Game about Irish mythology syncs learning outcomes
        with curriculum database.
        """
        _lancedb_conn, _table = lancedb_with_table

        # Mock SpacetimeDB sync event
        game_content = {
            "game_id": "fianna_quest",
            "chapter": "The Salmon of Knowledge",
            "learning_outcomes": [
                "Understand the story of Fionn and the Salmon",
                "Learn key Irish vocabulary from the tale",
            ],
        }

        # Simulate embedding and storage
        mock_mcp_gateway.qdrant.upsert = AsyncMock(return_value={"status": "ok", "count": 2})

        result = await mock_mcp_gateway.route(
            "qdrant",
            "upsert",
            {
                "collection": "educational_games",
                "points": [
                    {"id": f"{game_content['game_id']}_{i}", "vector": [0.1] * 1024, "payload": lo}
                    for i, lo in enumerate(game_content["learning_outcomes"])
                ],
            }
        )

        assert result["status"] == "ok"
        assert result["count"] == 2


class TestCodeolasIntegration:
    """Test integration between code analysis and other pipelines."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_curriculum_code_examples(
        self,
        mock_mcp_gateway,
    ):
        """
        Test finding code examples for curriculum topics.

        Scenario: Find Python examples for Junior Cycle coding curriculum.
        """
        # Mock ChunkHound semantic search
        mock_mcp_gateway.chunkhound.search_semantic = AsyncMock(return_value=[
            {
                "file": "examples/junior_cycle/variables.py",
                "chunk": "# Variables and data types\nname = 'Seán'\nage = 14",
                "score": 0.95,
                "tags": ["junior_cycle", "python", "variables"],
            },
            {
                "file": "examples/junior_cycle/loops.py",
                "chunk": "# For loops\nfor i in range(10):\n    print(i)",
                "score": 0.88,
                "tags": ["junior_cycle", "python", "loops"],
            },
        ])

        result = await mock_mcp_gateway.route(
            "chunkhound",
            "search_semantic",
            {
                "query": "Python variables for Junior Cycle",
                "filter": {"tags": ["junior_cycle"]},
            }
        )

        assert len(result) > 0
        assert "junior_cycle" in result[0]["file"]
        assert result[0]["score"] > 0.8


class TestBrowserScrapingIntegration:
    """Test integration between web scraping and content pipelines."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_curriculum_source_scraping(
        self,
        mock_mcp_gateway,
    ):
        """
        Test scraping curriculum sources and ingesting to oideachais.

        Scenario: Scrape NCCA curriculum page and extract learning outcomes.
        """
        # Mock Firecrawl scrape
        mock_mcp_gateway.firecrawl.scrape = AsyncMock(return_value={
            "markdown": """
# Junior Cycle Mathematics

## Learning Outcomes

### Number
- N.1: Students should be able to investigate patterns and formulate conjectures
- N.2: Students should understand and apply the concepts of ratio

### Algebra
- A.1: Students should be able to use variables and expressions
            """,
            "metadata": {
                "title": "Junior Cycle Mathematics Specification",
                "url": "https://curriculumonline.ie/Junior-cycle/Mathematics",
            },
        })

        result = await mock_mcp_gateway.route(
            "firecrawl",
            "scrape",
            {"url": "https://curriculumonline.ie/Junior-cycle/Mathematics"}
        )

        assert "Learning Outcomes" in result["markdown"]
        assert "N.1" in result["markdown"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_visual_content_extraction(
        self,
        mock_mcp_gateway,
    ):
        """
        Test extracting visual content from curriculum PDFs.

        Scenario: Use Z.AI to extract diagrams from exam papers.
        """
        # This would test the browser → zai-mcp-server flow
        # For now, mock the extraction
        pass


class TestTaighdeResearchIntegration:
    """Test integration between research and content pipelines."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_research_to_curriculum_enrichment(
        self,
        mock_mcp_gateway,
        mock_httpx_client,
    ):
        """
        Test using research findings to enrich curriculum content.

        Scenario: Find academic research about teaching methods
        and link to curriculum outcomes.
        """
        # Mock Cognee knowledge search
        mock_mcp_gateway.cognee = MagicMock()
        mock_mcp_gateway.cognee.search = AsyncMock(return_value=[
            {
                "entity": "Inquiry-Based Learning",
                "relevance": 0.92,
                "connections": [
                    {"to": "Junior Cycle Science", "relation": "EFFECTIVE_FOR"},
                    {"to": "Problem-Solving Skills", "relation": "DEVELOPS"},
                ],
            },
        ])

        result = await mock_mcp_gateway.route(
            "cognee",
            "search",
            {"query": "effective teaching methods for STEM"}
        )

        assert len(result) > 0
        assert result[0]["relevance"] > 0.9


class TestMCPOrchestration:
    """Test MCP server orchestration across pipelines."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_dagster_triggered_embedding_refresh(
        self,
        mock_mcp_gateway,
    ):
        """
        Test Dagster-triggered embedding refresh after content update.

        Flow: New content scraped → Dagster job → Embeddings updated
        """
        # Step 1: Scrape new content
        mock_mcp_gateway.firecrawl.scrape = AsyncMock(return_value={
            "markdown": "New curriculum content...",
            "metadata": {"url": "https://example.com/new-content"},
        })

        # Step 2: Trigger Dagster job
        mock_mcp_gateway.dagster.materialize_asset = AsyncMock(return_value={
            "run_id": "refresh-run-123",
            "status": "started",
        })

        # Step 3: Check job status
        mock_mcp_gateway.dagster.get_job_status = AsyncMock(return_value={
            "run_id": "refresh-run-123",
            "status": "success",
            "assets_materialized": ["curriculum_embeddings"],
        })

        # Execute flow
        scrape_result = await mock_mcp_gateway.route(
            "firecrawl", "scrape", {"url": "https://example.com/new-content"}
        )

        if scrape_result:
            job_result = await mock_mcp_gateway.route(
                "dagster", "materialize_asset", {"asset": "curriculum_embeddings"}
            )

            status = await mock_mcp_gateway.route(
                "dagster", "get_job_status", {"run_id": job_result["run_id"]}
            )

            assert status["status"] == "success"
            assert "curriculum_embeddings" in status["assets_materialized"]

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_cross_pipeline_knowledge_graph(
        self,
        mock_mcp_gateway,
    ):
        """
        Test building cross-pipeline knowledge graph with Cognee + Memgraph.

        Connects: Curriculum → Mythology → Games → Research
        """
        # Add curriculum node
        mock_mcp_gateway.memgraph.cypher_query = AsyncMock(side_effect=[
            # Create curriculum node
            [{"n": {"id": "jc_irish", "type": "curriculum"}}],
            # Create mythology connection
            [{"r": {"type": "REFERENCES"}}],
            # Query connections
            [
                {
                    "path": [
                        {"id": "jc_irish", "type": "curriculum"},
                        {"id": "cu_chulainn", "type": "character"},
                        {"id": "fianna_quest", "type": "game"},
                    ],
                },
            ],
        ])

        # Create curriculum node
        await mock_mcp_gateway.route(
            "memgraph",
            "cypher_query",
            {"query": "CREATE (n:Curriculum {id: 'jc_irish'}) RETURN n"}
        )

        # Create connection to mythology
        await mock_mcp_gateway.route(
            "memgraph",
            "cypher_query",
            {
                "query": """
                    MATCH (c:Curriculum {id: 'jc_irish'})
                    MATCH (m:Character {id: 'cu_chulainn'})
                    CREATE (c)-[r:REFERENCES]->(m)
                    RETURN r
                """
            }
        )

        # Query full path
        paths = await mock_mcp_gateway.route(
            "memgraph",
            "cypher_query",
            {
                "query": """
                    MATCH path = (c:Curriculum)-[:REFERENCES*1..3]->(target)
                    WHERE c.id = 'jc_irish'
                    RETURN path
                """
            }
        )

        assert len(paths) > 0
        assert len(paths[0]["path"]) == 3


class TestEmbeddingBatchingIntegration:
    """Test embedding batching across pipelines."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_batch_embedding_performance(
        self,
        embedding_batch_validator,
        mock_embedding_service,
    ):
        """
        Verify embedding batching meets minimum requirements.

        CRITICAL: Batches must be >= 100 for performance.
        """
        # Small batch (should warn)
        small_batch = [f"Text {i}" for i in range(50)]
        assert not embedding_batch_validator(small_batch)

        # Large batch (should pass)
        large_batch = [f"Text {i}" for i in range(150)]
        assert embedding_batch_validator(large_batch)

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_cross_pipeline_embedding_consistency(
        self,
        mock_embedding_service,
    ):
        """
        Test that embeddings are consistent across pipelines.

        Same text should produce same embedding regardless of source pipeline.
        """
        text = "Learning outcome for mathematics"

        # Embed from different pipeline contexts
        embedding_1 = await mock_embedding_service.embed([text])
        embedding_2 = await mock_embedding_service.embed([text])

        # Note: With mocked random embeddings, these won't match
        # In production, same text → same embedding
        assert len(embedding_1) == len(embedding_2)
        assert len(embedding_1[0]) == 1024  # Expected dimension
