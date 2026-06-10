"""This is a marimo notebook, which can be opened using:

```shell
marimo edit ./1_basics/3_jaffleshop_notebook.py
```
"""

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")

with app.setup:
    import pathlib
    import typing

    import dlt
    import marimo as mo
    import ibis
    from ibis import ir
    from dlt.sources.filesystem import filesystem, read_parquet
    from dlt.sources.rest_api import rest_api_resources


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    # `dlt` Jaffle Shop (tasty 😋)

    In this notebook, you'll learn how the `@dlt.hub.transformation` allow you write ELT pipelines that are crisp (like good jaffle).

    ## Declare, Organize, Execute, Review

    Here's a simple framework to define data pipelines:

    - **Declare** components you want to run (`@dlt.resource`, `@dlt.hub.transformation`). Efficient iterations and testing are key.
    - **Organize** components into meaningful units (into a `@dlt.source`, a DAG). You're solidifying your code.
    - **Execute** your pipeline to move data. This is an expensive operation that acts on data.
    - **Review** the execution results. This includes validating the schema and data.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    # Extract and Load (EL)
    During the **Extract** and **Load** steps, also called **ingestion**, we're moving data from different systems to a central location (e.g., data warehouse, data lakehouse, cloud bucket) for further processing.

    Here, we'll be retrieving customers, products, and orders information from our internal REST API. Separately, we'll be loading payments from a file of records stored in a filesystem.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""## Declare""")
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ### REST API source
    We use dlt's [declarative interface for REST API](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api/basic). The function `rest_api_source()` already assembles multiple resource defined under `resources`
    """
    )
    return


@app.cell
def _():
    jaffle_rest_resources: list = rest_api_resources({
        "client": {
            "base_url": "https://jaffle-shop.dlthub.com/api/v1",
            "paginator": {"type": "header_link"},
        },
        "resources": [  # individual resources
            "customers",
            "products",
            "orders",
        ],
        # set the time range for all resources
        "resource_defaults": {
            "endpoint": {
                "params": {
                    "start_date": "2017-01-01",
                    "end_date": "2017-01-15",
                },
            },
        }
    })
    return (jaffle_rest_resources,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""Access a single resource and explore its configuration""")
    return


@app.cell
def _(jaffle_rest_resources: list):
    product_resource = jaffle_rest_resources[1]
    product_resource
    return (product_resource,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""Retrieve data from the resource. Using `list()` on the object exhausts the generator""")
    return


@app.cell
def _(product_resource):
    _products = list(product_resource)
    _products[:3]  # show the first 3
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""### Filesystem source""")
    return


@app.cell
def _():
    files_directory = pathlib.Path(__file__).parent / "data"

    payments_files_resource = filesystem(
        bucket_url=str(files_directory), file_glob="*payments.parquet"
    )
    payments_files_resource
    return (payments_files_resource,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""When accessing `filesystem()`, we see that it returns files metadata without opening them.""")
    return


@app.cell
def _(payments_files_resource):
    _payments_files = list(payments_files_resource)
    _payments_files[:1]  # show the first
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    We're piping resources to process the file further! it opens the parquet and loads the table with pyarrow
    `read_parquet()` is applied to the file and reads it in chunks of 50 (default config)
    """
    )
    return


@app.cell
def _(payments_files_resource):
    payments_resource = (payments_files_resource | read_parquet).with_name(
        "payments"
    )
    _payments = list(payments_resource)
    _payments[:2]  # show the first 2
    return (payments_resource,)


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ## Organize
    Once you have all of your `dlt.Resource` defined, you can group resources into one or more `dlt.Source`.

    This allows you to organize related resources. It makes it convenient to configure and execute them together.
    """
    )
    return


@app.cell
def _(jaffle_rest_resources: list, payments_resource):
    @dlt.source
    def jaffle_shop_raw_data():
        """Raw data about the Jaffle Shop operations."""
        return (*jaffle_rest_resources, payments_resource)
    return (jaffle_shop_raw_data,)


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ## Execute
    We create a destination to a local DuckDB file. 

    Then, we create a `dlt.Pipeline` named `jaffle_ingest` and execute it. This pipeline and its metadata will be associated with the EL steps.
    """
    )
    return


@app.cell
def _():
    destination = dlt.destinations.duckdb("local_jaffle.duckdb")

    jaffle_ingest_pipe = dlt.pipeline("jaffle_ingest", destination=destination)
    return destination, jaffle_ingest_pipe


@app.cell
def _(jaffle_ingest_pipe, jaffle_shop_raw_data):
    ingest_load_info = jaffle_ingest_pipe.run(jaffle_shop_raw_data())
    ingest_load_info
    return (ingest_load_info,)


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ## Review
    Once you executed the pipeline and moved data, you want to validate results are as expected.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ### Pipeline
    `Pipeline.execute()` produces a `LoadInfo` object full of useful operational metadata about execution (file size, job duraction, etc.). This can be useful for debugging failed pipelines or emit metadata to other systems.
    """
    )
    return


@app.cell
def _(ingest_load_info):
    mo.inspect(ingest_load_info)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""You can also inspect the schema of the data produced by the pipeline.""")
    return


@app.cell
def _(jaffle_ingest_pipe):
    jaffle_ingest_pipe.default_schema
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ### Dataset
    The `dlt.Dataset` object allows to retrieve and interact with the data produced by `pipeline.run()`. You can retrieve the dataset directly from the pipeline.
    """
    )
    return


@app.cell
def _(jaffle_ingest_pipe):
    raw_dataset = jaffle_ingest_pipe.dataset()
    raw_dataset
    return (raw_dataset,)


@app.cell
def _(raw_dataset):
    raw_dataset.tables
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""Notebooks will provide autocompletions for table names and column names when you're typing `dlt.Dataset[""]` and `dlt.Relation[""]` respectively.""")
    return


@app.cell
def _(raw_dataset):
    raw_dataset["customers"].columns
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""The `dlt.Schema` of the dataset is the same as the pipeline schema. This can be confirmed by their equal `version_hash`""")
    return


@app.cell
def _(jaffle_ingest_pipe, raw_dataset):
    raw_dataset.schema.version_hash == jaffle_ingest_pipe.default_schema.version_hash
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""A `dlt.Relation` is a reference to a table found on the `dlt.Dataset`. The relation is a lazy object. You can use it to retrieve the table schema or get the data from the dataset.""")
    return


@app.cell
def _(raw_dataset):
    orders_rel = raw_dataset.table("orders")
    orders_rel.schema
    return (orders_rel,)


@app.cell
def _(orders_rel):
    orders_rel.df()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""Bonus: If you're running this notebook with `marimo`, you can view the table schema in an interactive GUI inside the `Datasource` panel. To enable this feature, you need to assign the `ibis` connection from the `dlt.Dataset` to a variable.""")
    return


@app.cell
def _(raw_dataset):
    ibis_con = raw_dataset.ibis()
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    # Transform (T)
    After ingesting data to a central location via EL, we can **Transform** it. This include: data validation, data clean up, aggregations, metrics, and more. 

    In `dlt` terms, a **transformation** is an any operation applied on a `dlt.Dataset`.

    In this tutorial, we'll be joining customers and orders tables and computing the total spendings per customer.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ## Declare
    We can start by accessing the `raw_dataset` we just produced and start iterate over our query.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ### Write a query
    We use the [ibis](https://github.com/ibis-project/ibis) library, which allows us to write SQL queries using a Python dataframe API. Operations are lazy and return a query plan that can be printed.
    """
    )
    return


@app.cell
def _(raw_dataset):
    orders = raw_dataset.table("orders").to_ibis()
    orders  # this prints the schema of the `orders` table
    return (orders,)


@app.cell
def _(orders):
    customer_orders_query = orders.group_by("customer_id").aggregate(
        first_order=orders.ordered_at.min(),
        most_recent_order=orders.ordered_at.max(),
        number_of_orders=orders.id.count(),
    )
    customer_orders_query  # we see the query plan
    return (customer_orders_query,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""By passing the query to the `dlt.Dataset`, we retrieve a new `dlt.Relation` that can execute the query.""")
    return


@app.cell
def _(customer_orders_query, raw_dataset):
    _customer_orders_rel = raw_dataset(customer_orders_query)
    # or use `raw_dataset.__call__(customer_orders_query)`
    _customer_orders_rel.df()
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ### Write a `@dlt.transformation`

    To streamline this process, we can define the query inside a `@dlt.hub.transformation`.

    The first argument of the function must be a `dlt.Dataset` object where the data should be outputed. The function must use a `yield` statement.
    """
    )
    return


@app.function
@dlt.hub.transformation
def customer_orders(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
    """Aggregate statistics about previous customer orders"""
    orders = dataset.table("orders").to_ibis()
    yield orders.group_by("customer_id").aggregate(
        first_order=orders.ordered_at.min(),
        most_recent_order=orders.ordered_at.max(),
        number_of_orders=orders.id.count(),
    )


@app.cell(hide_code=True)
def _():
    mo.md(r"""Calling the transformation function with a dataset produces a `dlt.Relation`.""")
    return


@app.cell
def _(raw_dataset):
    customers_orders_rel = list(customer_orders(raw_dataset))[0]
    customers_orders_rel
    return (customers_orders_rel,)


@app.cell
def _(customers_orders_rel):
    customers_orders_rel.schema
    return


@app.cell
def _(customers_orders_rel):
    customers_orders_rel.df()
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""### Define another transformations""")
    return


@app.function
@dlt.hub.transformation
def customer_payments(dataset: dlt.Dataset) -> typing.Iterator[ir.Table]:
    """Customer order and payment info"""
    orders = dataset.table("orders").to_ibis()
    payments = dataset.table("payments").to_ibis()
    yield (
        payments.left_join(orders, payments.order_id == orders.id)
        .group_by(orders.customer_id)
        .aggregate(total_amount=ibis._.amount.sum())
    )


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ## Organize
    By organizing our `@dlt.hub.transformation` in a `@dlt.source`, we can set their execution order. Also, it ensures they are executed as a single transaction; if a transformation fails, no data will be written to destination.
    """
    )
    return


@app.function
@dlt.source
def customers_metrics(raw_dataset: dlt.Dataset) -> list:
    return [
        customer_orders(raw_dataset),
        customer_payments(raw_dataset),
    ]


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ## Execute
    Despite iterating over our queries and executing transformations in the notebook, nothing has been pushed to destination yet. Only after `pipeline.run()` the data will be written to the destination.

    We create a new pipeline `jaffle_transform` that will be associated with the T step. We set the destination to the same local DuckDB instance we used before.
    """
    )
    return


@app.cell
def _(destination):
    jaffle_transform_pipe = dlt.pipeline("jaffle_transform", destination=destination)
    return (jaffle_transform_pipe,)


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    We retrieve the `dlt.Dataset` from the transform pipeline because we will need it as input. 

    It currently contains no data tables.
    """
    )
    return


@app.cell
def _(jaffle_transform_pipe, raw_dataset):
    transform_load_info = jaffle_transform_pipe.run(customers_metrics(raw_dataset))
    transform_load_info
    return


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ## Review

    You can now explore transformation results. Tables are now written to the processed dataset.
    """
    )
    return


@app.cell
def _(jaffle_transform_pipe):
    processed_dataset = jaffle_transform_pipe.dataset()
    processed_dataset.schema
    return


if __name__ == "__main__":
    app.run()
