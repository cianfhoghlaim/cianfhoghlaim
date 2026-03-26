# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "polars>=1.0.0",
#     "pandas>=2.0.0",
#     "altair>=5.0.0",
#     "python-dotenv>=1.0.0",
#     "pyiceberg>=0.7.0",
#     "pyarrow>=17.0.0",
#     "boto3>=1.35.0",
# ]
# ///

import marimo

__generated_with = "0.17.7"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Cloudflare Data Operations: R2 + DuckLake + Iceberg

    This notebook demonstrates Cloudflare's data infrastructure:

    1. **R2 Storage** - S3-compatible object storage with AWS SigV4 signing
    2. **D1 Database** - SQLite at the edge for structured data
    3. **DuckLake** - Lightweight lakehouse format on R2
    4. **PyIceberg** - Table format for analytics with time travel

    > Based on patterns from `/data/examples/cloudflare/` and `/data/examples/duckdb/cloudflare-ducklake/`
    """)
    return


@app.cell
def _():
    import marimo as mo
    import os
    from dotenv import load_dotenv

    load_dotenv()
    return mo, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Cloudflare API Configuration

    Configure your Cloudflare credentials to access R2, D1, and other services.
    """)
    return


@app.cell
def _(mo, os):
    # Configuration inputs
    cf_account_id = mo.ui.text(
        value=os.environ.get("CF_ACCOUNT_ID", ""),
        label="Cloudflare Account ID",
        placeholder="Your Cloudflare Account ID"
    )
    cf_api_token = mo.ui.text(
        value=os.environ.get("CF_API_TOKEN", ""),
        label="Cloudflare API Token",
        placeholder="Your Cloudflare API Token",
        kind="password"
    )

    mo.hstack([cf_account_id, cf_api_token], justify="start")
    return cf_account_id, cf_api_token


@app.cell
def _(cf_account_id, cf_api_token):
    CF_ACCOUNT_ID = cf_account_id.value
    CF_API_TOKEN = cf_api_token.value
    CF_API_BASE = "https://api.cloudflare.com"

    print(f"Account configured: {'✅' if CF_ACCOUNT_ID else '❌'}")
    print(f"Token configured: {'✅' if CF_API_TOKEN else '❌'}")
    return CF_ACCOUNT_ID, CF_API_BASE, CF_API_TOKEN


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. R2 Storage Operations

    R2 provides S3-compatible object storage. Operations require AWS SigV4 signing.
    """)
    return


@app.cell
def _():
    import json
    import hashlib
    import hmac
    import datetime
    import urllib.parse
    from urllib.request import Request, urlopen
    import pandas as pd
    return Request, datetime, hashlib, hmac, json, pd, urlopen


@app.cell
def _(
    CF_ACCOUNT_ID,
    CF_API_BASE,
    CF_API_TOKEN,
    Request,
    json,
    mo,
    pd,
    urlopen,
):
    def list_r2_buckets(account_id: str, token: str) -> pd.DataFrame:
        """List all R2 buckets in the account."""
        url = f"{CF_API_BASE}/client/v4/accounts/{account_id}/r2/buckets?per_page=100"
        request = Request(url, headers={"Authorization": f"Bearer {token}"})

        try:
            response = urlopen(request)
            data = json.load(response)
            if data.get("success") and data.get("result", {}).get("buckets"):
                return pd.DataFrame(data["result"]["buckets"])
            return pd.DataFrame()
        except Exception as e:
            print(f"Error listing buckets: {e}")
            return pd.DataFrame()

    # List buckets
    if CF_ACCOUNT_ID and CF_API_TOKEN:
        r2_buckets = list_r2_buckets(CF_ACCOUNT_ID, CF_API_TOKEN)
        if len(r2_buckets) > 0:
            mo.ui.table(r2_buckets, selection=None)
        else:
            mo.md("*No R2 buckets found or API error*")
    else:
        r2_buckets = pd.DataFrame()
        mo.md("*Configure credentials above*")
    return (r2_buckets,)


@app.cell
def _(mo, r2_buckets):
    # Bucket selector for operations
    bucket_options = r2_buckets["name"].tolist() if len(r2_buckets) > 0 else ["my-bucket"]

    bucket_selector = mo.ui.dropdown(
        options=bucket_options,
        value=bucket_options[0] if bucket_options else None,
        label="Select R2 Bucket"
    )
    bucket_selector
    return


@app.cell
def _(datetime, hashlib, hmac, os):
    def create_aws_sigv4_headers(
        method: str,
        host: str,
        path: str,
        access_key: str,
        secret_key: str,
        region: str = "auto",
        service: str = "s3",
        payload: bytes = b""
    ) -> dict:
        """
        Create AWS SigV4 signed headers for R2 requests.

        R2 uses AWS SigV4 signing for S3-compatible API access.
        """
        now = datetime.datetime.now(datetime.UTC)
        request_datetime = now.strftime('%Y%m%dT%H%M%SZ')
        request_date = now.strftime('%Y%m%d')

        # Payload hash
        payload_hash = hashlib.sha256(payload).hexdigest()

        # Canonical headers
        canonical_headers = '\n'.join([
            f'host:{host}',
            f'x-amz-content-sha256:{payload_hash}',
            f'x-amz-date:{request_datetime}\n'
        ])
        signed_headers = 'host;x-amz-content-sha256;x-amz-date'

        # Canonical request
        canonical_request = '\n'.join([
            method,
            path,
            '',  # query string
            canonical_headers,
            signed_headers,
            payload_hash
        ])

        # String to sign
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = f'{request_date}/{region}/{service}/aws4_request'
        hashed_canonical = hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

        string_to_sign = '\n'.join([
            algorithm,
            request_datetime,
            credential_scope,
            hashed_canonical
        ])

        # Signing key derivation
        def hmac_sha256(key, msg):
            return hmac.new(key, msg=msg.encode('utf-8'), digestmod=hashlib.sha256).digest()

        k_date = hmac_sha256(('AWS4' + secret_key).encode('utf-8'), request_date)
        k_region = hmac_sha256(k_date, region)
        k_service = hmac_sha256(k_region, service)
        k_signing = hmac_sha256(k_service, 'aws4_request')

        # Final signature
        signature = hmac.new(
            k_signing,
            msg=string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Authorization header
        authorization = (
            f'{algorithm} Credential={access_key}/{credential_scope}, '
            f'SignedHeaders={signed_headers}, Signature={signature}'
        )

        return {
            'x-amz-date': request_datetime,
            'x-amz-content-sha256': payload_hash,
            'Authorization': authorization
        }

    # Check for R2 credentials
    R2_ACCESS_KEY = os.environ.get("R2_ACCESS_KEY_ID", "")
    R2_SECRET_KEY = os.environ.get("R2_SECRET_ACCESS_KEY", "")

    print(f"R2 Access Key configured: {'✅' if R2_ACCESS_KEY else '❌'}")
    print(f"R2 Secret Key configured: {'✅' if R2_SECRET_KEY else '❌'}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. D1 Database Operations

    D1 provides SQLite at the edge. Execute SQL queries via the Cloudflare API.
    """)
    return


@app.cell
def _(
    CF_ACCOUNT_ID,
    CF_API_BASE,
    CF_API_TOKEN,
    Request,
    json,
    mo,
    pd,
    urlopen,
):
    def list_d1_databases(account_id: str, token: str) -> pd.DataFrame:
        """List all D1 databases in the account."""
        url = f"{CF_API_BASE}/client/v4/accounts/{account_id}/d1/database"
        request = Request(url, headers={"Authorization": f"Bearer {token}"})

        try:
            response = urlopen(request)
            data = json.load(response)
            if data.get("success") and data.get("result"):
                return pd.DataFrame(data["result"])
            return pd.DataFrame()
        except Exception as e:
            print(f"Error listing D1 databases: {e}")
            return pd.DataFrame()

    def query_d1(account_id: str, database_id: str, token: str, sql: str) -> dict:
        """Execute SQL query on a D1 database."""
        url = f"{CF_API_BASE}/client/v4/accounts/{account_id}/d1/database/{database_id}/query"
        payload = json.dumps({'sql': sql}).encode()
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            data=payload,
            method='POST'
        )

        try:
            response = urlopen(request)
            return json.load(response)
        except Exception as e:
            return {"success": False, "errors": [{"message": str(e)}]}

    # List D1 databases
    if CF_ACCOUNT_ID and CF_API_TOKEN:
        d1_databases = list_d1_databases(CF_ACCOUNT_ID, CF_API_TOKEN)
        if len(d1_databases) > 0:
            mo.ui.table(d1_databases[["uuid", "name", "version", "num_tables"]], selection=None)
        else:
            mo.md("*No D1 databases found or API error*")
    else:
        d1_databases = pd.DataFrame()
        mo.md("*Configure credentials above*")
    return d1_databases, query_d1


@app.cell
def _(d1_databases, mo):
    # D1 database selector
    d1_options = d1_databases[["uuid", "name"]].values.tolist() if len(d1_databases) > 0 else []

    d1_selector = mo.ui.dropdown(
        options={f"{name} ({uuid})": uuid for uuid, name in d1_options} if d1_options else {"None": None},
        label="Select D1 Database"
    )

    sql_input = mo.ui.text_area(
        label="SQL Query",
        placeholder="SELECT * FROM sqlite_master LIMIT 10;",
        value="SELECT * FROM sqlite_master LIMIT 10;"
    )

    mo.vstack([d1_selector, sql_input])
    return d1_selector, sql_input


@app.cell
def _(mo):
    run_d1_query_btn = mo.ui.run_button(label="Execute D1 Query")
    run_d1_query_btn
    return (run_d1_query_btn,)


@app.cell
def _(
    CF_ACCOUNT_ID,
    CF_API_TOKEN,
    d1_selector,
    mo,
    pd,
    query_d1,
    run_d1_query_btn,
    sql_input,
):
    d1_results = None

    if run_d1_query_btn.value and d1_selector.value:
        with mo.status.spinner(title="Executing query..."):
            result = query_d1(CF_ACCOUNT_ID, d1_selector.value, CF_API_TOKEN, sql_input.value)

            if result.get("success") and result.get("result"):
                d1_results = pd.DataFrame(result["result"][0].get("results", []))
                mo.ui.table(d1_results, selection=None)
            else:
                errors = result.get("errors", [])
                mo.md(f"**Query Error:** {errors}")
    else:
        mo.md("*Select a database and click Execute*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. PyIceberg with R2 Catalog

    Iceberg tables provide ACID transactions, time travel, and schema evolution on R2.
    """)
    return


@app.cell
def _(os):
    # PyIceberg configuration
    R2_WAREHOUSE = os.environ.get("R2_WAREHOUSE", "")
    R2_CATALOG_URI = os.environ.get("R2_CATALOG_URI", "")
    R2_CATALOG_TOKEN = os.environ.get("R2_TOKEN", "")

    print(f"R2 Warehouse: {'✅ ' + R2_WAREHOUSE[:30] + '...' if R2_WAREHOUSE else '❌ Not configured'}")
    print(f"R2 Catalog URI: {'✅ ' + R2_CATALOG_URI[:30] + '...' if R2_CATALOG_URI else '❌ Not configured'}")
    return R2_CATALOG_TOKEN, R2_CATALOG_URI, R2_WAREHOUSE


@app.cell
def _(R2_CATALOG_TOKEN, R2_CATALOG_URI, R2_WAREHOUSE, mo):
    from pyiceberg.catalog.rest import RestCatalog
    import polars as pl
    import pyarrow as pa

    iceberg_catalog = None
    iceberg_namespaces = []

    if R2_WAREHOUSE and R2_CATALOG_URI and R2_CATALOG_TOKEN:
        try:
            iceberg_catalog = RestCatalog(
                name="r2_catalog",
                warehouse=R2_WAREHOUSE,
                uri=R2_CATALOG_URI,
                token=R2_CATALOG_TOKEN,
            )
            iceberg_namespaces = iceberg_catalog.list_namespaces()
            mo.md(f"**Connected to Iceberg Catalog**\n\nNamespaces: {iceberg_namespaces}")
        except Exception as e:
            mo.md(f"**Iceberg Connection Error:** {e}")
    else:
        mo.md("*Configure R2 catalog environment variables to use Iceberg*")
    return iceberg_catalog, iceberg_namespaces


@app.cell
def _(iceberg_catalog, iceberg_namespaces, mo):
    # List tables in namespaces
    iceberg_tables = []

    if iceberg_catalog and iceberg_namespaces:
        for ns in iceberg_namespaces:
            try:
                tables = iceberg_catalog.list_tables(ns)
                for t in tables:
                    iceberg_tables.append({"namespace": ns[0], "table": t[1]})
            except Exception as e:
                print(f"Error listing tables in {ns}: {e}")

        if iceberg_tables:
            import pandas as pd
            mo.ui.table(pd.DataFrame(iceberg_tables), selection=None)
        else:
            mo.md("*No tables found. Create one below.*")
    return (pd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. DuckDB + DuckLake Integration

    DuckLake provides a lightweight lakehouse format that works seamlessly with DuckDB and R2.
    """)
    return


@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        -- Install DuckLake extension
        INSTALL ducklake FROM core_nightly;
        LOAD ducklake;

        -- Show DuckDB version
        SELECT version() as duckdb_version;
        """
    )
    return


@app.cell
def _(mo):
    # DuckLake connection configuration
    ducklake_catalog = mo.ui.text(
        value="ducklake:metadata.ducklake",
        label="DuckLake Catalog URI",
        placeholder="ducklake:metadata.ducklake"
    )
    ducklake_catalog
    return (ducklake_catalog,)


@app.cell
def _(ducklake_catalog, mo):
    # Connect to DuckLake
    try:
        _df = mo.sql(
            f"""
            ATTACH '{ducklake_catalog.value}' AS myducklake;
            SHOW ALL TABLES;
            """
        )
    except Exception as e:
        mo.md(f"*DuckLake not configured or error: {e}*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. GraphQL Analytics Query

    Cloudflare's GraphQL API provides detailed analytics for KV, R2, and Workers.
    """)
    return


@app.cell
def _(CF_API_BASE, Request, datetime, json, mo, urlopen):
    def query_cloudflare_graphql(account_id: str, token: str, query: str, variables: dict) -> dict:
        """Execute a GraphQL query against Cloudflare's API."""
        url = f"{CF_API_BASE}/client/v4/graphql"
        payload = json.dumps({"query": query, "variables": variables}).encode()
        request = Request(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            data=payload,
            method='POST'
        )

        try:
            response = urlopen(request)
            return json.load(response)
        except Exception as e:
            return {"errors": [{"message": str(e)}]}

    # Example: KV Operations Query
    KV_OPERATIONS_QUERY = """
    query KVOperationsSummary($accountTag: string!, $filter: AccountKVOperationsAdaptiveGroupsFilter_InputObject) {
      viewer {
        accounts(filter: {accountTag: $accountTag}) {
          kvOperationsAdaptiveGroups(limit: 10000, filter: $filter) {
            count
            sum { requests }
            dimensions {
              actionType
              namespaceId
            }
          }
        }
      }
    }
    """

    # Calculate date range (last 7 days)
    end_dt = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    start_dt = (datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    mo.md(f"""
    **GraphQL Analytics Query**

    Query KV operations from `{start_dt}` to `{end_dt}`
    """)
    return KV_OPERATIONS_QUERY, end_dt, query_cloudflare_graphql, start_dt


@app.cell
def _(mo):
    run_graphql_btn = mo.ui.run_button(label="Query KV Analytics")
    run_graphql_btn
    return (run_graphql_btn,)


@app.cell
def _(
    CF_ACCOUNT_ID,
    CF_API_TOKEN,
    KV_OPERATIONS_QUERY,
    end_dt,
    mo,
    pd,
    query_cloudflare_graphql,
    run_graphql_btn,
    start_dt,
):
    kv_analytics = None

    if run_graphql_btn.value and CF_ACCOUNT_ID and CF_API_TOKEN:
        with mo.status.spinner(title="Querying KV analytics..."):
            variables = {
                "accountTag": CF_ACCOUNT_ID,
                "filter": {
                    "AND": [
                        {"datetimeHour_geq": start_dt},
                        {"datetimeHour_leq": end_dt}
                    ]
                }
            }

            result = query_cloudflare_graphql(
                CF_ACCOUNT_ID,
                CF_API_TOKEN,
                KV_OPERATIONS_QUERY,
                variables
            )

            if "errors" not in result or result.get("errors") is None:
                try:
                    groups = result["data"]["viewer"]["accounts"][0]["kvOperationsAdaptiveGroups"]
                    rows = []
                    for g in groups:
                        rows.append({
                            "namespace_id": g["dimensions"]["namespaceId"],
                            "action_type": g["dimensions"]["actionType"],
                            "requests": g["sum"]["requests"],
                            "count": g["count"]
                        })
                    kv_analytics = pd.DataFrame(rows)
                    mo.ui.table(kv_analytics, selection=None)
                except Exception as e:
                    mo.md(f"**Parse Error:** {e}")
            else:
                mo.md(f"**GraphQL Error:** {result.get('errors')}")
    else:
        mo.md("*Configure credentials and click Query*")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Patterns Demonstrated

    ### R2 Storage (S3-Compatible)
    ```python
    # List buckets via REST API
    GET /client/v4/accounts/{account_id}/r2/buckets

    # Download objects requires AWS SigV4 signing
    headers = create_aws_sigv4_headers(
        method='GET',
        host=f'{bucket}.{account_id}.r2.cloudflarestorage.com',
        path=f'/{object_key}',
        access_key=R2_ACCESS_KEY,
        secret_key=R2_SECRET_KEY
    )
    ```

    ### D1 Database
    ```python
    # Execute SQL via API
    POST /client/v4/accounts/{account_id}/d1/database/{db_id}/query
    {"sql": "SELECT * FROM table LIMIT 10"}
    ```

    ### PyIceberg + R2
    ```python
    from pyiceberg.catalog.rest import RestCatalog

    catalog = RestCatalog(
        name="r2_catalog",
        warehouse=R2_WAREHOUSE,
        uri=R2_CATALOG_URI,
        token=R2_TOKEN,
    )

    # Create table
    catalog.create_table("namespace.table", schema=schema)

    # Query with time travel
    table = catalog.load_table("namespace.table")
    df = table.to_polars().filter(pl.col("date") == "2024-01-01")
    ```

    ### DuckLake
    ```sql
    INSTALL ducklake FROM core_nightly;
    LOAD ducklake;
    ATTACH 'ducklake:metadata.ducklake' AS myducklake;
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
