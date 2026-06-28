"""
DeFi Analytics Service for Crypteolas.

Provides DeFi metrics and analytics from DuckDB.
"""

from pathlib import Path
from typing import Any

import duckdb


class DefiAnalyticsService:
    """Service for DeFi analytics queries."""

    def __init__(self, db_path: str):
        """Initialize DuckDB connection."""
        self.db_path = db_path
        self._conn = None

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get or create connection."""
        if self._conn is None:
            self._conn = duckdb.connect(self.db_path)
        return self._conn

    def close(self):
        """Close connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    async def get_protocol_tvl(
        self,
        protocol: str,
        chain: str | None = None,
    ) -> dict:
        """Get TVL for a protocol."""
        try:
            if chain:
                result = self.conn.execute(
                    """
                    SELECT tvl_usd, chain, last_updated
                    FROM defi.protocol_tvl
                    WHERE protocol = ? AND chain = ?
                    ORDER BY last_updated DESC
                    LIMIT 1
                    """,
                    [protocol, chain],
                ).fetchone()
            else:
                result = self.conn.execute(
                    """
                    SELECT SUM(tvl_usd) as total_tvl, MAX(last_updated) as last_updated
                    FROM defi.protocol_tvl
                    WHERE protocol = ?
                    """,
                    [protocol],
                ).fetchone()

            if result:
                return {
                    "protocol": protocol,
                    "tvl_usd": result[0],
                    "chain": chain,
                    "last_updated": str(result[-1]) if result[-1] else None,
                }
            return {"protocol": protocol, "tvl_usd": None, "chain": chain}
        except Exception:
            return {"protocol": protocol, "tvl_usd": None, "chain": chain}

    async def get_protocol_yields(
        self,
        protocol: str,
        min_apy: float = 0,
        limit: int = 20,
    ) -> list[dict]:
        """Get yield opportunities for a protocol."""
        try:
            results = self.conn.execute(
                """
                SELECT pool_name, chain, tvl_usd, apy, tokens, reward_tokens
                FROM defi.yields
                WHERE protocol = ? AND apy >= ?
                ORDER BY apy DESC
                LIMIT ?
                """,
                [protocol, min_apy, limit],
            ).fetchall()

            return [
                {
                    "pool_name": r[0],
                    "chain": r[1],
                    "tvl_usd": r[2],
                    "apy": r[3],
                    "tokens": r[4],
                    "reward_tokens": r[5],
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_token_price(
        self,
        symbol: str,
        include_history: bool = False,
    ) -> dict:
        """Get token price and market data."""
        try:
            result = self.conn.execute(
                """
                SELECT price_usd, market_cap, volume_24h, price_change_24h, last_updated
                FROM defi.token_prices
                WHERE symbol = ?
                ORDER BY last_updated DESC
                LIMIT 1
                """,
                [symbol.upper()],
            ).fetchone()

            if result:
                data = {
                    "symbol": symbol.upper(),
                    "price_usd": result[0],
                    "market_cap": result[1],
                    "volume_24h": result[2],
                    "price_change_24h": result[3],
                    "last_updated": str(result[4]) if result[4] else None,
                }

                if include_history:
                    history = self.conn.execute(
                        """
                        SELECT price_usd, timestamp
                        FROM defi.token_price_history
                        WHERE symbol = ?
                        ORDER BY timestamp DESC
                        LIMIT 30
                        """,
                        [symbol.upper()],
                    ).fetchall()
                    data["history"] = [{"price": h[0], "timestamp": str(h[1])} for h in history]

                return data
            return {"symbol": symbol.upper(), "price_usd": None}
        except Exception:
            return {"symbol": symbol.upper(), "price_usd": None}

    async def get_funding_rates(
        self,
        symbol: str | None = None,
        exchange: str = "binance",
        limit: int = 20,
    ) -> list[dict]:
        """Get perpetual funding rates."""
        try:
            if symbol:
                results = self.conn.execute(
                    """
                    SELECT symbol, funding_rate, next_funding_time, open_interest_usd
                    FROM defi.funding_rates
                    WHERE exchange = ? AND symbol = ?
                    ORDER BY ABS(funding_rate) DESC
                    """,
                    [exchange, symbol.upper()],
                ).fetchall()
            else:
                results = self.conn.execute(
                    """
                    SELECT symbol, funding_rate, next_funding_time, open_interest_usd
                    FROM defi.funding_rates
                    WHERE exchange = ?
                    ORDER BY ABS(funding_rate) DESC
                    LIMIT ?
                    """,
                    [exchange, limit],
                ).fetchall()

            return [
                {
                    "symbol": r[0],
                    "funding_rate": r[1],
                    "next_funding_time": str(r[2]) if r[2] else None,
                    "open_interest_usd": r[3],
                    "annualized_rate": r[1] * 3 * 365 * 100 if r[1] else None,
                }
                for r in results
            ]
        except Exception:
            return []

    async def compare_protocols(
        self,
        protocols: list[str],
    ) -> list[dict]:
        """Compare multiple protocols."""
        try:
            placeholders = ",".join(["?"] * len(protocols))
            results = self.conn.execute(
                f"""
                SELECT protocol, SUM(tvl_usd) as total_tvl,
                       COUNT(DISTINCT chain) as chains,
                       MAX(last_updated) as last_updated
                FROM defi.protocol_tvl
                WHERE protocol IN ({placeholders})
                GROUP BY protocol
                ORDER BY total_tvl DESC
                """,
                protocols,
            ).fetchall()

            return [
                {
                    "protocol": r[0],
                    "tvl_usd": r[1],
                    "chains": r[2],
                    "last_updated": str(r[3]) if r[3] else None,
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_top_protocols(
        self,
        category: str | None = None,
        chain: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get top protocols by TVL."""
        try:
            query = """
                SELECT protocol, SUM(tvl_usd) as total_tvl,
                       COUNT(DISTINCT chain) as chains
                FROM defi.protocol_tvl
                WHERE 1=1
            """
            params = []

            if chain:
                query += " AND chain = ?"
                params.append(chain)

            query += " GROUP BY protocol ORDER BY total_tvl DESC LIMIT ?"
            params.append(limit)

            results = self.conn.execute(query, params).fetchall()

            return [
                {
                    "protocol": r[0],
                    "tvl_usd": r[1],
                    "chains": r[2],
                }
                for r in results
            ]
        except Exception:
            return []

    def list_supported_protocols(self) -> list[str]:
        """List all indexed protocols."""
        try:
            result = self.conn.execute(
                "SELECT DISTINCT protocol FROM defi.protocol_tvl ORDER BY protocol"
            ).fetchall()
            return [r[0] for r in result]
        except Exception:
            return []

    def list_supported_chains(self) -> list[str]:
        """List all supported chains."""
        try:
            result = self.conn.execute(
                "SELECT DISTINCT chain FROM defi.protocol_tvl ORDER BY chain"
            ).fetchall()
            return [r[0] for r in result]
        except Exception:
            return []
