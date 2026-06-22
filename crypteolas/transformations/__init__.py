"""
Ibis-based transformations for cryptocurrency analytics.

Provides analytical functions for:
- Funding rate analysis (Ethena basis trade)
- Yield spread calculations
- Protocol health metrics
- Stablecoin supply tracking
"""

from .crypto_analytics import (
    get_connection,
    # Funding Rate Analytics
    calculate_funding_metrics,
    funding_rate_timeseries,
    multi_exchange_funding_comparison,
    # Yield Analysis
    calculate_yield_spreads,
    build_yield_comparison_view,
    calculate_pendle_yields,
    # Protocol Health
    calculate_protocol_health,
    # Stablecoin Metrics
    calculate_stablecoin_metrics,
    # Summary
    defi_ecosystem_summary,
    create_analytics_views,
)

__all__ = [
    "get_connection",
    # Funding
    "calculate_funding_metrics",
    "funding_rate_timeseries",
    "multi_exchange_funding_comparison",
    # Yields
    "calculate_yield_spreads",
    "build_yield_comparison_view",
    "calculate_pendle_yields",
    # Protocol Health
    "calculate_protocol_health",
    # Stablecoins
    "calculate_stablecoin_metrics",
    # Summary
    "defi_ecosystem_summary",
    "create_analytics_views",
]
