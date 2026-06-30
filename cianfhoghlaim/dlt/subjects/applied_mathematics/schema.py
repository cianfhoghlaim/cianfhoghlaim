"""Applied Mathematics schema — Cianfhoghlaim Oideachais.

Pydantic models for the Applied Mathematics pipeline, mirroring the
BAML classes in `qpack_applied_mathematics.baml`.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AppmNCCALevel(str, Enum):
    LC_HL = "lc_hl"


class AppmTopicArea(str, Enum):
    UNIFORM_ACCELERATION = "uniform_acceleration"
    NEWTONS_LAWS = "newtons_laws"
    PROJECTILES = "projectiles"
    FRICTION = "friction"
    WORK_ENERGY_POWER = "work_energy_power"
    IMPULSE_MOMENTUM = "impulse_momentum"
    CIRCULAR_MOTION = "circular_motion"
    SIMPLE_HARMONIC = "simple_harmonic"
    RIGID_BODY = "rigid_body"
    STATICS = "statics"
    GRAVITY = "gravity"
    HYDROSTATICS = "hydrostatics"
    DIFFERENTIAL_EQUATIONS = "differential_equations"
    VECTORS = "vectors"
    DIMENSIONAL_ANALYSIS = "dimensional_analysis"


class AppmItemType(str, Enum):
    SHORT_ANSWER = "short_answer"
    WORKED_SOLUTION = "worked_solution"
    CONCEPTUAL = "conceptual"
    VISUAL_INTERPRETATION = "visual_interpretation"
    WORD_PROBLEM = "word_problem"
    PROOF = "proof"


class AppmFeedbackChannel(str, Enum):
    APPM_TUTOR = "appm_tutor"
    QUEST_GUIDE = "quest_guide"
    CURRICULUM_LOOKUP = "curriculum_lookup"
    RESEARCH_ASSISTANT = "research_assistant"
    MATH_BRIDGE = "math_bridge"


class AppmBilingualText(BaseModel):
    text_en: str
    text_ga: Optional[str] = None


class AppmEvidenceLink(BaseModel):
    source_pdf: str
    source_page: int = Field(..., ge=1)
    excerpt_en: str
    excerpt_ga: Optional[str] = None
    ncca_url: Optional[str] = None


class AppmNCCALearningOutcome(BaseModel):
    lo_code: str
    framework: str = "ncca-lc"
    level: AppmNCCALevel
    topic: AppmTopicArea
    competency_text: AppmBilingualText
    marking_scheme_excerpt: Optional[AppmBilingualText] = None
    evidence: AppmEvidenceLink


class AppmFormativeItem(BaseModel):
    id: str
    lo_code: str
    level: AppmNCCALevel
    topic: AppmTopicArea
    item_type: AppmItemType
    difficulty: int = Field(..., ge=1, le=5)
    prompt: AppmBilingualText
    expected_answer: AppmBilingualText
    marking_scheme: AppmBilingualText
    common_errors: list[AppmBilingualText]
    hints: list[AppmBilingualText] = Field(..., min_length=4, max_length=4)
    evidence: AppmEvidenceLink
    feedback_channel: AppmFeedbackChannel
    est_time_minutes: int = Field(..., ge=1, le=30)


class AppmFormativeItemAttempt(BaseModel):
    item_id: str
    student_response: str
    response_format: str
    time_taken_seconds: int
    hints_used: int = Field(..., ge=0, le=4)


class AppmScoreBreakdown(BaseModel):
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


class AppmQuestPack(BaseModel):
    id: str
    subject: str = "applied_mathematics"
    framework: str = "ncca-lc"
    level: AppmNCCALevel
    title: AppmBilingualText
    description: AppmBilingualText
    total_items: int
    total_marks: int
    est_time_minutes: int
    los_covered: list[str]
    items: list[AppmFormativeItem]
    prerequisites: list[str]
    cross_subject_links: list[str]
    generated_at: str
    generated_by: str = "appm_agent"


class AppmQuestPackValidation(BaseModel):
    pack_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]