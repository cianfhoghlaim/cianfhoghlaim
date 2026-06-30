"""
Database schemas for FIBO educational asset generation.

Defines dataclasses for:
- SyllabusPage: Indexed curriculum pages with ColPali embeddings
- CurriculumConcept: Extracted educational concepts
- GeneratedAsset: FIBO-generated images
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VisualRequirement:
    """Describes what type of visualization a concept needs."""

    diagram_type: str  # "molecular", "process_flow", "experimental_setup", etc.
    description: str
    complexity: str  # "simple", "moderate", "complex"
    style_preference: str | None = None  # "photograph", "illustration", etc.


@dataclass
class LearningOutcome:
    """A specific learning outcome from the curriculum."""

    code: str  # e.g., "LO1.1"
    description: str
    cognitive_level: str  # "Knowledge", "Understanding", "Application", "Analysis"
    visual_potential: float = 0.5  # 0.0-1.0 score for how visualizable


@dataclass
class SyllabusPage:
    """
    Schema for indexed syllabus pages using ColPali embeddings.

    Each page from a curriculum PDF is converted to an image
    and embedded using ColPali for visual document retrieval.
    """

    id: str  # UUID
    subject: str  # "chemistry", "biology", "geography"
    document_title: str  # "LC Chemistry Specification"
    page_number: int
    filename: str  # Original PDF filename
    language: str  # "en" or "ga" (Irish)

    # ColPali multi-vector embedding (list of patch embeddings)
    embedding: list[list[float]] = field(default_factory=list)

    # Metadata
    specification_version: str = "current"  # "current" or "upcoming"
    effective_from: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Content
    extracted_text: str | None = None  # OCR/extracted text if available
    page_image_path: str = ""  # Path to rendered page image


@dataclass
class CurriculumConcept:
    """
    Schema for extracted curriculum concepts.

    Represents an educational concept that can be visualized,
    extracted from syllabus pages using BAML + VLM.
    """

    id: str  # UUID
    subject: str  # "chemistry", "biology", "geography"
    topic_name: str
    strand: str | None = None  # Curriculum strand/unit

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
class GeneratedAsset:
    """
    Schema for FIBO-generated educational assets.

    Tracks the generated image along with full provenance
    linking back to curriculum concepts and specifications.
    """

    id: str  # UUID
    concept_id: str  # Foreign key to CurriculumConcept

    # Generation parameters
    fibo_prompt_json: str  # Full FIBO JSON used
    style_medium: str  # "photograph", "digital_illustration", etc.

    # Output
    image_path: str  # Path to generated image

    # Optional fields with defaults
    seed: int | None = None
    image_embedding: list[float] = field(default_factory=list)  # CLIP embedding

    # Quality metrics (from VLM validation)
    validation_score: float = 0.0
    scientific_accuracy: float = 0.0
    educational_clarity: float = 0.0
    concept_alignment: float = 0.0

    # Status
    status: str = "draft"  # "draft", "validated", "approved", "rejected"
    validation_issues: list[str] = field(default_factory=list)
    refinement_count: int = 0

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    validated_at: str | None = None


@dataclass
class FiboConfig:
    """Configuration for a FIBO image generation request."""

    # Core prompt components
    title: str
    short_description: str
    detailed_description: str

    # Visual style
    style: str = "digital_illustration"
    medium: str = "digital_art"
    color_palette: list[str] = field(default_factory=lambda: ["educational"])

    # Composition
    subject_position: str = "center"
    background: str = "clean"
    lighting: str = "soft"

    # Technical
    aspect_ratio: str = "1:1"
    quality: str = "high"

    # Educational metadata
    subject_area: str = ""
    diagram_type: str = "diagram"
    complexity_level: str = "moderate"

    def to_prompt(self) -> str:
        """Convert config to text prompt."""
        parts = [
            self.detailed_description,
            f"Style: {self.style}",
            f"Medium: {self.medium}",
            f"Background: {self.background}",
            f"Lighting: {self.lighting}",
        ]
        return ", ".join(parts)
