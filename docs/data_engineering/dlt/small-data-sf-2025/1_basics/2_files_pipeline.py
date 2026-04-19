import dlt
from dlt.sources.filesystem import filesystem, read_parquet

# Resource: iterate over files metadata in an object store / filesystem
files_resource = filesystem(
    bucket_url=str("./1_basics/data"),
    file_glob="*payments.parquet",
)

# Transformer: Read the file 
payments_resource = (
    files_resource
    | read_parquet(use_pyarrow=True)
).with_name("payments")  # assign a name to the new resource

# Pipeline and destination
jaffle_files_pipe = dlt.pipeline(
    "jaffleshop_files",
    destination="duckdb",
    dataset_name="jaffleshop",
)


if __name__ == "__main__":
    # Calling `.run()` the Resource executes the pipeline
    load_info = jaffle_files_pipe.run(payments_resource)
    print(load_info)
