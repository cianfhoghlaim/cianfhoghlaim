# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "duckdb>=1.0.0",
#     "ibis-framework[duckdb]>=9.0.0",
#     "polars>=1.0.0",
#     "altair>=5.0.0",
#     "pandas>=2.0.0",
#     "sqlmesh>=0.100.0",
#     "python-dotenv>=1.0.0",
# ]
# ///

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # SQLMesh + DuckDB + Ibis: Data Transformation Pipeline

        This notebook demonstrates the modern analytics stack:

        1. **DuckDB** - In-process OLAP database for analytical queries
        2. **Ibis** - Python DataFrame API that compiles to SQL
        3. **SQLMesh** - SQL transformation framework with incremental models
        4. **DuckLake** - Lightweight lakehouse format integration

        > Based on patterns from `/data/examples/sqlmesh/` and `/data/examples/duckdb/`
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv()
    return mo, os, Path, load_dotenv


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 1. DuckDB Connection & Extensions

        DuckDB provides in-process OLAP analytics with excellent performance on analytical queries.
        """
    )
    return


@app.cell
def _():
    import duckdb
    import ibis
    import polars as pl
    import altair as alt

    # Create in-memory DuckDB connection
    conn = duckdb.connect(":memory:")

    # Show version
    version = conn.execute("SELECT version()").fetchone()[0]
    print(f"DuckDB Version: {version}")
    return duckdb, ibis, pl, alt, conn, version


@app.cell
def _(conn, mo):
    # Install and load useful extensions
    _df = mo.sql(
        f"""
        -- Install extensions
        INSTALL httpfs;
        INSTALL json;
        INSTALL parquet;

        -- Load extensions
        LOAD httpfs;
        LOAD json;
        LOAD parquet;

        -- Show installed extensions
        SELECT extension_name, installed, loaded
        FROM duckdb_extensions()
        WHERE installed = true;
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 2. Sample Data: Space Missions Dataset

        Load sample data to demonstrate DuckDB's analytical capabilities.
        """
    )
    return


@app.cell
def _(conn, mo):
    # Create sample space missions data
    _df = mo.sql(
        f"""
        -- Create missions table
        CREATE OR REPLACE TABLE missions AS
        SELECT * FROM (VALUES
            (1, 'Apollo 11', 'Moon Landing', '1969-07-16', '1969-07-24', 'Success', 'USA'),
            (2, 'Voyager 1', 'Outer Planets', '1977-09-05', NULL, 'Active', 'USA'),
            (3, 'Mars Pathfinder', 'Mars Exploration', '1996-12-04', '1997-09-27', 'Success', 'USA'),
            (4, 'Chandrayaan-1', 'Lunar Orbiter', '2008-10-22', '2009-08-28', 'Success', 'India'),
            (5, 'Rosetta', 'Comet Study', '2004-03-02', '2016-09-30', 'Success', 'ESA'),
            (6, 'New Horizons', 'Pluto Flyby', '2006-01-19', NULL, 'Active', 'USA'),
            (7, 'Cassini', 'Saturn Study', '1997-10-15', '2017-09-15', 'Success', 'USA/ESA'),
            (8, 'JWST', 'Space Telescope', '2021-12-25', NULL, 'Active', 'USA/ESA/CSA'),
            (9, 'Perseverance', 'Mars Rover', '2020-07-30', NULL, 'Active', 'USA'),
            (10, 'Chang''e 5', 'Lunar Sample Return', '2020-11-24', '2020-12-17', 'Success', 'China')
        ) AS t(id, name, mission_type, launch_date, end_date, status, agency);

        -- Create astronauts table
        CREATE OR REPLACE TABLE astronauts AS
        SELECT * FROM (VALUES
            (1, 'Neil Armstrong', 'USA', 1, 'Commander'),
            (2, 'Buzz Aldrin', 'USA', 1, 'Pilot'),
            (3, 'Michael Collins', 'USA', 1, 'Command Module Pilot')
        ) AS t(id, name, nationality, mission_id, role);

        SELECT * FROM missions;
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 3. Ibis: Python DataFrame API

        Ibis provides a unified Python API that compiles to SQL, enabling:
        - Lazy evaluation (queries only execute when needed)
        - Backend-agnostic code (works with DuckDB, Postgres, BigQuery, etc.)
        - Composable transformations
        """
    )
    return


@app.cell
def _(ibis):
    # Connect Ibis to DuckDB
    ibis_conn = ibis.duckdb.connect(":memory:")

    # Show connection info
    print(f"Ibis backend: {ibis_conn.name}")
    return ibis_conn,


@app.cell
def _(ibis_conn):
    # Create sample data via Ibis
    import pandas as pd

    missions_data = pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Apollo 11', 'Voyager 1', 'Mars Pathfinder', 'JWST', 'Perseverance'],
        'mission_type': ['Moon Landing', 'Outer Planets', 'Mars', 'Telescope', 'Mars'],
        'launch_year': [1969, 1977, 1996, 2021, 2020],
        'status': ['Success', 'Active', 'Success', 'Active', 'Active'],
        'budget_millions': [25400, 865, 265, 10000, 2700]
    })

    # Create Ibis table
    missions_ibis = ibis_conn.create_table("missions", missions_data, overwrite=True)
    missions_ibis
    return pd, missions_data, missions_ibis


@app.cell
def _(missions_ibis, mo):
    # Ibis filtering and aggregation (lazy evaluation)
    active_missions = (
        missions_ibis
        .filter(missions_ibis.status == 'Active')
        .select('name', 'mission_type', 'launch_year', 'budget_millions')
        .order_by('launch_year')
    )

    mo.md(f"""
    **Ibis Query (Lazy)**

    ```python
    active_missions = (
        missions_ibis
        .filter(missions_ibis.status == 'Active')
        .select('name', 'mission_type', 'launch_year', 'budget_millions')
        .order_by('launch_year')
    )
    ```

    **Generated SQL:**
    ```sql
    {ibis.to_sql(active_missions)}
    ```
    """)
    return active_missions,


@app.cell
def _(active_missions, mo):
    # Execute and display
    active_df = active_missions.execute()
    mo.ui.table(active_df, selection=None)
    return active_df,


@app.cell
def _(ibis_conn, missions_ibis, mo):
    # Aggregation example
    budget_by_type = (
        missions_ibis
        .group_by('mission_type')
        .aggregate(
            total_budget=missions_ibis.budget_millions.sum(),
            mission_count=missions_ibis.id.count(),
            avg_budget=missions_ibis.budget_millions.mean()
        )
        .order_by(ibis_conn.desc(missions_ibis.budget_millions.sum()))
    )

    budget_df = budget_by_type.execute()
    mo.ui.table(budget_df, selection=None)
    return budget_by_type, budget_df


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 4. Interactive Visualization with Altair

        Combine Ibis queries with Altair for interactive visualizations.
        """
    )
    return


@app.cell
def _(alt, budget_df, mo):
    # Budget by mission type chart
    budget_chart = (
        alt.Chart(budget_df)
        .mark_bar()
        .encode(
            x=alt.X('mission_type:N', title='Mission Type', sort='-y'),
            y=alt.Y('total_budget:Q', title='Total Budget (Millions USD)'),
            color='mission_type:N',
            tooltip=['mission_type', 'total_budget', 'mission_count', 'avg_budget']
        )
        .properties(
            title='Space Mission Budgets by Type',
            width=500,
            height=300
        )
    )

    chart_widget = mo.ui.altair_chart(budget_chart, label="Budget Analysis")
    chart_widget
    return budget_chart, chart_widget


@app.cell
def _(chart_widget, mo):
    # Show selected data
    if chart_widget.value is not None and len(chart_widget.value) > 0:
        mo.ui.table(chart_widget.value, selection=None)
    else:
        mo.md("*Click on chart bars to select data*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 5. SQLMesh Model Patterns

        SQLMesh provides SQL transformation with:
        - **FULL models**: Complete refresh on each run
        - **INCREMENTAL_BY_TIME_RANGE**: Only process new data
        - **SEED models**: Static reference data
        - **Audits**: Data quality checks
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ### FULL Model Example

        ```sql
        -- models/missions_summary.sql
        MODEL (
            name missions.summary,
            kind FULL,
            cron '@daily',
            audits (not_null(columns := [mission_type, total_count]))
        );

        SELECT
            mission_type,
            status,
            COUNT(*) as total_count,
            SUM(budget_millions) as total_budget,
            AVG(budget_millions) as avg_budget,
            MIN(launch_year) as first_launch,
            MAX(launch_year) as latest_launch
        FROM missions.raw_missions
        GROUP BY mission_type, status;
        ```

        ### INCREMENTAL_BY_TIME_RANGE Model

        ```sql
        -- models/daily_metrics.sql
        MODEL (
            name missions.daily_metrics,
            kind INCREMENTAL_BY_TIME_RANGE (
                time_column launch_date,
                batch_size 30,
                lookback 7
            ),
            cron '@daily'
        );

        SELECT
            DATE_TRUNC('day', launch_date) as metric_date,
            COUNT(*) as launches,
            SUM(budget_millions) as daily_budget
        FROM missions.raw_missions
        WHERE launch_date BETWEEN @start_date AND @end_date
        GROUP BY 1;
        ```

        ### SEED Model

        ```sql
        -- models/reference/agency_codes.sql
        MODEL (
            name missions.agency_codes,
            kind SEED (
                path 'seeds/agency_codes.csv'
            )
        );
        ```
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 6. Ibis + SQLMesh Hybrid Pattern

        Combine Ibis Python expressions with SQLMesh for complex transformations.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ```python
        # models/ibis_model.py
        import typing as t
        from sqlmesh import ExecutionContext, model
        import ibis

        @model(
            "missions.ibis_aggregations",
            columns={
                "mission_type": "TEXT",
                "metric_name": "TEXT",
                "metric_value": "DOUBLE",
            },
            kind="full",
        )
        def execute(
            context: ExecutionContext,
            start: datetime,
            end: datetime,
            execution_time: datetime,
            **kwargs: t.Any,
        ) -> ibis.expr.types.Table:
            # Get Ibis connection from SQLMesh context
            conn = ibis.duckdb.connect(context.engine_adapter.connection)

            # Load source table
            missions = conn.table("missions.raw_missions")

            # Build Ibis expression
            result = (
                missions
                .filter(missions.launch_date >= start)
                .filter(missions.launch_date < end)
                .group_by('mission_type')
                .aggregate(
                    avg_budget=missions.budget_millions.mean(),
                    max_budget=missions.budget_millions.max(),
                    mission_count=missions.id.count()
                )
                .unpivot(
                    on=['avg_budget', 'max_budget', 'mission_count'],
                    names_to='metric_name',
                    values_to='metric_value'
                )
            )

            return result
        ```
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 7. DuckDB Advanced Features
        """
    )
    return


@app.cell
def _(conn, mo):
    # Window functions
    _df = mo.sql(
        f"""
        -- Cumulative budget by launch year
        WITH missions_cte AS (
            SELECT * FROM (VALUES
                (1, 'Apollo 11', 1969, 25400),
                (2, 'Voyager 1', 1977, 865),
                (3, 'Pathfinder', 1996, 265),
                (4, 'JWST', 2021, 10000),
                (5, 'Perseverance', 2020, 2700)
            ) AS t(id, name, launch_year, budget_millions)
        )
        SELECT
            name,
            launch_year,
            budget_millions,
            SUM(budget_millions) OVER (ORDER BY launch_year) as cumulative_budget,
            RANK() OVER (ORDER BY budget_millions DESC) as budget_rank,
            budget_millions * 100.0 / SUM(budget_millions) OVER () as pct_of_total
        FROM missions_cte
        ORDER BY launch_year;
        """,
        engine=conn
    )
    return


@app.cell
def _(conn, mo):
    # Pivot example
    _df = mo.sql(
        f"""
        -- Mission counts by decade
        WITH missions_decades AS (
            SELECT * FROM (VALUES
                ('Moon', 1960, 5), ('Moon', 1970, 3), ('Moon', 2020, 2),
                ('Mars', 1970, 2), ('Mars', 1990, 4), ('Mars', 2020, 3),
                ('Outer', 1970, 2), ('Outer', 1990, 1), ('Outer', 2000, 1)
            ) AS t(mission_type, decade, mission_count)
        )
        PIVOT missions_decades
        ON decade IN (1960, 1970, 1990, 2000, 2020)
        USING SUM(mission_count)
        GROUP BY mission_type;
        """,
        engine=conn
    )
    return


@app.cell
def _(conn, mo):
    # Read Parquet from URL
    _df = mo.sql(
        f"""
        -- Read remote Parquet file (example pattern)
        -- SELECT * FROM read_parquet('https://example.com/data.parquet') LIMIT 10;

        -- Query JSON directly
        SELECT
            json_extract('{"mission": "Apollo", "year": 1969}', '$.mission') as mission,
            json_extract('{"mission": "Apollo", "year": 1969}', '$.year')::INTEGER as year;
        """,
        engine=conn
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 8. SQLMesh Configuration

        SQLMesh uses YAML configuration for project setup.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ```yaml
        # config.yaml
        gateways:
          local:
            connection:
              type: duckdb
              database: ./data/warehouse.duckdb

          ducklake:
            connection:
              type: duckdb
              catalogs:
                myducklake:
                  type: ducklake
                  path: ducklake:metadata.ducklake

        default_gateway: local

        model_defaults:
          dialect: duckdb
          start: 2024-01-01

        # Environment-based configuration
        environments:
          dev:
            gateway: local
          prod:
            gateway: ducklake
        ```

        ### CLI Commands

        ```bash
        # Initialize project
        sqlmesh init

        # Plan changes
        sqlmesh plan

        # Apply changes
        sqlmesh plan --auto-apply

        # Run with date range
        sqlmesh run --start 2024-01-01 --end 2024-12-31

        # Audit models
        sqlmesh audit

        # Generate documentation
        sqlmesh docs
        ```
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Key Patterns Summary

        ### DuckDB Patterns
        ```sql
        -- Read multiple file formats
        SELECT * FROM read_parquet('*.parquet');
        SELECT * FROM read_csv('data.csv', header=true);
        SELECT * FROM read_json('data.json');

        -- Install extensions
        INSTALL httpfs; LOAD httpfs;

        -- S3/R2 access
        SET s3_region='auto';
        SET s3_endpoint='account.r2.cloudflarestorage.com';
        SELECT * FROM read_parquet('s3://bucket/path/*.parquet');
        ```

        ### Ibis Patterns
        ```python
        # Connect to backend
        conn = ibis.duckdb.connect("database.duckdb")

        # Lazy query building
        result = (
            table
            .filter(table.col > value)
            .group_by('category')
            .aggregate(total=table.amount.sum())
        )

        # Execute
        df = result.execute()  # Returns pandas DataFrame
        df = result.to_polars()  # Returns polars DataFrame
        ```

        ### SQLMesh Model Types
        - **FULL**: Complete refresh each run
        - **INCREMENTAL_BY_TIME_RANGE**: Process new time ranges
        - **INCREMENTAL_BY_UNIQUE_KEY**: Upsert by key
        - **SCD_TYPE_2**: Slowly changing dimensions
        - **SEED**: Static reference data from CSV
        - **EXTERNAL**: Read-only external tables
        """
    )
    return


if __name__ == "__main__":
    app.run()
