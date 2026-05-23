import dlt
import dlthub
from dlthub import Project, Cache, Dataset

# Initialize dlt+ Project
# This declarative manifest connects our local pipeline to the dltHub managed infrastructure
project = Project(
    name="oideachais_data_platform",
    description="Irish Education Data Pipeline",
    profiles=["dev", "prod"]
)

# Initialize dlt+ Cache
# Provides a portable DuckDB compute layer to test and transform Irish curriculum data
# before loading to the final destination (e.g., MotherDuck or LanceDB).
cache = Cache(
    engine="duckdb",
    storage_path=".dlt/cache/oideachais.duckdb"
)

# Define datasets for access in TanStack and Agents
# These schemas are exposed downstream to the UI and Agent frameworks
curriculum_dataset = Dataset(
    name="irish_curriculum_standards",
    schema="curriculum",
    description="Unified NCCA, CurriculumOnline, and Examinations.ie learning outcomes."
)

exam_dataset = Dataset(
    name="irish_state_examinations",
    schema="exams",
    description="State Examination Commission past papers, marking schemes, and statistics."
)

def apply_dlthub_wrappers(pipeline):
    """
    Applies the dlt+ caching and dataset registration to an existing dlt pipeline.
    """
    # Register the pipeline with the dltHub Project
    project.register_pipeline(pipeline)
    
    # Attach cache for pre-load transformations
    pipeline.use_cache(cache)
    
    # Register datasets to be published to the dltHub Data Catalog
    pipeline.publish_datasets([curriculum_dataset, exam_dataset])
    
    return pipeline
