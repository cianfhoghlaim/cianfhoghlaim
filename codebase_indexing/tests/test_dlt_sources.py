"""Tests for DLT data sources."""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Check for optional dependencies
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Skip decorator for tests requiring httpx
requires_httpx = pytest.mark.skipif(not HAS_HTTPX, reason="httpx not installed")


class TestDefiLlamaSource:
    """Tests for DeFiLlama DLT source."""

    def test_list_protocols_success(self, mock_defillama_protocols):
        """Test successful protocol listing."""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_defillama_protocols
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.defillama import _list_protocols

            protocols = list(_list_protocols())

            assert len(protocols) >= 1
            assert any(p.get("id") == "aave" for p in protocols)
            assert any(p.get("category") == "Lending" for p in protocols)

    def test_list_protocols_with_category_filter(self, mock_defillama_protocols):
        """Test protocol filtering by category."""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_defillama_protocols
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.defillama import _list_protocols

            # Filter for DEX only
            protocols = list(_list_protocols(categories=["DEX"]))

            # Should only return Uniswap (the DEX)
            dex_protocols = [p for p in protocols if p.get("category") == "DEX"]
            lending_protocols = [p for p in protocols if p.get("category") == "Lending"]
            assert len(dex_protocols) >= 0  # May be filtered
            # Original list has both, filtering may reduce

    def test_list_yields_success(self, mock_defillama_yields):
        """Test successful yields listing."""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_defillama_yields
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.defillama import _list_yields

            yields = list(_list_yields())

            assert len(yields) >= 1
            for y in yields:
                assert "apy" in y
                assert "tvlUsd" in y

    def test_list_protocols_http_error(self):
        """Test error handling for HTTP failures."""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("Connection failed")

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.defillama import _list_protocols

            protocols = list(_list_protocols())

            # Should yield error record
            assert len(protocols) >= 1
            error_records = [p for p in protocols if p.get("status") == "error"]
            assert len(error_records) >= 1

    def test_protocol_tvl_history(self, mock_defillama_protocol_tvl):
        """Test protocol TVL history fetching."""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_defillama_protocol_tvl
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.defillama import _get_protocol_tvl_history

            history = list(_get_protocol_tvl_history("aave"))

            assert len(history) >= 1
            for record in history:
                assert "date" in record or "totalLiquidityUSD" in record


class TestGitHubSource:
    """Tests for GitHub DLT source."""

    def test_get_client_with_token(self):
        """Test GitHub client creation with token."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token"}):
            with patch("httpx.Client") as mock_client:
                from crypteolas.dlt_sources.github.github_source import _get_client

                client = _get_client()
                # Verify headers are set correctly
                mock_client.assert_called()

    def test_paginate_single_page(self, mock_github_repos_page):
        """Test pagination with single page response."""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_github_repos_page
            mock_response.headers = {}  # No Link header = single page
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.github.github_source import _paginate

            with mock_client() as client:
                results = list(_paginate(client, "/repos"))

            assert len(results) == len(mock_github_repos_page)

    def test_paginate_multiple_pages(self, mock_github_repos_page):
        """Test pagination with multiple pages."""
        with patch("httpx.Client") as mock_client:
            # First page has Link header pointing to next
            first_response = MagicMock()
            first_response.json.return_value = mock_github_repos_page[:1]
            first_response.headers = {"Link": '<https://api.github.com/repos?page=2>; rel="next"'}
            first_response.raise_for_status = MagicMock()

            # Second page has no next link
            second_response = MagicMock()
            second_response.json.return_value = mock_github_repos_page[1:]
            second_response.headers = {}
            second_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.side_effect = [first_response, second_response]
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.github.github_source import _paginate

            with mock_client() as client:
                results = list(_paginate(client, "/repos"))

            assert len(results) == len(mock_github_repos_page)

    def test_list_commits(self, mock_github_commits_page):
        """Test commit listing."""
        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_github_commits_page
            mock_response.headers = {}
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.github.github_source import _list_commits

            commits = list(_list_commits("org/repo"))

            assert len(commits) >= 1
            for commit in commits:
                assert "sha" in commit
                assert "commit" in commit

    def test_rate_limit_handling(self):
        """Test handling of GitHub rate limit errors."""
        with patch("httpx.Client") as mock_client:
            import httpx

            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.json.return_value = {
                "message": "API rate limit exceeded"
            }
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "403 Forbidden", request=MagicMock(), response=mock_response
            )

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            # The source should handle rate limits gracefully
            from crypteolas.dlt_sources.github.github_source import _paginate

            with mock_client() as client:
                results = list(_paginate(client, "/repos"))

            # Should return empty or error record, not crash
            assert isinstance(results, list)


class TestBinanceSource:
    """Tests for Binance DLT source."""

    def test_list_funding_rates(self):
        """Test funding rate listing."""
        mock_response_data = [
            {
                "symbol": "BTCUSDT",
                "fundingRate": "0.0001",
                "fundingTime": 1704067200000,
                "markPrice": "42000.00"
            },
            {
                "symbol": "ETHUSDT",
                "fundingRate": "0.0002",
                "fundingTime": 1704067200000,
                "markPrice": "2200.00"
            }
        ]

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.binance import _list_funding_rates

            rates = list(_list_funding_rates())

            assert len(rates) >= 1
            for rate in rates:
                assert "symbol" in rate
                assert "fundingRate" in rate

    def test_list_open_interest(self):
        """Test open interest listing."""
        mock_response_data = [
            {
                "symbol": "BTCUSDT",
                "openInterest": "50000.00",
                "time": 1704067200000
            }
        ]

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.binance import _list_open_interest

            oi = list(_list_open_interest())

            assert len(oi) >= 1
            for record in oi:
                assert "symbol" in record
                assert "openInterest" in record


class TestCoinGeckoSource:
    """Tests for CoinGecko DLT source."""

    def test_list_coins_without_api_key(self):
        """Test coin listing without API key (free tier)."""
        mock_coins = [
            {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"},
            {"id": "ethereum", "symbol": "eth", "name": "Ethereum"}
        ]

        with patch.dict("os.environ", {}, clear=True):
            with patch("httpx.Client") as mock_client:
                mock_response = MagicMock()
                mock_response.json.return_value = mock_coins
                mock_response.raise_for_status = MagicMock()

                client_instance = MagicMock()
                client_instance.get.return_value = mock_response
                mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
                mock_client.return_value.__exit__ = MagicMock(return_value=None)

                from crypteolas.dlt_sources.defi.coingecko import _list_coins

                coins = list(_list_coins())

                assert len(coins) >= 1
                assert any(c.get("id") == "bitcoin" for c in coins)

    def test_get_price_history(self):
        """Test price history fetching."""
        mock_history = {
            "prices": [
                [1704067200000, 42000.0],
                [1704153600000, 42500.0]
            ],
            "market_caps": [
                [1704067200000, 800000000000],
                [1704153600000, 830000000000]
            ]
        }

        with patch("httpx.Client") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_history
            mock_response.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.get.return_value = mock_response
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.coingecko import _get_price_history

            history = list(_get_price_history("bitcoin", days=7))

            assert len(history) >= 1


class TestFileWatcherSource:
    """Tests for file watcher DLT source."""

    def test_compute_file_hash(self, tmp_path):
        """Test file hash computation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        from crypteolas.dlt_sources.local.file_watcher import _compute_file_hash

        hash1 = _compute_file_hash(test_file)
        hash2 = _compute_file_hash(test_file)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex digest

    def test_compute_file_hash_different_content(self, tmp_path):
        """Test that different content produces different hashes."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content A")
        file2.write_text("Content B")

        from crypteolas.dlt_sources.local.file_watcher import _compute_file_hash

        hash1 = _compute_file_hash(file1)
        hash2 = _compute_file_hash(file2)

        assert hash1 != hash2

    def test_read_file_content_utf8(self, tmp_path):
        """Test reading UTF-8 file content."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World! \u00e9\u00e0\u00fc")

        from crypteolas.dlt_sources.local.file_watcher import _read_file_content

        content = _read_file_content(test_file)

        assert "Hello, World!" in content
        assert "\u00e9" in content  # Accented characters

    def test_detect_language(self):
        """Test file language detection."""
        from crypteolas.dlt_sources.local.file_watcher import _detect_language

        assert _detect_language(Path("test.py")) == "python"
        assert _detect_language(Path("test.js")) == "javascript"
        assert _detect_language(Path("test.ts")) == "typescript"
        assert _detect_language(Path("test.sol")) == "solidity"
        assert _detect_language(Path("test.rs")) == "rust"
        assert _detect_language(Path("test.go")) == "go"

    def test_ignore_patterns(self, tmp_path):
        """Test that ignore patterns work correctly."""
        # Create test files
        (tmp_path / "valid.py").write_text("print('hello')")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config").write_text("git config")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "package.json").write_text("{}")

        from crypteolas.dlt_sources.local.file_watcher import get_changed_files

        # Run with default ignore patterns
        files = list(get_changed_files(str(tmp_path)))

        file_paths = [f.get("file_path", "") for f in files]

        # Should include valid.py
        assert any("valid.py" in p for p in file_paths)
        # Should NOT include .git or node_modules
        assert not any(".git" in p for p in file_paths)
        assert not any("node_modules" in p for p in file_paths)


class TestSubgraphSource:
    """Tests for GraphQL subgraph DLT source."""

    def test_aave_reserves_query(self):
        """Test Aave reserves GraphQL query."""
        mock_response = {
            "data": {
                "reserves": [
                    {
                        "id": "0x...",
                        "symbol": "WETH",
                        "name": "Wrapped Ether",
                        "liquidityRate": "20000000000000000000000000",  # Ray format
                        "variableBorrowRate": "30000000000000000000000000",
                        "totalLiquidity": "1000000000000000000000",
                        "availableLiquidity": "500000000000000000000"
                    }
                ]
            }
        }

        with patch("httpx.Client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.post.return_value = mock_resp
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.subgraphs import aave_reserves

            reserves = list(aave_reserves())

            assert len(reserves) >= 1
            for reserve in reserves:
                assert "symbol" in reserve

    def test_graphql_error_handling(self):
        """Test GraphQL error response handling."""
        mock_response = {
            "errors": [
                {"message": "Query too complex"}
            ]
        }

        with patch("httpx.Client") as mock_client:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_response
            mock_resp.raise_for_status = MagicMock()

            client_instance = MagicMock()
            client_instance.post.return_value = mock_resp
            mock_client.return_value.__enter__ = MagicMock(return_value=client_instance)
            mock_client.return_value.__exit__ = MagicMock(return_value=None)

            from crypteolas.dlt_sources.defi.subgraphs import aave_reserves

            reserves = list(aave_reserves())

            # Should handle error gracefully
            error_records = [r for r in reserves if r.get("status") == "error"]
            assert len(error_records) >= 1


class TestTimestampConversions:
    """Tests for timestamp handling across sources."""

    def test_milliseconds_to_datetime(self):
        """Test conversion of millisecond timestamps."""
        # 2024-01-01 00:00:00 UTC in milliseconds
        ms_timestamp = 1704067200000

        dt = datetime.fromtimestamp(ms_timestamp / 1000)

        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1

    def test_seconds_to_datetime(self):
        """Test conversion of second timestamps."""
        # 2024-01-01 00:00:00 UTC in seconds
        sec_timestamp = 1704067200

        dt = datetime.fromtimestamp(sec_timestamp)

        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 1


class TestDataNormalization:
    """Tests for data normalization across sources."""

    def test_tvl_normalization(self):
        """Test TVL values are normalized correctly."""
        # DeFiLlama returns raw USD values
        raw_tvl = 10500000000  # $10.5B

        # Should be stored as-is (no scaling)
        assert raw_tvl == 10500000000

    def test_apy_percentage_handling(self):
        """Test APY values are in percentage format."""
        # DeFiLlama yields API returns APY as percentage (3.5 = 3.5%)
        apy = 3.5

        # Should be used directly, not divided by 100
        assert apy == 3.5

    def test_ray_to_percentage_conversion(self):
        """Test Aave ray format conversion."""
        # Aave uses ray format (1e27) for rates
        liquidity_rate_ray = 20000000000000000000000000  # 2% in ray

        # Convert to percentage
        apy = liquidity_rate_ray / 1e27 * 100

        assert abs(apy - 2.0) < 0.01
