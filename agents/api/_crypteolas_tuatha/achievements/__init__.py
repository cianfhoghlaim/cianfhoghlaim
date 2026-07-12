"""
Crypteolas educational-achievement ledger (Phase 6 of the 6-phase
refactor plan; see `tuatha-formative-assessment-v1` openspec change
archived 2026-06-24).

Per the user's plan: "crypto = educational achievements (not
finance)". The ledger holds **skill-tree badges**, NOT a financial
token. x402 micropayments are reserved for gated game features
only (cosmetics, premium quests, paid DLC) — never for
educational content.

The 4 public surfaces:

- `AchievementLedger.issue(badge)` — issue a new skill-tree badge
  (also auto-issues a Cross-British-Isles Achiever mastery if
  the player has earned 1+ badge in each of the 5 frameworks)
- `AchievementLedger.list_badges(player_id, framework=...)` —
  list a player's badges
- `AchievementLedger.verify_signature(badge_id)` — verify the
  cryptographic evidence chain
- `AchievementLedger.cross_quest_relevance(player_id, realm)` —
  return the 3 most relevant badges for a new quest
"""

from .ledger import (
    AchievementLedger,
    CurriculumFramework,
    PentElementalRealm,
    SkillTreeBadge,
    SkillTreeMastery,
    issue_badge,
    list_badges,
    verify_badge,
)
from .schema import (
    SkillTreeBadgeRecord,
    SkillTreeMasteryRecord,
    build_embedding_text,
    skill_tree_badge_id,
)
from .storage import AchievementStorage

__all__ = [
    "AchievementLedger",
    "AchievementStorage",
    "CurriculumFramework",
    "PentElementalRealm",
    "SkillTreeBadge",
    "SkillTreeBadgeRecord",
    "SkillTreeMastery",
    "SkillTreeMasteryRecord",
    "build_embedding_text",
    "issue_badge",
    "list_badges",
    "skill_tree_badge_id",
    "verify_badge",
]
