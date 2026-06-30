"""Computer Science schema — Cianfhoghlaim Oideachais."""
from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CompNCCALevel(str, Enum):
    JC_CODING_SHORT_COURSE = "jc_coding_short_course"
    LC_OL = "lc_ol"
    LC_HL = "lc_hl"


class CompTopicArea(str, Enum):
    ALGORITHMS = "algorithms"
    DATA_STRUCTURES = "data_structures"
    PROGRAMMING = "programming"
    COMPUTATIONAL_THINKING = "computational_thinking"
    COMPUTER_SYSTEMS = "computer_systems"
    NETWORKS = "networks"
    DATABASES = "databases"
    WEB_DEVELOPMENT = "web_development"
    DATA_REPRESENTATION = "data_representation"
    ETHICS = "ethics"
    PROBLEM_SOLVING = "problem_solving"


class CompItemType(str, Enum):
    SHORT_ANSWER = "short_answer"
    CODE_COMPLETION = "code_completion"
    CODE_TRACE = "code_trace"
    CONCEPTUAL = "conceptual"
    ALGORITHM_DESIGN = "algorithm_design"
    DEBUGGING = "debugging"
    WORD_PROBLEM = "word_problem"


class CompFeedbackChannel(str, Enum):
    COMP_TUTOR = "comp_tutor"
    QUEST_GUIDE = "quest_guide"
    CURRICULUM_LOOKUP = "curriculum_lookup"
    CODE_REVIEWER = "code_reviewer"
    RESEARCH_ASSISTANT = "research_assistant"


class CompBilingualText(BaseModel):
    text_en: str
    text_ga: Optional[str] = None


class CompEvidenceLink(BaseModel):
    source_pdf: str
    source_page: int = Field(..., ge=1)
    excerpt_en: str
    excerpt_ga: Optional[str] = None
    ncca_url: Optional[str] = None


class CompNCCALearningOutcome(BaseModel):
    lo_code: str
    framework: str
    level: CompNCCALevel
    topic: CompTopicArea
    competency_text: CompBilingualText
    marking_scheme_excerpt: Optional[CompBilingualText] = None
    evidence: CompEvidenceLink


class CompFormativeItem(BaseModel):
    id: str
    lo_code: str
    level: CompNCCALevel
    topic: CompTopicArea
    item_type: CompItemType
    difficulty: int = Field(..., ge=1, le=5)
    prompt: CompBilingualText
    expected_answer: CompBilingualText
    marking_scheme: CompBilingualText
    common_errors: list[CompBilingualText]
    hints: list[CompBilingualText] = Field(..., min_length=4, max_length=4)
    evidence: CompEvidenceLink
    feedback_channel: CompFeedbackChannel
    est_time_minutes: int = Field(..., ge=1, le=30)


class CompFormativeItemAttempt(BaseModel):
    item_id: str
    student_response: str
    response_format: str
    time_taken_seconds: int
    hints_used: int = Field(..., ge=0, le=4)


class CompScoreBreakdown(BaseModel):
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


class CompQuestPack(BaseModel):
    id: str
    subject: str = "computer_science"
    framework: str
    level: CompNCCALevel
    title: CompBilingualText
    description: CompBilingualText
    total_items: int
    total_marks: int
    est_time_minutes: int
    los_covered: list[str]
    items: list[CompFormativeItem]
    prerequisites: list[str]
    cross_subject_links: list[str]
    generated_at: str
    generated_by: str = "comp_agent"


class CompQuestPackValidation(BaseModel):
    pack_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]