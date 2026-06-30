"""Geography schema — Cianfhoghlaim Oideachais."""
from __future__ import annotations

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class GeogNCCALevel(str, Enum):
    JC = "jc"
    LC_OL = "lc_ol"
    LC_HL = "lc_hl"


class GeogTopicArea(str, Enum):
    PHYSICAL_RIVERS = "physical_rivers"
    PHYSICAL_COASTS = "physical_coasts"
    PHYSICAL_CLIMATE = "physical_climate"
    PHYSICAL_BIOMES = "physical_biomes"
    PHYSICAL_PLATE_TECTONICS = "physical_plate_tectonics"
    PHYSICAL_GLACIATION = "physical_glaciation"
    REGIONAL_IRELAND = "regional_ireland"
    REGIONAL_EUROPE = "regional_europe"
    REGIONAL_SUB_CONTINENT = "regional_sub_continent"
    REGIONAL_GLOBAL = "regional_global"
    GEOECOLOGY = "geoecology"
    HUMAN_POPULATION = "human_population"
    HUMAN_URBAN = "human_urban"
    HUMAN_ECONOMIC = "human_economic"
    HUMAN_DEVELOPMENT = "human_development"
    FIELDWORK_INVESTIGATION = "fieldwork_investigation"


class GeogItemType(str, Enum):
    SHORT_ANSWER = "short_answer"
    WORKED_SOLUTION = "worked_solution"
    MAP_INTERPRETATION = "map_interpretation"
    GRAPH_READING = "graph_reading"
    OS_MAP_SKILLS = "os_map_skills"
    CONCEPTUAL = "conceptual"
    ESSAY_PROMPT = "essay_prompt"
    FIELDWORK_REPORT = "fieldwork_report"


class GeogFeedbackChannel(str, Enum):
    GEOG_TUTOR = "geog_tutor"
    QUEST_GUIDE = "quest_guide"
    CURRICULUM_LOOKUP = "curriculum_lookup"
    RESEARCH_ASSISTANT = "research_assistant"


class GeogBilingualText(BaseModel):
    text_en: str
    text_ga: Optional[str] = None


class GeogEvidenceLink(BaseModel):
    source_pdf: str
    source_page: int = Field(..., ge=1)
    excerpt_en: str
    excerpt_ga: Optional[str] = None
    ncca_url: Optional[str] = None


class GeogNCCALearningOutcome(BaseModel):
    lo_code: str
    framework: str
    level: GeogNCCALevel
    topic: GeogTopicArea
    competency_text: GeogBilingualText
    marking_scheme_excerpt: Optional[GeogBilingualText] = None
    evidence: GeogEvidenceLink


class GeogFormativeItem(BaseModel):
    id: str
    lo_code: str
    level: GeogNCCALevel
    topic: GeogTopicArea
    item_type: GeogItemType
    difficulty: int = Field(..., ge=1, le=5)
    prompt: GeogBilingualText
    expected_answer: GeogBilingualText
    marking_scheme: GeogBilingualText
    common_errors: list[GeogBilingualText]
    hints: list[GeogBilingualText] = Field(..., min_length=4, max_length=4)
    evidence: GeogEvidenceLink
    feedback_channel: GeogFeedbackChannel
    est_time_minutes: int = Field(..., ge=1, le=30)


class GeogFormativeItemAttempt(BaseModel):
    item_id: str
    student_response: str
    response_format: str
    time_taken_seconds: int
    hints_used: int = Field(..., ge=0, le=4)


class GeogScoreBreakdown(BaseModel):
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


class GeogQuestPack(BaseModel):
    id: str
    subject: str = "geography"
    framework: str
    level: GeogNCCALevel
    title: GeogBilingualText
    description: GeogBilingualText
    total_items: int
    total_marks: int
    est_time_minutes: int
    los_covered: list[str]
    items: list[GeogFormativeItem]
    prerequisites: list[str]
    cross_subject_links: list[str]
    generated_at: str
    generated_by: str = "geog_agent"


class GeogQuestPackValidation(BaseModel):
    pack_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]