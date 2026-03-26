# /// script
# dependencies = [
#     "dlt-init-openapi",
#     "marimo",
# ]
# ///

import marimo

__generated_with = "0.17.8"
app = marimo.App()


@app.cell
def _():
    import subprocess
    return (subprocess,)


@app.cell
def _():
    # magic command not supported in marimo; please file an issue to add support
    # %load_ext autoreload
    # '%autoreload 2' command supported automatically in marimo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Automatically extract data from APIs with dlt and OpenAPI

    This Colab notebook demonstrates how to extract data from APIs in Python using dlt. It covers the usage of:
    - [data load tool (dlt) Python library](https://github.com/dlt-hub/dlt)
    - [dlt OpenAPI source generator](https://github.com/dlt-hub/dlt-init-openapi)
    - [REST API generic source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api)

    Let's start with a quick refresher.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # REST API Clients and `dlt`

    A REST API (Representational State Transfer Application Programming Interface) is a set of rules and conventions for building and interacting with web services. It allows different systems to communicate over the Internet using standard HTTP methods.

    Generating a REST API client in Python can be done in several ways. Two popular methods are:

    - Manually creating the client using the Requests library.
    - Automatically generating the client using an OpenAPI spec.

    Another method is using the [dlt rest_api source.](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api)

    [dlt](https://github.com/dlt-hub/dlt) is an open-source library that you can add to your Python scripts to load data from various and often messy data sources into well-structured, live datasets.

    The `rest_api` source in `dlt` is a versatile and generic tool designed to help you extract data from any REST API. By using a declarative configuration, you can define API endpoints, their relationships, pagination handling, and authentication methods effortlessly.

    > See this Colab: [dlt Rest API helpers tutorial](https://colab.research.google.com/drive/1qnzIM2N4iUL8AOX1oBUypzwoM3Hj5hhG?usp=sharing) for details.

    The team behind dlt has taken a step further by creating a REST API client generator based on the rest_api source and OpenAPI specifications: [`dlt-init-openapi`](https://pypi.org/project/dlt-init-openapi/).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # What is OpenAPI?

    The OpenAPI Specification (OAS) provides a standard way to describe the endpoints, request and response formats, authentication methods, and other details of an API. It uses JSON or YAML to define the API’s structure, making it both human-readable and easily parsable by machines.

    Here is an example of an OpenAPI specification in YAML format for a simple API that manages a list of items:
    ```
    openapi: 3.0.0
    info:
      title: Simple Item API
      description: A simple API to manage items.
      version: 1.0.0
    servers:
      - url: http://api.example.com/v1
    paths:
      /items:
        get:
          summary: List all items
          responses:
            '200':
              description: A list of items
              content:
                application/json:
                  schema:
                    type: array
                    items:
                      $ref: '#/components/schemas/Item'

      /items/{itemId}:
        get:
          summary: Get an item by ID
          parameters:
            - in: path
              name: itemId
              required: true
              schema:
                type: string
    ...
    ```

    Basic Information:

    - **openapi**: The version of the OpenAPI Specification being used.

    - **info**: Contains metadata about the API (title, description, version).

    - **servers**: Specifies the base URL for the API.

    Paths:

    - Defines the available endpoints and operations on each endpoint.
    - /items:
      - get: Lists all items.
    - /items/{itemId}:
      - get: Retrieves a specific item by ID.


    More details about OpenAPI can be found on the [official website](https://swagger.io/specification/).

    Now, let's see how to use `dlt-init-openapi` to generate a dlt source from an OpenAPI spec.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # dlt OpenAPI Source Creator: dlt-init-openapi

    `dlt-init-openapi` leverages the OpenAPI specification to create data pipelines that can handle complex data extraction tasks. Whether you're dealing with pagination, primary key discovery, endpoint relationship mapping, or authentication, this tool simplifies the process and automates much of the boilerplate code needed for data integration.

    `dlt-init-openapi` generates `dlt` pipelines from OpenAPI 3.x documents/specs using the [dlt `rest_api`](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) source. If not familiar with `dlt` or its data sources, please read:

    - [Getting started](https://dlthub.com/docs/getting-started) to learn the dlt basics.
    - [dlt rest_api](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api) to learn how our `rest_api` source works.

    Let's start by installing the [dlt-init-openapi](https://pypi.org/project/dlt-init-openapi/) package with `pip`:
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Installation
    """)
    return


@app.cell
def _(subprocess):
    # packages added via marimo's package management: dlt-init-openapi !pip install -q -U dlt-init-openapi
    #! dlt-init-openapi --version
    subprocess.call(['dlt-init-openapi', '--version'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Let me show you the magic: PokeAPI
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Initialize the source with OpenAPI Spec
    """)
    return


@app.cell
def _(subprocess):
    #! dlt-init-openapi pokemon --no-interactive --url https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml
    subprocess.call(['dlt-init-openapi', 'pokemon', '--no-interactive', '--url', 'https://raw.githubusercontent.com/cliffano/pokeapi-clients/ec9a2707ef2a85f41b747d8df013e272ef650ec5/specification/pokeapi.yml'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `dlt-init-openai` generated the folder `pokemon_pipeline` with source `pokemon` in it and `pokemon_pipeline.py` script with pipeline example.

    ```shell
    pokemon_pipeline/
    ├── .dlt/
    │   ├── config.toml     # dlt config, learn more at dlthub.com/docs
    │   └── secrets.toml    # your secrets, only needed for APIs with auth
    ├── pokemon/
    │   └── __init__.py     # your rest_api dictionary, learn more below
    ├── rest_api/
    │   └── ...             # rest_api copied from our verified sources repo
    ├── .gitignore
    ├── pokemon_pipeline.py # your pipeline file that you can execute
    ├── README.md           # a list of your endpoints with some additional info
    └── requirements.txt    # the pip requirements for your pipeline
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Run the pipeline
    """)
    return


@app.cell
def _():
    import dlt

    from pokemon_pipeline.pokemon import pokemon_source

    base_url = "https://pokeapi.co"

    if __name__ == "__main__":
        pipeline = dlt.pipeline(
            pipeline_name="pokemon_pipeline",
            destination='duckdb',
            dataset_name="pokemon_data",
            progress="log",
            export_schema_path="schemas/export"
        )
        source = pokemon_source(base_url)
        print(source.resources.keys())
        info = pipeline.run(source.with_resources("pokemon_list"))
        print(pipeline.last_trace.last_normalize_info)
        print(info)
    return dlt, pipeline


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Explore the data
    """)
    return


@app.cell
def _(display, pipeline):
    import duckdb
    from google.colab import data_table
    data_table.enable_dataframe_formatter()

    conn = duckdb.connect(f"{pipeline.pipeline_name}.duckdb")
    conn.sql(f"SET search_path = '{pipeline.dataset_name}'")
    data_table = conn.sql("SELECT * FROM pokemon").df()
    print(data_table.shape)
    display(data_table.head(5))
    return data_table, duckdb


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **It's a kind of magic**, isn't it?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Real-life example: Hacker News
    Yeah, we know that this APIs world is not so easy, let's consider some more realistic example - Hacker News API.

    API documentation: https://github.com/HackerNews/API?tab=readme-ov-file
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Initialize source with OpenAPI Spec

    We could find only community [OpenAPI/Swagger Spec](https://gist.github.com/wing328/44a6cb6c899feda4c2bd44747e9dcbc8) for Hacker News API. Let's give it a try.

    To convert Swagger to OpenAPI 3.0 we can use key `--allow-openapi-2`.
    """)
    return


app._unparsable_cell(
    r"""
    #! dlt-init-openapi hacker_news_api_swagger --no-interactive --allow-openapi-2 \
    subprocess.call(['dlt-init-openapi', 'hacker_news_api_swagger', '--no-interactive', '--allow-openapi-2', '\\'])
    --url \"https://gist.githubusercontent.com/wing328/44a6cb6c899feda4c2bd44747e9dcbc8/raw/737d3cf34daeef32280c66c5790c7de1a7b26905/hacker_news_api_swagger.json\"
    """,
    name="_"
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `dlt-init-openai` generates a `<source_name>_pipeline` folder in your working directory with the pipeline scripts in it. Let's see what files were generated and see what's inside the `hacker_news_api_swagger_pipeline.py` script.
    """)
    return


@app.cell
def _(subprocess):
    #! cd hacker_news_api_swagger_pipeline && ls && cat hacker_news_api_swagger_pipeline.py
    subprocess.call(['cd', 'hacker_news_api_swagger_pipeline', '&&', 'ls', '&&', 'cat', 'hacker_news_api_swagger_pipeline.py'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Run the draft pipeline
    """)
    return


@app.cell
def _(dlt):
    from hacker_news_api_swagger_pipeline.hacker_news_api_swagger import hacker_news_api_swagger_source
    base_url_1 = 'https://hacker-news.firebaseio.com/v0'
    if __name__ == '__main__':
        pipeline_1 = dlt.pipeline(pipeline_name='hacker_news_api_swagger_pipeline', destination='duckdb', dataset_name='hacker_news_api_swagger_data', progress='log', export_schema_path='schemas/export')
        source_1 = hacker_news_api_swagger_source(base_url_1)
        info_1 = pipeline_1.run(source_1)
        print(pipeline_1.last_trace.last_normalize_info)
        print(info_1)
    return (pipeline_1,)


@app.cell
def _(data_table, display, duckdb, pipeline_1):
    data_table.enable_dataframe_formatter()
    conn_1 = duckdb.connect(f'{pipeline_1.pipeline_name}.duckdb')
    conn_1.sql(f"SET search_path = '{pipeline_1.dataset_name}'")
    data_table_1 = conn_1.sql('SELECT * FROM item').df()
    display(data_table_1)
    return (data_table_1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Oh Gosh it's empty! Obviously the data was not loaded :(((
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Let's make it right
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **We don't believe in magic**, we believe only in correct and comprehensive specs. Unfortunately, HN OpenAPI Spec is quite poor, let's figure out how to make it work correctly.
    """)
    return


@app.cell
def _(subprocess):
    #! cd hacker_news_api_swagger_pipeline && ls && cat hacker_news_api_swagger/__init__.py
    subprocess.call(['cd', 'hacker_news_api_swagger_pipeline', '&&', 'ls', '&&', 'cat', 'hacker_news_api_swagger/__init__.py'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Start with "item" endpoint.

    > **Items** :
    Stories, comments, jobs, Ask HNs and even polls are just items. They're identified by their ids, which are unique integers, and live under `/v0/item/<id>`.


    "FILL_ME_IN" value seems to hint that something needs to be done with it.
    ```
    {
        "name": "item",
        "table_name": "item",
        "endpoint": {
            "data_selector": "$",
            "path": "/item/{id}.json",
            "params": {
                "id": "FILL_ME_IN",  # TODO: fill in path parameter
            },
        },
    },
    ```

    Look at the page [Define resource relationship.](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#define-resource-relationships)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Copy-paste our source config and fill missed fields.
    """)
    return


@app.cell
def _(dlt):
    from typing import List
    from dlt.extract.source import DltResource
    from rest_api import rest_api_source
    from rest_api.typing import RESTAPIConfig

    @dlt.source(name='hacker_news_api_swagger_source', max_table_nesting=2)
    def hacker_news_api_swagger_source_1(base_url: str=dlt.config.value) -> List[DltResource]:
        source_config: RESTAPIConfig = {'client': {'base_url': base_url}, 'resources': [{'name': 'item', 'table_name': 'item', 'primary_key': 'id', 'write_disposition': 'merge', 'endpoint': {'data_selector': '$', 'path': '/item/{id}.json', 'params': {'id': {'type': 'resolve', 'field': '$', 'resource': 'topstory'}, 'parallelized': True}, 'paginator': 'auto'}}, {'name': 'maxitem', 'table_name': 'maxitem', 'endpoint': {'data_selector': '$', 'path': '/maxitem.json', 'paginator': 'auto'}}, {'name': 'topstory', 'table_name': 'topstory', 'endpoint': {'data_selector': '$', 'path': '/topstories.json', 'paginator': 'auto'}}, {'name': 'update', 'table_name': 'update', 'endpoint': {'data_selector': 'items', 'path': '/updates.json', 'paginator': 'auto'}}, {'name': 'user', 'table_name': 'user', 'primary_key': 'id', 'write_disposition': 'merge', 'endpoint': {'data_selector': '$', 'path': '/user/{id}.json', 'params': {'id': 'FILL_ME_IN'}, 'paginator': 'auto'}}]}
        return rest_api_source(source_config)  # source configuration  # TODO: fill in path parameter
    return (
        DltResource,
        List,
        RESTAPIConfig,
        hacker_news_api_swagger_source_1,
        rest_api_source,
    )


@app.cell
def _(dlt, hacker_news_api_swagger_source_1):
    base_url_2 = 'https://hacker-news.firebaseio.com/v0'
    if __name__ == '__main__':
        pipeline_2 = dlt.pipeline(pipeline_name='hacker_news_api_swagger_pipeline', destination='duckdb', dataset_name='hacker_news_api_swagger_data', full_refresh=True, export_schema_path='schemas/export')
        source_2 = hacker_news_api_swagger_source_1(base_url_2)
        info_2 = pipeline_2.run(source_2.with_resources('topstory', 'item'))
        print(pipeline_2.last_trace.last_normalize_info)
        print(info_2)
    return (pipeline_2,)


@app.cell
def _(data_table_1, display, duckdb, pipeline_2):
    data_table_1.enable_dataframe_formatter()
    conn_2 = duckdb.connect(f'{pipeline_2.pipeline_name}.duckdb')
    conn_2.sql(f"SET search_path = '{pipeline_2.dataset_name}'")
    data_table_2 = conn_2.sql('SELECT * FROM item').df().head()
    display(data_table_2)
    return (data_table_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Well, it was not so hard as well, but we didn't even try to implement pagination, in HN case it's tricky and probably even easier to do without any generator.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Customization: Stripe API

    Let's look at an example where a generator would be really helpful: Stripe API.

    [Stripe](https://stripe.com/en-de) is a leading payment processing platform known for its powerful and flexible APIs, which enable businesses to seamlessly handle online payments and transactions. One of the standout features of Stripe is its excellent documentation, which is widely regarded as one of the best in the industry. Additionally, Stripe provides a **comprehensive OpenAPI specification.**


    Spec: https://github.com/stripe/openapi
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Initialize the source with Stripe OpenAPI Spec

      This will take a while, you have time to make a coffee...
    """)
    return


@app.cell
def _(subprocess):
    #! dlt-init-openapi stripe --no-interactive --url "https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json"
    subprocess.call(['dlt-init-openapi', 'stripe', '--no-interactive', '--url', 'https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pipeline was generated, 247 endpoints were found, but you remember **we do not believe in magic** and we need to make sure that source was generated correctly. Also we need to provide `base_url`, secrets, query parameters, etc.

    Stripe is well known for its high-quality API and documentation, so you will find
    [here](https://docs.stripe.com/api) all required information:
    - base url;
    - authentication type;
    - response example;
    - curl example;
    - pagination type;
    - rate limits;
    - available query parameters.


    Walk through this [dlt REST API tutorial](https://colab.research.google.com/drive/1qnzIM2N4iUL8AOX1oBUypzwoM3Hj5hhG?usp=sharing) to learn how to investigate API documentation and avoid struggling with building a REST API client.

    We're gonna explore a few endpoints: [customers list](https://docs.stripe.com/api/customers/list), [subscriptions list](https://docs.stripe.com/api/subscriptions/list).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Base URL

    First, we check our autogenerated `config.toml` file. We can see that base_url was succesfully taken from spec, so we can skip this step.
    """)
    return


@app.cell
def _(subprocess):
    #! cat stripe_pipeline/.dlt/config.toml
    subprocess.call(['cat', 'stripe_pipeline/.dlt/config.toml'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Authentication

    As you know, to gain access to the API you will need a secret token. [Here is a guide](https://docs.stripe.com/keys) how to get the key.


    Let's explore the [Stripe API Authentication methods.](https://docs.stripe.com/stripe-apps/api-authentication)

    It says here:

    >Authentication to the API is performed via HTTP Basic Auth. Provide your API key as the basic auth username value. You do not need to provide a password.

    Let's check what type of authentication was generated by the tool:
    """)
    return


@app.cell
def _(subprocess):
    #! cd stripe_pipeline && head --lines=50 stripe/__init__.py
    subprocess.call(['cd', 'stripe_pipeline', '&&', 'head', '--lines=50', 'stripe/__init__.py'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
    "auth": {
        "type": "http_basic",
    ...
    ```
    What a surprise! The authentication method was carefully taken from the specification and correctly added to the configuration. We don't need to change anything.

    The REST API source supports various authentication methods, such as token-based, query parameters, basic auth, etc. All available authentication types you can find at [dlt rest_api documentation.](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#authentication)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Pagination

    Well, let's take a look at how the tool coped with pagination.
    First, we will find out what type of pagination the Stripe API has:

    >Stripe’s list API methods use **cursor-based pagination** through the `starting_after` and `ending_before` parameters. Both parameters accept an existing object `ID` value (see below) and return objects in reverse chronological order.

    Unfortunately, the generator detected the paginator incorrectly:

    ```
    "paginator": {
        "type": "page_number",
        "page_param": "page",
        "total_path": "\",
        "maximum_page": 20,
    },
    ```
    We can easily fix it, go to [the rest_api documentation](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#pagination) and find correct pagination type:

    >**JSONResponseCursorPaginator** handles pagination based on a cursor in the JSON response. \
    *Parameters*: \
    `cursor_path`: A JSONPath expression pointing to the cursor in the JSON response. This cursor is used to fetch subsequent pages. Defaults to "cursors.next".\
    `cursor_param`: The query parameter used to send the cursor value in the next request. Defaults to "after".

    ```
    "paginator": {
        "type": "cursor",
        "cursor_path": "id",
        "cursor_param": "starting_after",
    },
    ```

    We cared about the basic requirements, let's try to run the pipeline!

    > Due to the fact that the Stripe API contains a large number of endpoints and the source script is very large, we will copy and paste part of the source configuration from the generated `stripe_pipeline/stripe/__init__.py` script into a Notebook cell below and add the above modifications right here.
    """)
    return


@app.cell
def _(DltResource, List, RESTAPIConfig, dlt, rest_api_source):
    @dlt.source(name='stripe_source', max_table_nesting=2)
    def stripe_source(username: str=dlt.secrets.value, password: str=dlt.secrets.value, base_url: str=dlt.config.value) -> List[DltResource]:
        source_config: RESTAPIConfig = {'client': {'base_url': base_url, 'auth': {'type': 'http_basic', 'username': username, 'password': password}, 'paginator': {'type': 'cursor', 'cursor_path': 'id', 'cursor_param': 'starting_after'}}, 'resources': [{'name': 'get_customers', 'table_name': 'customer', 'primary_key': 'id', 'write_disposition': 'merge', 'endpoint': {'data_selector': 'data', 'path': '/v1/customers', 'params': {}}}, {'name': 'get_subscriptions', 'table_name': 'subscription', 'primary_key': 'id', 'write_disposition': 'merge', 'endpoint': {'data_selector': 'data', 'path': '/v1/subscriptions', 'params': {}}}]}
        return rest_api_source(source_config)  # source configuration  # Paginator configuration  # Pagination type: cursor-based pagination  # Path to the cursor field in the response data  # Query parameter name to send the cursor value in the request  # <p>Returns a list of your customers. The customers are returned sorted by creation date, with the most recent customers appearing first.</p>  # the parameters below can optionally be configured  # "created": "OPTIONAL_CONFIG",  # "email": "OPTIONAL_CONFIG",  # "ending_before": "OPTIONAL_CONFIG",  # "expand": "OPTIONAL_CONFIG",  # "limit": "OPTIONAL_CONFIG",  # "starting_after": "OPTIONAL_CONFIG",  # "test_clock": "OPTIONAL_CONFIG",  # <p>By default, returns a list of subscriptions that have not been canceled. In order to list canceled subscriptions, specify <code>status=canceled</code>.</p>  # the parameters below can optionally be configured  # "automatic_tax": "OPTIONAL_CONFIG",  # "collection_method": "OPTIONAL_CONFIG",  # "created": "OPTIONAL_CONFIG",  # "current_period_end": "OPTIONAL_CONFIG",  # "current_period_start": "OPTIONAL_CONFIG",  # "customer": "OPTIONAL_CONFIG",  # "ending_before": "OPTIONAL_CONFIG",  # "expand": "OPTIONAL_CONFIG",  # "limit": "OPTIONAL_CONFIG",  # "price": "OPTIONAL_CONFIG",  # "starting_after": "OPTIONAL_CONFIG",  # "status": "OPTIONAL_CONFIG",  # "test_clock": "OPTIONAL_CONFIG",
    return (stripe_source,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Run the pipeline
    """)
    return


@app.cell
def _(dlt, stripe_source):
    import os
    from google.colab import userdata
    api_key = os.getenv('STRIPE_SECRET_KEY', userdata.get('STRIPE_SECRET_KEY'))
    base_url_3 = 'https://api.stripe.com/'
    pipeline_3 = dlt.pipeline(pipeline_name='stripe_pipeline', destination='duckdb', dataset_name='stripe_data', progress='log', export_schema_path='schemas/export')
    source_3 = stripe_source(username=api_key, password='', base_url=base_url_3)
    print(source_3.resources.keys())
    return os, pipeline_3, source_3, userdata


@app.cell
def _(pipeline_3, source_3):
    info_3 = pipeline_3.run(source_3.with_resources('get_customers', 'get_subscriptions'))
    print(pipeline_3.last_trace.last_normalize_info)
    print(info_3)
    return


@app.cell
def _(data_table_2, display, duckdb, pipeline_3):
    data_table_2.enable_dataframe_formatter()
    conn_3 = duckdb.connect(f'{pipeline_3.pipeline_name}.duckdb')
    conn_3.sql(f"SET search_path = '{pipeline_3.dataset_name}'")
    data_table_3 = conn_3.sql('SELECT * FROM customer').df().head()
    display(data_table_3)
    return (conn_3,)


@app.cell
def _(conn_3, display):
    data_table_4 = conn_3.sql('SELECT * FROM subscription').df().head()
    display(data_table_4)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Incremental loading

    Some APIs provide a way to fetch only new or changed data (most often by using a timestamp field like `updated_at`, `created_at`, or incremental IDs). This is called incremental loading and is very useful as it allows you to reduce the load time and the amount of data transferred.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We wanna load data from [customers list endpoint](https://docs.stripe.com/api/customers/list) incrementally. Let's configure it.

    To turn an endpoint into an incremental one, we must define a special parameter in the `params` section of [endpoint configuration](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api#endpoint-configuration).
    """)
    return


@app.cell
def _(subprocess):
    #! grep -C 10 ' "path": "/v1/customers",' /content/stripe_pipeline/stripe/__init__.py
    subprocess.call(['grep', '-C', '10', ' "path": "/v1/customers",', '/content/stripe_pipeline/stripe/__init__.py'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Uncomment `created` parameter and turn it into incremental:

    ```python
    # <p>Returns a list of your customers. The customers are returned sorted by creation date, with the most recent customers appearing first.</p>
    {
        "name": "get_customers",
        "table_name": "customer",
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {
            "data_selector": "data",
            "path": "/v1/customers",
            "params": {
                # the parameters below can optionally be configured
                "created": {  # Limits the fetched issues to those created since a specific date and time
                    "type": "incremental",
                    "cursor_path": "created", # Path to the field used for tracking new customers
                    "initial_value": 1590589285, # Initial value for the cursor when fetching data for the first time
                },
                # "email": "OPTIONAL_CONFIG",
                # "ending_before": "OPTIONAL_CONFIG",
                # "expand": "OPTIONAL_CONFIG",
                # "limit": "OPTIONAL_CONFIG",
                # "starting_after": "OPTIONAL_CONFIG",
                # "test_clock": "OPTIONAL_CONFIG",
            },
        },
    },
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Replace the old code with updated.

    > Due to the fact that the Stripe API contains a large number of endpoints and the source script is very large, we will copy and paste part of the source configuration from the generated `stripe_pipeline/stripe/__init__.py` script into a Notebook cell and add the above modifications right here.
    """)
    return


@app.cell
def _(DltResource, List, RESTAPIConfig, dlt, rest_api_source):
    @dlt.source(name='stripe_source', max_table_nesting=2)
    def stripe_source_1(username: str=dlt.secrets.value, password: str=dlt.secrets.value, base_url: str=dlt.config.value) -> List[DltResource]:
        source_config: RESTAPIConfig = {'client': {'base_url': base_url, 'auth': {'type': 'http_basic', 'username': username, 'password': password}, 'paginator': {'type': 'cursor', 'cursor_path': 'id', 'cursor_param': 'starting_after'}}, 'resources': [{'name': 'get_customers', 'table_name': 'customer', 'primary_key': 'id', 'write_disposition': 'merge', 'endpoint': {'data_selector': 'data', 'path': '/v1/customers', 'params': {'created': {'type': 'incremental', 'cursor_path': 'created', 'initial_value': 1590589285}}}}]}
        return rest_api_source(source_config)  # the parameters below can optionally be configured  # Limits the fetched issues to those created since a specific date and time  # Path to the field used for tracking new customers  # Wednesday, May 27, 2020 2:21:25 PM # Initial value for the cursor when fetching data for the first time  # ...
    return (stripe_source_1,)


@app.cell
def _(dlt, os, stripe_source_1, userdata):
    api_key_1 = os.getenv('STRIPE_SECRET_KEY', userdata.get('STRIPE_SECRET_KEY'))
    base_url_4 = 'https://api.stripe.com/'
    pipeline_4 = dlt.pipeline(pipeline_name='incremental_stripe_pipeline', destination='duckdb', dataset_name='incremental_stripe_data', progress='log', export_schema_path='schemas/export')
    source_4 = stripe_source_1(username=api_key_1, password='', base_url=base_url_4)
    info_4 = pipeline_4.run(source_4.with_resources('get_customers'))
    print(pipeline_4.last_trace.last_normalize_info)
    print(info_4)
    return pipeline_4, source_4


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Run the pipeline again and make sure that the data has not been loaded again:
    """)
    return


@app.cell
def _(pipeline_4, source_4):
    info_5 = pipeline_4.run(source_4.with_resources('get_customers'))
    print(pipeline_4.last_trace.last_normalize_info)
    print(info_5)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Links

    More Information about how to build efficient data pipelines you can find in our official documentation:
    - `dlt` [Getting Started](https://dlthub.com/docs/getting-started),
    - [REST API Source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api),
    - [REST API Client](https://dlthub.com/docs/general-usage/http/rest-client),
    - `dlt` [Sources](https://dlthub.com/docs/general-usage/source) and [Resources](https://dlthub.com/docs/general-usage/resource),
    - [Incremental loading](https://dlthub.com/docs/general-usage/incremental-loading),
    - Our pre-built [Verified Sources](https://dlthub.com/docs/dlt-ecosystem/verified-sources/),
    - Available [Destinations](https://dlthub.com/docs/dlt-ecosystem/destinations/).


    ## **[Give `dlt` a ⭐ on GitHub](https://github.com/dlt-hub/dlt)**
    ## **[Join the `dlt` community on Slack](https://dlthub.com/community)**
    """)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
