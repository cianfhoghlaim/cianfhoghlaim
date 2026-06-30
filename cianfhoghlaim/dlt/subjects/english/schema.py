"""English schema — Cianfhoghlaim Oideachais."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EnglNCCALevel(str, Enum):
    JC = "jc"
    LC_OL = "lc_ol"
    LC_HL = "lc_hl"


class EnglTopicArea(str, Enum):
    COMPREHENDING = "comprehending"
    COMPOSITION = "composition"
    COMPARATIVE = "comparative"
    POETRY_PRESCRIBED = "poetry_prescribed"
    POETRY_UNSEEN = "poetry_unseen"
    DRAMA_PRESCRIBED = "drama_prescribed"
    FILM = "film"
    SPOKEN_ENGLISH = "spoken_english"
    LITERARY_GENRE = "literary_genre"
    MEDIA_LITERACY = "media_literacy"


class EnglItemType(str, Enum):
    COMPREHENSION_ITEM = "comprehension_item"
    COMPOSITION_PROMPT = "composition_prompt"
    COMPARATIVE_ITEM = "comparative_item"
    POETRY_ANALYSIS = "poetry_analysis"
    UNSEEN_POETRY_ITEM = "unseen_poetry_item"
    DRAMA_ANALYSIS = "drama_analysis"
    FILM_ANALYSIS = "film_analysis"
    MEDIA_LITERACY_ITEM = "media_literacy_item"


class EnglFeedbackChannel(str, Enum):
    ENGL_TUTOR = "engl_tutor"
    QUEST_GUIDE = "quest_guide"
    CURRICULUM_LOOKUP = "curriculum_lookup"
    RESEARCH_ASSISTANT = "research_assistant"


class EnglBilingualText(BaseModel):
    text_en: str
    text_ga: Optional[str] = None


class EnglEvidenceLink(BaseModel):
    source_pdf: str
    source_page: int = Field(..., ge=1)
    excerpt_en: str
    excerpt_ga: Optional[str] = None
    ncca_url: Optional[str] = None


class EnglNCCALearningOutcome(BaseModel):
    lo_code: str
    framework: str
    level: EnglNCCALevel
    topic: EnglTopicArea
    competency_text: EnglBilingualText
    marking_scheme_excerpt: Optional[EnglBilingualText] = None
    evidence: EnglEvidenceLink


class EnglFormativeItem(BaseModel):
    id: str
    lo_code: str
    level: EnglNCCALevel
    topic: EnglTopicArea
    item_type: EnglItemType
    difficulty: int = Field(..., ge=1, le=5)
    prompt: EnglBilingualText
    expected_answer: EnglBilingualText
    marking_scheme: EnglBilingualText
    common_errors: list[EnglBilingualText]
    hints: list[EnglBilingualText] = Field(..., min_length=4, max_length=4)
    evidence: EnglEvidenceLink
    feedback_channel: EnglFeedbackChannel
    est_time_minutes: int = Field(..., ge=1, le=30)


class EnglFormativeItemAttempt(BaseModel):
    item_id: str
    student_response: str
    response_format: str
    time_taken_seconds: int
    hints_used: int = Field(..., ge=0, le=4)


class EnglScoreBreakdown(BaseModel):
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


class EnglQuestPack(BaseModel):
    id: str
    subject: str = "english"
    framework: str
    level: EnglNCCALevel
    title: EnglBilingualText
    description: EnglBilingualText
    total_items: int
    total_marks: int
    est_time_minutes: int
    los_covered: list[str]
    items: list[EnglFormativeItem]
    prerequisites: list[str]
    cross_subject_links: list[str]
    generated_at: str
    generated_by: str = "engl_agent"


class EnglQuestPackValidation(BaseModel):
    pack_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]