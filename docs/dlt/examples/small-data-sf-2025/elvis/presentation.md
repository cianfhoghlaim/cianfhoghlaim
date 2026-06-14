# small-data-sf 2025

## PART 1

```py
# PART 1 - data loading
from elvis.helpers.cloudflare.dlt_client import (
    load_json_to_cloudflare_r2,
    get_cloudflare_r2_credentials,
    get_r2_endpoint_url,
)

# PART 1A
from dlt.common.configuration.specs import AwsCredentials

# PART 1B
import dlt
import os

os.environ["DATA_WRITER__DISABLE_COMPRESSION"] = "True"
dlt.config["data_writer.disable_compression"] = True

credentials: AwsCredentials = get_cloudflare_r2_credentials()
endpoint_url: str = get_r2_endpoint_url(account_id="cloudflare-account-id")

pipeline: dlt.Pipeline = dlt.pipeline(
    pipeline_name="pipeline_name",
    destination=dlt.destinations.filesystem(
        bucket_url="s3://bucket_name",
        credentials=credentials,
        client_kwargs={
            "endpoint_url": endpoint_url,
        },
    ),
    dataset_name="dataset_name",
)
```

---

## PART 2

```sh
dlt init sql_database duckdb --eject
```

 ---

 ## PART 3

Navigate to the jupyter notebook, these are helper commands for viewing the output of the pipelines we run!

 ```sh
 duckdb elvis.duckdb -c "
from elvis.small_data.stars
select 
    'https://github.com/' || repo_name as url,
    star_count, year, month,
order by star_count desc
limit 100"
 ```

 ```sh
 duckdb elvis.duckdb -c "
 from elvis.small_data.perplexity
 select
     filename,	
     programming_language,
     license,
     description,
 where license = 'MIT License'
 limit 100
 "
 ```

```sh
duckdb analytics.duckdb -c "
from small_data.monthly_stars
select
    *
limit 100
"
```

```sh
duckdb analytics.duckdb -c "
from small_data.monthly_stars
select
    *
limit 100
"
```

```sh
duckdb fraud_detector.duckdb -c "
from fraud_detection.fraud_detection_source
select
    description, url,
"
```