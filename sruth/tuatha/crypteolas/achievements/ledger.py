"""
The achievement ledger — the canonical Phase 6 implementation
of the tuatha/crypteolas/achievements/ directory (per the
`tuatha-formative-assessment-v1` openspec change archived
2026-06-24, and the `.agents/skills/tuatha-achievement-ledger/`
skill).

The 4 public methods:

- `issue(badge)` — issue a new skill-tree badge (also auto-issues
  a Cross-British-Isles Achiever mastery if the player has earned
  1+ badge in each of the 5 frameworks)
- `list_badges(player_id, framework=...)` — list a player's badges
- `verify_signature(badge_id)` — verify the cryptographic
  evidence chain
- `cross_quest_relevance(player_id, realm)` — return the 3 most
  relevant badges for a new quest

The cryptographic evidence chain uses eth_account
(Sign-In With Ethereum) — the same wallet identity as the
player's authentication (per the `.agents/skills/tuatha-mmo/`
skill's SIWE pattern).

The BGE-M3 embeddings are produced by the
`oideachais.cocoindex_flows.leabharlann_embedding` flow's
`embed_text` function (the canonical embedding model).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .schema import (
    FRAMEWORK_TO_REALM,
    CurriculumFramework,
    PentElementalRealm,
    SkillTreeBadge,
    SkillTreeMastery,
    build_embedding_text,
)
from .storage import AchievementStorage


def _sign_evidence(evidence: str, agent_wallet: str) -> str:
    """Sign the evidence with the agent's wallet (the cryptographic chain)."""
    try:
        from eth_account import Account
        from eth_account.messages import encode_defunct

        agent_private_key = __import__(
            "os",
        ).environ.get("TuatHA_AGENT_PRIVATE_KEY", "")
        if not agent_private_key:
            return ""
        msg = encode_defunct(text=evidence)
        signed = Account.sign_message(msg, private_key=agent_private_key)
        return signed.signature.hex()
    except ImportError:
        return ""
    except Exception:
        return ""


def _verify_evidence(
    evidence: str, signature: str, expected_address: str,
) -> bool:
    """Verify the evidence signature (the cryptographic chain)."""
    try:
        from eth_account import Account
        from eth_account.messages import encode_defunct

        if not signature or not expected_address:
            return False
        msg = encode_defunct(text=evidence)
        recovered = Account.recover_message(msg, signature=signature)
        return recovered.lower() == expected_address.lower()
    except ImportError:
        return False
    except Exception:
        return False


def _compute_embedding(text: str) -> list[float]:
    """Compute the 1024-dim BGE-M3 embedding via the canonical oideachais flow."""
    try:
        from sruth.oideachais.cocoindex_flows.leabharlann_embedding import embed_text

        return embed_text(text)
    except Exception:
        return [0.0] * 1024


class AchievementLedger:
    """The canonical Phase 6 achievement ledger.

    The 4 public methods (issue, list_badges, verify_signature,
    cross_quest_relevance) cover the full skill-tree badge
    lifecycle.
    """

    def __init__(self, storage: AchievementStorage | None = None) -> None:
        self.storage = storage or AchievementStorage()
        self.storage.init_storage()

    async def issue(self, badge: SkillTreeBadge) -> dict[str, Any]:
        """Issue a new skill-tree badge.

        Side effects:
        - Inserts the badge into the `crypteolas_achievements` table
        - Signs the evidence with the agent's wallet
        - Auto-issues a Cross-British-Isles Achiever mastery if
          the player has now earned 1+ badge in each of the 5
          frameworks
        """
        evidence_signature = _sign_evidence(
            badge.evidence,
            agent_wallet=badge.agent_issuer,
        )
        embedding = _compute_embedding(
            build_embedding_text(
                badge.evidence, badge.subject, badge.competency,
            ),
        )
        record = {
            **badge.to_dict(),
            "evidence_signature": evidence_signature,
            "vector": embedding,
        }
        self.storage.insert_badge(record)

        mastery = self._maybe_issue_mastery(badge)
        return {
            "badge": badge.to_dict(),
            "evidence_signature": evidence_signature,
            "mastery_issued": mastery.to_dict() if mastery else None,
        }

    def _maybe_issue_mastery(
        self, badge: SkillTreeBadge,
    ) -> SkillTreeMastery | None:
        """Auto-issue a Cross-British-Isles Achiever mastery if the
        player has now earned 1+ badge in each of the 5 frameworks.
        """
        if badge.player_id is None:
            return None
        player_id = badge.player_id
        frameworks = self.storage.list_player_frameworks(player_id=player_id)
        if len(frameworks) < 5:
            return None
        if CurriculumFramework.NCCA.value not in frameworks:
            return None
        if CurriculumFramework.CFE.value not in frameworks:
            return None
        if CurriculumFramework.CFW.value not in frameworks:
            return None
        if CurriculumFramework.CCEA.value not in frameworks:
            return None
        if CurriculumFramework.SQA.value not in frameworks:
            return None
        realm = FRAMEWORK_TO_REALM[badge.framework]
        source_badges = self.storage.list_badges(
            player_id=player_id, limit=500,
        )
        source_badge_ids = [b["badge_id"] for b in source_badges]
        mastery = SkillTreeMastery(
            realm=realm,
            player_id=player_id,
            date_earned=datetime.now(timezone.utc),
            source_badge_ids=source_badge_ids,
        )
        mastery_record = {
            **mastery.to_dict(),
            "vector": [0.0] * 1024,
        }
        self.storage.insert_mastery(mastery_record)
        return mastery

    async def list_badges(
        self,
        player_id: str,
        framework: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List a player's badges (optional framework filter)."""
        return self.storage.list_badges(
            player_id=player_id, framework=framework, limit=limit,
        )

    async def verify_signature(self, badge_id: str) -> dict[str, Any]:
        """Verify the cryptographic evidence chain for a badge."""
        record = self.storage.get_badge(badge_id)
        if record is None:
            return {"badge_id": badge_id, "verified": False, "reason": "not_found"}
        ok = _verify_evidence(
            record["evidence"],
            record.get("evidence_signature", ""),
            record["agent_issuer"],
        )
        return {
            "badge_id": badge_id,
            "verified": ok,
            "agent_issuer": record["agent_issuer"],
            "signature": record.get("evidence_signature", ""),
        }

    async def cross_quest_relevance(
        self,
        player_id: str,
        realm: PentElementalRealm,
        query_text: str = "",
    ) -> list[dict[str, Any]]:
        """Return the 3 most relevant badges for a new quest.

        The relevance is computed by LanceDB vector search
        (BGE-M3 embedding of the query text + the player's
        existing badges in the same realm).
        """
        if query_text:
            embedding = _compute_embedding(query_text)
        else:
            embedding = [0.0] * 1024
        return self.storage.search_badges_by_realm(
            player_id=player_id,
            realm=realm.value,
            query_embedding=embedding,
            limit=3,
        )


async def issue_badge(badge: SkillTreeBadge) -> dict[str, Any]:
    return await AchievementLedger().issue(badge)


async def list_badges(
    player_id: str,
    framework: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return await AchievementLedger().list_badges(
        player_id=player_id, framework=framework, limit=limit,
    )


async def verify_badge(badge_id: str) -> dict[str, Any]:
    return await AchievementLedger().verify_signature(badge_id)
