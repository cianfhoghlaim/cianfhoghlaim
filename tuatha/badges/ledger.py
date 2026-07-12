"""badges.ledger — Convex wrapper for SkillTreeBadge CRUD.

The Convex `badges` table is the source of truth for off-chain badge
records. Reads are fast (Convex subscriptions mirror to the client),
writes are validated by the schema in `badges.schema.SkillTreeBadge`.

See `convex/badges.ts` (deployed alongside the TanStack Start app) for
the client-side schema.
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Optional

from .schema import SkillTreeBadge, EvidenceLink


async def issue_badge(
    student_id: str,
    framework: str,
    level: str,
    subject: str,
    competency_code: str,
    agent_issuer: str,
    evidence: EvidenceLink,
    competency_text: Optional[Any] = None,
) -> SkillTreeBadge:
    """Mint a new SkillTreeBadge and persist it to Convex.

    Args:
        student_id: Hash of student pseudonym + salt (never PII).
        framework: 'ncca-lc' or 'ncca-jc'.
        level: 'hl', 'ol', 'fl', or 'jc'.
        subject: Canonical slug.
        competency_code: NCCA LO code.
        agent_issuer: Agent that issued the badge (e.g. 'math_agent').
        evidence: Pointer to the formative item + student response.
        competency_text: Optional bilingual text describing the competency.

    Returns:
        The persisted SkillTreeBadge.
    """
    import uuid

    from .graph import upsert_badge_node
    from .vector import index_badge_embedding

    # 1. Build the canonical evidence hash (used as the Merkle leaf)
    evidence_hash = hashlib.sha256(
        f"{student_id}|{competency_code}|{evidence.score_pct}|{evidence.response}".encode()
    ).hexdigest()

    # 2. Sign with the agent's wallet (placeholder; production uses eth_account)
    signature = os.environ.get("MATH_AGENT_SIGNATURE_KEY", "dev-placeholder-signature")

    badge = SkillTreeBadge(
        id=str(uuid.uuid4()),
        student_id=student_id,
        framework=framework,
        level=level,
        subject=subject,
        competency_code=competency_code,
        competency_text=competency_text or {"text_en": competency_code, "text_ga": None},
        date_earned=datetime.now(tz=timezone.utc),
        agent_issuer=agent_issuer,
        evidence=evidence,
        evidence_hash=evidence_hash,
        signature=signature,
    )

    # 3. Write to Convex (real impl uses the Convex Python SDK)
    try:
        from convex import ConvexClient

        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        client.mutation("badges:create", badge.model_dump(mode="json"))
    except ImportError:
        # Convex SDK not installed in dev — log + skip the write
        pass

    # 4. Mirror to FalkorDB (cross-realm mastery graph)
    try:
        await upsert_badge_node(badge)
    except Exception:
        pass

    # 5. Index the badge in LanceDB (semantic search)
    try:
        await index_badge_embedding(badge)
    except Exception:
        pass

    return badge


async def fetch_badges_for_student(student_id: str) -> list[SkillTreeBadge]:
    """Return all SkillTreeBadges for a student, ordered by date_earned desc."""
    try:
        from convex import ConvexClient

        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        rows = client.query("badges:listByStudent", {"student_id": student_id})
        return [SkillTreeBadge(**r) for r in rows]
    except ImportError:
        return []


async def fetch_badges_since(since_iso: str) -> list[SkillTreeBadge]:
    """Return all badges minted since the given ISO datetime string.

    Used by the `daily_credential_anchor` Dagster asset.
    """
    try:
        from convex import ConvexClient

        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        rows = client.query("badges:listSince", {"since": since_iso})
        return [SkillTreeBadge(**r) for r in rows]
    except ImportError:
        return []