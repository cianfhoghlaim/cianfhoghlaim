import os
import dlt
import sys

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.dirname(__file__))

os.environ['DLT_DISABLE_PLUGINS'] = 'true'
os.environ['USE_DUCKLAKE'] = 'false'
os.environ['USE_LOCAL_SCRAPES'] = 'true'

from data_platform.dlt_sources.ireland.curriculum_source import curriculum_source

# Try running just one pipeline to see if it populates the local duckdb
pipeline = dlt.pipeline(
    pipeline_name='curriculum_unified',
    destination='duckdb',
    dataset_name='curriculum'
)

source = curriculum_source(cycle='junior_cycle', subject='mathematics', language='en')
print("Running pipeline...")
load_info = pipeline.run(source)
print(load_info)
