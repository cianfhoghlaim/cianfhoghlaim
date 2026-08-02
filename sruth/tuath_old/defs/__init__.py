# Dagster definitions for EduVision
# Educational asset generation for Irish Leaving Certificate

from .curriculum.sources import curriculum_metadata, specification_pdfs, curriculum_documents
from .curriculum.processing import indexed_pages, extracted_concepts, visualizable_concepts
from .curriculum.resources import (
    LanceDBResource,
    CocoIndexResource,
    DLTResource,
    ColPaliResource,
    Qwen3VLResource,
)
from .fibo_generation.assets import fibo_json_configs, generated_images
from .fibo_generation.resources import FiboResource, ValidationResource

# Instantiate resources with names matching asset parameter names
# These are auto-discovered by load_from_defs_folder
dlt_resource = DLTResource()
lancedb_resource = LanceDBResource()
cocoindex_resource = CocoIndexResource()
colpali_resource = ColPaliResource()
qwen3vl_resource = Qwen3VLResource()
fibo_resource = FiboResource()
validation_resource = ValidationResource()

__all__ = [
    # Curriculum assets
    "curriculum_metadata",
    "specification_pdfs",
    "curriculum_documents",
    "indexed_pages",
    "extracted_concepts",
    "visualizable_concepts",
    # FIBO generation assets
    "fibo_json_configs",
    "generated_images",
    # Resource instances (for Dagster to discover)
    "dlt_resource",
    "lancedb_resource",
    "cocoindex_resource",
    "colpali_resource",
    "qwen3vl_resource",
    "fibo_resource",
    "validation_resource",
    # Resource classes (for type hints)
    "LanceDBResource",
    "CocoIndexResource",
    "DLTResource",
    "ColPaliResource",
    "Qwen3VLResource",
    "FiboResource",
    "ValidationResource",
]
