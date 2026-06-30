"""Chemistry schema — Cianfhoghlaim Oideachais."""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ChemNCCALevel(str, Enum):
    JC = "jc"
    LC_OL = "lc_ol"
    LC_HL = "lc_hl"


class ChemTopicArea(str, Enum):
    ATOMIC_STRUCTURE = "atomic_structure"
    BONDING = "bonding"
    STOICHIOMETRY = "stoichiometry"
    ACIDS_BASES = "acids_bases"
    ORGANIC_CHEMISTRY = "organic_chemistry"
    THERMODYNAMICS = "thermodynamics"
    ELECTROCHEMISTRY = "electrochemistry"
    EQUILIBRIA = "equilibria"
    PERIODIC_TABLE = "periodic_table"
    RATES_OF_REACTION = "rates_of_reaction"
    STATES_OF_MATTER = "states_of_matter"
    WATER_CHEMISTRY = "water_chemistry"
    CHEMICAL_EQUILIBRIUM = "chemical_equilibrium"
    ATOMIC_SPECTROSCOPY = "atomic_spectroscopy"
    NUCLEAR_CHEMISTRY = "nuclear_chemistry"


class ChemItemType(str, Enum):
    SHORT_ANSWER = "short_answer"
    WORKED_SOLUTION = "worked_solution"
    BALANCE_EQUATION = "balance_equation"
    STRUCTURE_DRAWING = "structure_drawing"
    CONCEPTUAL = "conceptual"
    VISUAL_INTERPRETATION = "visual_interpretation"
    WORD_PROBLEM = "word_problem"
    LAB_PROCEDURE = "lab_procedure"


class ChemFeedbackChannel(str, Enum):
    CHEM_TUTOR = "chem_tutor"
    QUEST_GUIDE = "quest_guide"
    CURRICULUM_LOOKUP = "curriculum_lookup"
    LAB_ASSISTANT = "lab_assistant"
    RESEARCH_ASSISTANT = "research_assistant"


class ChemBilingualText(BaseModel):
    text_en: str
    text_ga: Optional[str] = None


class ChemEvidenceLink(BaseModel):
    source_pdf: str
    source_page: int = Field(..., ge=1)
    excerpt_en: str
    excerpt_ga: Optional[str] = None
    ncca_url: Optional[str] = None


class ChemNCCALearningOutcome(BaseModel):
    lo_code: str
    framework: str
    level: ChemNCCALevel
    topic: ChemTopicArea
    competency_text: ChemBilingualText
    marking_scheme_excerpt: Optional[ChemBilingualText] = None
    evidence: ChemEvidenceLink


class ChemFormativeItem(BaseModel):
    id: str
    lo_code: str
    level: ChemNCCALevel
    topic: ChemTopicArea
    item_type: ChemItemType
    difficulty: int = Field(..., ge=1, le=5)
    prompt: ChemBilingualText
    expected_answer: ChemBilingualText
    marking_scheme: ChemBilingualText
    common_errors: list[ChemBilingualText]
    hints: list[ChemBilingualText] = Field(..., min_length=4, max_length=4)
    evidence: ChemEvidenceLink
    feedback_channel: ChemFeedbackChannel
    est_time_minutes: int = Field(..., ge=1, le=30)


class ChemFormativeItemAttempt(BaseModel):
    item_id: str
    student_response: str
    response_format: str
    time_taken_seconds: int
    hints_used: int = Field(..., ge=0, le=4)


class ChemScoreBreakdown(BaseModel):
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


class ChemQuestPack(BaseModel):
    id: str
    subject: str = "chemistry"
    framework: str
    level: ChemNCCALevel
    title: ChemBilingualText
    description: ChemBilingualText
    total_items: int
    total_marks: int
    est_time_minutes: int
    los_covered: list[str]
    items: list[ChemFormativeItem]
    prerequisites: list[str]
    cross_subject_links: list[str]
    generated_at: str
    generated_by: str = "chem_agent"


class ChemQuestPackValidation(BaseModel):
    pack_id: str
    is_valid: bool
    errors: list[str]
    warnings: list[str]