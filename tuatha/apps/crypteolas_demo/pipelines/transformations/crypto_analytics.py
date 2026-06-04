"""
Ibis-based transformations for cryptocurrency analytics.

Provides analytical functions for:
- Funding rate analysis (Ethena basis trade)
- Yield spread calculations
- Protocol health metrics
- Stablecoin supply tracking
"""

from datetime import datetime, timedelta
from typing import Any, Optional

import ibis
from ibis import _


def get_connection(db_path: str = "data/crypto_analytics.duckdb") -> ibis.BaseBackend:
    """Get DuckDB connection via Ibis."""
    return ibis.duckdb.connect(db_path)


# =============================================================================
# Funding Rate Analytics (Critical for Ethena)
# =============================================================================


def calculate_funding_metrics(
    con: ibis.BaseBackend,
    table_name: str = "binance_funding_rates",
    symbol: str = "ETHUSDT",
    lookback_days: int = 30,
) -> ibis.Table:
    """
    Calculate funding rate metrics for basis trade analysis.

    This is critical for understanding Ethena's yield generation mechanism.
    Funding rates are paid every 8 hours (3x daily).

    Args:
        con: Ibis connection
        table_name: Source table name
        symbol: Trading pair symbol
        lookback_days: Analysis window

    Returns:
        Table with funding metrics including annualized APR
    """
    cutoff = datetime.utcnow() - timedelta(days=lookback_days)

    funding = con.table(table_name)

    # Filter to symbol and time range
    filtered = funding.filter(
        (funding.symbol == symbol) & (funding.fundingTime >= cutoff)
    )

    # Calculate metrics
    metrics = filtered.group_by([]).aggregate(
        avg_funding_rate=_.fundingRate.mean(),
        median_funding_rate=_.fundingRate.approx_median(),
        min_funding_rate=_.fundingRate.min(),
        max_funding_rate=_.fundingRate.max(),
        std_funding_rate=_.fundingRate.std(),
        positive_rate_pct=(_.fundingRate > 0).mean() * 100,
        negative_rate_pct=(_.fundingRate < 0).mean() * 100,
        count=_.fundingRate.count(),
    )

    # Calculate annualized APR (8-hour rate * 3 * 365)
    # Funding is paid 3 times per day
    metrics = metrics.mutate(
        annualized_apr_avg=metrics.avg_funding_rate * 3 * 365 * 100,
        annualized_apr_median=metrics.median_funding_rate * 3 * 365 * 100,
    )

    return metrics


def funding_rate_timeseries(
    con: ibis.BaseBackend,
    table_name: str = "binance_funding_rates",
    symbols: Optional[list[str]] = None,
    resample: str = "1D",
) -> ibis.Table:
    """
    Create funding rate time series for visualization.

    Args:
        con: Ibis connection
        table_name: Source table
        symbols: Filter symbols
        resample: Resampling period

    Returns:
        Resampled funding rate data
    """
    funding = con.table(table_name)

    if symbols:
        funding = funding.filter(funding.symbol.isin(symbols))

    # Truncate to day for daily aggregation
    with_date = funding.mutate(date=_.fundingTime.date())

    # Aggregate by date and symbol
    daily = with_date.group_by([_.date, _.symbol]).aggregate(
        avg_rate=_.fundingRate.mean(),
        sum_rate=_.fundingRate.sum(),
        count=_.fundingRate.count(),
        # Annualized (3 funding periods per day)
        daily_annualized_apr=_.fundingRate.sum() * 365 * 100,
    )

    return daily.order_by([_.date.desc(), _.symbol])


# =============================================================================
# Yield Spread Analysis
# =============================================================================


def calculate_yield_spreads(
    con: ibis.BaseBackend,
    yields_table: str = "defillama_yields",
    stablecoin_only: bool = True,
    min_tvl: float = 1_000_000,
) -> ibis.Table:
    """
    Calculate yield spreads across protocols and pools.

    Args:
        con: Ibis connection
        yields_table: Source table
        stablecoin_only: Filter to stablecoin pools
        min_tvl: Minimum TVL filter

    Returns:
        Table with yield comparisons
    """
    yields = con.table(yields_table)

    # Apply filters
    filtered = yields.filter(yields.tvl_usd >= min_tvl)

    if stablecoin_only:
        filtered = filtered.filter(yields.stablecoin == True)  # noqa: E712

    # Calculate spreads from base rate
    # Using Aave USDC as reference (approximately risk-free DeFi rate)
    with_spreads = filtered.mutate(
        total_apy=ibis.coalesce(_.apy_base, 0) + ibis.coalesce(_.apy_reward, 0),
    )

    # Rank by APY within chain
    ranked = with_spreads.mutate(
        apy_rank=ibis.row_number().over(
            ibis.window(group_by=[_.chain], order_by=[_.apy.desc()])
        )
    )

    return ranked.order_by([_.apy.desc()])


def build_yield_comparison_view(
    con: ibis.BaseBackend,
    yields_table: str = "defillama_yields",
    protocols: Optional[list[str]] = None,
) -> ibis.Table:
    """
    Build yield comparison across Ethena ecosystem protocols.

    Args:
        con: Ibis connection
        yields_table: Source table
        protocols: Filter protocols

    Returns:
        Comparative yield table
    """
    if protocols is None:
        protocols = ["ethena", "aave-v3", "pendle", "curve-dex", "lido"]

    yields = con.table(yields_table)

    filtered = yields.filter(yields.project.isin(protocols))

    # Aggregate by protocol
    by_protocol = filtered.group_by([_.project]).aggregate(
        pool_count=_.pool.count(),
        total_tvl=_.tvl_usd.sum(),
        avg_apy=_.apy.mean(),
        max_apy=_.apy.max(),
        min_apy=_.apy.min(),
        weighted_avg_apy=(_.apy * _.tvl_usd).sum() / _.tvl_usd.sum(),
    )

    return by_protocol.order_by([_.weighted_avg_apy.desc()])


# =============================================================================
# Protocol Health Metrics
# =============================================================================


def calculate_protocol_health(
    con: ibis.BaseBackend,
    reserves_table: str = "aave_reserves",
    positions_table: str = "aave_user_positions",
) -> dict[str, ibis.Table]:
    """
    Calculate Aave protocol health metrics.

    Args:
        con: Ibis connection
        reserves_table: Reserves data table
        positions_table: User positions table

    Returns:
        Dict of health metric tables
    """
    reserves = con.table(reserves_table)
    positions = con.table(positions_table)

    # Reserve utilization analysis
    utilization = reserves.select(
        symbol=_.symbol,
        utilization_rate=_.utilizationRate,
        supply_apr=_.supplyAPR * 100,
        borrow_apr=_.borrowAPR * 100,
        total_supply=_.totalSupply,
        total_debt=_.totalVariableDebt,
        available_liquidity=_.availableLiquidity,
        ltv=_.ltv * 100,
        liquidation_threshold=_.liquidationThreshold * 100,
    ).order_by([_.utilization_rate.desc()])

    # Liquidation risk analysis
    at_risk = positions.filter(
        (positions.healthFactor.notnull()) & (positions.healthFactor < 1.5)
    )

    liquidation_risk = at_risk.group_by([_.reserve]).aggregate(
        at_risk_positions=_.user.count(),
        total_collateral_at_risk=_.totalCollateralUSD.sum(),
        total_debt_at_risk=_.totalDebtUSD.sum(),
        avg_health_factor=_.healthFactor.mean(),
        min_health_factor=_.healthFactor.min(),
    ).order_by([_.min_health_factor.asc()])

    return {
        "utilization": utilization,
        "liquidation_risk": liquidation_risk,
    }


# =============================================================================
# Stablecoin Metrics
# =============================================================================


def calculate_stablecoin_metrics(
    con: ibis.BaseBackend,
    stablecoins_table: str = "defillama_stablecoins",
    history_table: str = "defillama_stablecoin_history",
    symbols: Optional[list[str]] = None,
) -> dict[str, ibis.Table]:
    """
    Calculate stablecoin supply and peg metrics.

    Args:
        con: Ibis connection
        stablecoins_table: Current stablecoin data
        history_table: Historical supply data
        symbols: Filter symbols

    Returns:
        Dict of stablecoin metric tables
    """
    if symbols is None:
        symbols = ["USDe", "USDC", "USDT", "DAI"]

    stablecoins = con.table(stablecoins_table)

    filtered = stablecoins.filter(stablecoins.symbol.isin(symbols))

    # Current supply comparison
    supply_comparison = filtered.select(
        symbol=_.symbol,
        name=_.name,
        circulating=_.circulating,
        price=_.price,
        peg_deviation=(_.price - 1.0).abs() * 100,  # Deviation from $1 peg
        peg_type=_.peg_type,
        peg_mechanism=_.peg_mechanism,
    ).order_by([_.circulating.desc()])

    # Market share
    total_supply = filtered.aggregate(total=_.circulating.sum())

    market_share = filtered.mutate(
        market_share_pct=_.circulating / total_supply.total * 100
    ).select(
        symbol=_.symbol,
        circulating=_.circulating,
        market_share_pct=_.market_share_pct,
    )

    return {
        "supply_comparison": supply_comparison,
        "market_share": market_share,
    }


# =============================================================================
# Pendle Yield Analysis
# =============================================================================


def calculate_pendle_yields(
    con: ibis.BaseBackend,
    markets_table: str = "pendle_markets",
    min_tvl: float = 100_000,
) -> ibis.Table:
    """
    Calculate Pendle fixed yield opportunities.

    PT (Principal Token) provides fixed yield locked until maturity.
    This is relevant for Ethena users seeking yield certainty.

    Args:
        con: Ibis connection
        markets_table: Pendle markets table
        min_tvl: Minimum TVL filter

    Returns:
        Table with Pendle yield analysis
    """
    markets = con.table(markets_table)

    # Filter active markets with liquidity
    active = markets.filter(
        (markets.daysToMaturity > 0) & (markets.tvlUSD >= min_tvl)
    )

    # Calculate yield metrics
    yields = active.select(
        market_id=_.id,
        pt_symbol=_.ptSymbol,
        sy_symbol=_.sySymbol,
        expiry=_.expiry,
        days_to_maturity=_.daysToMaturity,
        # Fixed yield from PT
        implied_fixed_apy=_.impliedAPY * 100,
        # Underlying floating yield
        underlying_apy=_.underlyingAPY * 100,
        # Spread (fixed - floating)
        yield_spread=(_.impliedAPY - _.underlyingAPY) * 100,
        # Liquidity
        tvl_usd=_.tvlUSD,
        volume_usd=_.volumeUSD,
        # Prices
        pt_price=_.ptPriceUSD,
        yt_price=_.ytPriceUSD,
    ).order_by([_.implied_fixed_apy.desc()])

    return yields


# =============================================================================
# Cross-Protocol Analysis
# =============================================================================


def ethena_ecosystem_summary(
    con: ibis.BaseBackend,
) -> dict[str, Any]:
    """
    Generate Ethena ecosystem summary across all data sources.

    Returns:
        Summary metrics for dashboard display
    """
    summary = {}

    # Funding rate summary
    try:
        funding_metrics = calculate_funding_metrics(con)
        summary["funding"] = {
            "annualized_apr": funding_metrics.execute().to_dict(orient="records")[0],
        }
    except Exception:
        summary["funding"] = None

    # Yield comparison
    try:
        yields = build_yield_comparison_view(con)
        summary["yields"] = yields.execute().to_dict(orient="records")
    except Exception:
        summary["yields"] = None

    # Stablecoin metrics
    try:
        stables = calculate_stablecoin_metrics(con)
        summary["stablecoins"] = {
            "supply": stables["supply_comparison"].execute().to_dict(orient="records"),
            "market_share": stables["market_share"].execute().to_dict(orient="records"),
        }
    except Exception:
        summary["stablecoins"] = None

    return summary


# =============================================================================
# View Creation Utilities
# =============================================================================


def create_analytics_views(con: ibis.BaseBackend) -> None:
    """
    Create persistent views for dashboard queries.

    Args:
        con: Ibis connection (must be DuckDB)
    """
    # Funding rate daily view
    con.raw_sql("""
        CREATE OR REPLACE VIEW v_funding_daily AS
        SELECT
            DATE_TRUNC('day', "fundingTime") as date,
            symbol,
            AVG("fundingRate") as avg_rate,
            SUM("fundingRate") as sum_rate,
            SUM("fundingRate") * 365 * 100 as daily_annualized_apr,
            COUNT(*) as funding_count
        FROM binance_funding_rates
        GROUP BY DATE_TRUNC('day', "fundingTime"), symbol
        ORDER BY date DESC, symbol
    """)

    # Yield rankings view
    con.raw_sql("""
        CREATE OR REPLACE VIEW v_yield_rankings AS
        SELECT
            project,
            symbol,
            chain,
            tvl_usd,
            apy,
            apy_base,
            apy_reward,
            stablecoin,
            ROW_NUMBER() OVER (PARTITION BY chain ORDER BY apy DESC) as rank_in_chain,
            ROW_NUMBER() OVER (ORDER BY apy DESC) as global_rank
        FROM defillama_yields
        WHERE tvl_usd >= 100000
        ORDER BY apy DESC
    """)

    # Stablecoin comparison view
    con.raw_sql("""
        CREATE OR REPLACE VIEW v_stablecoin_comparison AS
        SELECT
            symbol,
            name,
            circulating,
            price,
            ABS(price - 1.0) * 100 as peg_deviation_pct,
            circulating / SUM(circulating) OVER () * 100 as market_share_pct
        FROM defillama_stablecoins
        WHERE symbol IN ('USDe', 'USDC', 'USDT', 'DAI', 'FRAX')
        ORDER BY circulating DESC
    """)

    print("Analytics views created successfully")
