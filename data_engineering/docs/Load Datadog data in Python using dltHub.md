---
title: "Load Datadog data in Python using dltHub"
source: "https://dlthub.com/workspace/source/datadog"
author:
published: 2025-07-15
created: 2025-12-29
description: "Build a Datadog-to-database or-dataframe pipeline in Python using dlt with automatic Cursor support."
tags:
  - "clippings"
---
![Datadog connector icon](https://dlthub.com/workspace/_next/image?url=https%3A%2F%2Fimg.logo.dev%2Fdatadoghq.com%3Ftoken%3Dpk_YkEESHvtSxKYU1570SChwA&w=256&q=75)

Build a Datadog-to-database or-dataframe pipeline in Python using dlt with automatic Cursor support.

In this guide, we'll set up a complete Datadog data pipeline from API credentials to your first data load in just 10 minutes. You'll end up with a fully declarative Python pipeline based on dlt's REST API connector, like in the partial example code below:

```
Example code@dlt.source
def datadog_source(access_token=dlt.secrets.value):
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.datadoghq.com/api/v1/",
            "auth": {
                "type": "bearer",
                "token": access_token,
            },
        },
        "resources": [
            "audit_logs",
            "dashboards",
            "incidents"
            ],
    }
    [...]
    yield from rest_api_resources(config)

def get_data() -> None:
    # Connect to destination
    pipeline = dlt.pipeline(
        pipeline_name='datadog_pipeline',
        destination='duckdb',
        dataset_name='datadog_data', 
    )
    # Load the data
    load_info = pipeline.run(datadog_source())
    print(load_info)
```

### Why use dltHub Workspace with LLM Context to generate Python pipelines?

- Accelerate pipeline development with AI-native context
- Debug pipelines, validate schemas and data with the integrated **Pipeline Dashboard**
- Build Python notebooks for end users of your data
- **Low maintenance** thanks to Schema evolution with type inference, resilience and self documenting REST API connectors. A shallow learning curve makes the pipeline easy to extend by any team member
- dlt is the tool of choice for Pythonic Iceberg Lakehouses, bringing mature data loading loading to pythonic Iceberg with or without catalogs

## What you’ll do

We’ll show you how to generate a readable and easily maintainable Python script that fetches data from datadog’s API and loads it into Iceberg, DataFrames, files, or a database of your choice. Here are some of the endpoints you can load:

- Audit Logs: Fetch logs for auditing purposes.
- Dashboards: Access and manage dashboards.
- Downtimes: Retrieve information on scheduled downtimes.
- Incident Teams: Manage teams involved in incident response.
- Incidents: Access incident information and details.
- Logs: Retrieve logs for monitoring and analysis.
- Metrics: Query and retrieve metrics data.
- Monitors: Access and manage monitors for various metrics.
- Service Level Objectives: Retrieve information on service level objectives.
- Synthetic Tests: Manage and retrieve synthetic test results.
- Users: Access user information and management.
- Series: Retrieve time series data.

You will then debug the Datadog pipeline using our Pipeline Dashboard tool to ensure it is copying the data correctly, before building a Notebook to explore your data and build reports.

## Setup & steps to follow

```
💡Before getting started, let's make sure Cursor is set up correctly:

We suggest using a model like Claude 3.7 Sonnet or better
Index the REST API Source tutorial: https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api/ and add it to context as @dlt rest api

Read our full steps on setting up Cursor
```

Now you're ready to get started!

1. ⚙️ **Set up `dlt` Workspace**
	Install dlt with duckdb support:
	```
	pip install "dlt[workspace]"
	```
	Initialize a dlt pipeline with Datadog support.
	```
	dlt init dlthub:datadog duckdb
	```
	The `init` command will setup the necessary files and folders for the next step.
2. 🤠 **Start LLM-assisted coding**
	Here’s a prompt to get you started:
3. 🔒 **Set up credentials**
	Authentication requires both an API key and an application key to access the endpoints. The API key is provided in the header named 'DD-API-KEY'.
	To get the appropriate API keys, please visit the original source at [https://www.datadoghq.com/](https://www.datadoghq.com/). If you want to protect your environment secrets in a production environment, look into [setting up credentials with dlt](https://dlthub.com/docs/walkthroughs/add_credentials).
4. 🏃♀️ **Run the pipeline in the Python terminal in Cursor**
	```
	python datadog_pipeline.py
	```
	If your pipeline runs correctly, you’ll see something like the following:
	```
	Pipeline datadog load step completed in 0.26 seconds
	1 load package(s) were loaded to destination duckdb and into dataset datadog_data
	The duckdb destination used duckdb:/datadog.duckdb location to store data
	Load package 1749667187.541553 is LOADED and contains no failed jobs
	```
5. 📈 **Debug your pipeline and data with the Pipeline Dashboard**
	Now that you have a running pipeline, you need to make sure it’s correct, so you do not introduce silent failures like misconfigured pagination or incremental loading errors. By launching the dlt Workspace Pipeline Dashboard, you can see various information about the pipeline to enable you to test it. Here you can see:
	- Pipeline overview: State, load metrics
	- Data’s schema: tables, columns, types, hints
	- You can query the data itself
	```
	dlt pipeline datadog_pipeline show
	```
6. 🐍 **Build a Notebook with data explorations and reports**
	With the pipeline and data partially validated, you can continue with custom data explorations and reports. To get started, paste the snippet below into a new marimo Notebook and ask your LLM to go from there. Jupyter Notebooks and regular Python scripts are supported as well.
	```
	import dlt
	data = dlt.pipeline("datadog_pipeline").dataset()
	# get "audit_logs" table as Pandas frame
	data.audit_logs.df().head()
	```

## Running into errors?

While accessing the API, it's important to note that both API key and application key are required. Additionally, some endpoints may have rate limits that could affect the frequency of requests. Unauthorized access may occur if credentials are invalid, and permissions should be checked if access is forbidden.

### Extra resources:

- [Learn more with our 1h LLM-assisted coding course!](https://www.youtube.com/watch?v=GGid70rnJuM)

## Next steps

- [How to deploy a pipeline](https://dlthub.com/docs/walkthroughs/deploy-a-pipeline)
- [How to explore your data in marimo Notebooks](https://dlthub.com/docs/general-usage/dataset-access/marimo)
- [How to query your data in Python with dataset](https://dlthub.com/docs/general-usage/dataset-access/dataset)
- [How to create REST API Sources with Cursor](https://dlthub.com/docs/dlt-ecosystem/llm-tooling/cursor-restapi)