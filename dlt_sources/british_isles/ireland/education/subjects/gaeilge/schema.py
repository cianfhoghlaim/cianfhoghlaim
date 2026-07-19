"""Gaeilge schema — Cianfhoghlaim Oideachais.

Pydantic models for the Gaeilge pipeline. Note: text_ga is REQUIRED;
text_en may be null for native comprehension items.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class GaelNCCALevel(str, Enum):
    JC = "jc"
    LC_FL = "lc_fl"
    LC_OL = "lc_ol"
    LC_HL = "lc_hl"


class GaelTopicArea(str, Enum):
    LEAMHTHUISCINT = "leamhthuiscint"
    LITRIOCHT = "litriocht"
    GRAMADACH = "gramadach"
    FILIOCHT = "filiocht"
    PROS = "pros"
    BEALOIDEAS = "bealoideas"
    SCRIBHNEoireacht = "scribhneoireacht"
    CLUASTUISCINT = "cluastuiscint"
    SCOLAI = "scolai"
    CUNTASAIOCHT = "cuntasaiocht"


class GaelItemType(str, Enum):
    LEAMHTHUISCINT_ITEM = "leamhthuiscint_item"
    GRAMADACH_ITEM = "gramadach_item"
    AISTRÚCHÁN_ITEM = "aistriuchan_item"
    COMHRÁ_ITEM = "comhra_item"
    FILÍOCHT_ANALYSIS = "filiocht_analysis"
    LITRÍOCHT_ANALYSIS = "litriocht_analysis"
    COMPOSITION_PROMPT = "composition_prompt"
    CLUASTUISCINT_ITEM = "cluastuiscint_item"


class GaelFeedbackChannel(str, Enum):
    GAEL_TUTOR = "gael_tutor"
    QUEST_GUIDE = "quest_guide"
    CURRICULUM_LOOKUP = "curriculum_lookup"
    GRAMADACH_REVIEW = "gramadach_review"
    RESEARCH_ASSISTANT = "research_assistant"


class GaelBilingualText(BaseModel):
    text_en: Optional[str] = None
    text_ga: str  # REQUIRED for Gaeilge


class GaelEvidenceLink(BaseModel):
    source_pdf: str
    source_page: int = Field(..., ge=1)
    excerpt_ga: str  # REQUIRED
    excerpt_en: Optional[str] = None
    ncca_url: Optional[str] = None


class GaelNCCALearningOutcome(BaseModel):
    lo_code: str
    framework: str
    level: GaelNCCALevel
    topic: GaelTopicArea
    competency_text: GaelBilingualText
    marking_scheme_excerpt: Optional[GaelBilingualText] = None
    evidence: GaelEvidenceLink


class GaelFormativeItem(BaseModel):
    id: str
    lo_code: str
    level: GaelNCCALevel
    topic: GaelTopicArea
    item_type: GaelItemType
    difficulty: int = Field(..., ge=1, le=5)
    prompt: GaelBilingualText
    expected_answer: GaelBilingualText
    marking_scheme: GaelBilingualText
    common_errors: list[GaelBilingualText]
    hints: list[GaelBilingualText] = Field(..., min_length=4, max_length=4)
    evidence: GaelEvidenceLink
    feedback_channel: GaelFeedbackChannel
    est_time_minutes: int = Field(..., ge=1, le=30)


class GaelFormativeItemAttempt(BaseModel):
    item_id: str
    student_response: str
    response_format: str
    time_taken_seconds: int
    hints_used: int = Field(..., ge=0, le=4)


class GaelScoreBreakdown(BaseModel):
    item_id: str
    lo_code: str
    total_marks: int
    marks_awarded: int
    marks_per_step: list[int]
    is_correct: bool
    partial_credit_pct: float = Field(..., ge=0, le=100)
    feedback_ga: str  # REQUIRED
    feedback_en: Optional[str] = None
    next_recommended_lo: Optional[str] = None
    badge_earned: bool


class GaelQuestPack(BaseModel):
    id: str
    subject: str = "gaeilge"
    framework: str
    level: GaelNCCALevel
    title: GaelBilingualText
    description: GaelBilingualText
    total_items: int
    total_marks: int
    est_time_minutes: int
    los_covered: list[str]
    items: list[GaelFormativeItem]
    prerequisites: list[str]
    cross_subject_links: list[str]
    generated_at: str
    generated_by: str = "gael_agent"


class GaelQuestPackValidation(BaseModel):
    pack_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]