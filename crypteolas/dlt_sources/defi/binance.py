"""
DLT source for Binance API - Funding rates, open interest, market data.

API Reference: https://binance-docs.github.io/apidocs/

Provides access to:
- Perpetual futures funding rates
- Open interest data
- Spot and futures market data
- Order book depth
"""

from datetime import datetime, timezone
from typing import Any, Iterator

import dlt
import httpx

# Binance API base URLs
BINANCE_SPOT_URL = "https://api.binance.com/api/v3"
BINANCE_FUTURES_URL = "https://fapi.binance.com/fapi/v1"


def _get_spot_client() -> httpx.Client:
    """Get HTTP client for Binance Spot API."""
    return httpx.Client(base_url=BINANCE_SPOT_URL, timeout=30.0)


def _get_futures_client() -> httpx.Client:
    """Get HTTP client for Binance Futures API."""
    return httpx.Client(base_url=BINANCE_FUTURES_URL, timeout=30.0)


def _list_exchange_info() -> Iterator[dict[str, Any]]:
    """List spot exchange trading pairs and rules."""
    with _get_spot_client() as client:
        try:
            response = client.get("/exchangeInfo")
            response.raise_for_status()
            data = response.json()

            for symbol in data.get("symbols", []):
                yield {
                    "symbol": symbol.get("symbol"),
                    "status": symbol.get("status"),
                    "base_asset": symbol.get("baseAsset"),
                    "base_precision": symbol.get("baseAssetPrecision"),
                    "quote_asset": symbol.get("quoteAsset"),
                    "quote_precision": symbol.get("quoteAssetPrecision"),
                    "order_types": symbol.get("orderTypes"),
                    "iceberg_allowed": symbol.get("icebergAllowed"),
                    "oco_allowed": symbol.get("ocoAllowed"),
                    "quote_order_qty_market_allowed": symbol.get("quoteOrderQtyMarketAllowed"),
                    "is_spot_trading_allowed": symbol.get("isSpotTradingAllowed"),
                    "is_margin_trading_allowed": symbol.get("isMarginTradingAllowed"),
                    "permissions": symbol.get("permissions", []),
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging
            logging.warning(f"Binance spot exchange info API error: {e}")


def _list_24h_tickers() -> Iterator[dict[str, Any]]:
    """List 24h price change statistics for all symbols."""
    with _get_spot_client() as client:
        try:
            response = client.get("/ticker/24hr")
            response.raise_for_status()
            tickers = response.json()

            for ticker in tickers:
                yield {
                    "symbol": ticker.get("symbol"),
                    "price_change": float(ticker.get("priceChange", 0)),
                    "price_change_percent": float(ticker.get("priceChangePercent", 0)),
                    "weighted_avg_price": float(ticker.get("weightedAvgPrice", 0)),
                    "prev_close_price": float(ticker.get("prevClosePrice", 0)),
                    "last_price": float(ticker.get("lastPrice", 0)),
                    "last_qty": float(ticker.get("lastQty", 0)),
                    "bid_price": float(ticker.get("bidPrice", 0)),
                    "bid_qty": float(ticker.get("bidQty", 0)),
                    "ask_price": float(ticker.get("askPrice", 0)),
                    "ask_qty": float(ticker.get("askQty", 0)),
                    "open_price": float(ticker.get("openPrice", 0)),
                    "high_price": float(ticker.get("highPrice", 0)),
                    "low_price": float(ticker.get("lowPrice", 0)),
                    "volume": float(ticker.get("volume", 0)),
                    "quote_volume": float(ticker.get("quoteVolume", 0)),
                    "open_time": ticker.get("openTime"),
                    "close_time": ticker.get("closeTime"),
                    "trade_count": ticker.get("count"),
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging
            logging.warning(f"Binance 24h tickers API error: {e}")


def _list_futures_exchange_info() -> Iterator[dict[str, Any]]:
    """List futures exchange trading pairs and rules."""
    with _get_futures_client() as client:
        try:
            response = client.get("/exchangeInfo")
            response.raise_for_status()
            data = response.json()

            for symbol in data.get("symbols", []):
                yield {
                    "symbol": symbol.get("symbol"),
                    "pair": symbol.get("pair"),
                    "contract_type": symbol.get("contractType"),
                    "delivery_date": symbol.get("deliveryDate"),
                    "onboard_date": symbol.get("onboardDate"),
                    "status": symbol.get("status"),
                    "maint_margin_percent": float(symbol.get("maintMarginPercent", 0)),
                    "required_margin_percent": float(symbol.get("requiredMarginPercent", 0)),
                    "base_asset": symbol.get("baseAsset"),
                    "quote_asset": symbol.get("quoteAsset"),
                    "margin_asset": symbol.get("marginAsset"),
                    "price_precision": symbol.get("pricePrecision"),
                    "quantity_precision": symbol.get("quantityPrecision"),
                    "base_precision": symbol.get("baseAssetPrecision"),
                    "quote_precision": symbol.get("quotePrecision"),
                    "underlying_type": symbol.get("underlyingType"),
                    "underlying_sub_type": symbol.get("underlyingSubType", []),
                    "settle_plan": symbol.get("settlePlan"),
                    "trigger_protect": float(symbol.get("triggerProtect", 0)),
                    "liquidation_fee": float(symbol.get("liquidationFee", 0)),
                    "market_take_bound": float(symbol.get("marketTakeBound", 0)),
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging
            logging.warning(f"Binance futures exchange info API error: {e}")


def _list_funding_rates(symbols: list[str] | None = None) -> Iterator[dict[str, Any]]:
    """List current funding rates for perpetual futures."""
    with _get_futures_client() as client:
        try:
            response = client.get("/premiumIndex")
            response.raise_for_status()
            data = response.json()

            for item in data:
                symbol = item.get("symbol")
                if symbols and symbol not in symbols:
                    continue

                yield {
                    "symbol": symbol,
                    "mark_price": float(item.get("markPrice", 0)),
                    "index_price": float(item.get("indexPrice", 0)),
                    "estimated_settle_price": float(item.get("estimatedSettlePrice", 0)),
                    "last_funding_rate": float(item.get("lastFundingRate", 0)),
                    "next_funding_time": item.get("nextFundingTime"),
                    "interest_rate": float(item.get("interestRate", 0)),
                    "time": item.get("time"),
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging
            logging.warning(f"Binance funding rates API error: {e}")


def _list_funding_rate_history(
    symbol: str,
    limit: int = 100,
) -> Iterator[dict[str, Any]]:
    """Get historical funding rates for a symbol."""
    with _get_futures_client() as client:
        try:
            response = client.get(
                "/fundingRate",
                params={"symbol": symbol, "limit": limit},
            )
            response.raise_for_status()
            data = response.json()

            for item in data:
                yield {
                    "symbol": item.get("symbol"),
                    "funding_rate": float(item.get("fundingRate", 0)),
                    "funding_time": item.get("fundingTime"),
                    "mark_price": float(item.get("markPrice", 0)) if item.get("markPrice") else None,
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging
            logging.warning(f"Binance funding rate history API error for {symbol}: {e}")


def _list_open_interest(symbols: list[str] | None = None) -> Iterator[dict[str, Any]]:
    """List open interest for futures symbols."""
    with _get_futures_client() as client:
        try:
            response = client.get("/openInterest")
            response.raise_for_status()
            data = response.json()

            # This endpoint returns single symbol, so we need to iterate
            if isinstance(data, dict):
                data = [data]

            for item in data:
                symbol = item.get("symbol")
                if symbols and symbol not in symbols:
                    continue

                yield {
                    "symbol": symbol,
                    "open_interest": float(item.get("openInterest", 0)),
                    "time": item.get("time"),
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging
            logging.warning(f"Binance open interest API error: {e}")


def _list_long_short_ratio(
    symbol: str,
    period: str = "5m",
    limit: int = 30,
) -> Iterator[dict[str, Any]]:
    """Get top trader long/short ratio for a symbol."""
    with _get_futures_client() as client:
        try:
            response = client.get(
                "/topLongShortPositionRatio",
                params={"symbol": symbol, "period": period, "limit": limit},
            )
            response.raise_for_status()
            data = response.json()

            for item in data:
                yield {
                    "symbol": symbol,
                    "long_short_ratio": float(item.get("longShortRatio", 0)),
                    "long_account": float(item.get("longAccount", 0)),
                    "short_account": float(item.get("shortAccount", 0)),
                    "timestamp": item.get("timestamp"),
                    "period": period,
                    "data_status": "success",
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            import logging
            logging.warning(f"Binance long/short ratio API error for {symbol}: {e}")


@dlt.source(name="binance")
def binance_source(
    include_spot: bool = True,
    include_futures: bool = True,
    symbols: list[str] | None = None,
    funding_history_symbols: list[str] | None = None,
    long_short_symbols: list[str] | None = None,
):
    """
    DLT source for Binance data.

    Args:
        include_spot: Include spot market data
        include_futures: Include futures market data
        symbols: Filter to specific symbols for funding/OI data
        funding_history_symbols: Symbols for historical funding rates
        long_short_symbols: Symbols for long/short ratio data

    Returns:
        DLT source with spot, futures, funding, open_interest resources
    """

    @dlt.resource(
        name="spot_exchange_info",
        write_disposition="replace",
        primary_key=["symbol"],
    )
    def spot_exchange_info():
        """Spot trading pairs and rules."""
        if not include_spot:
            return
        yield from _list_exchange_info()

    @dlt.resource(
        name="spot_24h_tickers",
        write_disposition="replace",
        primary_key=["symbol"],
    )
    def spot_24h_tickers():
        """Spot 24h price statistics."""
        if not include_spot:
            return
        yield from _list_24h_tickers()

    @dlt.resource(
        name="futures_exchange_info",
        write_disposition="replace",
        primary_key=["symbol"],
    )
    def futures_exchange_info():
        """Futures trading pairs and rules."""
        if not include_futures:
            return
        yield from _list_futures_exchange_info()

    @dlt.resource(
        name="funding_rates",
        write_disposition="replace",
        primary_key=["symbol"],
    )
    def funding_rates():
        """Current perpetual funding rates."""
        if not include_futures:
            return
        yield from _list_funding_rates(symbols)

    @dlt.resource(
        name="funding_rate_history",
        write_disposition="merge",
        primary_key=["symbol", "funding_time"],
    )
    def funding_rate_history():
        """Historical funding rates."""
        if not funding_history_symbols:
            return
        for symbol in funding_history_symbols:
            yield from _list_funding_rate_history(symbol)

    @dlt.resource(
        name="long_short_ratio",
        write_disposition="merge",
        primary_key=["symbol", "timestamp"],
    )
    def long_short_ratio():
        """Top trader long/short ratio."""
        if not long_short_symbols:
            return
        for symbol in long_short_symbols:
            yield from _list_long_short_ratio(symbol)

    return (
        spot_exchange_info,
        spot_24h_tickers,
        futures_exchange_info,
        funding_rates,
        funding_rate_history,
        long_short_ratio,
    )
