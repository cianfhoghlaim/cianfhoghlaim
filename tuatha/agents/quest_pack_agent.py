"""tuatha/agents/quest_pack_agent.py — the ADK 2 agent that generates BAML quest packs.

Per the 2026-10-08-tuatha-closed-loop-mmo-v1 saga change (Plan 8 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

The 27th agent in the fleet. Generates a quest pack for one subject
(one quest per learning outcome, linked to the asset reward).
"""
from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, UTC
from typing import Any

logger = logging.getLogger(__name__)


# The canonical 5-quest template per session
QUEST_TEMPLATES = [
    {
        "quest_type": "INTRODUCE",
        "title_template": "Welcome to the {subject} realm",
        "description_template": "Meet {deity} and learn the basics of {subject}.",
        "reward_template": "The {deity}'s introductory blessing (visual asset).",
        "weight": 0.2,
    },
    {
        "quest_type": "CHALLENGE",
        "title_template": "The {treasure} Challenge",
        "description_template": "Prove your {subject} skills by solving the {deity}'s riddle.",
        "reward_template": "The {treasure} (visual asset).",
        "weight": 0.3,
    },
    {
        "quest_type": "DEEP_DIVE",
        "title_template": "The {subject} Mystery",
        "description_template": "Investigate the deepest {subject} concept with {deity}'s guidance.",
        "reward_template": "The deepest {subject} insight (visual asset).",
        "weight": 0.3,
    },
    {
        "quest_type": "BOSS",
        "title_template": "The {subject} Boss Battle",
        "description_template": "Defeat the {subject} boss using everything you've learned.",
        "reward_template": "The {subject} victory crown (visual asset).",
        "weight": 0.15,
    },
    {
        "quest_type": "REFLECTION",
        "title_template": "The {subject} Reflection",
        "description_template": "Reflect on your {subject} journey with {deity}.",
        "reward_template": "The {deity}'s blessing (visual asset).",
        "weight": 0.05,
    },
]


def generate_quest_pack(subject: str = "mathematics", language: str = "en") -> dict[str, Any]:
    """Generate the per-session quest pack.

    Args:
        subject: The NCCA subject (default: mathematics)
        language: en | ga | cy | gd | gv | kw | br

    Returns:
        The quest pack dict with session_id + 5 quests
    """
    import importlib
    mod = importlib.import_module("orchestration.defs.4_asset_generation.tuatha_realm_asset")
    SUBJECT_DEITIES = getattr(mod, "SUBJECT_DEITIES", None) or {}
    SUBJECT_LEARNING_OUTCOMES = getattr(mod, "SUBJECT_LEARNING_OUTCOMES", None) or {}

    session_id = hashlib.sha256(
        f"{subject}|{language}|{datetime.now(UTC).isoformat()}".encode()
    ).hexdigest()[:16]

    deity_info = SUBJECT_DEITIES.get(subject, {
        "deity": "The Dagda", "treasure": "Cauldron of Plenty"
    })

    # The 5 outcomes per session
    outcomes = SUBJECT_LEARNING_OUTCOMES.get(subject, [
        f"LC-{subject.upper()[:4]}-LO-3.1.1",
        f"LC-{subject.upper()[:4]}-LO-3.1.2",
        f"LC-{subject.upper()[:4]}-LO-3.2.1",
        f"LC-{subject.upper()[:4]}-LO-3.3.1",
        f"LC-{subject.upper()[:4]}-LO-3.4.1",
    ])

    # Build the 5 quests (1 per outcome)
    quests = []
    for i, (template, outcome) in enumerate(zip(QUEST_TEMPLATES, outcomes)):
        quest = {
            "quest_id": str(uuid.uuid4())[:8],
            "quest_type": template["quest_type"],
            "title": template["title_template"].format(
                subject=subject.title(), deity=deity_info["deity"], treasure=deity_info["treasure"],
            ),
            "description": template["description_template"].format(
                subject=subject, deity=deity_info["deity"],
            ),
            "reward": template["reward_template"].format(
                subject=subject, deity=deity_info["deity"], treasure=deity_info["treasure"],
            ),
            "learning_outcome_code": outcome,
            "weight": template["weight"],
            "subject": subject,
            "language": language,
            "session_id": session_id,
        }
        quests.append(quest)

    return {
        "session_id": session_id,
        "subject": subject,
        "language": language,
        "deity": deity_info["deity"],
        "treasure": deity_info["treasure"],
        "quests": quests,
        "total_weight": sum(t["weight"] for t in QUEST_TEMPLATES),
        "created_at": datetime.now(UTC).isoformat(),
    }


def quest_pack_agent():
    """The canonical ADK 2 agent factory for the quest pack generator."""
    try:
        from google.adk.agents import LlmAgent
        from google.adk.tools import FunctionTool

        generate_quest_pack_tool = FunctionTool(func=generate_quest_pack)

        return LlmAgent(
            name="quest_pack_agent",
            model="minimax-m3",
            description=(
                "Generates a Tuatha British Isles MMO quest pack for one subject + one language. "
                "Returns 5 quests (one per learning outcome) linked to the asset rewards."
            ),
            instruction=(
                "You are the quest pack agent. Call generate_quest_pack(subject='mathematics') "
                "and return the 5 quests linked to the NCCA learning outcomes."
            ),
            tools=[generate_quest_pack_tool],
        )
    except ImportError:
        return None


__all__ = ["generate_quest_pack", "quest_pack_agent"]
