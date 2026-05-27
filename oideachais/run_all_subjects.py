import os
import sys
import dlt

sys.path.insert(0, os.path.dirname(__file__))

os.environ['DLT_DISABLE_PLUGINS'] = 'true'
os.environ['USE_DUCKLAKE'] = 'false'
os.environ['USE_LOCAL_SCRAPES'] = 'true'

from data_platform.dlt_sources.ireland.curriculum_source import curriculum_source

pipeline = dlt.pipeline(
    pipeline_name='curriculum_unified',
    destination='duckdb',
    dataset_name='curriculum'
)

subjects = ['geography', 'chemistry', 'gaeilge', 'english', 'biology', 'history', 'business-studies']
cycles = ['junior_cycle', 'senior_cycle']

for cycle in cycles:
    for subject in subjects:
        print(f"Running {cycle} - {subject}...")
        try:
            source = curriculum_source(cycle=cycle, subject=subject, language='en')
            pipeline.run(source)
            print(f"Success: {cycle} - {subject}")
        except Exception as e:
            print(f"Failed {cycle} - {subject}: {e}")
