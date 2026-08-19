"""Canonical Pydantic v2 schema for the meaisinfoghlaim alignment layer.

Per the 2026-08-15-meaisinfoghlaim-ireland-england-roadmap (Plan 2).

Provides the canonical typed schemas for:
  - ExamMarkingAlignment    (UC 2: q_id join ExamPaper <-> MarkingScheme)
  - TopicGraphEdge          (UC 3: subject topic graph edges)
  - DiagramIndexEntry       (UC 8: diagram-to-topic indexer)
  - BilingualConcept        (UC 7: EN<->GA concept pair registry)
  - CrossLinguisticConcept  (UC 7: BAML ExtractCrossLinguisticConcept output)
  - BilingualTopicEdge      (UC 7 + UC 3: bilingual topic graph edges with language_pair dimension)
  - BilingualCoverageAudit  (UC 7 + UC 10: per-cohort bilingual coverage audit)

The schemas are Pydantic v2 (BaseModel) so they have:
  - JSON-serializable (for LanceDB + MotherDuck + MLflow logging)
  - Field validators (enforce [0.0, 1.0] on confidence scores, enums on capability/stage)
  - ConfigDict to freeze slots for hashability
  - model_dump_json() / model_validate_json() for roundtripping

Generalisable: every schema's keys are jurisdiction/stage/subject/board-agnostic
(works for Scotland Nat 5/Higher/Adv Higher, Wales EN/CY, NI CCEA, etc.).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Capability + Stage enums (the canonical enumeration for the BIEP pipeline)
# ---------------------------------------------------------------------------


class Capability(str, Enum):
    """The canonical OCR/VLM capability enum (mirrors the ocr-router contract)."""

    FORMS = "forms"  # handwritten + printed forms
    LAYOUT = "layout"  # dense + sparse layout
    TABLES_LATEX = "tables+latex"  # math + table extraction
    DOCTAGS = "doctags"  # IBM DocTags format
    GAELIC = "gaelic"  # Modern Irish (Gaeilge) text
    ENGLISH = "english"  # English text
    TESSERACT_FALLBACK = "tesseract-fallback"  # legacy Tesseract


class Stage(str, Enum):
    """The canonical qualification-stage enum (jurisdiction-agnostic)."""

    PRIMARY = "primary"
    JC = "jc"  # Junior Cycle (Ireland)
    KS3 = "ks3"  # England (Key Stage 3)
    GCSE = "gcse"  # England
    LC = "lc"  # Leaving Cert (Ireland)
    A_LEVEL = "a_level"  # England
    NAT_5 = "national_5"  # Scotland
    HIGHER = "higher"
    ADV_HIGHER = "advanced_higher"


class LanguagePair(str, Enum):
    """The canonical bilingual language-pair dimension."""

    EN_GA = "en-ga"  # English <-> Irish (Ireland primary)
    EN_CY = "en-cy"  # English <-> Welsh (Wales primary)
    EN_GD = "en-gd"  # English <-> Scottish Gaelic (Scotland primary)


# ---------------------------------------------------------------------------
# UC 2: ExamMarkingAlignment
# ---------------------------------------------------------------------------


class ExamMarkingAlignment(BaseModel):
    """The canonical join between ExamPaper and MarkingScheme on q_id.

    Per the 2026-08-15 plan (Plan 2, UC 2): 1 row per (paper_code, q_id,
    mark_allocation_id) tuple. Used by the BIEP v3 alignment dashboard +
    the per-subject regression summary.
    """

    model_config = ConfigDict(frozen=True, slots=True)

    alignment_id: str = Field(..., description="Canonical UUID for the alignment row")
    cohort_key: str = Field(..., description="Canonical 'jurisdiction/stage/subject/board/language' key")
    paper_code: str = Field(..., description="The exam paper code (e.g. 'lc_chem_2024_p1')")
    q_id: str = Field(..., description="The question ID from the ExamPaper schema")
    mark_allocation_id: str = Field(..., description="The mark allocation ID from the MarkingScheme schema")
    marks_awarded: int = Field(..., ge=0, description="Marks awarded for this alignment (from MarkingScheme)")
    marks_available: int = Field(..., ge=0, description="Marks available for this question (from ExamPaper)")
    alignment_confidence: float = Field(..., ge=0.0, le=1.0, description="q_id match confidence (1.0 = exact match)")
    partial_credit_rule: str | None = Field(default=None, description="Partial-credit rule id (from MarkingScheme)")
    common_mistake: str | None = Field(default=None, description="Canonical common mistake id")
    related_lo_id: str | None = Field(default=None, description="The related learning outcome (from ExamPaper)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("paper_code")
    @classmethod
    def _validate_paper_code(cls, v: str) -> str:
        """Enforce canonical paper_code format: 'lc_<subject>_<year>_<part>'."""
        if not re.match(r"^[a-z0-9_]+$", v):
            raise ValueError(
                f"paper_code must match '^[a-z0-9_]+$' (got {v!r})"
            )
        return v

    @model_validator(mode="after")
    def _validate_marks_consistency(self) -> "ExamMarkingAlignment":
        """Marks awarded must be <= marks available."""
        if self.marks_awarded > self.marks_available:
            raise ValueError(
                f"marks_awarded ({self.marks_awarded}) > marks_available "
                f"({self.marks_available})"
            )
        return self


# ---------------------------------------------------------------------------
# UC 3: TopicGraphEdge
# ---------------------------------------------------------------------------


class TopicGraphEdge(BaseModel):
    """The canonical topic-graph edge for a subject.

    Per the 2026-08-15 plan (Plan 2, UC 3): 1 row per (subject, topic_a,
    topic_b, weight) tuple. Nodes are topic IDs; edges are weighted by
    relevance (0.0-1.0).
    """

    model_config = ConfigDict(frozen=True, slots=True)

    edge_id: str = Field(..., description="Canonical UUID for the edge")
    cohort_key: str = Field(..., description="Canonical 'jurisdiction/stage/subject/board/language' key")
    topic_a: str = Field(..., description="The first topic ID (e.g. 'algebra_linear_equations')")
    topic_b: str = Field(..., description="The second topic ID (e.g. 'algebra_quadratic_equations')")
    weight: float = Field(..., ge=0.0, le=1.0, description="Edge weight (relevance 0.0-1.0)")
    edge_type: Literal["prerequisite", "related", "extension"] = Field(default="related")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# UC 7: CrossLinguisticConcept (BAML ExtractCrossLinguisticConcept output)
# ---------------------------------------------------------------------------


class CrossLinguisticConcept(BaseModel):
    """The canonical cross-linguistic concept (EN<->GA) extracted by BAML.

    Per the 2026-08-15 plan (Plan 2, UC 7): produced by the BAML
    ExtractCrossLinguisticConcept function (in baml_src/british_isles/
    ireland/education/lc_extraction/cross_linguistic.baml).
    """

    model_config = ConfigDict(frozen=True, slots=True)

    concept_id: str = Field(..., description="Canonical UUID")
    en_term: str = Field(..., description="The English term (e.g. 'algebra')")
    ga_term: str = Field(..., description="The Irish term (e.g. 'ailgéabar')")
    definition_en: str | None = Field(default=None, description="English definition")
    definition_ga: str | None = Field(default=None, description="Irish definition")
    language_pair: LanguagePair = Field(default=LanguagePair.EN_GA)
    domain: str = Field(default="curriculum", description="'curriculum' | 'exam' | 'folklore'")
    subject: str | None = Field(default=None)
    stage: Stage | None = Field(default=None)
    topic_id: str | None = Field(default=None, description="The topic this concept belongs to")
    translation_fidelity: float = Field(default=1.0, ge=0.0, le=1.0)
    cultural_note: str | None = Field(default=None)
    source_url: str | None = Field(default=None, description="e.g. https://www.tearma.ie/...")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# UC 7 + Plan 2: BilingualConcept (the canonical registry entry)
# ---------------------------------------------------------------------------


class BilingualConcept(BaseModel):
    """The canonical EN<->GA concept pair registry entry (Plan 2 bilingual).

    This is the unified schema for the bilingual_concept_registry; one row
    per concept pair. Bridges the BAML ExtractCrossLinguisticConcept
    output + the manual operator-curated entries.
    """

    model_config = ConfigDict(frozen=True, slots=True)

    pair_id: str = Field(..., description="Canonical UUID for the pair")
    en_term: str = Field(..., description="The English term (e.g. 'algebra')")
    ga_term: str = Field(..., description="The Irish term (e.g. 'ailgéabar')")
    definition_en: str | None = Field(default=None)
    definition_ga: str | None = Field(default=None)
    language_pair: LanguagePair = Field(default=LanguagePair.EN_GA)
    subject_id: str = Field(..., description="The canonical subject ID (matches the Ireland LC subject list)")
    stage: Stage = Field(..., description="The qualification stage")
    topic_id: str = Field(..., description="The topic this concept belongs to")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction / curation confidence (0-1)")
    source_url: str | None = Field(default=None)
    extraction_method: Literal["baml", "operator_curated", "hybrid"] = Field(default="baml")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# UC 3 + UC 7: BilingualTopicEdge (the topic graph edge with language_pair dimension)
# ---------------------------------------------------------------------------


class BilingualTopicEdge(BaseModel):
    """The canonical bilingual topic graph edge (Plan 2 UC 3 + UC 7).

    Same shape as TopicGraphEdge but with the bilingual language_pair
    dimension + the bilingual concept anchor (the bilingual_concept_registry
    pair_id that anchors the edge).
    """

    model_config = ConfigDict(frozen=True, slots=True)

    edge_id: str = Field(..., description="Canonical UUID for the edge")
    cohort_key: str = Field(..., description="Canonical 'jurisdiction/stage/subject/board/language' key")
    topic_a: str = Field(..., description="First topic ID (e.g. 'algebra_linear_equations')")
    topic_b: str = Field(..., description="Second topic ID")
    weight: float = Field(..., ge=0.0, le=1.0)
    language_pair: LanguagePair = Field(..., description="The language pair this edge anchors")
    anchored_pair_id: str | None = Field(
        default=None,
        description="The bilingual_concept_registry pair_id that anchors this edge (the concept that makes the topic edge bilingual)",
    )
    edge_type: Literal["prerequisite", "related", "extension"] = Field(default="related")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# UC 8: DiagramIndexEntry (the diagram-to-topic indexer output)
# ---------------------------------------------------------------------------


class DiagramIndexEntry(BaseModel):
    """The canonical diagram index entry (Plan 2 UC 8).

    One row per diagram in the syllabus PDFs (extracted by BAML
    ExtractSyllabusDiagram). Stored in LanceDB for semantic search.
    """

    model_config = ConfigDict(frozen=True, slots=True)

    entry_id: str = Field(..., description="Canonical UUID")
    cohort_key: str = Field(..., description="Canonical cohort key")
    page_number: int = Field(..., ge=1)
    caption: str = Field(..., description="The diagram caption (BAML extraction)")
    diagram_role: Literal["concept_map", "flowchart", "diagram", "table", "image"] = Field(default="diagram")
    related_topic_id: str | None = Field(default=None)
    related_lo_id: str | None = Field(default=None)
    bounding_box_json: str | None = Field(default=None, description="JSON-serialized bbox {x, y, w, h, page}")
    ocr_text: str | None = Field(default=None, description="OCR'd text from within the diagram region")
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_pdf_path: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# UC 7 + UC 10: BilingualCoverageAudit (per-cohort audit, >= 95% gate)
# ---------------------------------------------------------------------------


class BilingualCoverageAudit(BaseModel):
    """The canonical per-cohort bilingual EN<->GA coverage audit.

    Per the 2026-08-15 plan (Plan 2): 1 row per cohort. Gates at >= 95%
    bilingual coverage per the locked BIEP v3 threshold.
    """

    model_config = ConfigDict(frozen=True, slots=True)

    audit_id: str = Field(..., description="Canonical UUID")
    cohort_key: str = Field(..., description="Canonical cohort key (e.g. 'ireland/lc/mathematics/en')")
    language_pair: LanguagePair = Field(default=LanguagePair.EN_GA)

    # The 3 canonical coverage metrics
    en_topic_count: int = Field(..., ge=0, description="Number of topics with an EN extraction")
    en_topic_total: int = Field(..., ge=0, description="Total topic count for the cohort")
    en_coverage_pct: float = Field(default=0.0, ge=0.0, le=1.0)

    ga_topic_count: int = Field(..., ge=0, description="Number of topics with a GA extraction")
    ga_topic_total: int = Field(..., ge=0)
    ga_coverage_pct: float = Field(default=0.0, ge=0.0, le=1.0)

    bilingual_pairs_found: int = Field(..., ge=0, description="Count of EN<->GA pairs in the registry")
    gap_topics: list[str] = Field(default_factory=list, description="Topics missing EN or GA coverage")

    # The gate
    THRESHOLD: ClassVar[float] = 0.95
    passed_threshold: bool = Field(default=False)

    duration_s: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def _compute_derived(self) -> "BilingualCoverageAudit":
        """Compute coverage_pct + passed_threshold from raw counts."""
        en_pct = (
            self.en_topic_count / self.en_topic_total
            if self.en_topic_total > 0
            else 0.0
        )
        ga_pct = (
            self.ga_topic_count / self.ga_topic_total
            if self.ga_topic_total > 0
            else 0.0
        )
        # Both EN and GA must independently meet the threshold
        passed = en_pct >= self.THRESHOLD and ga_pct >= self.THRESHOLD
        # Round to 4 dp
        object.__setattr__(self, "en_coverage_pct", round(en_pct, 4))
        object.__setattr__(self, "ga_coverage_pct", round(ga_pct, 4))
        object.__setattr__(self, "passed_threshold", passed)
        return self


__all__ = [
    "Capability",
    "Stage",
    "LanguagePair",
    "ExamMarkingAlignment",
    "TopicGraphEdge",
    "CrossLinguisticConcept",
    "BilingualConcept",
    "BilingualTopicEdge",
    "DiagramIndexEntry",
    "BilingualCoverageAudit",
]



# ============================================================================
# Plan 3 schemas (cross-qualification + regression)
# ============================================================================


class QualificationLevel(str, Enum):
    """The canonical qualification-level enum (the qualification axis for Plan 3)."""

    PRIMARY = "primary"
    JC = "jc"
    KS3 = "ks3"
    GCSE = "gcse"
    LC = "lc"
    A_LEVEL = "a_level"
    NATIONAL_5 = "national_5"
    HIGHER = "higher"
    ADVANCED_HIGHER = "advanced_higher"
    FOUNDATION = "foundation"


class Board(str, Enum):
    """The canonical examination-board enum (England + future)."""

    AQA = "aqa"
    OCR = "ocr"
    EDEXCEL = "edexcel"
    CCEA = "ccea"  # Northern Ireland
    IOMGCE = "iomgce"  # Isle of Man
    SQA = "sqa"  # Scotland
    WJEC = "wjec"  # Wales
    CBSE = "cbse"  # India
    NONE = "none"  # jurisdictions without boards (Ireland, Scotland)


class QualificationEquivalence(BaseModel):
    """One row of the canonical cross-qualification subject map (Plan 3 UC 4 + cross-qual).

    Per the 2026-08-15 plan: 30 pre-loaded equivalences (Chemistry LC <-> A-Level,
    Coding JC <-> GCSE, Mathematics LC <-> A-Level, etc.). The equivalence_strength
    is in [0.0, 1.0] where 1.0 = identical curriculum.
    """

    model_config = ConfigDict(frozen=True, slots=True)

    map_id: str = Field(..., description="Canonical UUID")
    qualification_a: QualificationLevel = Field(..., description="e.g. LC")
    jurisdiction_a: str = Field(..., description="e.g. ireland, england")
    subject_a: str = Field(..., description="e.g. chemistry, coding")
    board_a: Board = Field(default=Board.NONE)
    qualification_b: QualificationLevel = Field(..., description="e.g. A_LEVEL")
    jurisdiction_b: str = Field(..., description="e.g. england")
    subject_b: str = Field(..., description="e.g. chemistry, computer_science")
    board_b: Board = Field(default=Board.NONE)
    equivalence_strength: float = Field(..., ge=0.0, le=1.0)
    notes: str | None = Field(default=None)
    year_aligned: int = Field(default=2026)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        a = f"{self.jurisdiction_a}/{self.qualification_a.value}/{self.subject_a}"
        b = f"{self.jurisdiction_b}/{self.qualification_b.value}/{self.subject_b}"
        if self.board_a != Board.NONE:
            a = f"{a}/{self.board_a.value}"
        if self.board_b != Board.NONE:
            b = f"{b}/{self.board_b.value}"
        return f"{a} <-> {b} (strength={self.equivalence_strength})"


class CrossQualificationTopicAlignment(BaseModel):
    """One row of per-topic alignment (Plan 3 UC cross-qual)."""

    model_config = ConfigDict(frozen=True, slots=True)

    alignment_id: str = Field(..., description="Canonical UUID")
    qualification_a: QualificationLevel
    jurisdiction_a: str
    topic_a: str = Field(..., description="topic ID in qualification_a")
    qualification_b: QualificationLevel
    jurisdiction_b: str
    topic_b: str = Field(..., description="topic ID in qualification_b")
    alignment_score: float = Field(..., ge=0.0, le=1.0)
    common_concepts_json: str = Field(default="[]", description="JSON-serialized list of bilingual concept pair_ids")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RegressionBaseline(BaseModel):
    """One row of the canonical regression baseline (Plan 3 UC 5)."""

    model_config = ConfigDict(frozen=True, slots=True)

    baseline_id: str = Field(..., description="Canonical UUID")
    cohort_key: str = Field(..., description="e.g. 'ireland/lc/chemistry/aqa/2024/en'")
    subject_id: str
    stage: QualificationLevel
    board: Board = Field(default=Board.NONE)
    year: int
    content_hash: str = Field(..., description="SHA256 of the canonical syllabus/exam content")
    canonical_json: str = Field(..., description="JSON-serialized canonical curriculum/exam content")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    superseded_by: str | None = Field(default=None, description="baseline_id of the newer baseline that superseded this one")


class RegressionDiff(BaseModel):
    """One row of the regression diff output (Plan 3 UC 5)."""

    model_config = ConfigDict(frozen=True, slots=True)

    diff_id: str = Field(..., description="Canonical UUID")
    cohort_key: str
    baseline_old_id: str = Field(..., description="The older baseline's baseline_id")
    baseline_new_id: str = Field(..., description="The newer baseline's baseline_id")
    content_hash_changed: bool = Field(..., description="True iff the SHA256 differs")
    added_topics: list = Field(default_factory=list)
    removed_topics: list = Field(default_factory=list)
    modified_concepts_json: str = Field(default="{}", description="JSON of {topic_id: {old, new}} modifications")
    duration_ms: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CrossJurisdictionDiff(BaseModel):
    """One row of the cross-jurisdiction diff output (Plan 3 UC 4)."""

    model_config = ConfigDict(frozen=True, slots=True)

    diff_id: str = Field(..., description="Canonical UUID")
    qualification_a: QualificationLevel
    jurisdiction_a: str
    subject_a: str
    qualification_b: QualificationLevel
    jurisdiction_b: str
    subject_b: str
    equivalence_id: str | None = Field(default=None, description="FK to QualificationEquivalence.map_id")
    topic_count_a: int = Field(..., ge=0)
    topic_count_b: int = Field(..., ge=0)
    aligned_topic_count: int = Field(default=0, ge=0)
    alignment_pct: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BoardDiff(BaseModel):
    """One row of the England board diff output (Plan 3 UC 6)."""

    model_config = ConfigDict(frozen=True, slots=True)

    diff_id: str = Field(..., description="Canonical UUID")
    cohort_key: str = Field(..., description="e.g. 'england/gcse/chemistry/2024'")
    board_a: Board
    board_b: Board
    syllabus_hash_a: str
    syllabus_hash_b: str
    content_changed: bool
    added_modules: list = Field(default_factory=list)
    removed_modules: list = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CrossQualificationGap(BaseModel):
    """One row of the cross-qualification gap output (Plan 3 UC cross-qual)."""

    model_config = ConfigDict(frozen=True, slots=True)

    gap_id: str = Field(..., description="Canonical UUID")
    qualification_a: QualificationLevel
    jurisdiction_a: str
    subject_a: str
    topic_id: str = Field(..., description="The gap topic ID in qualification_a")
    candidate_qualifications: list = Field(
        default_factory=list,
        description="The qualification_b values where this topic might be covered",
    )
    severity: Literal["low", "medium", "high"] = Field(
        default="medium",
        description="The gap severity (operator-curated or auto-inferred)",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    # Plan 2 schemas (re-exported)
    "Capability",
    "Stage",
    "LanguagePair",
    "ExamMarkingAlignment",
    "TopicGraphEdge",
    "CrossLinguisticConcept",
    "BilingualConcept",
    "BilingualTopicEdge",
    "DiagramIndexEntry",
    "BilingualCoverageAudit",
    # Plan 3 schemas
    "QualificationLevel",
    "Board",
    "QualificationEquivalence",
    "CrossQualificationTopicAlignment",
    "RegressionBaseline",
    "RegressionDiff",
    "CrossJurisdictionDiff",
    "BoardDiff",
    "CrossQualificationGap",
]



# ============================================================================
# Plan 4 schemas (per-cohort registry + lifecycle)
# ============================================================================


class CohortLifecycleState(str, Enum):
    """The canonical per-cohort lifecycle state (Plan 4)."""

    NOT_STARTED = "not_started"
    EXTRACTING = "extracting"
    EVALUATING = "evaluating"
    REGISTERED = "registered"
    PROMOTED = "promoted"


class CohortRow(BaseModel):
    """The canonical per-cohort registry row (Plan 4).

    1 row per (jurisdiction, stage, subject, board, language, year) tuple.
    Bilingual-aware (the language_pair dimension tracks which languages
    have been extracted for the cohort).
    """

    model_config = ConfigDict(frozen=True, slots=True)

    cohort_id: str = Field(..., description="Canonical UUID")
    jurisdiction: str = Field(..., description="e.g. 'ireland', 'england'")
    stage: str = Field(..., description="e.g. 'lc', 'gcse', 'a_level'")
    subject: str = Field(..., description="e.g. 'chemistry', 'mathematics'")
    board: str = Field(default="none", description="e.g. 'aqa', 'ocr', 'edexcel'")
    language: str = Field(default="en", description="Primary extraction language")
    year: int = Field(..., description="Extraction target year (e.g. 2024)")

    # Bilingual-aware (Plan 2 extension): tracks which languages have been
    # extracted for the cohort. Per the locked >= 95% bilingual coverage gate.
    language_pair: str | None = Field(
        default=None,
        description="The bilingual language pair (e.g. 'en-ga'). None = monolingual cohort.",
    )
    en_extracted: bool = Field(default=False, description="True iff an EN extraction has run")
    ga_extracted: bool = Field(default=False, description="True iff a GA extraction has run")
    en_extraction_count: int = Field(default=0, ge=0)
    ga_extraction_count: int = Field(default=0, ge=0)

    # The canonical lifecycle state
    lifecycle_state: CohortLifecycleState = Field(default=CohortLifecycleState.NOT_STARTED)
    lifecycle_updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # v3 milestone-counts reference (per the BIEP v3 spec)
    # Ireland: 64 LC + 18 JC subjects = 82 (x 2 languages = 164)
    # England: 43 GCSE + 49 A-Level = 92 (x 3 boards = 276)
    expected_extractions: int = Field(default=0, ge=0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        board = f"/{self.board}" if self.board and self.board != "none" else ""
        return f"{self.jurisdiction}/{self.stage}/{self.subject}{board}/{self.language}/{self.year}"

    @property
    def cohort_key(self) -> str:
        """The canonical cohort_key string (for joining with Plan 2/3 outputs)."""
        return str(self)


class DatasetConfig(BaseModel):
    """The canonical extraction dataset config (Plan 4 factory output)."""

    model_config = ConfigDict(frozen=True, slots=True)

    cohort: CohortRow
    syllabus_pdf_urls: list = Field(default_factory=list)
    exam_pdf_urls: list = Field(default_factory=list)
    dlt_source_name: str = Field(default="", description="The dlt source module to invoke")
    baml_functions: list = Field(
        default_factory=list,
        description="The BAML ExtractXxx functions to call",
    )
    parallel_extractions: int = Field(default=4, description="Max parallel BAML calls (BIEP v3 default = 4)")
    ocr_backend: str = Field(default="olmmocr", description="The OCR backend for the PDF pre-processing")
    ragas_threshold: float = Field(default=0.95, description="BIEP v3 faithfulness gate")
    bilingual_coverage_threshold: float = Field(default=0.95, description="BIEP v3 bilingual coverage gate")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ += [
    # Plan 4 schemas
    "CohortLifecycleState",
    "CohortRow",
    "DatasetConfig",
]
