"""
Database schemas for EduVision educational asset generation.

Defines dataclasses for:
- SyllabusPage: Indexed curriculum pages with ColPali embeddings
- CurriculumConcept: Extracted educational concepts
- GeneratedAsset: FIBO-generated images
- AssetLineage: Full provenance tracking
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SyllabusPage:
    """
    Schema for indexed syllabus pages using ColPali embeddings.

    Each page from a curriculum PDF is converted to an image
    and embedded using ColPali for visual document retrieval.
    """
    id: str                          # UUID
    subject: str                     # "chemistry", "biology", "geography"
    document_title: str              # "LC Chemistry Specification"
    page_number: int
    filename: str                    # Original PDF filename
    language: str                    # "en" or "ga" (Irish)

    # ColPali multi-vector embedding (list of patch embeddings)
    # Shape: [num_patches, 128] - stored as flattened for LanceDB
    embedding: list[list[float]] = field(default_factory=list)

    # Metadata
    specification_version: str = "current"  # "current" or "upcoming"
    effective_from: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Content
    extracted_text: Optional[str] = None    # OCR/extracted text if available
    page_image_path: str = ""               # Path to rendered page image


@dataclass
class VisualRequirement:
    """Describes what type of visualization a concept needs."""
    diagram_type: str      # "molecular", "process_flow", "experimental_setup", etc.
    description: str
    complexity: str        # "simple", "moderate", "complex"
    style_preference: Optional[str] = None  # "photograph", "illustration", etc.


@dataclass
class LearningOutcome:
    """A specific learning outcome from the curriculum."""
    code: str              # e.g., "LO1.1"
    description: str
    cognitive_level: str   # "Knowledge", "Understanding", "Application", "Analysis"
    visual_potential: float = 0.5  # 0.0-1.0 score for how visualizable


@dataclass
class CurriculumConcept:
    """
    Schema for extracted curriculum concepts.

    Represents an educational concept that can be visualized,
    extracted from syllabus pages using BAML + Qwen3-VL.
    """
    id: str                          # UUID
    subject: str                     # "chemistry", "biology", "geography"
    topic_name: str
    strand: Optional[str] = None     # Curriculum strand/unit

    title: str = ""
    description: str = ""
    keywords: list[str] = field(default_factory=list)

    # Semantic embedding for concept search
    text_embedding: list[float] = field(default_factory=list)  # 384-dim

    # References
    source_page_ids: list[str] = field(default_factory=list)
    learning_outcomes: list[LearningOutcome] = field(default_factory=list)
    visual_requirements: list[VisualRequirement] = field(default_factory=list)

    # Metadata
    difficulty_level: str = "ordinary"  # "foundation", "ordinary", "higher"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SourceReference:
    """Reference to source curriculum document."""
    subject: str
    strand: str
    document_url: str
    document_type: str      # "specification" or "syllabus"
    page_number: Optional[int] = None
    language: str = "en"


@dataclass
class GenerationMetadata:
    """Metadata about the FIBO generation process."""
    fibo_version: str
    model_checkpoint: str
    generation_timestamp: str
    inference_time_ms: int
    seed: Optional[int] = None


@dataclass
class GeneratedAsset:
    """
    Schema for FIBO-generated educational assets.

    Tracks the generated image along with full provenance
    linking back to curriculum concepts and specifications.
    """
    id: str                          # UUID
    concept_id: str                  # Foreign key to CurriculumConcept

    # Generation parameters
    fibo_prompt_json: str            # Full FIBO JSON used
    style_medium: str                # "photograph", "digital_illustration", etc.

    # Output
    image_path: str                  # Path to generated image

    # Optional fields with defaults
    seed: Optional[int] = None
    image_embedding: list[float] = field(default_factory=list)  # CLIP embedding

    # Quality metrics (from Qwen3-VL validation)
    validation_score: float = 0.0
    scientific_accuracy: float = 0.0
    educational_clarity: float = 0.0
    concept_alignment: float = 0.0

    # Status
    status: str = "draft"            # "draft", "validated", "approved", "rejected"
    validation_issues: list[str] = field(default_factory=list)
    refinement_count: int = 0

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    validated_at: Optional[str] = None


@dataclass
class AssetLineage:
    """
    Complete lineage tracking for generated educational assets.

    Tracks the full path from curriculum source to generated image,
    enabling source attribution for each asset.
    """
    # Required fields first
    asset_id: str
    source_reference: SourceReference
    concept_id: str
    concept_topic: str

    # Optional fields with defaults
    learning_outcome_codes: list[str] = field(default_factory=list)
    fibo_config_hash: str = ""       # Hash of FIBO JSON config used
    fibo_config: dict = field(default_factory=dict)
    output_path: str = ""
    file_size_bytes: int = 0
    image_dimensions: tuple[int, int] = (0, 0)
    generation: Optional[GenerationMetadata] = None
    colpali_similarity_score: Optional[float] = None
    most_similar_page_id: Optional[str] = None
