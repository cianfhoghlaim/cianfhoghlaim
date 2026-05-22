# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "dlt[duckdb]>=1.18.2",
#     "ibis-framework[duckdb]>=11.0.0",
#     "lancedb>=0.6.0",
#     "python-dotenv",
#     "altair>=5.0.0",
#     "pandas",
#     "httpx",
# ]
# ///
"""DeFi Analytics Dashboard - Unified DeFi Intelligence.

This marimo notebook provides a unified view of:
1. Funding rates across exchanges (Binance, Bybit, OKX)
2. DeFi protocol yields (Aave, Compound, Lido, Pendle)
3. Stablecoin metrics
4. ETH staking analytics

Usage:
    marimo edit crypteolas/notebooks/04_defi_dashboard.py
"""
import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # DeFi Analytics Dashboard

    A unified view of DeFi data across multiple dimensions:

    | Data Source | Type | Purpose |
    |-------------|------|---------|
    | **Funding Rates** | CEX | Perpetual contract funding |
    | **Protocol Yields** | DeFi | Lending/staking APYs |
    | **Stablecoins** | Tokens | Supply and peg metrics |
    | **ETH Staking** | L1 | Validator and APR data |

    ---
    """)
    return


@app.cell
def _():
    import marimo as mo
    import os
    from pathlib import Path

    project_root = Path(__file__).parent.parent if "__file__" in dir() else Path.cwd().parent
    if (project_root / "pyproject.toml").exists():
        os.chdir(project_root)

    return mo, os, Path, project_root


@app.cell
def _():
    from dotenv import load_dotenv
    load_dotenv()
    return (load_dotenv,)


@app.cell
def _(mo):
    # Tabs for different views
    tabs = mo.ui.tabs({
        "Overview": "overview",
        "Funding Rates": "funding",
        "Protocol Yields": "yields",
        "Stablecoins": "stablecoins",
        "ETH Staking": "staking",
    })
    tabs
    return (tabs,)


# ============================================================================
# OVERVIEW TAB
# ============================================================================

@app.cell
def _(mo, tabs):
    if tabs.value == "overview":
        mo.md(r"""
        ## DeFi Analytics Overview

        This dashboard integrates multiple DeFi data sources for comprehensive analytics:

        ### 1. Funding Rates (CEX)
        - **What**: Perpetual futures funding rates
        - **Sources**: Binance, Bybit, OKX
        - **Use Case**: Basis trade opportunities, sentiment analysis

        ### 2. Protocol Yields (DeFi)
        - **What**: Lending rates, staking APYs
        - **Sources**: DeFiLlama, protocol subgraphs
        - **Use Case**: Yield optimization, risk assessment

        ### 3. Stablecoins
        - **What**: Supply, peg deviation, market cap
        - **Sources**: CoinGecko, DeFiLlama
        - **Use Case**: Liquidity analysis, peg monitoring

        ### 4. ETH Staking
        - **What**: Validator stats, APR, queue
        - **Sources**: Beaconcha.in
        - **Use Case**: Staking decisions, network health
        """)
    return


# ============================================================================
# FUNDING RATES TAB
# ============================================================================

@app.cell
def _(mo, tabs):
    import altair as alt
    import pandas as pd

    if tabs.value == "funding":
        mo.md("## Funding Rate Analytics")

        # Symbol selector
        symbol_select = mo.ui.dropdown(
            options=["ETHUSDT", "BTCUSDT", "SOLUSDT", "AVAXUSDT"],
            value="ETHUSDT",
            label="Symbol",
        )

        exchange_select = mo.ui.multiselect(
            options=["binance", "bybit", "okx"],
            value=["binance", "bybit", "okx"],
            label="Exchanges",
        )

        mo.hstack([symbol_select, exchange_select])
    return alt, pd


@app.cell
def _(mo, tabs):
    if tabs.value == "funding":
        fetch_funding_button = mo.ui.run_button(label="Fetch Funding Data")
        fetch_funding_button
    return


@app.cell
def _(mo, tabs, alt, pd):
    import httpx

    if tabs.value == "funding":
        # Mock funding rate data (replace with actual API calls)
        funding_data = [
            {"exchange": "Binance", "symbol": "ETHUSDT", "rate": 0.00045, "annualized": 4.93},
            {"exchange": "Bybit", "symbol": "ETHUSDT", "rate": 0.00042, "annualized": 4.60},
            {"exchange": "OKX", "symbol": "ETHUSDT", "rate": 0.00048, "annualized": 5.26},
            {"exchange": "Binance", "symbol": "BTCUSDT", "rate": 0.00038, "annualized": 4.16},
            {"exchange": "Bybit", "symbol": "BTCUSDT", "rate": 0.00035, "annualized": 3.83},
            {"exchange": "OKX", "symbol": "BTCUSDT", "rate": 0.00040, "annualized": 4.38},
        ]

        df = pd.DataFrame(funding_data)

        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("exchange:N", title="Exchange"),
            y=alt.Y("annualized:Q", title="Annualized Rate (%)"),
            color="symbol:N",
            column="symbol:N",
            tooltip=["exchange", "symbol", "rate", "annualized"]
        ).properties(
            width=200,
            height=250,
            title="Funding Rates by Exchange"
        )

        mo.ui.altair_chart(chart)
    return httpx,


@app.cell
def _(mo, tabs, pd):
    if tabs.value == "funding":
        # Summary table
        summary_data = [
            {"Metric": "Best Rate (ETH)", "Value": "OKX: 5.26%"},
            {"Metric": "Worst Rate (ETH)", "Value": "Bybit: 4.60%"},
            {"Metric": "Arbitrage Spread", "Value": "0.66%"},
            {"Metric": "Positive Rate %", "Value": "72%"},
        ]

        mo.ui.table(pd.DataFrame(summary_data))
    return


# ============================================================================
# PROTOCOL YIELDS TAB
# ============================================================================

@app.cell
def _(mo, tabs, alt, pd):
    if tabs.value == "yields":
        mo.md("## Protocol Yield Comparison")

        # Mock yield data
        yield_data = [
            {"protocol": "Aave V3", "asset": "USDC", "apy": 4.2, "tvl": 2.1e9, "type": "lending"},
            {"protocol": "Compound", "asset": "USDC", "apy": 3.8, "tvl": 1.8e9, "type": "lending"},
            {"protocol": "Lido", "asset": "stETH", "apy": 3.1, "tvl": 28e9, "type": "staking"},
            {"protocol": "Pendle", "asset": "PT-stETH", "apy": 4.5, "tvl": 450e6, "type": "yield"},
            {"protocol": "Ethena", "asset": "sUSDe", "apy": 12.5, "tvl": 3.2e9, "type": "synthetic"},
            {"protocol": "MakerDAO", "asset": "sDAI", "apy": 5.0, "tvl": 2.5e9, "type": "lending"},
        ]

        df = pd.DataFrame(yield_data)
        df["tvl_b"] = df["tvl"] / 1e9

        chart = alt.Chart(df).mark_circle(size=200).encode(
            x=alt.X("apy:Q", title="APY (%)"),
            y=alt.Y("protocol:N", title="Protocol"),
            size=alt.Size("tvl_b:Q", title="TVL (B)", scale=alt.Scale(range=[100, 1000])),
            color=alt.Color("type:N", title="Type"),
            tooltip=["protocol", "asset", "apy", "tvl_b", "type"]
        ).properties(
            width=600,
            height=300,
            title="Yield vs TVL by Protocol"
        )

        mo.ui.altair_chart(chart)
    return


@app.cell
def _(mo, tabs, pd):
    if tabs.value == "yields":
        mo.md("""
        ### Risk-Adjusted Recommendations

        | Risk Level | Protocol | Asset | APY | Notes |
        |------------|----------|-------|-----|-------|
        | Low | Lido | stETH | 3.1% | Largest liquid staking |
        | Medium | Aave V3 | USDC | 4.2% | Battle-tested lending |
        | Medium | Pendle | PT-stETH | 4.5% | Fixed yield, no IL |
        | Higher | Ethena | sUSDe | 12.5% | Delta-neutral basis trade |
        """)
    return


# ============================================================================
# STABLECOINS TAB
# ============================================================================

@app.cell
def _(mo, tabs, alt, pd):
    if tabs.value == "stablecoins":
        mo.md("## Stablecoin Metrics")

        # Mock stablecoin data
        stable_data = [
            {"symbol": "USDT", "supply": 120e9, "price": 1.0001, "peg_dev": 0.01},
            {"symbol": "USDC", "supply": 35e9, "price": 0.9998, "peg_dev": -0.02},
            {"symbol": "DAI", "supply": 5.2e9, "price": 1.0002, "peg_dev": 0.02},
            {"symbol": "USDe", "supply": 3.8e9, "price": 0.9995, "peg_dev": -0.05},
            {"symbol": "FRAX", "supply": 0.8e9, "price": 0.9999, "peg_dev": -0.01},
        ]

        df = pd.DataFrame(stable_data)
        df["supply_b"] = df["supply"] / 1e9

        # Supply chart
        supply_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("supply_b:Q", title="Supply (Billions)"),
            y=alt.Y("symbol:N", sort="-x", title="Stablecoin"),
            color=alt.Color("symbol:N", legend=None),
            tooltip=["symbol", "supply_b", "price", "peg_dev"]
        ).properties(
            width=500,
            height=200,
            title="Stablecoin Supply"
        )

        mo.ui.altair_chart(supply_chart)
    return


@app.cell
def _(mo, tabs, alt, pd):
    if tabs.value == "stablecoins":
        # Peg deviation chart
        stable_data = [
            {"symbol": "USDT", "peg_dev": 0.01},
            {"symbol": "USDC", "peg_dev": -0.02},
            {"symbol": "DAI", "peg_dev": 0.02},
            {"symbol": "USDe", "peg_dev": -0.05},
            {"symbol": "FRAX", "peg_dev": -0.01},
        ]

        df = pd.DataFrame(stable_data)

        peg_chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("symbol:N", title="Stablecoin"),
            y=alt.Y("peg_dev:Q", title="Peg Deviation (%)"),
            color=alt.condition(
                alt.datum.peg_dev > 0,
                alt.value("#22c55e"),
                alt.value("#ef4444")
            ),
            tooltip=["symbol", "peg_dev"]
        ).properties(
            width=400,
            height=200,
            title="Peg Deviation from $1.00"
        )

        mo.ui.altair_chart(peg_chart)
    return


# ============================================================================
# ETH STAKING TAB
# ============================================================================

@app.cell
def _(mo, tabs, pd):
    if tabs.value == "staking":
        mo.md("## ETH Staking Analytics")

        # Mock staking data
        staking_metrics = [
            {"Metric": "Current APR", "Value": "3.1%"},
            {"Metric": "Total Validators", "Value": "950,000"},
            {"Metric": "Total Staked", "Value": "32.5M ETH"},
            {"Metric": "Entry Queue", "Value": "~45 days"},
            {"Metric": "Exit Queue", "Value": "~2 days"},
            {"Metric": "Network Participation", "Value": "99.5%"},
        ]

        mo.ui.table(pd.DataFrame(staking_metrics))
    return


@app.cell
def _(mo, tabs, alt, pd):
    if tabs.value == "staking":
        # APR history chart
        apr_history = [
            {"date": "2024-07", "apr": 3.8},
            {"date": "2024-08", "apr": 3.6},
            {"date": "2024-09", "apr": 3.4},
            {"date": "2024-10", "apr": 3.3},
            {"date": "2024-11", "apr": 3.2},
            {"date": "2024-12", "apr": 3.1},
        ]

        df = pd.DataFrame(apr_history)

        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X("date:O", title="Month"),
            y=alt.Y("apr:Q", title="APR (%)", scale=alt.Scale(domain=[2.5, 4.5])),
            tooltip=["date", "apr"]
        ).properties(
            width=500,
            height=250,
            title="ETH Staking APR Trend"
        )

        mo.ui.altair_chart(chart)
    return


@app.cell
def _(mo, tabs):
    if tabs.value == "staking":
        mo.md("""
        ### Liquid Staking Comparison

        | Provider | Market Share | APY | Fee |
        |----------|-------------|-----|-----|
        | Lido | 29.5% | 3.1% | 10% |
        | Coinbase | 12.8% | 2.9% | 25% |
        | Rocket Pool | 3.2% | 3.0% | 14% |
        | Frax Ether | 1.5% | 3.4% | 10% |
        """)
    return


# ============================================================================
# CROSS-DATA INSIGHTS
# ============================================================================

@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Cross-Data Insights

    Key observations from combined DeFi data:
    """)
    return


@app.cell
def _(mo, pd):
    insights = [
        {"Category": "Yield Opportunity", "Insight": "Ethena sUSDe offers 12.5% vs 3.1% ETH staking - premium for delta-neutral risk"},
        {"Category": "Funding Arbitrage", "Insight": "OKX-Bybit spread of 0.66% annualized on ETH perpetuals"},
        {"Category": "Stablecoin Risk", "Insight": "USDe shows largest peg deviation at -0.05% - monitor closely"},
        {"Category": "Staking Queue", "Insight": "45-day entry queue suggests high demand, consider liquid alternatives"},
    ]

    mo.ui.table(pd.DataFrame(insights))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Data Pipeline Status

    To refresh data, run the Dagster pipelines:

    ```bash
    # Run all DeFi data pipelines
    dagster asset materialize --select defi_aggregate_stats

    # Run specific pipeline
    dagster asset materialize --select binance_funding_rates
    ```

    ## Resources

    - [DeFiLlama API](https://defillama.com/docs/api)
    - [Beaconcha.in API](https://beaconcha.in/api/v1/docs)
    - [CoinGecko API](https://www.coingecko.com/en/api)
    """)
    return


if __name__ == "__main__":
    app.run()
