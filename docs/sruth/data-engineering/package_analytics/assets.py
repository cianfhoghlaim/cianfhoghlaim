import os
import logging as log
import subprocess
from datetime import datetime

from dagster_dbt import dbt_assets, DbtCliResource
from dagster import asset, OpExecutionContext, file_relative_path
from .resources import dbt_manifest_path, CustomDagsterDbtTranslator
from .constants import DATA_PATH, BIGQUERY_DATASET

import ibis
from dotenv import load_dotenv

load_dotenv()
log.basicConfig(level=log.INFO)


@asset(compute_kind="python", group_name="raw")
def ingest_pypi():
    """
    Ingest the PyPI data.
    """

    project_id = os.getenv("GCP_PROJECT_ID")
    log.info(f"Project ID: {project_id}")

    overwrite = os.getenv("PYPI_OVERWRITE", False)
    log.info(f"Overwrite: {overwrite}")

    packages = os.getenv("PYPI_PACKAGES").split(",")
    metadata = {"packages": packages, "num_rows_returned": []}
    for package in packages:
        log.info(f"Package: {package}")
        output_dir = os.path.join(DATA_PATH, "ingest", "pypi", package, "file_downloads.delta")

        # if table exists for package, only query data since last run
        if os.path.exists(output_dir) and not overwrite:
            start_time = (
                ibis.duckdb.connect()
                .sql(f"select MAX(timestamp) from delta_scan('{output_dir}')")
                .execute()
                .iloc[0, 0]
            )
        else:
            start_time = os.getenv("START_DATE")

        end_time = os.getenv("END_DATE", datetime.now())

        log.info(f"Start time: {start_time}")
        log.info(f"End time: {end_time}")

        query = f"""
            SELECT *
            FROM `{BIGQUERY_DATASET}`
            WHERE file.project = '{package}'
            AND timestamp > TIMESTAMP("{start_time}")
            AND timestamp <= TIMESTAMP("{end_time}")
        """

        con = ibis.connect(f"bigquery://{project_id}")
        log.info(f"Executing query:\n{query}")
        table = con.sql(query)

        log.info(f"Writing to: {output_dir}")
        if overwrite:
            table.to_delta(output_dir, mode="overwrite")
        else:
            table.to_delta(output_dir, mode="append")


@asset(deps=[ingest_pypi], compute_kind="duckdb", group_name="prepared")
def downloads():
    """
    Merge the PyPI delta tables via DuckDB.
    """

    # could be a local path, or MotherDuck token
    database = os.getenv("DUCKDB_DATABASE")
    con = ibis.duckdb.connect(database)

    # construct an SQL union statement of Delta table paths to load into a `downloads` table
    delta_paths = []
    for dirpath, _, filenames in os.walk(DATA_PATH):
        if os.path.basename(dirpath) == "file_downloads.delta":
            delta_paths.append(os.path.abspath(dirpath))

    sql_delta_select_statements = [f"select * from delta_scan('{path}')" for path in delta_paths]
    sql_delta_union_query = " UNION ALL ".join(sql_delta_select_statements)

    log.info(f"Creating table with query:\n{sql_delta_union_query}")
    con.raw_sql(f"create or replace table downloads as ({sql_delta_union_query})")


@dbt_assets(manifest=dbt_manifest_path, dagster_dbt_translator=CustomDagsterDbtTranslator())
def pypi_daily_stats(context: OpExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


@asset(compute_kind="evidence", group_name="reporting", deps=[pypi_daily_stats])
def evidence_dashboard():
    """Dashboard built using Evidence showing PyPI metrics."""
    evidence_project_path = file_relative_path(__file__, "../dashboard")

    evidence_duckdb_path = evidence_project_path + "/sources/pypi_analytics/pypi_analytics.duckdb"
    con = ibis.connect(evidence_duckdb_path)

    con.drop_table("pypi_daily_stats", force=True)
    con.create_table(
        "pypi_daily_stats",
        obj=ibis.connect(os.getenv("DUCKDB_DATABASE")).table("pypi_daily_stats").to_pandas(),
    )
    con.disconnect()

    subprocess.run(["npm", "--prefix", evidence_project_path, "install"])
    subprocess.run(["npm", "--prefix", evidence_project_path, "run", "sources"])
    subprocess.run(["npm", "--prefix", evidence_project_path, "run", "build"])
