"""
DLT source for Bybit API - Funding rates and market data.

API Reference: https://bybit-exchange.github.io/docs/v5/intro

Provides access to:
- Perpetual futures funding rates
- Open interest data
- Market data
"""

from datetime import datetime, timezone
from typing import Any, Iterator, Optional

import dlt
import httpx

# Bybit API base URL
BYBIT_API_URL = "https://api.bybit.com"


def _get_client() -> httpx.Client:
    """Get HTTP client for Bybit API."""
    return httpx.Client(base_url=BYBIT_API_URL, timeout=30.0)


@dlt.resource(
    name="bybit_funding_history",
    primary_key=["symbol", "funding_rate_timestamp"],
    write_disposition="merge",
)
def bybit_funding_history(
    symbols: Optional[list[str]] = None,
    category: str = "linear",
    limit: int = 200,
) -> Iterator[dict[str, Any]]:
    """
    Fetch historical funding rate data from Bybit.

    Args:
        symbols: List of symbols to fetch (default: ["ETHUSDT", "BTCUSDT"])
        category: Product type (linear, inverse)
        limit: Number of records per request

    Yields:
        Funding rate records
    """
    if symbols is None:
        symbols = ["ETHUSDT", "BTCUSDT"]

    with _get_client() as client:
        for symbol in symbols:
            try:
                response = client.get(
                    "/v5/market/funding/history",
                    params={
                        "category": category,
                        "symbol": symbol,
                        "limit": limit,
                    },
                )
                response.raise_for_status()
                data = response.json()

                if data.get("retCode") != 0:
                    import logging

                    logging.warning(
                        f"Bybit funding history API error for {symbol}: {data.get('retMsg')}"
                    )
                    continue

                for rate in data.get("result", {}).get("list", []):
                    funding_time = int(rate.get("fundingRateTimestamp", 0))
                    yield {
                        "symbol": symbol,
                        "funding_rate": float(rate.get("fundingRate", 0)),
                        "funding_rate_timestamp": datetime.fromtimestamp(
                            funding_time / 1000, tz=timezone.utc
                        ).isoformat(),
                        "funding_rate_timestamp_ms": funding_time,
                        "annualized_rate": float(rate.get("fundingRate", 0)) * 3 * 365,
                        "exchange": "bybit",
                        "category": category,
                        "data_status": "success",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }

            except Exception as e:
                import logging

                logging.warning(f"Bybit funding history API error for {symbol}: {e}")


@dlt.resource(
    name="bybit_open_interest",
    primary_key=["symbol", "timestamp"],
    write_disposition="merge",
)
def bybit_open_interest(
    symbols: Optional[list[str]] = None,
    category: str = "linear",
    interval: str = "1h",
    limit: int = 200,
) -> Iterator[dict[str, Any]]:
    """
    Fetch open interest data from Bybit.

    Args:
        symbols: List of symbols
        category: Product type
        interval: Time interval (5min, 15min, 30min, 1h, 4h, 1d)
        limit: Number of records

    Yields:
        Open interest records
    """
    if symbols is None:
        symbols = ["ETHUSDT", "BTCUSDT"]

    with _get_client() as client:
        for symbol in symbols:
            try:
                response = client.get(
                    "/v5/market/open-interest",
                    params={
                        "category": category,
                        "symbol": symbol,
                        "intervalTime": interval,
                        "limit": limit,
                    },
                )
                response.raise_for_status()
                data = response.json()

                if data.get("retCode") != 0:
                    continue

                for oi in data.get("result", {}).get("list", []):
                    timestamp = int(oi.get("timestamp", 0))
                    yield {
                        "symbol": symbol,
                        "open_interest": float(oi.get("openInterest", 0)),
                        "timestamp": datetime.fromtimestamp(
                            timestamp / 1000, tz=timezone.utc
                        ).isoformat(),
                        "timestamp_ms": timestamp,
                        "exchange": "bybit",
                        "category": category,
                        "interval": interval,
                        "data_status": "success",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }

            except Exception as e:
                import logging

                logging.warning(f"Bybit open interest API error for {symbol}: {e}")


@dlt.resource(
    name="bybit_tickers",
    primary_key=["symbol"],
    write_disposition="replace",
)
def bybit_tickers(
    category: str = "linear",
) -> Iterator[dict[str, Any]]:
    """
    Fetch current ticker data from Bybit.

    Args:
        category: Product type (spot, linear, inverse, option)

    Yields:
        Ticker records
    """
    with _get_client() as client:
        try:
            response = client.get(
                "/v5/market/tickers",
                params={"category": category},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("retCode") != 0:
                return

            for ticker in data.get("result", {}).get("list", []):
                yield {
                    "symbol": ticker.get("symbol"),
                    "last_price": float(ticker.get("lastPrice", 0)),
                    "index_price": float(ticker.get("indexPrice", 0)),
                    "mark_price": float(ticker.get("markPrice", 0)),
                    "prev_price_24h": float(ticker.get("prevPrice24h", 0)),
                    "price_24h_pcnt": float(ticker.get("price24hPcnt", 0)),
                    "high_price_24h": float(ticker.get("highPrice24h", 0)),
                    "low_price_24h": float(ticker.get("lowPrice24h", 0)),
                    "volume_24h": float(ticker.get("volume24h", 0)),
                    "turnover_24h": float(ticker.get("turnover24h", 0)),
                    "open_interest": float(ticker.get("openInterest", 0)),
                    "open_interest_value": float(ticker.get("openInterestValue", 0)),
                    "funding_rate": float(ticker.get("fundingRate", 0)),
                    "next_funding_time": ticker.get("nextFundingTime"),
                    "bid_price": float(ticker.get("bid1Price", 0)),
                    "ask_price": float(ticker.get("ask1Price", 0)),
                    "exchange": "bybit",
                    "category": category,
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging

            logging.warning(f"Bybit tickers API error: {e}")


@dlt.source(name="bybit_source")
def bybit_source(
    symbols: Optional[list[str]] = None,
    include_tickers: bool = True,
    include_funding: bool = True,
    include_oi: bool = True,
) -> Iterator[Any]:
    """
    Bybit data source combining funding, OI, and tickers.

    Args:
        symbols: Symbols to fetch
        include_tickers: Include ticker data
        include_funding: Include funding rate history
        include_oi: Include open interest

    Yields:
        Bybit data resources
    """
    if include_tickers:
        yield bybit_tickers()
    if include_funding:
        yield bybit_funding_history(symbols=symbols)
    if include_oi:
        yield bybit_open_interest(symbols=symbols)


def run_bybit_pipeline(
    symbols: Optional[list[str]] = None,
    destination: str = "duckdb",
    dataset_name: str = "defi_raw",
):
    """Run Bybit pipeline standalone."""
    pipeline = dlt.pipeline(
        pipeline_name="bybit_data",
        destination=destination,
        dataset_name=dataset_name,
    )

    source = bybit_source(symbols=symbols)
    load_info = pipeline.run(source)
    print(f"Bybit pipeline completed: {load_info}")
    return pipeline


if __name__ == "__main__":
    run_bybit_pipeline()
