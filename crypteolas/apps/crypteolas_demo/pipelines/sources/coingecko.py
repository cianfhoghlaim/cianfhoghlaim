"""
CoinGecko API source for cryptocurrency price and market data.

Uses dlt's REST API source with declarative configuration.
Supports incremental loading for efficient updates.
"""

from datetime import datetime, timedelta
from typing import Any, Iterator, Optional

import dlt
from dlt.sources.rest_api import rest_api_source, RESTAPIConfig


@dlt.source(name="coingecko")
def coingecko_source(
    api_key: str = dlt.secrets.value,
    days_back: int = 30,
    tokens: Optional[list[str]] = None,
) -> Iterator[dlt.resource]:
    """
    CoinGecko API source for price and market data.

    Args:
        api_key: CoinGecko API key (optional for public endpoints)
        days_back: Number of days to fetch for incremental loads
        tokens: List of token IDs to fetch. Defaults to Ethena ecosystem tokens.

    Yields:
        DLT resources for each configured endpoint
    """
    if tokens is None:
        tokens = [
            "ethena-usde",
            "ethena-staked-usde",
            "ethereum",
            "usd-coin",
        ]

    # Configure client with optional API key
    client_config = {
        "base_url": "https://api.coingecko.com/api/v3",
    }

    if api_key:
        client_config["headers"] = {"x-cg-demo-api-key": api_key}

    # Build resources for each token
    resources = []

    for token_id in tokens:
        resources.append(
            {
                "name": f"price_{token_id.replace('-', '_')}",
                "endpoint": {
                    "path": f"/coins/{token_id}/market_chart",
                    "params": {
                        "vs_currency": "usd",
                        "days": str(days_back),
                    },
                },
                "data_selector": "prices",
                "primary_key": "timestamp",
                "write_disposition": "merge",
            }
        )

    # Add global market data
    resources.append(
        {
            "name": "global_market",
            "endpoint": {
                "path": "/global",
            },
            "primary_key": "updated_at",
            "write_disposition": "append",
        }
    )

    yield from rest_api_source(
        RESTAPIConfig(client=client_config, resources=resources)
    )


@dlt.resource(
    name="coingecko_prices",
    primary_key=["token_id", "timestamp"],
    write_disposition="merge",
)
def coingecko_prices(
    token_ids: list[str],
    days: int = 30,
    api_key: Optional[str] = None,
) -> Iterator[dict[str, Any]]:
    """
    Fetch price history for multiple tokens with transformation.

    This resource fetches data and transforms it into a normalized format
    suitable for analytics.

    Args:
        token_ids: List of CoinGecko token IDs
        days: Number of days of history
        api_key: Optional API key for higher rate limits

    Yields:
        Normalized price records
    """
    import httpx

    base_url = "https://api.coingecko.com/api/v3"
    headers = {}

    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    client = httpx.Client(base_url=base_url, headers=headers, timeout=30.0)

    for token_id in token_ids:
        try:
            response = client.get(
                f"/coins/{token_id}/market_chart",
                params={"vs_currency": "usd", "days": str(days)},
            )
            response.raise_for_status()
            data = response.json()

            # Transform prices array into records
            for price_point in data.get("prices", []):
                timestamp_ms, price = price_point
                yield {
                    "token_id": token_id,
                    "timestamp": datetime.utcfromtimestamp(timestamp_ms / 1000),
                    "price_usd": price,
                    "source": "coingecko",
                    "fetched_at": datetime.utcnow(),
                }

            # Also yield market cap and volume if available
            market_caps = data.get("market_caps", [])
            volumes = data.get("total_volumes", [])

            for i, mc_point in enumerate(market_caps):
                timestamp_ms, market_cap = mc_point
                record = {
                    "token_id": token_id,
                    "timestamp": datetime.utcfromtimestamp(timestamp_ms / 1000),
                    "market_cap_usd": market_cap,
                    "source": "coingecko",
                    "fetched_at": datetime.utcnow(),
                }

                # Add volume if available at same index
                if i < len(volumes):
                    record["volume_24h_usd"] = volumes[i][1]

                yield record

        except httpx.HTTPError as e:
            # Log error but continue with other tokens
            print(f"Error fetching {token_id}: {e}")
            continue

    client.close()


@dlt.resource(
    name="coingecko_token_info",
    primary_key="id",
    write_disposition="merge",
)
def coingecko_token_info(
    token_ids: list[str],
    api_key: Optional[str] = None,
) -> Iterator[dict[str, Any]]:
    """
    Fetch detailed token information for knowledge graph entities.

    Args:
        token_ids: List of CoinGecko token IDs
        api_key: Optional API key

    Yields:
        Token metadata records
    """
    import httpx

    base_url = "https://api.coingecko.com/api/v3"
    headers = {}

    if api_key:
        headers["x-cg-demo-api-key"] = api_key

    client = httpx.Client(base_url=base_url, headers=headers, timeout=30.0)

    for token_id in token_ids:
        try:
            response = client.get(f"/coins/{token_id}")
            response.raise_for_status()
            data = response.json()

            # Extract relevant fields for knowledge graph
            yield {
                "id": data["id"],
                "symbol": data["symbol"].upper(),
                "name": data["name"],
                "contract_address": data.get("platforms", {}).get("ethereum"),
                "categories": data.get("categories", []),
                "description": data.get("description", {}).get("en", "")[:500],
                "homepage": data.get("links", {}).get("homepage", [None])[0],
                "github": data.get("links", {}).get("repos_url", {}).get("github", []),
                "twitter": data.get("links", {}).get("twitter_screen_name"),
                "market_cap_rank": data.get("market_cap_rank"),
                "coingecko_rank": data.get("coingecko_rank"),
                "genesis_date": data.get("genesis_date"),
                "sentiment_votes_up_percentage": data.get(
                    "sentiment_votes_up_percentage"
                ),
                "fetched_at": datetime.utcnow(),
            }

        except httpx.HTTPError as e:
            print(f"Error fetching info for {token_id}: {e}")
            continue

    client.close()


# Convenience function for running standalone
def run_coingecko_pipeline(
    tokens: Optional[list[str]] = None,
    days: int = 30,
    destination_type: str = "duckdb",
):
    """
    Run the CoinGecko pipeline standalone.

    Args:
        tokens: Token IDs to fetch
        days: Days of history
        destination_type: Target destination
    """
    from pipelines.shared.duckdb_destination import create_pipeline

    if tokens is None:
        tokens = ["ethena-usde", "ethena-staked-usde", "ethereum"]

    pipeline, metadata = create_pipeline(
        pipeline_name="coingecko_prices",
        destination_type=destination_type,
    )

    # Run price fetching
    load_info = pipeline.run(
        coingecko_prices(token_ids=tokens, days=days),
    )

    print(f"CoinGecko pipeline completed: {load_info}")
    return load_info


if __name__ == "__main__":
    run_coingecko_pipeline()
