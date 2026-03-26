# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.18.4"
app = marimo.App(
    css_file="/usr/local/_marimo/custom.css",
    auto_download=["html"],
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ⚙️ Demo: Using dlt and Dagster to Ingest, Orchestrate, and Parallelize API Pipelines

    In this demo, we’ll put dlt and Dagster into action by building a simple, production-style data pipeline — extracting data from the **Jaffle Shop API**, processing it with `dlt`, and materializing it into a local **DuckDB** database.

    ---

    ## 🔍 What We'll Cover

    This demo is broken into two parts:

    ### 📝 **In This Notebook**
    We’ll focus on the first part of the workflow:
    - Creating a `dlt` pipeline using `rest_api_source`
    - Configuring and running the pipeline locally
    - Inspecting the loaded data in DuckDB

    ### 🧑‍💻 **Live Walkthrough (During the Demo)**
    The following topics will be demonstrated live:
    - Registering the dlt pipeline as a Dagster asset using `dlt_asset`
    - Scheduling, monitoring, and lineage tracking in the Dagster UI
    - Running multiple dlt pipelines in **parallel** using Dagster orchestration

    ---

    By the end of this demo, you’ll see how dlt and Dagster work together to streamline data ingestion, asset management, and parallel execution — all with minimal boilerplate and maximum visibility.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Installation
    """)
    return


app._unparsable_cell(
    r"""
    !uv pip install \"dlt[duckdb]\"
    """,
    name="_"
)


@app.cell
def _():

    def _():
        import marimo as mo
        import dlt
        from dlt.sources.rest_api import rest_api_source

        # Create a new configuration with incremental loading for orders
        incremental_config = {
            "client": {
                "base_url": "https://jaffle-shop.scalevector.ai/api/v1/"
            },
            "resource_defaults": {
                "primary_key": "id",
                "endpoint": {
                    "params": {
                        "page_size": 100
                    }
                }
            },
            "resources": [
                {"name": "customers", "endpoint": {"path": "customers"}},
                # This is the modified 'orders' resource
                {
                    "name": "orders",
                    "endpoint": {
                        "path": "orders",
                        # 3. Add incremental loading configuration
                        "incremental": {
                            "cursor_path": "ordered_at",
                            "initial_value": "2017-08-01"
                        }
                    }
                },
                {"name": "items", "endpoint": {"path": "items"}},
                {"name": "products", "primary_key": "sku", "endpoint": {"path": "products"}},
                {"name": "supplies", "endpoint": {"path": "supplies"}},
            ]
        }

        # Create the new dlt source from our modified config
        incremental_dlt_source = rest_api_source(incremental_config)

        # 4. Add a processing step to filter records
        incremental_dlt_source.orders.add_filter(
            lambda item: item.get("order_total", 0) <= 500
        )

        # Create and run a new pipeline with the incremental source
        # We use a new pipeline and dataset name to avoid conflicts
        incremental_pipeline = dlt.pipeline(
        pipeline_name="jaffle_shop_incremental",
        destination="duckdb",
        dataset_name="jaffle_shop_incremental_dataset",
        progress="log"
        )
    
        # Run the pipeline with the 'merge' write disposition for incremental loading
        load_info_incremental = incremental_pipeline.run(
        incremental_dlt_source,
        write_disposition="merge"
        )
    
        load_info_incremental

    
        # Access the newly loaded data from the incremental pipeline
        incremental_dataset = incremental_pipeline.dataset()
    
        # Load the filtered 'orders' table into a DataFrame
        incremental_orders_df = incremental_dataset.orders.df()
    
        # Get the final number of rows
        num_rows = len(incremental_orders_df)
    
        mo.md(f"""
        ## 🔍 Final Answer
    
        After applying the incremental loading (starting from `2017-08-01`) and filtering out orders with `order_total > 500`, the resulting `orders` table contains **{num_rows}** rows.
        """)
        return

    _()
    return


@app.cell
def _(incremental_pipeline):
    # Access the newly loaded data from the incremental pipeline
    incremental_dataset = incremental_pipeline.dataset()

    # Load the filtered 'orders' table into a DataFrame
    incremental_orders_df = incremental_dataset.orders.df()

    # Get the final number of rows
    num_rows = len(incremental_orders_df)
    return


@app.cell
def _():
    return


@app.cell
def _():
    import dlt
    import requests
    return dlt, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## About the API: Jaffle Shop API

    In this demo, we’ll load data from the **Jaffle Shop API** — a fictional e-commerce service designed for testing and analytics workflows.
    It provides RESTful endpoints for common entities such as:

    - `customers`
    - `orders`
    - `items`
    - `products`
    - `supplies`


    This makes it a perfect sandbox for demonstrating data ingestion pipelines and transformations using `dlt`.

    Check out the Jaffle Shops documentation:
    https://jaffle-shop.scalevector.ai/docs#/
    """)
    return


@app.cell
def _():
    # sample url
    base_url = "https://jaffle-shop.scalevector.ai/api/v1/"
    endpoint = "orders"
    url = f"{base_url}{endpoint}"
    url
    return (url,)


@app.cell
def _(requests, url):
    # sample response
    response = requests.get(url)
    data = response.json()
    data[0]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Loading Data from REST APIs with `rest_api_source`

    If you're working with external APIs, `dlt` provides a built-in utility called **`rest_api_source`** to make REST data ingestion simple and production-ready.

    This function helps you:

    - Handle various pagination styles automatically (offset, cursor, page-based, etc.)
    - Manage retries and rate limits gracefully
    - Load data incrementally with built-in state tracking
    - Normalize and infer schema automatically

    It’s ideal for wrapping external services into reusable, declarative data sources.

    You can find a thorough explanation of how to use `dlt` to load data from a REST API in the official tutorial:
    https://dlthub.com/docs/tutorial/rest-api
    """)
    return


@app.cell
def _():
    from dlt.sources.rest_api import rest_api_source

    config = {"client": {
            "base_url": "https://jaffle-shop.scalevector.ai/api/v1/"
        },
        "resource_defaults": {
            "primary_key": "id",
            "endpoint": {
                "params": {
                    "page_size": 100
                }
            }
        },
        "resources": [
                {"name": "customers", "endpoint": {"path": "customers"}},
                {"name": "orders", "endpoint": {"path": "orders"}},
                {"name": "items", "endpoint": {"path": "items"}},
                {"name": "products", "primary_key": "sku", "endpoint": {"path": "products"}},
                {"name": "supplies", "endpoint": {"path": "supplies"}},
            ]
    }
    return config, rest_api_source


@app.cell
def _(config, rest_api_source):
    # create dlt source
    dlt_source = rest_api_source(config)
    dlt_source
    return (dlt_source,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    #### 🛑 Limiting API Pagination for the Demo

    To keep the demo lightweight and fast, we limit how many pages of data are fetched from each endpoint in the Jaffle Shop API. This is especially useful when working with paginated REST APIs that may return large datasets by default.
    """)
    return


@app.cell
def _(dlt_source):
    # limit for number of pages
    RESOURCE_LIMIT= 10

    # add limit to number of pages collected for each endpoint
    dlt_source.customers.add_limit(RESOURCE_LIMIT)
    dlt_source.orders.add_limit(RESOURCE_LIMIT)
    dlt_source.items.add_limit(RESOURCE_LIMIT)
    dlt_source.products.add_limit(RESOURCE_LIMIT)
    dlt_source.supplies.add_limit(RESOURCE_LIMIT)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 🔄 The `dlt.pipeline`: The Core of Every dlt Workflow

    At the heart of every `dlt` project is the **`dlt.pipeline`** — a high-level object that orchestrates the full process.

    With `dlt.pipeline`, you can:

    - Define the pipeline name, destination, and configuration
    - Run data through the sources
    - Automatically handle schema generation, state management, and data loading
    - Track and inspect run metrics and logs
    """)
    return


@app.cell
def _(dlt):
    # create pipeline object
    jaffle_shop_pipeline = dlt.pipeline(
            pipeline_name=f"jaffle_shop",
            destination="duckdb",
            dataset_name="jaffle_shop_dataset",
            progress="log"
        )
    return (jaffle_shop_pipeline,)


@app.cell
def _(dlt_source, jaffle_shop_pipeline):
    # run pipeline
    load_info = jaffle_shop_pipeline.run(dlt_source, write_disposition="replace")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📊 Accessing Pipeline and Dataset Info After a Run

    Once your `dlt` pipeline has completed, you can programmatically access its metadata and loaded data using the returned `pipeline` object.

    To learn more about accessing loaded datasets with dlt, check out the following: https://dlthub.com/docs/general-usage/dataset-access/dataset
    """)
    return


@app.cell
def _(jaffle_shop_pipeline):
    # Pipeline object
    jaffle_shop_pipeline
    return


@app.cell
def _(jaffle_shop_pipeline):
    dataset = jaffle_shop_pipeline.dataset()
    dataset # Displays basic metadata about the dataset
    return (dataset,)


@app.cell
def _(dataset):
    # List all user-defined table names in the schema (exclude internal _dlt tables)
    [table for table in dataset.schema.tables.keys() if table[:4]!="_dlt"]
    return


@app.cell
def _(dataset):
    # Load the 'orders' table into a DataFrame for inspection
    orders = dataset.orders
    orders_df = orders.df()
    orders_df.head()
    return


@app.cell
def _(dataset):
    # Load the 'orders__items' nested table into a DataFrame
    orders_items = dataset.orders__items
    orders_items_df = orders_items.df()
    orders_items_df.head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ⚙️ Transitioning from `dlt` to `dlt_assets`: Scheduling and Multiprocessing with Dagster

    So far, we’ve used **`dlt`** to build a working pipeline — ideal for data ingestion, transformation, and loading with minimal configuration.

    But what if you want to:

    - **Schedule your pipeline** to run hourly, daily, or on custom intervals?
    - **Parallelize execution** across multiple workers for faster performance?
    - Leverage a production-grade orchestration framework with a **UI for observability, logs, retries**, and more?

    That’s where **`dlt_assets`** comes in.

    `dlt_assets` lets you define your `dlt` pipelines as **Dagster assets**, enabling seamless integration with **Dagster’s orchestration engine**. This unlocks:

    - **Scheduling**: Run your pipelines on a defined cadence using Dagster’s scheduler
    - **Multiprocessing**: Use multiple workers to run pipeline components in parallel, improving throughput and scalability
    - **Production reliability**: Retry logic, logging, alerting, and monitoring — all via Dagster's tooling

    ---

    Next, we'll refactor our existing `dlt` pipeline into a `dlt_assets` asset and show how to connect it to Dagster.
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
