# 1. Basics: ELT and dlt


## Directory content
- `1_rest_api_pipeline.py` A script that shows a typical `dlt` pipeline to load data from a REST API. It will load Jaffleshop data from our REST API and ingest it in a local duckdb. Run it via:

    ```shell
    python 1_rest_api_pipeline.py
    ```

- `2_files_pipeline.py` A script that shows a typical `dlt` pipeline to load data from an object store / filesystem. It will load Jaffleshop data from a local file (found in `./data` and ingest it in a local duckdb (the same where REST API data was loaded). Run it via:

    ```shell
    python 2_files_pipeline.py
    ```

- `3_jaffleshop_notebook.py` A notebook tutorial showing the full ELT life cycle and some convenience method for interactive development. Run it via

    ```shell
    marimo edit 3_jaffleshop_notebook.py
    ```