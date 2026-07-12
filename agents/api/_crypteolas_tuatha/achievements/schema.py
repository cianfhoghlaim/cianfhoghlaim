"""
The 8-field skill-tree badge schema + the 5 Pent-Elemental
realm types (per the `.agents/skills/tuatha-achievement-ledger/`
and `.agents/skills/pent-elemental-cosmology/` skills).

The 8 fields are derived from the British Isles formative
assessment framework (`.agents/skills/british-isles-formative-assessment/`):

  1. framework (CurriculumFramework: NCCA / CfE / CfW / CCEA / SQA)
  2. level (str, e.g. "JC3" / "CfE Third Level" / "Progression Step 3")
  3. subject (str, e.g. "Gaeilge" / "Mathematics")
  4. competency (str, e.g. "Vocabulary" / "Problem-solving")
  5. learning_outcome_code (str, e.g. "JC-Gaeilge-LO-2.4")
  6. date_earned (datetime)
  7. agent_issuer (str, e.g. "quest_guide_agent")
  8. evidence (str, a 3-sentence player reflection)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class CurriculumFramework(StrEnum):
    """The 5 British Isles curriculum frameworks (one per Celtic nation)."""

    NCCA = "NCCA"
    CFE = "CFE"
    CFW = "CFW"
    CCEA = "CCEA"
    SQA = "SQA"


class PentElementalRealm(StrEnum):
    """The 5 Pent-Elemental Cosmology realms (1 per framework)."""

    SPIRIT = "spirit"
    WATER = "water"
    FIRE = "fire"
    EARTH = "earth"
    AIR = "air"


FRAMEWORK_TO_REALM: dict[CurriculumFramework, PentElementalRealm] = {
    CurriculumFramework.NCCA: PentElementalRealm.EARTH,
    CurriculumFramework.CFE: PentElementalRealm.WATER,
    CurriculumFramework.CFW: PentElementalRealm.FIRE,
    CurriculumFramework.CCEA: PentElementalRealm.AIR,
    CurriculumFramework.SQA: PentElementalRealm.SPIRIT,
}


def skill_tree_badge_id(
    framework: CurriculumFramework,
    level: str,
    subject: str,
    date_earned: datetime,
) -> str:
    """Generate a canonical skill-tree badge id."""
    return (
        f"{framework.value}-{level.replace(' ', '_')}-{subject.replace(' ', '_')}-"
        f"{date_earned.astimezone(UTC).isoformat(timespec='seconds').replace(':', '-')}"
    )


def build_embedding_text(
    evidence: str,
    subject: str,
    competency: str,
) -> str:
    """Build the text used to compute the 1024-dim BGE-M3 embedding."""
    return f"{subject} | {competency} | {evidence}"


@dataclass
class SkillTreeBadge:
    """The 8-field skill-tree badge (the Phase 6 deliverable)."""

    framework: CurriculumFramework
    level: str
    subject: str
    competency: str
    learning_outcome_code: str
    date_earned: datetime
    agent_issuer: str
    evidence: str

    player_id: str | None = None
    realm: PentElementalRealm | None = None
    xp_awarded: int = 100
    badge_id: str = ""

    def __post_init__(self) -> None:
        if not self.badge_id:
            self.badge_id = skill_tree_badge_id(
                self.framework, self.level, self.subject, self.date_earned,
            )
        if self.realm is None:
            self.realm = FRAMEWORK_TO_REALM[self.framework]

    def to_dict(self) -> dict[str, Any]:
        return {
            "badge_id": self.badge_id,
            "framework": self.framework.value,
            "level": self.level,
            "subject": self.subject,
            "competency": self.competency,
            "learning_outcome_code": self.learning_outcome_code,
            "date_earned": self.date_earned.astimezone(UTC).isoformat(),
            "agent_issuer": self.agent_issuer,
            "evidence": self.evidence,
            "player_id": self.player_id,
            "realm": self.realm.value if self.realm else None,
            "xp_awarded": self.xp_awarded,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SkillTreeBadge:
        return cls(
            framework=CurriculumFramework(data["framework"]),
            level=data["level"],
            subject=data["subject"],
            competency=data["competency"],
            learning_outcome_code=data["learning_outcome_code"],
            date_earned=datetime.fromisoformat(data["date_earned"]),
            agent_issuer=data["agent_issuer"],
            evidence=data["evidence"],
            player_id=data.get("player_id"),
            realm=(
                PentElementalRealm(data["realm"])
                if data.get("realm")
                else None
            ),
            xp_awarded=data.get("xp_awarded", 100),
            badge_id=data.get("badge_id", ""),
        )


@dataclass
class SkillTreeMastery:
    """The Cross-British-Isles Achiever mastery (1 per Pent-Elemental realm)."""

    realm: PentElementalRealm
    player_id: str
    date_earned: datetime
    source_badge_ids: list[str] = field(default_factory=list)
    mastery_id: str = ""

    def __post_init__(self) -> None:
        if not self.mastery_id:
            ts = self.date_earned.astimezone(UTC).isoformat(
                timespec="seconds",
            ).replace(":", "-")
            self.mastery_id = f"mastery-{self.realm.value}-{self.player_id}-{ts}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "mastery_id": self.mastery_id,
            "realm": self.realm.value,
            "player_id": self.player_id,
            "date_earned": self.date_earned.astimezone(UTC).isoformat(),
            "source_badge_ids": list(self.source_badge_ids),
        }
