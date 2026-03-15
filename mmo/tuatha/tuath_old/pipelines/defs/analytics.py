"""
Analytics assets for crypto data transformations.

- Funding rate metrics from Binance data
- Yield comparison across protocols
- Protocol health metrics from Aave data
"""

from typing import Any

from dagster import (
    asset,
    AssetExecutionContext,
    AssetIn,
    Definitions,
    MetadataValue,
    Output,
)


@asset(
    group_name="analytics",
    ins={
        "binance_funding_assets": AssetIn(),
    },
)
def funding_rate_metrics(
    context: AssetExecutionContext,
    binance_funding_assets,
) -> Output[dict[str, Any]]:
    """Calculate funding rate analytics."""
    from crypteolas.pipelines.transformations.crypto_analytics import (
        calculate_funding_metrics,
        funding_rate_timeseries,
        get_connection,
    )

    context.log.info("Calculating funding rate metrics...")

    con = get_connection("data/crypto_analytics.duckdb")

    metrics = calculate_funding_metrics(con, symbol="ETHUSDT")
    timeseries = funding_rate_timeseries(con, symbols=["ETHUSDT", "BTCUSDT"])

    # Execute and return
    metrics_df = metrics.execute()
    timeseries_df = timeseries.execute()

    return Output(
        value={
            "metrics": metrics_df.to_dict(orient="records"),
            "timeseries_rows": len(timeseries_df),
        },
        metadata={
            "avg_funding_rate": MetadataValue.float(
                metrics_df["avg_funding_rate"].iloc[0]
                if len(metrics_df) > 0
                else 0
            ),
            "annualized_apr": MetadataValue.float(
                metrics_df["annualized_apr_avg"].iloc[0]
                if len(metrics_df) > 0
                else 0
            ),
        },
    )


@asset(
    group_name="analytics",
    ins={
        "defillama_assets": AssetIn(),
    },
)
def yield_comparison(
    context: AssetExecutionContext,
    defillama_assets,
) -> Output[dict[str, Any]]:
    """Build yield comparison across protocols."""
    from crypteolas.pipelines.transformations.crypto_analytics import (
        build_yield_comparison_view,
        calculate_yield_spreads,
        get_connection,
    )

    context.log.info("Building yield comparison...")

    con = get_connection("data/crypto_analytics.duckdb")

    comparison = build_yield_comparison_view(
        con,
        protocols=["ethena", "aave-v3", "pendle", "lido"],
    )
    spreads = calculate_yield_spreads(con, stablecoin_only=True)

    comparison_df = comparison.execute()
    spreads_df = spreads.execute()

    return Output(
        value={
            "comparison": comparison_df.to_dict(orient="records"),
            "top_yields": spreads_df.head(10).to_dict(orient="records"),
        },
        metadata={
            "protocols_compared": MetadataValue.int(len(comparison_df)),
            "yield_pools_analyzed": MetadataValue.int(len(spreads_df)),
        },
    )


@asset(
    group_name="analytics",
    ins={
        "aave_subgraph_assets": AssetIn(),
    },
)
def protocol_health_metrics(
    context: AssetExecutionContext,
    aave_subgraph_assets,
) -> Output[dict[str, Any]]:
    """Calculate protocol health metrics."""
    from crypteolas.pipelines.transformations.crypto_analytics import (
        calculate_protocol_health,
        get_connection,
    )

    context.log.info("Calculating protocol health metrics...")

    con = get_connection("data/crypto_analytics.duckdb")

    health = calculate_protocol_health(con)

    utilization_df = health["utilization"].execute()
    risk_df = health["liquidation_risk"].execute()

    return Output(
        value={
            "utilization": utilization_df.to_dict(orient="records"),
            "liquidation_risk": risk_df.to_dict(orient="records"),
        },
        metadata={
            "reserves_analyzed": MetadataValue.int(len(utilization_df)),
            "at_risk_positions": MetadataValue.int(len(risk_df)),
        },
    )


# Export definitions for load_from_defs_folder
defs = Definitions(
    assets=[funding_rate_metrics, yield_comparison, protocol_health_metrics],
)
