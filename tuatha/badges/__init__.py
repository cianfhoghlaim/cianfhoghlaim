"""badges — Hybrid x402 educational credential subsystem.

Off-chain `SkillTreeBadge` records (Convex + FalkorDB + LanceDB) plus
a daily Merkle root anchored on Base L2 via the `CredAnchor` smart
contract.

**Educational, not financial.** Students do not buy anything with real
money; the gas for the daily Merkle anchor is paid from the platform's
treasury (Base L2 ≈ $0.01/anchor). The educational credits are issued
by the platform as quest-completion rewards.

Verifiable by any third party (employer, university) via the public
`/anchor/<date>` page on the TanStack Start 2D client.

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D4)
    openspec/specs/cianfhoghlaim-educational-mmo/spec.md
"""
from __future__ import annotations

from .schema import (
    BilingualText,
    EvidenceLink,
    SkillTreeBadge,
    CredentialAnchor,
    MerkleBatch,
)
from .ledger import (
    issue_badge,
    fetch_badges_for_student,
    fetch_badges_since,
)
from .graph import (
    upsert_badge_node,
    fetch_student_mastery,
)
from .vector import (
    index_badge_embedding,
    semantic_search_badges,
)

__all__ = [
    # Schema
    "BilingualText",
    "EvidenceLink",
    "SkillTreeBadge",
    "CredentialAnchor",
    "MerkleBatch",
    # Ledger (Convex)
    "issue_badge",
    "fetch_badges_for_student",
    "fetch_badges_since",
    # Graph (FalkorDB)
    "upsert_badge_node",
    "fetch_student_mastery",
    # Vector (LanceDB)
    "index_badge_embedding",
    "semantic_search_badges",
]