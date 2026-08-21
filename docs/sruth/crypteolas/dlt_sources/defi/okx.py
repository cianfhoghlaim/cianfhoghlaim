"""
DLT source for OKX API - Funding rates and market data.

API Reference: https://www.okx.com/docs-v5/

Provides access to:
- Perpetual swap funding rates
- Mark price and index price
- Open interest data
"""

from datetime import datetime, timezone
from typing import Any, Iterator, Optional

import dlt
import httpx

# OKX API base URL
OKX_API_URL = "https://www.okx.com/api/v5"


def _get_client() -> httpx.Client:
    """Get HTTP client for OKX API."""
    return httpx.Client(base_url=OKX_API_URL, timeout=30.0)


@dlt.resource(
    name="okx_funding_history",
    primary_key=["inst_id", "funding_time"],
    write_disposition="merge",
)
def okx_funding_history(
    inst_ids: Optional[list[str]] = None,
    limit: int = 100,
) -> Iterator[dict[str, Any]]:
    """
    Fetch historical funding rate data from OKX.

    Args:
        inst_ids: List of instrument IDs (default: ["ETH-USDT-SWAP", "BTC-USDT-SWAP"])
        limit: Number of records per request (max 100)

    Yields:
        Funding rate records
    """
    if inst_ids is None:
        inst_ids = ["ETH-USDT-SWAP", "BTC-USDT-SWAP"]

    with _get_client() as client:
        for inst_id in inst_ids:
            try:
                response = client.get(
                    "/public/funding-rate-history",
                    params={
                        "instId": inst_id,
                        "limit": limit,
                    },
                )
                response.raise_for_status()
                data = response.json()

                if data.get("code") != "0":
                    import logging

                    logging.warning(
                        f"OKX funding history API error for {inst_id}: {data.get('msg')}"
                    )
                    continue

                for rate in data.get("data", []):
                    funding_time = int(rate.get("fundingTime", 0))
                    yield {
                        "inst_id": inst_id,
                        "funding_rate": float(rate.get("fundingRate", 0)),
                        "realized_rate": float(rate.get("realizedRate", 0))
                        if rate.get("realizedRate")
                        else None,
                        "funding_time": datetime.fromtimestamp(
                            funding_time / 1000, tz=timezone.utc
                        ).isoformat(),
                        "funding_time_ms": funding_time,
                        "annualized_rate": float(rate.get("fundingRate", 0)) * 3 * 365,
                        "exchange": "okx",
                        "inst_type": "SWAP",
                        "data_status": "success",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }

            except Exception as e:
                import logging

                logging.warning(f"OKX funding history API error for {inst_id}: {e}")


@dlt.resource(
    name="okx_current_funding",
    primary_key=["inst_id"],
    write_disposition="replace",
)
def okx_current_funding(
    inst_ids: Optional[list[str]] = None,
) -> Iterator[dict[str, Any]]:
    """
    Fetch current funding rate from OKX.

    Args:
        inst_ids: List of instrument IDs

    Yields:
        Current funding rate records
    """
    if inst_ids is None:
        inst_ids = ["ETH-USDT-SWAP", "BTC-USDT-SWAP"]

    with _get_client() as client:
        for inst_id in inst_ids:
            try:
                response = client.get(
                    "/public/funding-rate",
                    params={"instId": inst_id},
                )
                response.raise_for_status()
                data = response.json()

                if data.get("code") != "0":
                    continue

                for rate in data.get("data", []):
                    next_time = int(rate.get("nextFundingTime", 0))
                    yield {
                        "inst_id": inst_id,
                        "funding_rate": float(rate.get("fundingRate", 0)),
                        "next_funding_rate": float(rate.get("nextFundingRate", 0))
                        if rate.get("nextFundingRate")
                        else None,
                        "next_funding_time": datetime.fromtimestamp(
                            next_time / 1000, tz=timezone.utc
                        ).isoformat()
                        if next_time
                        else None,
                        "exchange": "okx",
                        "data_status": "success",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }

            except Exception as e:
                import logging

                logging.warning(f"OKX current funding API error for {inst_id}: {e}")


@dlt.resource(
    name="okx_open_interest",
    primary_key=["inst_id", "timestamp"],
    write_disposition="merge",
)
def okx_open_interest(
    inst_type: str = "SWAP",
    uly: Optional[str] = None,
) -> Iterator[dict[str, Any]]:
    """
    Fetch open interest data from OKX.

    Args:
        inst_type: Instrument type (SWAP, FUTURES, OPTION)
        uly: Underlying (e.g., "ETH-USDT")

    Yields:
        Open interest records
    """
    with _get_client() as client:
        try:
            params = {"instType": inst_type}
            if uly:
                params["uly"] = uly

            response = client.get("/public/open-interest", params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != "0":
                return

            for oi in data.get("data", []):
                ts = int(oi.get("ts", 0))
                yield {
                    "inst_id": oi.get("instId"),
                    "inst_type": oi.get("instType"),
                    "open_interest": float(oi.get("oi", 0)),
                    "open_interest_ccy": float(oi.get("oiCcy", 0)),
                    "timestamp": datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat(),
                    "timestamp_ms": ts,
                    "exchange": "okx",
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging

            logging.warning(f"OKX open interest API error: {e}")


@dlt.resource(
    name="okx_mark_price",
    primary_key=["inst_id"],
    write_disposition="replace",
)
def okx_mark_price(
    inst_type: str = "SWAP",
) -> Iterator[dict[str, Any]]:
    """
    Fetch mark price data from OKX.

    Args:
        inst_type: Instrument type

    Yields:
        Mark price records
    """
    with _get_client() as client:
        try:
            response = client.get(
                "/public/mark-price",
                params={"instType": inst_type},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("code") != "0":
                return

            for price in data.get("data", []):
                ts = int(price.get("ts", 0))
                yield {
                    "inst_id": price.get("instId"),
                    "inst_type": price.get("instType"),
                    "mark_price": float(price.get("markPx", 0)),
                    "timestamp": datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat(),
                    "exchange": "okx",
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging

            logging.warning(f"OKX mark price API error: {e}")


@dlt.source(name="okx_source")
def okx_source(
    inst_ids: Optional[list[str]] = None,
    include_funding_history: bool = True,
    include_current_funding: bool = True,
    include_oi: bool = True,
    include_mark_price: bool = True,
) -> Iterator[Any]:
    """
    OKX data source combining funding, OI, and mark prices.

    Args:
        inst_ids: Instrument IDs to fetch
        include_funding_history: Include historical funding rates
        include_current_funding: Include current funding rate
        include_oi: Include open interest
        include_mark_price: Include mark prices

    Yields:
        OKX data resources
    """
    if include_current_funding:
        yield okx_current_funding(inst_ids=inst_ids)
    if include_funding_history:
        yield okx_funding_history(inst_ids=inst_ids)
    if include_oi:
        yield okx_open_interest()
    if include_mark_price:
        yield okx_mark_price()


def run_okx_pipeline(
    inst_ids: Optional[list[str]] = None,
    destination: str = "duckdb",
    dataset_name: str = "defi_raw",
):
    """Run OKX pipeline standalone."""
    pipeline = dlt.pipeline(
        pipeline_name="okx_data",
        destination=destination,
        dataset_name=dataset_name,
    )

    source = okx_source(inst_ids=inst_ids)
    load_info = pipeline.run(source)
    print(f"OKX pipeline completed: {load_info}")
    return pipeline


if __name__ == "__main__":
    run_okx_pipeline()
