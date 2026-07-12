"""History schema — Cianfhoghlaim Oideachais."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class HistNCCALevel(str, Enum):
    JC = "jc"
    LC_OL = "lc_ol"
    LC_HL = "lc_hl"


class HistTopicArea(str, Enum):
    EARLY_MODERN_IRELAND_1500_1800 = "early_modern_ireland_1500_1800"
    MODERN_IRELAND_1800_PRESENT = "modern_ireland_1800_present"
    EUROPEAN_HISTORY = "european_history"
    WORLD_HISTORY = "world_history"
    RESEARCH_STUDY = "research_study"
    DOCUMENT_STUDY = "document_study"
    SHORT_ANSWERS_DOCUMENTS = "short_answers_documents"


class HistItemType(str, Enum):
    DOCUMENT_BASED_QUESTION = "document_based_question"
    ESSAY_PROMPT = "essay_prompt"
    SHORT_ANSWER = "short_answer"
    CONCEPTUAL = "conceptual"
    SOURCE_COMPARISON = "source_comparison"


class HistFeedbackChannel(str, Enum):
    HIST_TUTOR = "hist_tutor"
    QUEST_GUIDE = "quest_guide"
    CURRICULUM_LOOKUP = "curriculum_lookup"
    RESEARCH_ASSISTANT = "research_assistant"


class HistBilingualText(BaseModel):
    text_en: str
    text_ga: Optional[str] = None


class HistEvidenceLink(BaseModel):
    source_pdf: str
    source_page: int = Field(..., ge=1)
    excerpt_en: str
    excerpt_ga: Optional[str] = None
    ncca_url: Optional[str] = None


class HistNCCALearningOutcome(BaseModel):
    lo_code: str
    framework: str
    level: HistNCCALevel
    topic: HistTopicArea
    competency_text: HistBilingualText
    marking_scheme_excerpt: Optional[HistBilingualText] = None
    evidence: HistEvidenceLink


class HistFormativeItem(BaseModel):
    id: str
    lo_code: str
    level: HistNCCALevel
    topic: HistTopicArea
    item_type: HistItemType
    difficulty: int = Field(..., ge=1, le=5)
    prompt: HistBilingualText
    expected_answer: HistBilingualText
    marking_scheme: HistBilingualText
    common_errors: list[HistBilingualText]
    hints: list[HistBilingualText] = Field(..., min_length=4, max_length=4)
    evidence: HistEvidenceLink
    feedback_channel: HistFeedbackChannel
    est_time_minutes: int = Field(..., ge=1, le=30)


class HistFormativeItemAttempt(BaseModel):
    item_id: str
    student_response: str
    response_format: str
    time_taken_seconds: int
    hints_used: int = Field(..., ge=0, le=4)


class HistScoreBreakdown(BaseModel):
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


class HistQuestPack(BaseModel):
    id: str
    subject: str = "history"
    framework: str
    level: HistNCCALevel
    title: HistBilingualText
    description: HistBilingualText
    total_items: int
    total_marks: int
    est_time_minutes: int
    los_covered: list[str]
    items: list[HistFormativeItem]
    prerequisites: list[str]
    cross_subject_links: list[str]
    generated_at: str
    generated_by: str = "hist_agent"


class HistQuestPackValidation(BaseModel):
    pack_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]