# Curriculum processing assets and resources
from .sources import curriculum_metadata, specification_pdfs, curriculum_documents
from .processing import indexed_pages, extracted_concepts, visualizable_concepts
from .resources import (
    LanceDBResource,
    CocoIndexResource,
    DLTResource,
    ColPaliResource,
    Qwen3VLResource,
)

__all__ = [
    "curriculum_metadata",
    "specification_pdfs",
    "curriculum_documents",
    "indexed_pages",
    "extracted_concepts",
    "visualizable_concepts",
    "LanceDBResource",
    "CocoIndexResource",
    "DLTResource",
    "ColPaliResource",
    "Qwen3VLResource",
]
