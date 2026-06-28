"""
DLT source for CoinGecko API - Token prices, market data, exchanges.

API Reference: https://docs.coingecko.com/reference/introduction

Provides access to:
- Token prices and market data
- Historical price data
- Exchange information
- Trending tokens
"""

import os
from datetime import datetime, timezone
from typing import Any, Iterator

import dlt
import httpx

# CoinGecko API base URL
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"


def _get_client() -> httpx.Client:
    """Get HTTP client for CoinGecko API."""
    api_key = os.environ.get("COINGECKO_API_KEY")
    headers = {}
    if api_key:
        headers["x-cg-demo-api-key"] = api_key
    return httpx.Client(base_url=COINGECKO_API_URL, timeout=30.0, headers=headers)


def _list_coins(
    per_page: int = 250,
    max_pages: int = 4,
) -> Iterator[dict[str, Any]]:
    """List all coins with market data."""
    with _get_client() as client:
        for page in range(1, max_pages + 1):
            try:
                response = client.get(
                    "/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": per_page,
                        "page": page,
                        "sparkline": False,
                        "price_change_percentage": "1h,24h,7d,30d",
                    },
                )
                response.raise_for_status()
                coins = response.json()

                if not coins:
                    break

                for coin in coins:
                    yield {
                        "id": coin.get("id"),
                        "symbol": coin.get("symbol"),
                        "name": coin.get("name"),
                        "image": coin.get("image"),
                        "current_price": coin.get("current_price"),
                        "market_cap": coin.get("market_cap"),
                        "market_cap_rank": coin.get("market_cap_rank"),
                        "fully_diluted_valuation": coin.get("fully_diluted_valuation"),
                        "total_volume": coin.get("total_volume"),
                        "high_24h": coin.get("high_24h"),
                        "low_24h": coin.get("low_24h"),
                        "price_change_24h": coin.get("price_change_24h"),
                        "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
                        "price_change_percentage_1h": coin.get("price_change_percentage_1h_in_currency"),
                        "price_change_percentage_7d": coin.get("price_change_percentage_7d_in_currency"),
                        "price_change_percentage_30d": coin.get("price_change_percentage_30d_in_currency"),
                        "market_cap_change_24h": coin.get("market_cap_change_24h"),
                        "market_cap_change_percentage_24h": coin.get("market_cap_change_percentage_24h"),
                        "circulating_supply": coin.get("circulating_supply"),
                        "total_supply": coin.get("total_supply"),
                        "max_supply": coin.get("max_supply"),
                        "ath": coin.get("ath"),
                        "ath_change_percentage": coin.get("ath_change_percentage"),
                        "ath_date": coin.get("ath_date"),
                        "atl": coin.get("atl"),
                        "atl_change_percentage": coin.get("atl_change_percentage"),
                        "atl_date": coin.get("atl_date"),
                        "last_updated": coin.get("last_updated"),
                        "status": "success",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }

            except Exception as e:
                # Log error but don't yield - errors shouldn't go to the coins table
                import logging
                logging.warning(f"CoinGecko API error on page {page}: {e}")
                break


def _get_coin_details(coin_id: str) -> dict[str, Any]:
    """Get detailed coin information."""
    with _get_client() as client:
        try:
            response = client.get(
                f"/coins/{coin_id}",
                params={
                    "localization": False,
                    "tickers": False,
                    "market_data": True,
                    "community_data": True,
                    "developer_data": True,
                    "sparkline": False,
                },
            )
            response.raise_for_status()
            data = response.json()

            market_data = data.get("market_data", {})

            return {
                "id": data.get("id"),
                "symbol": data.get("symbol"),
                "name": data.get("name"),
                "description": data.get("description", {}).get("en"),
                "categories": data.get("categories", []),
                "platforms": data.get("platforms", {}),
                "links_homepage": data.get("links", {}).get("homepage", []),
                "links_blockchain_site": data.get("links", {}).get("blockchain_site", []),
                "links_repos_github": data.get("links", {}).get("repos_url", {}).get("github", []),
                "links_twitter": data.get("links", {}).get("twitter_screen_name"),
                "links_telegram": data.get("links", {}).get("telegram_channel_identifier"),
                "genesis_date": data.get("genesis_date"),
                "sentiment_votes_up": data.get("sentiment_votes_up_percentage"),
                "sentiment_votes_down": data.get("sentiment_votes_down_percentage"),
                "watchlist_portfolio_users": data.get("watchlist_portfolio_users"),
                "market_cap_rank": data.get("market_cap_rank"),
                "coingecko_rank": data.get("coingecko_rank"),
                "coingecko_score": data.get("coingecko_score"),
                "developer_score": data.get("developer_score"),
                "community_score": data.get("community_score"),
                "liquidity_score": data.get("liquidity_score"),
                "public_interest_score": data.get("public_interest_score"),
                # Community data
                "twitter_followers": data.get("community_data", {}).get("twitter_followers"),
                "reddit_subscribers": data.get("community_data", {}).get("reddit_subscribers"),
                "telegram_members": data.get("community_data", {}).get("telegram_channel_user_count"),
                # Developer data
                "github_forks": data.get("developer_data", {}).get("forks"),
                "github_stars": data.get("developer_data", {}).get("stars"),
                "github_subscribers": data.get("developer_data", {}).get("subscribers"),
                "github_total_issues": data.get("developer_data", {}).get("total_issues"),
                "github_closed_issues": data.get("developer_data", {}).get("closed_issues"),
                "github_pull_requests_merged": data.get("developer_data", {}).get("pull_requests_merged"),
                "github_commit_count_4_weeks": data.get("developer_data", {}).get("commit_count_4_weeks"),
                "last_updated": data.get("last_updated"),
                "status": "success",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {
                "id": coin_id,
                "error": str(e),
                "status": "error",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }


def _get_price_history(
    coin_id: str,
    days: int = 365,
) -> Iterator[dict[str, Any]]:
    """Get historical price data for a coin."""
    with _get_client() as client:
        try:
            response = client.get(
                f"/coins/{coin_id}/market_chart",
                params={
                    "vs_currency": "usd",
                    "days": days,
                    "interval": "daily",
                },
            )
            response.raise_for_status()
            data = response.json()

            prices = data.get("prices", [])
            market_caps = data.get("market_caps", [])
            total_volumes = data.get("total_volumes", [])

            for i, (timestamp, price) in enumerate(prices):
                yield {
                    "coin_id": coin_id,
                    "timestamp": timestamp,
                    "date": datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc).date().isoformat(),
                    "price": price,
                    "market_cap": market_caps[i][1] if i < len(market_caps) else None,
                    "total_volume": total_volumes[i][1] if i < len(total_volumes) else None,
                    "status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            # Log error but don't yield - errors shouldn't go to the price_history table
            import logging
            logging.warning(f"CoinGecko price history error for {coin_id}: {e}")


def _list_exchanges() -> Iterator[dict[str, Any]]:
    """List top exchanges by volume."""
    with _get_client() as client:
        try:
            response = client.get(
                "/exchanges",
                params={"per_page": 100},
            )
            response.raise_for_status()
            exchanges = response.json()

            for exchange in exchanges:
                yield {
                    "id": exchange.get("id"),
                    "name": exchange.get("name"),
                    "year_established": exchange.get("year_established"),
                    "country": exchange.get("country"),
                    "description": exchange.get("description"),
                    "url": exchange.get("url"),
                    "image": exchange.get("image"),
                    "has_trading_incentive": exchange.get("has_trading_incentive"),
                    "trust_score": exchange.get("trust_score"),
                    "trust_score_rank": exchange.get("trust_score_rank"),
                    "trade_volume_24h_btc": exchange.get("trade_volume_24h_btc"),
                    "trade_volume_24h_btc_normalized": exchange.get("trade_volume_24h_btc_normalized"),
                    "status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            # Log error but don't yield - errors shouldn't go to the exchanges table
            import logging
            logging.warning(f"CoinGecko exchanges API error: {e}")


def _get_trending() -> Iterator[dict[str, Any]]:
    """Get trending coins and NFTs."""
    with _get_client() as client:
        try:
            response = client.get("/search/trending")
            response.raise_for_status()
            data = response.json()

            for item in data.get("coins", []):
                coin = item.get("item", {})
                yield {
                    "type": "coin",
                    "id": coin.get("id"),
                    "coin_id": coin.get("coin_id"),
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "thumb": coin.get("thumb"),
                    "slug": coin.get("slug"),
                    "price_btc": coin.get("price_btc"),
                    "score": coin.get("score"),
                    "status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

            for nft in data.get("nfts", []):
                yield {
                    "type": "nft",
                    "id": nft.get("id"),
                    "name": nft.get("name"),
                    "symbol": nft.get("symbol"),
                    "thumb": nft.get("thumb"),
                    "native_currency_symbol": nft.get("native_currency_symbol"),
                    "floor_price_in_native_currency": nft.get("floor_price_in_native_currency"),
                    "floor_price_24h_percentage_change": nft.get("floor_price_24h_percentage_change"),
                    "status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            # Log error but don't yield - errors shouldn't go to the trending table
            import logging
            logging.warning(f"CoinGecko trending API error: {e}")


@dlt.source(name="coingecko")
def coingecko_source(
    include_coins: bool = True,
    include_exchanges: bool = True,
    include_trending: bool = True,
    coin_ids: list[str] | None = None,
    price_history_days: int = 365,
    max_pages: int = 4,
):
    """
    DLT source for CoinGecko data.

    Args:
        include_coins: Include market data for top coins
        include_exchanges: Include exchange data
        include_trending: Include trending coins/NFTs
        coin_ids: List of coin IDs for detailed data and price history
        price_history_days: Days of price history to fetch
        max_pages: Maximum pages for coin listings

    Returns:
        DLT source with coins, exchanges, trending, coin_details, price_history resources
    """

    @dlt.resource(
        name="coins",
        write_disposition="merge",
        primary_key=["id"],
    )
    def coins():
        """Top coins by market cap."""
        if not include_coins:
            return
        yield from _list_coins(max_pages=max_pages)

    @dlt.resource(
        name="exchanges",
        write_disposition="merge",
        primary_key=["id"],
    )
    def exchanges():
        """Top exchanges by volume."""
        if not include_exchanges:
            return
        yield from _list_exchanges()

    @dlt.resource(
        name="trending",
        write_disposition="replace",
        primary_key=["type", "id"],
    )
    def trending():
        """Trending coins and NFTs."""
        if not include_trending:
            return
        yield from _get_trending()

    @dlt.resource(
        name="coin_details",
        write_disposition="merge",
        primary_key=["id"],
    )
    def coin_details():
        """Detailed coin information."""
        if not coin_ids:
            return
        for coin_id in coin_ids:
            yield _get_coin_details(coin_id)

    @dlt.resource(
        name="price_history",
        write_disposition="merge",
        primary_key=["coin_id", "date"],
    )
    def price_history():
        """Historical price data."""
        if not coin_ids:
            return
        for coin_id in coin_ids:
            yield from _get_price_history(coin_id, days=price_history_days)

    return coins, exchanges, trending, coin_details, price_history
