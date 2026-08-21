import os
from datetime import datetime, timedelta

from google.cloud import bigquery
from google.cloud import storage
from google.oauth2 import service_account
from google.auth.exceptions import DefaultCredentialsError
from loguru import logger
import time
from .models import PypiJobParameters, FileDownloads
import pyarrow as pa
import dlt
import fire

from dotenv import load_dotenv

load_dotenv()

from tqdm import tqdm

PYPI_PUBLIC_DATASET = "bigquery-public-data.pypi.file_downloads"
GCS_BUCKET = "gs://pypi_downloads"


def get_bigquery_client(project_name: str) -> bigquery.Client:
    """Get Big Query client"""
    try:
        service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        if service_account_path:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )
            bigquery_client = bigquery.Client(project=project_name, credentials=credentials)
            return bigquery_client

        raise EnvironmentError("No valid credentials found for BigQuery authentication.")

    except DefaultCredentialsError as creds_error:
        raise creds_error


def get_gcs_client(project_name: str) -> storage.Client:
    """Get GCS Storage client"""
    try:
        service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        if service_account_path:
            credentials = service_account.Credentials.from_service_account_file(
                service_account_path
            )
            storage_client = storage.Client(project=project_name, credentials=credentials)
            return storage_client

        raise EnvironmentError("No valid credentials found for GCS authentication.")

    except DefaultCredentialsError as creds_error:
        raise creds_error


def bigquery_to_gcs(params: PypiJobParameters) -> None:
    bigquery_client = get_bigquery_client(project_name=params.gcp_project)
    storage_client = get_gcs_client(project_name=params.gcp_project)

    start_date = datetime.strptime(params.start_date, "%Y-%m-%d")
    end_date = datetime.strptime(params.end_date, "%Y-%m-%d")

    date_list = [
        (start_date + timedelta(days=x)).strftime("%Y-%m-%d")
        for x in range((end_date - start_date).days + 1)
    ]

    for date in date_list:
        start_time = time.time()

        blob = f"/package={params.pypi_project}/year={date}/{datetime.now()}*.parquet"
        uri = f"{GCS_BUCKET}/blob"

        query_str = build_pypi_export_query(
            package=params.pypi_project, date=date, destination_uri=uri
        )

        logger.info(f"Running query: {query_str}")

        result = bigquery_client.query_and_wait(query_str)
        elapsed_time = time.time() - start_time

        logger.info(f"Query executed in {elapsed_time:.2f} seconds")

        landed = storage_client.bucket(GCS_BUCKET).blob(uri).exists()

        if landed:
            logger.info(f"Parquet saved to GCS: {uri}")
        else:
            logger.error(f"Failed to find parquet file in GCS")


def build_pypi_export_query(
    package: str,
    date: datetime,
    destination_uri: str,
    pypi_public_dataset: str = PYPI_PUBLIC_DATASET,
    destination_bucket: str = GCS_BUCKET,
) -> str:
    # Query the public PyPI dataset from BigQuery
    # /!\ This is a large dataset, filter accordingly /!\
    return f"""
    EXPORT DATA OPTIONS(
        uri='{destination_uri}',
        format='PARQUET',
        overwrite=true,
        compression='GZIP'
        ) AS
    SELECT *
    FROM
        `{pypi_public_dataset}`
    WHERE
        project = '{package}'
        AND DATE(timestamp) = DATE("{date}")
    LIMIT 9223372036854775807
    """


def build_pypi_query(
    params: PypiJobParameters, pypi_public_dataset: str = PYPI_PUBLIC_DATASET
) -> str:
    # Query the public PyPI dataset from BigQuery
    # /!\ This is a large dataset, filter accordingly /!\
    return f"""
    SELECT *
    FROM
        `{pypi_public_dataset}`
    WHERE
        project = '{params.pypi_project}'
        AND {params.timestamp_column} >= TIMESTAMP("{params.start_date}")
        AND {params.timestamp_column} < TIMESTAMP("{params.end_date}")
    """


@dlt.source
def bigquery_source(params: PypiJobParameters, bigquery_client: bigquery.Client):
    for project in params.pypi_project:
        query_str = build_pypi_query(params)

        return dlt.resource(
            get_bigquery_result,
            name=project,
        )(query_str, bigquery_client)


def get_bigquery_result(query_str: str, bigquery_client: bigquery.Client) -> pa.Table:
    """Get query result from BigQuery and yield rows as dictionaries."""
    try:
        start_time = time.time()
        logger.info(f"Running query: {query_str}")

        pa_tbl = bigquery_client.query(query_str).to_arrow()

        elapsed_time = time.time() - start_time
        logger.info(f"Query executed and data loaded in {elapsed_time:.2f} seconds")

        yield pa_tbl

    except Exception as e:
        logger.error(f"Error running query: {e}")
        raise


def main(params: PypiJobParameters):

    # bigquery_to_gcs(params)

    bigquery_client = get_bigquery_client(project_name=params.gcp_project)

    data_source = bigquery_source(params, bigquery_client=bigquery_client)

    pipeline = dlt.pipeline(
        pipeline_name=f"bigquery_{params.pypi_project}_{datetime.now()}",
        destination=dlt.destinations.duckdb("pypi_analytics.duckdb"),
        dataset_name="main",
    )

    load_info = pipeline.run(data_source, write_disposition="append", table_name=params.table_name)

    print(load_info)


if __name__ == "__main__":
    fire.Fire(lambda **kwargs: main(PypiJobParameters(**kwargs)))
