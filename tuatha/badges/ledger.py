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

from .schema import BilingualText, EvidenceLink, EvidenceType, KeyCompetency, SkillTreeBadge


async def issue_badge(
    student_id: str,
    framework: str,
    level: str,
    subject: str,
    competency_code: str,
    agent_issuer: str,
    evidence: EvidenceLink,
    competency_text: Optional[Any] = None,
    key_competencies: Optional[list[KeyCompetency]] = None,
    evidence_type: EvidenceType = EvidenceType.FORMATIVE_ITEM,
    student_wallet_address: Optional[str] = None,
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
        key_competencies: Which of the NCCA's 7 senior-cycle key
            competencies this badge evidences (per
            `docs-informed-quest-and-credential-generation-v1`). Callers
            SHOULD pass this — defaults to empty only for callers not yet
            updated.
        evidence_type: FORMATIVE_ITEM (default) or
            CLASSROOM_BASED_ASSESSMENT.
        student_wallet_address: The student's on-chain wallet address
            (from their SIWE auth session), if known. When provided,
            `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`'s
            `AchievementToken.mint()` is called for this badge. When
            omitted (the common case today — the Convex `students`
            table has no `walletAddress` field yet, so callers cannot
            reliably supply one), minting is skipped entirely — a
            badge without a wallet-linked student is still a complete,
            valid off-chain credential; the achievement token is an
            additive reward, not a prerequisite for badge issuance.

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
        key_competencies=key_competencies or [],
        evidence_type=evidence_type,
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
        # Explicit camelCase mapping — found while wiring this that
        # `badge.model_dump(mode="json")` (snake_case, nested `evidence`
        # object) does not match `badges:create`'s validator (camelCase,
        # flattened `evidence*` fields) at all; passing the raw dump
        # would have failed Convex's argument validation on every call.
        # Per `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`.
        client.mutation(
            "badges:create",
            {
                "studentId": badge.student_id,
                "framework": badge.framework,
                "level": badge.level,
                "subject": badge.subject,
                "competencyCode": badge.competency_code,
                "competencyTextEn": badge.competency_text.text_en,
                "competencyTextGa": badge.competency_text.text_ga,
                "agentIssuer": badge.agent_issuer,
                "evidenceItemId": badge.evidence.item_id,
                "evidenceResponse": badge.evidence.response,
                "evidenceScorePct": badge.evidence.score_pct,
                # Previously dropped silently (found while adding the
                # read-path fix below): the badges table now has
                # matching evidence* columns to receive these.
                "evidenceFeedbackEn": badge.evidence.feedback_en,
                "evidenceFeedbackGa": badge.evidence.feedback_ga,
                "evidenceSourcePdf": badge.evidence.source_pdf,
                "evidenceSourcePage": badge.evidence.source_page,
                "evidenceHash": badge.evidence_hash,
                "signature": badge.signature,
                "keyCompetencies": [kc.value for kc in badge.key_competencies],
                "evidenceType": badge.evidence_type.value,
            },
        )
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

    # 6. Mint an AchievementToken for this badge (learn-to-earn reward),
    # only when a wallet address is available. Best-effort: a failed or
    # skipped mint never blocks badge issuance — the off-chain
    # SkillTreeBadge is the source of truth regardless.
    if student_wallet_address:
        try:
            from .achievement_token_client import mint_for_badge

            await mint_for_badge(student_wallet_address, evidence_hash)
        except Exception:
            pass

    return badge


def _row_to_badge(row: dict[str, Any]) -> SkillTreeBadge:
    """Reconstruct a SkillTreeBadge from a Convex `badges` row.

    Found while wiring the read path: the row is flat and camelCase
    (Convex's own shape, per `convex/schema.ts`), while `SkillTreeBadge`
    is nested and snake_case (`competency_text: BilingualText`,
    `evidence: EvidenceLink`) — the same mismatch `issue_badge()`'s
    write path already had to fix, mirrored here for reads. Without
    this mapper, `SkillTreeBadge(**row)` would raise a Pydantic
    validation error on every real row (unknown fields `studentId` /
    `competencyTextEn` / `_id` / `_creationTime`, missing required
    fields `student_id` / `competency_text` / `evidence`).
    """
    return SkillTreeBadge(
        id=row.get("_id", row.get("id", "")),
        student_id=row["studentId"],
        framework=row["framework"],
        level=row["level"],
        subject=row["subject"],
        competency_code=row["competencyCode"],
        competency_text=BilingualText(
            text_en=row["competencyTextEn"], text_ga=row.get("competencyTextGa")
        ),
        key_competencies=[KeyCompetency(kc) for kc in row.get("keyCompetencies", [])],
        evidence_type=EvidenceType(row.get("evidenceType", EvidenceType.FORMATIVE_ITEM.value)),
        date_earned=datetime.fromtimestamp(row["dateEarned"] / 1000, tz=timezone.utc),
        agent_issuer=row["agentIssuer"],
        evidence=EvidenceLink(
            item_id=row["evidenceItemId"],
            response=row["evidenceResponse"],
            score_pct=row["evidenceScorePct"],
            feedback_en=row.get("evidenceFeedbackEn") or "",
            feedback_ga=row.get("evidenceFeedbackGa"),
            source_pdf=row.get("evidenceSourcePdf"),
            source_page=row.get("evidenceSourcePage"),
        ),
        evidence_hash=row["evidenceHash"],
        signature=row["signature"],
        on_chain_anchor=row.get("onChainAnchor"),
        anchor_date=row.get("anchorDate"),
    )


async def fetch_badges_for_student(student_id: str) -> list[SkillTreeBadge]:
    """Return all SkillTreeBadges for a student, ordered by date_earned desc."""
    try:
        from convex import ConvexClient

        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        rows = client.query("badges:listByStudent", {"studentId": student_id})
        return [_row_to_badge(r) for r in rows]
    except ImportError:
        return []


async def fetch_badges_since(since_iso: str) -> list[SkillTreeBadge]:
    """Return all badges minted since the given ISO datetime string.

    Used by the `daily_credential_anchor` Dagster asset.
    """
    try:
        from convex import ConvexClient

        since_ms = int(datetime.fromisoformat(since_iso).timestamp() * 1000)
        client = ConvexClient(os.environ.get("CONVEX_URL", "http://localhost:3210"))
        rows = client.query("badges:listSince", {"sinceMs": since_ms})
        return [_row_to_badge(r) for r in rows]
    except ImportError:
        return []