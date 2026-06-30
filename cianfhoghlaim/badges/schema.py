"""badges.schema — Pydantic models for the hybrid x402 educational credential.

Mirrors the BAML types in `qpack_mathematics.baml` for the parts that
overlap (BilingualText, EvidenceLink) and adds the credential-specific
types (SkillTreeBadge, CredentialAnchor, MerkleBatch).
"""
from __future__ import annotations

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

    item_id: str @Field(description="The formative item UUID")
    response: str @Field(description="Verbatim student response")
    score_pct: float @Field(..., ge=0, le=100)
    feedback_en: str
    feedback_ga: Optional[str] = None
    source_pdf: Optional[str] = None
    source_page: Optional[int] = None


class SkillTreeBadge(BaseModel):
    """One earned educational credential.

    Stored off-chain in Convex + FalkorDB + LanceDB. The off-chain
    record is the source of truth for the student; the on-chain
    Merkle anchor is the third-party-verifiable proof.
    """

    id: str @Field(description="UUID")
    student_id: str @Field(description="Hash of student pseudonym + salt; never PII")
    framework: str @Field(description="One of: 'ncca-lc', 'ncca-jc'")
    level: str @Field(description="One of: 'hl', 'ol', 'fl', 'jc'")
    subject: str @Field(description="Canonical slug, e.g. 'mathematics', 'gaeilge'")
    competency_code: str @Field(description="NCCA LO code, e.g. 'LC-MATHS-LO-2.4'")
    competency_text: BilingualText
    date_earned: datetime
    agent_issuer: str @Field(description="Agent that issued the badge, e.g. 'math_agent'")
    evidence: EvidenceLink
    evidence_hash: str @Field(description="SHA-256 of evidence, used as the Merkle leaf")
    signature: str @Field(description="ETH signature from agent_issuer wallet")
    on_chain_anchor: Optional[str] = Field(
        default=None, description="Base L2 tx_hash; populated when Merkle batch closes"
    )
    anchor_date: Optional[str] = Field(
        default=None, description="YYYY-MM-DD of the daily anchor batch"
    )


class MerkleBatch(BaseModel):
    """One daily Merkle batch — the unit anchored on Base L2."""

    id: str @Field(description="UUID")
    batch_date: str @Field(description="YYYY-MM-DD")
    merkle_root: str @Field(description="Hex-encoded 32-byte Merkle root")
    leaf_count: int @Field(..., ge=0)
    badge_ids: list[str] @Field(description="The badge IDs included in this batch")
    tx_hash: Optional[str] = Field(default=None, description="Base L2 tx_hash")
    published_at: Optional[datetime] = None


class CredentialAnchor(BaseModel):
    """The on-chain anchor record (returned by the CredAnchor contract)."""

    batch_id: str
    merkle_root: str
    timestamp: int @Field(description="Block timestamp on Base L2")
    tx_hash: str