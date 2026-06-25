"""
Binance Futures API source for funding rates and market data.

Provides funding rate history for perpetual contracts, which is
critical for understanding Ethena's delta-neutral yield mechanism.
"""

from datetime import datetime
from typing import Any, Iterator, Optional

import dlt
from dlt.sources.helpers.rest_client import RESTClient


@dlt.resource(
    name="binance_funding_rates",
    primary_key=["symbol", "fundingTime"],
    write_disposition="merge",
)
def binance_funding_rates(
    symbols: list[str],
    start_time: Optional[int] = None,
    limit: int = 1000,
) -> Iterator[dict[str, Any]]:
    """
    Fetch funding rate history from Binance Futures.

    Funding rates are paid every 8 hours. This is crucial data for
    understanding Ethena's basis trade strategy.

    Args:
        symbols: List of trading pair symbols (e.g., ["ETHUSDT", "BTCUSDT"])
        start_time: Start timestamp in milliseconds (default: 30 days ago)
        limit: Max records per request (max 1000)

    Yields:
        Funding rate records
    """
    import httpx

    base_url = "https://fapi.binance.com"

    # Default to 30 days ago
    if start_time is None:
        start_time = int((datetime.utcnow().timestamp() - 30 * 24 * 3600) * 1000)

    client = httpx.Client(base_url=base_url, timeout=30.0)

    for symbol in symbols:
        current_start = start_time

        while True:
            params = {
                "symbol": symbol,
                "startTime": current_start,
                "limit": limit,
            }

            response = client.get("/fapi/v1/fundingRate", params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            for record in data:
                yield {
                    "symbol": record["symbol"],
                    "fundingTime": datetime.utcfromtimestamp(
                        record["fundingTime"] / 1000
                    ),
                    "fundingRate": float(record["fundingRate"]),
                    "markPrice": float(record.get("markPrice", 0)),
                    "exchange": "binance",
                    "fetched_at": datetime.utcnow(),
                }

            # Move to next page
            last_time = data[-1]["fundingTime"]
            current_start = last_time + 1

            # Stop if we've reached current time
            if last_time >= datetime.utcnow().timestamp() * 1000:
                break

    client.close()


@dlt.resource(
    name="binance_funding_info",
    primary_key="symbol",
    write_disposition="replace",
)
def binance_funding_info(
    symbols: list[str],
) -> Iterator[dict[str, Any]]:
    """
    Fetch current funding rate caps and next funding time.

    Args:
        symbols: List of trading pair symbols

    Yields:
        Funding info records
    """
    import httpx

    client = httpx.Client(
        base_url="https://fapi.binance.com",
        timeout=30.0,
    )

    response = client.get("/fapi/v1/fundingInfo")
    response.raise_for_status()
    data = response.json()

    for info in data:
        if info["symbol"] in symbols:
            yield {
                "symbol": info["symbol"],
                "adjustedFundingRateCap": float(info.get("adjustedFundingRateCap", 0)),
                "adjustedFundingRateFloor": float(
                    info.get("adjustedFundingRateFloor", 0)
                ),
                "fundingIntervalHours": info.get("fundingIntervalHours", 8),
                "exchange": "binance",
                "fetched_at": datetime.utcnow(),
            }

    client.close()


@dlt.resource(
    name="binance_open_interest",
    primary_key=["symbol", "timestamp"],
    write_disposition="merge",
)
def binance_open_interest_history(
    symbols: list[str],
    period: str = "5m",
    limit: int = 500,
) -> Iterator[dict[str, Any]]:
    """
    Fetch open interest history.

    Args:
        symbols: Trading pair symbols
        period: Time period (5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d)
        limit: Max records per request

    Yields:
        Open interest records
    """
    import httpx

    client = httpx.Client(
        base_url="https://fapi.binance.com",
        timeout=30.0,
    )

    for symbol in symbols:
        try:
            response = client.get(
                "/futures/data/openInterestHist",
                params={
                    "symbol": symbol,
                    "period": period,
                    "limit": limit,
                },
            )
            response.raise_for_status()
            data = response.json()

            for record in data:
                yield {
                    "symbol": record["symbol"],
                    "timestamp": datetime.utcfromtimestamp(record["timestamp"] / 1000),
                    "sumOpenInterest": float(record["sumOpenInterest"]),
                    "sumOpenInterestValue": float(record["sumOpenInterestValue"]),
                    "exchange": "binance",
                }

        except httpx.HTTPError as e:
            print(f"Error fetching OI for {symbol}: {e}")
            continue

    client.close()


@dlt.resource(
    name="binance_long_short_ratio",
    primary_key=["symbol", "timestamp"],
    write_disposition="merge",
)
def binance_long_short_ratio(
    symbols: list[str],
    period: str = "5m",
    limit: int = 500,
) -> Iterator[dict[str, Any]]:
    """
    Fetch long/short ratio history (top trader positions).

    Args:
        symbols: Trading pair symbols
        period: Time period
        limit: Max records

    Yields:
        Long/short ratio records
    """
    import httpx

    client = httpx.Client(
        base_url="https://fapi.binance.com",
        timeout=30.0,
    )

    for symbol in symbols:
        try:
            # Top trader long/short ratio (accounts)
            response = client.get(
                "/futures/data/topLongShortAccountRatio",
                params={
                    "symbol": symbol,
                    "period": period,
                    "limit": limit,
                },
            )
            response.raise_for_status()
            data = response.json()

            for record in data:
                yield {
                    "symbol": record["symbol"],
                    "timestamp": datetime.utcfromtimestamp(record["timestamp"] / 1000),
                    "longShortRatio": float(record["longShortRatio"]),
                    "longAccount": float(record["longAccount"]),
                    "shortAccount": float(record["shortAccount"]),
                    "ratio_type": "top_accounts",
                    "exchange": "binance",
                }

        except httpx.HTTPError as e:
            print(f"Error fetching L/S ratio for {symbol}: {e}")
            continue

    client.close()


@dlt.source(name="binance_funding")
def binance_funding_source(
    symbols: Optional[list[str]] = None,
    days_back: int = 30,
) -> Iterator[dlt.resource]:
    """
    Binance Futures funding data source.

    Args:
        symbols: Trading pairs to track
        days_back: History depth

    Yields:
        All Binance funding-related resources
    """
    if symbols is None:
        symbols = ["ETHUSDT", "BTCUSDT"]

    start_time = int((datetime.utcnow().timestamp() - days_back * 24 * 3600) * 1000)

    yield binance_funding_rates(symbols=symbols, start_time=start_time)
    yield binance_funding_info(symbols=symbols)
    yield binance_open_interest_history(symbols=symbols)
    yield binance_long_short_ratio(symbols=symbols)


def run_binance_pipeline(
    symbols: Optional[list[str]] = None,
    days_back: int = 30,
    destination_type: str = "duckdb",
):
    """
    Run the Binance funding pipeline standalone.

    Args:
        symbols: Trading pairs
        days_back: History depth
        destination_type: Target destination
    """
    from pipelines.shared.duckdb_destination import create_pipeline

    if symbols is None:
        symbols = ["ETHUSDT", "BTCUSDT"]

    pipeline, metadata = create_pipeline(
        pipeline_name="binance_funding",
        destination_type=destination_type,
    )

    load_info = pipeline.run(
        binance_funding_source(symbols=symbols, days_back=days_back)
    )

    print(f"Binance pipeline completed: {load_info}")
    return load_info


if __name__ == "__main__":
    run_binance_pipeline()
