"""badges.schema — Pydantic models for the hybrid x402 educational credential.

Mirrors the BAML types in `qpack_mathematics.baml` for the parts that
overlap (BilingualText, EvidenceLink) and adds the credential-specific
types (SkillTreeBadge, CredentialAnchor, MerkleBatch).

The 13 éraic (Lugh's compensation) treasure definitions mirror the BAML
types in `baml/education/_shared/eiraic_treasures.baml` and are wired
into SkillTreeBadge via the `eiraic_treasures_unlocked` field. The
BAML file is the regenerated types for use inside LLM extraction
prompts; this module is the Python-side canonical authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class BilingualText(BaseModel):
    """Bilingual EN + GA text. text_ga may be None for EN-only content."""

    text_en: str
    text_ga: Optional[str] = None


class EvidenceLink(BaseModel):
    """Pointer to the source NCCA PDF page + the student response."""

    item_id: str = Field(description="The formative item UUID")
    response: str = Field(description="Verbatim student response")
    score_pct: float = Field(..., ge=0, le=100)
    feedback_en: str
    feedback_ga: Optional[str] = None
    source_pdf: Optional[str] = None
    source_page: Optional[int] = None


class KeyCompetency(str, Enum):
    """The 7 NCCA senior-cycle key competencies, bounded by literacies +
    numeracy per `leaving_certificate/the-potential-of-technology-to-
    support-online-certification-and-reporting.pdf` Figure 1 (H2 Learning
    for NCCA, Aug 2024). Added by `docs-informed-quest-and-credential-
    generation-v1` to ground `SkillTreeBadge` in the NCCA's own
    terminology rather than inventing a competency taxonomy from scratch.
    """

    THINKING_AND_SOLVING_PROBLEMS = "THINKING_AND_SOLVING_PROBLEMS"
    BEING_CREATIVE = "BEING_CREATIVE"
    COMMUNICATING = "COMMUNICATING"
    WORKING_WITH_OTHERS = "WORKING_WITH_OTHERS"
    PARTICIPATING_IN_SOCIETY = "PARTICIPATING_IN_SOCIETY"
    CULTIVATING_WELLBEING = "CULTIVATING_WELLBEING"
    MANAGING_LEARNING_AND_SELF = "MANAGING_LEARNING_AND_SELF"


class EvidenceType(str, Enum):
    """Distinguishes the kind of evidence that triggered badge issuance,
    per the NCCA's own "recording/reporting/certifying" terminology (same
    source PDF as `KeyCompetency`). `FORMATIVE_ITEM` is a single scored
    formative-assessment response; `CLASSROOM_BASED_ASSESSMENT` mirrors
    the NCCA's own Junior Cycle CBA terminology for a larger, teacher-
    assessed body of work.
    """

    FORMATIVE_ITEM = "FORMATIVE_ITEM"
    CLASSROOM_BASED_ASSESSMENT = "CLASSROOM_BASED_ASSESSMENT"


class SkillTreeBadge(BaseModel):
    """One earned educational credential.

    Stored off-chain in Convex + FalkorDB + LanceDB. The off-chain
    record is the source of truth for the student; the on-chain
    Merkle anchor is the third-party-verifiable proof.
    """

    id: str = Field(description="UUID")
    student_id: str = Field(description="Hash of student pseudonym + salt; never PII")
    framework: str = Field(description="One of: 'ncca-lc', 'ncca-jc'")
    level: str = Field(description="One of: 'hl', 'ol', 'fl', 'jc'")
    subject: str = Field(description="Canonical slug, e.g. 'mathematics', 'gaeilge'")
    competency_code: str = Field(description="NCCA LO code, e.g. 'LC-MATHS-LO-2.4'")
    competency_text: BilingualText
    key_competencies: list[KeyCompetency] = Field(
        default_factory=list,
        description=(
            "Which of the NCCA's 7 senior-cycle key competencies this "
            "badge evidences (e.g. THINKING_AND_SOLVING_PROBLEMS for a "
            "worked-solution item). May be empty for badges issued before "
            "this field existed; new issuance SHOULD always populate it."
        ),
    )
    evidence_type: EvidenceType = Field(
        default=EvidenceType.FORMATIVE_ITEM,
        description="The kind of evidence that triggered issuance.",
    )
    date_earned: datetime
    agent_issuer: str = Field(description="Agent that issued the badge, e.g. 'math_agent'")
    evidence: EvidenceLink
    evidence_hash: str = Field(description="SHA-256 of evidence, used as the Merkle leaf")
    signature: str = Field(description="ETH signature from agent_issuer wallet")
    on_chain_anchor: Optional[str] = Field(
        default=None, description="Base L2 tx_hash; populated when Merkle batch closes"
    )
    anchor_date: Optional[str] = Field(
        default=None, description="YYYY-MM-DD of the daily anchor batch"
    )
    eiraic_treasures_unlocked: list[str] = Field(
        default_factory=list,
        description=(
            "The éraic treasure_ids (from EIRAIC_TREASURES) that this badge "
            "unlocked. Typically the badge unlocks the single treasure whose "
            "primary_subject matches the badge's subject; cross-subject badges "
            "or master-tier badges (tier 13) may unlock multiple."
        ),
    )


class MerkleBatch(BaseModel):
    """One daily Merkle batch — the unit anchored on Base L2."""

    id: str = Field(description="UUID")
    batch_date: str = Field(description="YYYY-MM-DD")
    merkle_root: str = Field(description="Hex-encoded 32-byte Merkle root")
    leaf_count: int = Field(..., ge=0)
    badge_ids: list[str] = Field(description="The badge IDs included in this batch")
    tx_hash: Optional[str] = Field(default=None, description="Base L2 tx_hash")
    published_at: Optional[datetime] = None


class CredentialAnchor(BaseModel):
    """The on-chain anchor record (returned by the CredAnchor contract)."""

    batch_id: str
    merkle_root: str
    timestamp: int = Field(description="Block timestamp on Base L2")
    tx_hash: str


# =============================================================================
# Éraic na Coiced — the 13 treasures of Lugh
# =============================================================================
# At the Second Battle of Mag Tuired (Cath Maige Tuired), the Tuatha Dé Danann
# demanded éraic (compensation) from the Fomorians for the death of Cian mac
# Cainte. Lugh — the Samildánach himself — composed the list.
#
# Each treasure is also a pedagogical *competency signal* — a teaching
# superpower that maps to a single NCCA subject area (or a cross-subject
# mastery signal). The Python definitions below are the single source of
# truth for the Cianfhoghlaim Educational MMO; the BAML types in
# `baml/education/_shared/eiraic_treasures.baml` mirror them so the
# `GetEiraicTreasures` LLM extraction can populate them for any subject.
#
# The 13 treasures + their primary subject mapping:
#
#   1.  Pig Skin of Dobar            (healing)                  → Biology
#   2.  Heifer Skin of Dobar         (landscape stewardship)    → Geography
#   3.  Spear of Assal               (precision strike)         → Mathematics
#   4.  Chariot of the king of Sidrach (motion / dynamics)      → Applied Mathematics
#   5.  Sword of Caladbolg           (iterative two-handed cut) → Computer Science
#   6.  Seven pigs of Easmal         (regenerate daily)         → All subjects
#   7.  Whelp of the king of Ioruaidh (pursuit narrative)       → English
#   8.  Cooking spit of Innis Cera   (daily food / livelihood)  → Gaeilge
#   9.  Armour of the king of Clochur (defence & witness)       → History
#   10. Three apples of the Hesperides (cross-realm bounty)     → Cross-subject
#   11. Pigskin bag of the healing well (citation vessel)       → Citation rigor
#   12. Feather of the Bird of Crannog (instant healing)        → Recovery from failure
#   13. Lugh's own samildanach       (master of all arts)       → Universal mastery
# =============================================================================


class EiraicSubject(str, Enum):
    """The primary NCCA subject each éraic treasure anchors."""

    BIOLOGY = "BIOLOGY"
    GEOGRAPHY = "GEOGRAPHY"
    MATHEMATICS = "MATHEMATICS"
    APPLIED_MATHEMATICS = "APPLIED_MATHEMATICS"
    COMPUTER_SCIENCE = "COMPUTER_SCIENCE"
    ALL_SUBJECTS = "ALL_SUBJECTS"
    ENGLISH = "ENGLISH"
    GAEILGE = "GAEILGE"
    HISTORY = "HISTORY"
    CROSS_SUBJECT = "CROSS_SUBJECT"
    CITATION_RIGOR = "CITATION_RIGOR"
    RECOVERY_FROM_FAILURE = "RECOVERY_FROM_FAILURE"
    UNIVERSAL_MASTERY = "UNIVERSAL_MASTERY"


class EiraicCapability(str, Enum):
    """The pedagogical capability each treasure grants."""

    HEALING = "HEALING"
    LANDSCAPE_STEWARDSHIP = "LANDSCAPE_STEWARDSHIP"
    PRECISION = "PRECISION"
    MOTION_DYNAMICS = "MOTION_DYNAMICS"
    ITERATIVE_CUT = "ITERATIVE_CUT"
    REGENERATION = "REGENERATION"
    NARRATIVE_PURSUIT = "NARRATIVE_PURSUIT"
    LINGUISTIC_LIVELIHOOD = "LINGUISTIC_LIVELIHOOD"
    HISTORICAL_DEFENCE = "HISTORICAL_DEFENCE"
    CROSS_REALM_SYNTHESIS = "CROSS_REALM_SYNTHESIS"
    CITATION_HYGIENE = "CITATION_HYGIENE"
    RESILIENCE_AFTER_FAILURE = "RESILIENCE_AFTER_FAILURE"
    UNIVERSAL_MASTERY = "UNIVERSAL_MASTERY"


class EiraicProvenance(str, Enum):
    """The mythological owner of the treasure (who paid the éraic)."""

    TDD_DOBAR = "TDD_DOBAR"
    TDD_SIDRACH = "TDD_SIDRACH"
    FOMORIAN_ASSAL = "FOMORIAN_ASSAL"
    FOMORIAN_CLOCHUR = "FOMORIAN_CLOCHUR"
    FOMORIAN_EASMAL = "FOMORIAN_EASMAL"
    FOMORIAN_IORUAIDH = "FOMORIAN_IORUAIDH"
    TDD_INNIS_CERA = "TDD_INNIS_CERA"
    HESPERIDES = "HESPERIDES"
    TDD_LUGH = "TDD_LUGH"
    TUATHA_DE_DANANN = "TUATHA_DE_DANANN"


@dataclass(frozen=True)
class EiraicTitle:
    """Bilingual EN + GA title for one éraic treasure."""

    en: str
    ga: str


@dataclass(frozen=True)
class EiraicTreasure:
    """One of the 13 canonical éraic treasures paid at Mag Tuired.

    Mirrors the BAML class shape from `eiraic_treasures.baml`. Frozen so
    the list-of-13 can be shared as the single source of truth across
    the Cianfhoghlaim Educational MMO's 8-subject agent roster.

    Attributes:
        treasure_id: Canonical kebab-case slug, e.g. ``eiraic_3_spear_assal``.
        title: Bilingual EN + GA name.
        provenance: Who owned the treasure in mythology.
        capability: The pedagogical superpower it grants.
        primary_subject: The NCCA subject it is the *primary* anchor for.
        rationale_en: 1-3 sentences linking mythology to syllabus.
        rationale_ga: Irish-language rationale; None if unattested.
        mmo_signal: How the Cianfhoghlaim MMO surfaces this on a
            SkillTreeBadge (1 sentence).
        tier: The ordinal éraic position (1..13).
    """

    treasure_id: str
    title: EiraicTitle
    provenance: EiraicProvenance
    capability: EiraicCapability
    primary_subject: EiraicSubject
    rationale_en: str
    rationale_ga: Optional[str]
    mmo_signal: str
    tier: int


EIRAIC_TREASURES: list[EiraicTreasure] = [
    EiraicTreasure(
        treasure_id="eiraic_1_pig_skin_dobar",
        title=EiraicTitle(
            en="Skin of the Pig of Dobar",
            ga="An Cranncin Muc Dobar",
        ),
        provenance=EiraicProvenance.TDD_DOBAR,
        capability=EiraicCapability.HEALING,
        primary_subject=EiraicSubject.BIOLOGY,
        rationale_en=(
            "The Pig of Dobar's skin healed any wound it was laid upon — "
            "a mythic analogue of cellular repair, immune response, and "
            "tissue regeneration. Maps to Leaving Certificate Biology's "
            "cell-structure, immunology, and homeostasis learning outcomes."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Healing badge awarded on completion of a Biology LC quest "
            "(LC-BIO-LO-2.4 — cell structure and function)."
        ),
        tier=1,
    ),
    EiraicTreasure(
        treasure_id="eiraic_2_heifer_skin_dobar",
        title=EiraicTitle(
            en="Skin of the Heifer of Dobar",
            ga="Craicean na Tarbh Gile Dobar",
        ),
        provenance=EiraicProvenance.TDD_DOBAR,
        capability=EiraicCapability.LANDSCAPE_STEWARDSHIP,
        primary_subject=EiraicSubject.GEOGRAPHY,
        rationale_en=(
            "The Heifer of Dobar's skin conferred efficacy across every "
            "landscape — a mythic analogue of geographic literacy and the "
            "interaction between physical environments and human activity."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Stewardship badge awarded by geog_agent on completion of a "
            "Geography LC quest (LC-GEOG-LO-1.3 — physical processes shaping "
            "landscapes)."
        ),
        tier=2,
    ),
    EiraicTreasure(
        treasure_id="eiraic_3_spear_assal",
        title=EiraicTitle(
            en="Spear of Assal",
            ga="Sleagh Assail",
        ),
        provenance=EiraicProvenance.FOMORIAN_ASSAL,
        capability=EiraicCapability.PRECISION,
        primary_subject=EiraicSubject.MATHEMATICS,
        rationale_en=(
            "The Spear of Assal never missed its mark. Mathematics trains "
            "the same faculty: precise reasoning, exact statements, and "
            "deductions that always hit their target."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Precision badge awarded by math_agent on completion of a "
            "calculus / algebra HL quest (LC-MATHS-LO-2.4 — differentiation)."
        ),
        tier=3,
    ),
    EiraicTreasure(
        treasure_id="eiraic_4_chariot_sidrach",
        title=EiraicTitle(
            en="Chariot of the king of Sidrach",
            ga="Cairt Rí Shidrach",
        ),
        provenance=EiraicProvenance.TDD_SIDRACH,
        capability=EiraicCapability.MOTION_DYNAMICS,
        primary_subject=EiraicSubject.APPLIED_MATHEMATICS,
        rationale_en=(
            "The chariot of Sidrach was driven by a single wheel that "
            "moved over land and sea alike — a mythic vehicle of motion "
            "and dynamics. Applied Mathematics owns this: kinematics, "
            "Newton's laws, and the mathematics of moving bodies."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Dynamics badge awarded by appm_agent on completion of a "
            "mechanics quest (LC-APPM-LO-3.2 — particle dynamics)."
        ),
        tier=4,
    ),
    EiraicTreasure(
        treasure_id="eiraic_5_sword_caladbolg",
        title=EiraicTitle(
            en="Sword of Caladbolg",
            ga="Claíomh Caladbolg",
        ),
        provenance=EiraicProvenance.TUATHA_DE_DANANN,
        capability=EiraicCapability.ITERATIVE_CUT,
        primary_subject=EiraicSubject.COMPUTER_SCIENCE,
        rationale_en=(
            "Caladbolg was wielded with a two-handed cut, the warrior "
            "iterating stroke upon stroke until no resistance remained. "
            "Computer Science mirrors this: loops, recursion, and "
            "divide-and-conquer reduce intractable problems by iteration."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Iterative-cut badge awarded by comp_agent on completion of a "
            "loops / recursion quest (LC-COMP-LO-2.5 — algorithmic iteration)."
        ),
        tier=5,
    ),
    EiraicTreasure(
        treasure_id="eiraic_6_pigs_easmal",
        title=EiraicTitle(
            en="Seven pigs of Easmal",
            ga="Seacht Muc Easmal",
        ),
        provenance=EiraicProvenance.FOMORIAN_EASMAL,
        capability=EiraicCapability.REGENERATION,
        primary_subject=EiraicSubject.ALL_SUBJECTS,
        rationale_en=(
            "The seven pigs of Easmal could be slaughtered at night and "
            "be alive again by morning. Renewal of effort and resilience "
            "apply to every subject — the daily practice that makes a master."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Regeneration badge awarded by any subject agent when a student "
            "completes a daily-streak quest (regenerate after every missed day)."
        ),
        tier=6,
    ),
    EiraicTreasure(
        treasure_id="eiraic_7_whelp_ioruaidh",
        title=EiraicTitle(
            en="Whelp of the king of Ioruaidh",
            ga="Cuileann Rí Ioruaidh",
        ),
        provenance=EiraicProvenance.FOMORIAN_IORUAIDH,
        capability=EiraicCapability.NARRATIVE_PURSUIT,
        primary_subject=EiraicSubject.ENGLISH,
        rationale_en=(
            "The whelp tracked its quarry across sea and land by the "
            "scent of its voice. English trains the same faculty: the "
            "pursuit of meaning through narrative structure, voice, and "
            "the trace left by an author's language."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Narrative-pursuit badge awarded by engl_agent on completion of "
            "a reading-comprehension or close-reading quest (LC-ENGL-LO-1.5)."
        ),
        tier=7,
    ),
    EiraicTreasure(
        treasure_id="eiraic_8_spit_innis_cera",
        title=EiraicTitle(
            en="Cooking spit of the woman of Innis Cera",
            ga="Bior Fréimh Mná Inis Cera",
        ),
        provenance=EiraicProvenance.TDD_INNIS_CERA,
        capability=EiraicCapability.LINGUISTIC_LIVELIHOOD,
        primary_subject=EiraicSubject.GAEILGE,
        rationale_en=(
            "The spit of the woman of Innis Cera was a daily provider — "
            "the food of the household. Gaeilge is the daily provider of "
            "Irish linguistic life: the household tongue whose use sustains "
            "the community."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Linguistic-livelihood badge awarded by gael_agent on completion "
            "of an oral / written Gaeilge production quest (LC-GAEL-LO-3.1)."
        ),
        tier=8,
    ),
    EiraicTreasure(
        treasure_id="eiraic_9_armour_clochur",
        title=EiraicTitle(
            en="Helmet and breastplate of the king of Clochur",
            ga="Clogas agus Lucht Cíoch Clogur",
        ),
        provenance=EiraicProvenance.FOMORIAN_CLOCHUR,
        capability=EiraicCapability.HISTORICAL_DEFENCE,
        primary_subject=EiraicSubject.HISTORY,
        rationale_en=(
            "The armour of Clochur protected its bearer against every "
            "wound, and bore witness to every battle. History is the "
            "same: a defence against forgetting, a witness-bearing record "
            "of what happened and why."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Historical-defence badge awarded by hist_agent on completion of "
            "a source-analysis or document-evidence quest (LC-HIST-LO-1.4)."
        ),
        tier=9,
    ),
    EiraicTreasure(
        treasure_id="eiraic_10_apples_hesperides",
        title=EiraicTitle(
            en="Three apples of the Hesperides",
            ga="Trí Úll Hesperides",
        ),
        provenance=EiraicProvenance.HESPERIDES,
        capability=EiraicCapability.CROSS_REALM_SYNTHESIS,
        primary_subject=EiraicSubject.CROSS_SUBJECT,
        rationale_en=(
            "The apples of the Hesperides came from beyond the known world "
            "and conferred wisdom drawn from another realm. Cross-subject "
            "mastery is the same faculty: synthesis across domains that "
            "yields insight unavailable inside any single subject."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Cross-realm badge awarded when a student completes one quest "
            "in each of two or more subjects within a single MMO session."
        ),
        tier=10,
    ),
    EiraicTreasure(
        treasure_id="eiraic_11_pigskin_bag_healing",
        title=EiraicTitle(
            en="Pigskin bag of the healing well",
            ga="Mála Craicinn Muice Tobair Sláine",
        ),
        provenance=EiraicProvenance.TDD_DOBAR,
        capability=EiraicCapability.CITATION_HYGIENE,
        primary_subject=EiraicSubject.CITATION_RIGOR,
        rationale_en=(
            "The pigskin bag carried water from a healing well; the right "
            "vessel preserved the cure. Citation hygiene is the same: the "
            "right reference, in the right form, preserves the argument's "
            "integrity."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Citation-hygiene badge awarded when a student response includes "
            "at least one correctly-formatted NCCA syllabus citation."
        ),
        tier=11,
    ),
    EiraicTreasure(
        treasure_id="eiraic_12_feather_bird_crannog",
        title=EiraicTitle(
            en="Feather of the Bird of Crannog",
            ga="Cleit Éan Lochair",
        ),
        provenance=EiraicProvenance.TUATHA_DE_DANANN,
        capability=EiraicCapability.RESILIENCE_AFTER_FAILURE,
        primary_subject=EiraicSubject.RECOVERY_FROM_FAILURE,
        rationale_en=(
            "The Bird of Crannog could not be wounded; if struck, the wound "
            "healed the moment the feather was applied. Recovery from failure "
            "is the same faculty: the resilience that turns a wrong attempt "
            "into the next correct attempt."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Resilience badge awarded when a student who previously failed a "
            "quest completes it on retry within 7 days."
        ),
        tier=12,
    ),
    EiraicTreasure(
        treasure_id="eiraic_13_samildanach_lugh",
        title=EiraicTitle(
            en="Samildánacht Lugh",
            ga="Samhildánacht Lugh",
        ),
        provenance=EiraicProvenance.TDD_LUGH,
        capability=EiraicCapability.UNIVERSAL_MASTERY,
        primary_subject=EiraicSubject.UNIVERSAL_MASTERY,
        rationale_en=(
            "Lugh the Samildánach — master of all arts — composed the éraic "
            "itself. Tier 13 is therefore the universal-mastery badge: earned "
            "by the student who has unlocked all twelve preceding treasures."
        ),
        rationale_ga=None,
        mmo_signal=(
            "Universal-mastery badge awarded when a student's "
            "eiraic_treasures_unlocked list contains all 12 preceding "
            "treasure_ids."
        ),
        tier=13,
    ),
]


def get_treasures_for_eiraic_tier(tier: int) -> list[str]:
    """Return the treasure_ids in ``EIRAIC_TREASURES`` for the given tier.

    The canonical éraic has 13 tiers (1..13), each holding exactly one
    treasure. Out-of-range tiers return an empty list (LBYL — fail soft
    rather than raise, so badge validators don't crash on bad data).

    Args:
        tier: The ordinal éraic position (1..13).

    Returns:
        A list of ``treasure_id`` strings for that tier. Empty if the
        tier is out of range or no treasure is defined for it.
    """
    if not isinstance(tier, int) or tier < 1 or tier > len(EIRAIC_TREASURES):
        return []
    return [
        treasure.treasure_id
        for treasure in EIRAIC_TREASURES
        if treasure.tier == tier
    ]