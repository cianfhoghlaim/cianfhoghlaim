"""Example dlt pipeline ingesting a REST API"""

import dlt
from dlt.sources.rest_api import rest_api_source

# Source: Use the built-in REST API source. The `resource`
# field creates a resource per API endpoint. 
jaffleshop_rest_source = rest_api_source(
    {
        # configure the request client; includes headers, paginator, auth
        "client": {
            "base_url": "https://jaffle-shop.dlthub.com/api/v1",
            "paginator": {"type": "header_link"},
        },
        # defines one resource per endpoint
        "resources": [
            "customers",  # implicitly: https://jaffle-shop.dlthub.com/api/v1/customers
            "products",
            "orders",
        ],
        # configure parameters for all endpoints
        "resource_defaults": {
            "endpoint": {
                # filter date range using query params
                "params": {
                    "start_date": "2017-01-01",
                    "end_date": "2017-01-15",
                },
            },
        },
    }
)

# Pipeline and Destination: use `dlt.pipeline` to create a pipeline
# with a name and assign it a destination. We use shorthand destination.
# It's equivalent to calling: `dlt.destinations.duckdb()`
jaffle_rest_pipe = dlt.pipeline(
    "jaffleshop_rest",
    destination="duckdb",
    dataset_name="jaffleshop",
)

if __name__ == "__main__":
    # Calling `.run()` on the Source executes the pipeline
    load_info = jaffle_rest_pipe.run(jaffleshop_rest_source)
    print(load_info)

    # Dataset: the dataset can be retrieved directly from the pipeline
    # jaffleshop_rest_dataset = jaffle_rest_pipe.dataset()