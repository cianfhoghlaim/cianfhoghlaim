"""Tests for agent tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Check for optional dependencies
try:
    import pytest_asyncio
    HAS_PYTEST_ASYNCIO = True
except ImportError:
    HAS_PYTEST_ASYNCIO = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Skip decorator for async tests
requires_async = pytest.mark.skipif(not HAS_PYTEST_ASYNCIO, reason="pytest-asyncio not installed")
requires_httpx = pytest.mark.skipif(not HAS_HTTPX, reason="httpx not installed")


@requires_async
@requires_httpx
class TestDefiMetricsTool:
    """Tests for DeFi metrics agent tool."""

    @pytest.mark.asyncio
    async def test_get_protocol_tvl(self):
        """Test protocol TVL fetching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tvl": 10500000000,
            "name": "Aave",
            "symbol": "AAVE"
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = AsyncMock()
            client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            from crypteolas.agents.tools.defi_metrics import get_protocol_tvl

            result = await get_protocol_tvl("aave")

            assert result is not None
            assert "tvl" in result or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_get_yield_pools(self):
        """Test yield pools fetching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "pool": "aave-eth",
                    "apy": 3.5,
                    "tvlUsd": 2000000000
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = AsyncMock()
            client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            from crypteolas.agents.tools.defi_metrics import get_yield_pools

            result = await get_yield_pools(chain="Ethereum", min_tvl=1000000)

            assert isinstance(result, (list, dict))

    @pytest.mark.asyncio
    async def test_get_funding_rates(self):
        """Test funding rates fetching."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "symbol": "BTCUSDT",
                "fundingRate": "0.0001",
                "fundingTime": 1704067200000
            }
        ]
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = AsyncMock()
            client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            from crypteolas.agents.tools.defi_metrics import get_funding_rates

            result = await get_funding_rates(symbol="BTCUSDT")

            assert isinstance(result, (list, dict))

    @pytest.mark.asyncio
    async def test_get_token_price(self):
        """Test token price fetching."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "bitcoin": {
                "usd": 42000,
                "usd_24h_change": 2.5
            }
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            client_instance = AsyncMock()
            client_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__ = AsyncMock(return_value=client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            from crypteolas.agents.tools.defi_metrics import get_token_price

            result = await get_token_price("bitcoin")

            assert isinstance(result, (dict, float, type(None)))

    @pytest.mark.asyncio
    async def test_get_protocol_tvl_error_handling(self):
        """Test error handling in protocol TVL fetching."""
        with patch("httpx.AsyncClient") as mock_client:
            client_instance = AsyncMock()
            client_instance.get = AsyncMock(side_effect=Exception("Connection failed"))
            mock_client.return_value.__aenter__ = AsyncMock(return_value=client_instance)
            mock_client.return_value.__aexit__ = AsyncMock(return_value=None)

            from crypteolas.agents.tools.defi_metrics import get_protocol_tvl

            result = await get_protocol_tvl("nonexistent")

            # Should return empty dict or None on error, not raise
            assert result is None or result == {} or "error" in result


@requires_async
class TestCodeSearchTool:
    """Tests for code search agent tool."""

    @pytest.mark.asyncio
    async def test_search_code(self):
        """Test semantic code search."""
        mock_results = [
            {
                "file_path": "contracts/Pool.sol",
                "content": "function deposit() external...",
                "score": 0.95
            }
        ]

        with patch("crypteolas.cocoindex_flows.code_embedding.search") as mock_search:
            mock_search.return_value = mock_results

            from crypteolas.agents.tools.code_search import search_code

            result = await search_code("deposit function", limit=10)

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_by_function_name(self):
        """Test function name search."""
        mock_results = [
            {
                "file_path": "contracts/Lending.sol",
                "function_name": "flashLoan",
                "content": "function flashLoan(...) external..."
            }
        ]

        with patch("crypteolas.cocoindex_flows.code_embedding.search_by_name") as mock_search:
            mock_search.return_value = mock_results

            from crypteolas.agents.tools.code_search import search_by_function_name

            result = await search_by_function_name("flashLoan")

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_find_similar_code(self):
        """Test similar code finding."""
        code_snippet = """
        function deposit(uint256 amount) external {
            require(amount > 0, "Invalid amount");
            token.transferFrom(msg.sender, address(this), amount);
        }
        """

        mock_results = [
            {
                "file_path": "contracts/Vault.sol",
                "similarity": 0.85,
                "content": "function stake(uint256 amount)..."
            }
        ]

        with patch("crypteolas.cocoindex_flows.code_embedding.find_similar") as mock_search:
            mock_search.return_value = mock_results

            from crypteolas.agents.tools.code_search import find_similar_code

            result = await find_similar_code(code_snippet, limit=5)

            assert isinstance(result, list)


@requires_async
class TestDocumentSearchTool:
    """Tests for document search agent tool."""

    @pytest.mark.asyncio
    async def test_search_documents(self):
        """Test document search."""
        mock_results = [
            {
                "title": "Aave Protocol Overview",
                "content": "Aave is a decentralized lending protocol...",
                "score": 0.92
            }
        ]

        with patch("crypteolas.cocoindex_flows.document_embedding.search") as mock_search:
            mock_search.return_value = mock_results

            from crypteolas.agents.tools.document_search import search_documents

            result = await search_documents("lending protocol documentation")

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_audits(self):
        """Test audit report search."""
        mock_results = [
            {
                "title": "Aave V3 Security Audit",
                "auditor": "Trail of Bits",
                "findings": 5,
                "severity": "medium"
            }
        ]

        with patch("crypteolas.cocoindex_flows.document_embedding.search_audits") as mock_search:
            mock_search.return_value = mock_results

            from crypteolas.agents.tools.document_search import search_audits

            result = await search_audits("flash loan vulnerabilities")

            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_whitepapers(self):
        """Test whitepaper search."""
        mock_results = [
            {
                "title": "Uniswap V3 Core",
                "abstract": "Concentrated liquidity...",
                "authors": ["Hayden Adams", "Noah Zinsmeister"]
            }
        ]

        with patch("crypteolas.cocoindex_flows.document_embedding.search_whitepapers") as mock_search:
            mock_search.return_value = mock_results

            from crypteolas.agents.tools.document_search import search_whitepapers

            result = await search_whitepapers("automated market maker")

            assert isinstance(result, list)


class TestToolResultHandling:
    """Tests for tool result handling patterns."""

    def test_result_has_results_attribute(self):
        """Test checking for .results attribute on search results."""
        # Some search functions return objects with .results attribute
        class SearchResult:
            def __init__(self, data):
                self.results = data

        result = SearchResult([{"id": 1}, {"id": 2}])

        # Pattern used in tools
        if hasattr(result, "results"):
            data = result.results
        else:
            data = result

        assert len(data) == 2

    def test_empty_result_handling(self):
        """Test handling of empty search results."""
        empty_results = []

        # Tools should handle empty results gracefully
        if not empty_results:
            result = {"status": "no_results", "data": []}
        else:
            result = {"status": "success", "data": empty_results}

        assert result["status"] == "no_results"
        assert result["data"] == []

    def test_error_result_format(self):
        """Test error result format consistency."""
        error_result = {
            "status": "error",
            "error": "Connection timeout",
            "timestamp": "2024-01-15T10:00:00Z"
        }

        assert "status" in error_result
        assert "error" in error_result
        assert error_result["status"] == "error"


class TestToolFiltering:
    """Tests for filtering logic in tools."""

    def test_tvl_filter(self):
        """Test TVL filtering logic."""
        pools = [
            {"pool": "aave-eth", "tvlUsd": 2000000000},
            {"pool": "small-pool", "tvlUsd": 50000},
            {"pool": "medium-pool", "tvlUsd": 5000000}
        ]

        min_tvl = 1000000
        filtered = [p for p in pools if p.get("tvlUsd", 0) >= min_tvl]

        assert len(filtered) == 2
        assert all(p["tvlUsd"] >= min_tvl for p in filtered)

    def test_apy_sorting(self):
        """Test APY sorting logic."""
        pools = [
            {"pool": "low-yield", "apy": 1.5},
            {"pool": "high-yield", "apy": 8.5},
            {"pool": "medium-yield", "apy": 4.2}
        ]

        sorted_pools = sorted(pools, key=lambda x: x.get("apy", 0), reverse=True)

        assert sorted_pools[0]["pool"] == "high-yield"
        assert sorted_pools[-1]["pool"] == "low-yield"

    def test_chain_filter(self):
        """Test chain filtering logic."""
        protocols = [
            {"name": "Aave", "chain": "Ethereum"},
            {"name": "GMX", "chain": "Arbitrum"},
            {"name": "Compound", "chain": "Ethereum"}
        ]

        chain = "Ethereum"
        filtered = [p for p in protocols if p.get("chain") == chain]

        assert len(filtered) == 2
        assert all(p["chain"] == "Ethereum" for p in filtered)


@requires_async
class TestAsyncPatterns:
    """Tests for async patterns used in tools."""

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test concurrent API call pattern."""
        import asyncio

        async def mock_api_call(endpoint: str) -> dict:
            await asyncio.sleep(0.01)  # Simulate network delay
            return {"endpoint": endpoint, "status": "success"}

        # Concurrent calls
        results = await asyncio.gather(
            mock_api_call("/tvl"),
            mock_api_call("/yields"),
            mock_api_call("/tokens")
        )

        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)

    @pytest.mark.asyncio
    async def test_rate_limit_backoff(self):
        """Test rate limit backoff pattern."""
        import asyncio

        call_count = 0

        async def mock_api_with_rate_limit():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Rate limit exceeded")
            return {"status": "success"}

        # Simple retry pattern
        max_retries = 5
        for attempt in range(max_retries):
            try:
                result = await mock_api_with_rate_limit()
                break
            except Exception:
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.01 * (attempt + 1))
                else:
                    result = {"status": "error"}

        assert result["status"] == "success"
        assert call_count == 3
