"""
Lakehouse Pipeline Demo - Marimo Notebook

Demonstrates the full local/remote data pipeline:
- dlt for data ingestion
- DuckLake for SQL catalog (local PostgreSQL or PlanetScale)
- Lance Namespace for vector table registration
- Garage S3 (local) or Cloudflare R2 (remote) for object storage
"""

import marimo

__generated_with = "0.18.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Lakehouse Pipeline Demo

        This notebook demonstrates the unified data lakehouse architecture:

        | Layer | Local | Remote |
        |-------|-------|--------|
        | Query Engine | DuckDB | MotherDuck |
        | SQL Catalog | DuckLake | DuckLake (PlanetScale) |
        | Vector Catalog | Lance Namespace | Lance Namespace |
        | Object Storage | Garage S3 | Cloudflare R2 |

        **Key Pattern**: Same code, different destination. Validate locally, deploy to cloud.
        """
    )
    return


@app.cell
def _():
    import os
    import duckdb
    import requests

    # Check if we have dlt installed
    try:
        import dlt
        HAS_DLT = True
    except ImportError:
        HAS_DLT = False
        print("dlt not installed. Run: pip install 'dlt[ducklake]'")

    # Check if we have lancedb installed
    try:
        import lancedb
        HAS_LANCEDB = True
    except ImportError:
        HAS_LANCEDB = False
        print("lancedb not installed. Run: pip install lancedb")

    return os, duckdb, requests, HAS_DLT, HAS_LANCEDB


@app.cell
def _(mo):
    # Configuration selector
    environment = mo.ui.radio(
        options={"local": "Local Development", "remote": "Remote Production"},
        value="local",
        label="Environment"
    )
    environment
    return (environment,)


@app.cell
def _(environment, os):
    # Configuration based on environment selection
    if environment.value == "local":
        CONFIG = {
            "ducklake_conn": f"ducklake:postgres:host={os.getenv('LOCAL_HOST', 'localhost')} "
                            f"port={os.getenv('LOCAL_PORT', '5432')} "
                            f"user={os.getenv('LOCAL_USER', 'ducklake_user')} "
                            f"password={os.getenv('LOCAL_PASSWORD', 'ducklake_password')} "
                            f"dbname={os.getenv('LOCAL_DBNAME', 'ducklake_catalog')}",
            "data_path": "ducklake_data/",
            "lance_root": "s3://lance/",
            "s3_endpoint": os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900"),
            "lance_namespace_url": os.getenv("LANCE_NAMESPACE_URL", "http://localhost:8182"),
            "destination": "ducklake"
        }
    else:
        CONFIG = {
            "ducklake_conn": f"ducklake:postgres:host={os.getenv('PLANETSCALE_HOST', 'aws.connect.psdb.cloud')} "
                            f"user={os.getenv('PLANETSCALE_USER', 'lakehouse')} "
                            f"password={os.getenv('PLANETSCALE_PASSWORD', '')} "
                            f"dbname={os.getenv('PLANETSCALE_DBNAME', 'lakehouse')} "
                            f"sslmode=require",
            "data_path": f"r2://{os.getenv('R2_BUCKET_NAME', 'lakehouse')}/ducklake/",
            "lance_root": f"r2://{os.getenv('R2_BUCKET_NAME', 'lakehouse')}/lance/",
            "r2_endpoint": f"https://{os.getenv('R2_ACCOUNT_ID', 'xxx')}.r2.cloudflarestorage.com",
            "lance_namespace_url": os.getenv("LANCE_NAMESPACE_URL", "https://lance-api.cianfhoghlaim.ie"),
            "destination": "motherduck"
        }

    print(f"Using {environment.value} configuration")
    return (CONFIG,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 1: Define Data Source

        Using the Hacker News API as our example data source.
        The `@dlt.resource` decorator handles incremental loading and schema inference.
        """
    )
    return


@app.cell
def _(requests, HAS_DLT):
    if HAS_DLT:
        import dlt

        @dlt.resource(
            table_name="stories",
            write_disposition="merge",
            primary_key="id"
        )
        def hacker_news_stories(limit: int = 30):
            """Fetch top Hacker News stories."""
            ids = requests.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                timeout=10
            ).json()[:limit]

            for story_id in ids:
                story = requests.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json",
                    timeout=10
                ).json()
                if story:
                    yield story
    else:
        hacker_news_stories = None
        print("dlt not available - skipping resource definition")

    return (hacker_news_stories,)


@app.cell
def _(mo):
    # Run pipeline button
    run_pipeline = mo.ui.run_button(label="Run Pipeline")
    run_pipeline
    return (run_pipeline,)


@app.cell
def _(mo, run_pipeline, hacker_news_stories, CONFIG, HAS_DLT):
    pipeline_result = None

    if run_pipeline.value and HAS_DLT and hacker_news_stories:
        import dlt

        mo.md("**Running pipeline...**")

        # Create pipeline with appropriate destination
        pipeline = dlt.pipeline(
            pipeline_name="lakehouse_demo",
            destination=CONFIG["destination"],
            dataset_name="hacker_news"
        )

        # Run the pipeline
        try:
            load_info = pipeline.run(hacker_news_stories(30))
            pipeline_result = f"Loaded {len(load_info.loads_ids)} batches to {CONFIG['destination']}"
            mo.md(f"**Success**: {pipeline_result}")
        except Exception as e:
            pipeline_result = f"Error: {e}"
            mo.md(f"**Error**: {pipeline_result}")
    elif not HAS_DLT:
        mo.md("**dlt not installed** - Install with: `pip install 'dlt[ducklake]'`")
    else:
        mo.md("Click **Run Pipeline** to load data to DuckLake")

    return (pipeline_result,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 2: Query with DuckDB

        DuckDB can query DuckLake tables directly using the `ducklake` extension.
        The same queries work whether data is local or in the cloud.
        """
    )
    return


@app.cell
def _(duckdb, CONFIG, mo):
    # Query the data
    try:
        conn = duckdb.connect()
        conn.execute("INSTALL ducklake; LOAD ducklake;")

        # Try to attach the DuckLake database
        # For demo, use local DuckDB file if postgres is not available
        try:
            conn.execute(f"ATTACH '{CONFIG['ducklake_conn']}' AS lakehouse (DATA_PATH '{CONFIG['data_path']}');")
            attached = True
        except Exception as e:
            # Fall back to local DuckDB-based DuckLake
            conn.execute("ATTACH 'ducklake:duckdb:lakehouse_demo.duckdb' AS lakehouse;")
            attached = True
            print(f"Using local DuckDB fallback: {e}")

        if attached:
            # Query the stories
            df = conn.execute("""
                SELECT id, title, score, by, time
                FROM lakehouse.hacker_news.stories
                ORDER BY score DESC
                LIMIT 10
            """).df()

            mo.ui.table(df)
        else:
            mo.md("Could not attach DuckLake database")

    except Exception as e:
        mo.md(f"**Query Error**: {e}\n\nMake sure you've run the pipeline first.")
        df = None

    return (df,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 3: Register Lance Table

        Lance tables are registered in the Iceberg catalog using the "trojan horse" pattern.
        The table appears as an Iceberg table with `table_type=lance` property.
        """
    )
    return


@app.cell
def _(mo, CONFIG, requests, HAS_LANCEDB):
    # Lance namespace registration
    lance_result = None

    if HAS_LANCEDB:
        # Check if lance-namespace sidecar is available
        try:
            health = requests.get(f"{CONFIG['lance_namespace_url']}/health", timeout=5)
            if health.status_code == 200:
                mo.md(f"**Lance Namespace**: Connected to {CONFIG['lance_namespace_url']}")

                # Try to create a namespace
                try:
                    requests.post(
                        f"{CONFIG['lance_namespace_url']}/namespaces",
                        json={"namespace": ["embeddings"]},
                        timeout=10
                    )
                except Exception:
                    pass  # Namespace may already exist

                # Register a Lance table
                response = requests.post(
                    f"{CONFIG['lance_namespace_url']}/namespaces/embeddings/tables",
                    json={
                        "name": "articles",
                        "location": f"{CONFIG['lance_root']}embeddings/articles"
                    },
                    timeout=10
                )

                if response.status_code in [200, 201, 409]:  # 409 = already exists
                    lance_result = "Lance table 'embeddings.articles' registered in Iceberg catalog"
                    mo.md(f"**Success**: {lance_result}")
                else:
                    lance_result = f"Registration returned: {response.status_code}"
                    mo.md(f"**Note**: {lance_result}")
            else:
                mo.md(f"**Lance Namespace unavailable** at {CONFIG['lance_namespace_url']}")
        except requests.exceptions.ConnectionError:
            mo.md(
                f"**Lance Namespace not running** at {CONFIG['lance_namespace_url']}\n\n"
                "Start the lakehouse stack: `docker compose up -d`"
            )
    else:
        mo.md("**lancedb not installed** - Install with: `pip install lancedb`")

    return (lance_result,)


@app.cell
def _(mo):
    mo.md(
        """
        ## Step 4: Switch to Remote

        To deploy to production, change the environment selector above to **Remote Production**.

        The same code works with:
        - **MotherDuck** instead of local DuckDB
        - **PlanetScale PostgreSQL** for catalog metadata
        - **Cloudflare R2** for object storage
        - **Lance Cloud** for vector storage

        **Environment Variables Required for Remote**:
        ```bash
        export MOTHERDUCK_TOKEN="your-token"
        export PLANETSCALE_HOST="aws.connect.psdb.cloud"
        export PLANETSCALE_USER="lakehouse"
        export PLANETSCALE_PASSWORD="your-password"
        export R2_ACCESS_KEY_ID="your-key"
        export R2_SECRET_ACCESS_KEY="your-secret"
        export R2_ACCOUNT_ID="your-account"
        ```
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        ## Architecture Summary

        ```
        ┌─────────────────────────────────────────────────────────────┐
        │                     Data Pipeline (dlt)                      │
        │  @dlt.resource → pipeline.run() → destination               │
        └─────────────────────┬───────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
              ┌─────▼─────┐       ┌─────▼─────┐
              │ DuckLake  │       │ Lance NS  │
              │ (SQL)     │       │ (Vector)  │
              └─────┬─────┘       └─────┬─────┘
                    │                   │
              ┌─────▼─────────────────▼─────┐
              │       Iceberg Catalog        │
              │       (Lakekeeper)           │
              └─────────────┬────────────────┘
                            │
              ┌─────────────▼────────────────┐
              │        Object Storage         │
              │   Garage (local) / R2 (cloud) │
              └───────────────────────────────┘
        ```
        """
    )
    return


if __name__ == "__main__":
    app.run()
