from setuptools import find_packages, setup

setup(
    name="package_analytics",
    packages=find_packages(exclude=["package_analytics_tests"]),
    install_requires=[
        "dagster",
        "dagster-dbt",
        "dagster-duckdb",
        "dagster-webserver",
        "dbt-duckdb",
        "duckdb",
        "ibis-framework[duckdb,bigquery,deltalake]",
        "dlt",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
