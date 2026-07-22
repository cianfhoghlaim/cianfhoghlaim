"""Mathematics schema — Cianfhoghlaim Oideachais.

Pydantic models for the Mathematics pipeline. These mirror the BAML
classes in `cianfhoghlaim/baml/qpack_mathematics.baml` and are used
for runtime type validation in the Dagster assets.

The BAML file is the source of truth (it controls the LLM contract);
this module mirrors the shapes so the Python pipeline can be type-checked
without round-tripping through BAML codegen.

See:
    cianfhoghlaim/baml/qpack_mathematics.baml (source of truth)
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MathNCCALevel(str, Enum):
    JC = "jc"
    LC_FL = "lc_fl"
    LC_OL = "lc_ol"
    LC_HL = "lc_hl"


class MathTopicArea(str, Enum):
    ALGEBRA = "algebra"
    FUNCTIONS_AND_CALCULUS = "functions_and_calculus"
    DIFFERENTIATION = "differentiation"
    INTEGRATION = "integration"
    COORDINATE_GEOMETRY = "coordinate_geometry"
    TRIGONOMETRY = "trigonometry"
    COMPLEX_NUMBERS = "complex_numbers"
    SEQUENCES_AND_SERIES = "sequences_and_series"
    PROBABILITY = "probability"
    STATISTICS = "statistics"
    FINANCE = "finance"
    GEOMETRY = "geometry"
    MECHANICS = "mechanics"
    NUMBER_SYSTEMS = "number_systems"
    ARITHMETIC = "arithmetic"
    SETS_AND_LOGIC = "sets_and_logic"


class FormativeItemType(str, Enum):
    SHORT_ANSWER = "short_answer"
    WORKED_SOLUTION = "worked_solution"
    CONCEPTUAL = "conceptual"
    VISUAL_INTERPRETATION = "visual_interpretation"
    WORD_PROBLEM = "word_problem"
    PROOF = "proof"


class FeedbackChannel(str, Enum):
    MATH_TUTOR = "math_tutor"
    QUEST_GUIDE = "quest_guide"
    CURRICULUM_LOOKUP = "curriculum_lookup"
    RESEARCH_ASSISTANT = "research_assistant"


class BilingualText(BaseModel):
    """Bilingual EN + GA text. text_ga may be None for EN-only content."""

    text_en: str
    text_ga: Optional[str] = None


class EvidenceLink(BaseModel):
    """Pointer to the source NCCA PDF page for a learning outcome."""

    source_pdf: str
    source_page: int = Field(..., ge=1)
    excerpt_en: str
    excerpt_ga: Optional[str] = None
    ncca_url: Optional[str] = None


class MathNCCALearningOutcome(BaseModel):
    """One NCCA learning outcome, typed."""

    lo_code: str
    framework: str = Field(..., description="One of: 'ncca-lc', 'ncca-jc'")
    level: MathNCCALevel
    topic: MathTopicArea
    competency_text: BilingualText
    marking_scheme_excerpt: Optional[BilingualText] = None
    evidence: EvidenceLink


class FormativeItem(BaseModel):
    """One formative assessment item — the atomic unit of practice."""

    id: str
    lo_code: str
    level: MathNCCALevel
    topic: MathTopicArea
    item_type: FormativeItemType
    difficulty: int = Field(..., ge=1, le=5)
    prompt: BilingualText
    expected_answer: BilingualText
    marking_scheme: BilingualText
    common_errors: list[BilingualText]
    hints: list[BilingualText] = Field(..., min_length=4, max_length=4)
    evidence: EvidenceLink
    feedback_channel: FeedbackChannel
    est_time_minutes: int = Field(..., ge=1, le=30)


class FormativeItemAttempt(BaseModel):
    """One student's attempt at one formative item."""

    item_id: str
    student_response: str
    response_format: str
    time_taken_seconds: int
    hints_used: int = Field(..., ge=0, le=4)


class ScoreBreakdown(BaseModel):
    """Per-step scoring + feedback for one attempt."""

    item_id: str
    lo_code: str
    total_marks: int
    marks_awarded: int
    marks_per_step: list[int]
    is_correct: bool
    partial_credit_pct: float = Field(..., ge=0, le=100)
    feedback_en: str
    feedback_ga: Optional[str] = None
    next_recommended_lo: Optional[str] = None
    badge_earned: bool


class QuestPack(BaseModel):
    """One quest pack delivered to a student. Contains ≥1 item per LO."""

    id: str
    subject: str = "mathematics"
    framework: str = Field(..., description="One of: 'ncca-lc', 'ncca-jc'")
    level: MathNCCALevel
    title: BilingualText
    description: BilingualText
    total_items: int
    total_marks: int
    est_time_minutes: int
    los_covered: list[str]
    items: list[FormativeItem]
    prerequisites: list[str]
    cross_subject_links: list[str]
    generated_at: str
    generated_by: str = "math_agent"


class QuestPackValidation(BaseModel):
    """Validation result for a quest pack."""

    pack_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]