"""
Dagster assets for blockchain data and token operations.

Asset Flow:
    user_learning_activity
        → computed_xp_rewards
        → pending_token_mints
        → nft_evolution_queue
"""

from typing import Any

from dagster import (
    asset,
    AssetExecutionContext,
    Config,
    MaterializeResult,
    MetadataValue,
)
from pydantic import Field

from .resources import Web3Resource, ContractResource


class LearningActivityConfig(Config):
    """Configuration for learning activity asset."""

    subject: str = Field(
        default="irish",
        description="Subject filter (irish, welsh, scottish, manx, chemistry, etc.)"
    )
    min_score: float = Field(
        default=0.7,
        description="Minimum score threshold for XP rewards"
    )
    lookback_hours: int = Field(
        default=24,
        description="Hours to look back for activities"
    )


@asset(
    group_name="blockchain",
    description="Fetch learning activities from the platform database",
)
def user_learning_activity(
    context: AssetExecutionContext,
    config: LearningActivityConfig,
) -> list[dict]:
    """
    Retrieve recent learning activities eligible for rewards.

    Returns activities from:
    - Quiz completions
    - Translation submissions
    - Voice recordings (oracy mining)
    - Handwriting submissions (OCR training)
    """
    # In production, this would query from LanceDB/PostgreSQL
    # For now, return mock data
    activities = [
        {
            "user_id": "0x1234...abcd",
            "activity_type": "quiz_completion",
            "subject": config.subject,
            "score": 0.85,
            "language": "ga",  # Irish
            "timestamp": "2024-01-15T10:30:00Z",
            "challenge_id": "chemistry_q1",
        },
        {
            "user_id": "0x5678...efgh",
            "activity_type": "translation_submission",
            "subject": config.subject,
            "score": 0.92,
            "language": "cy",  # Welsh
            "timestamp": "2024-01-15T11:15:00Z",
            "challenge_id": "translation_001",
        },
    ]

    # Filter by minimum score
    filtered = [a for a in activities if a["score"] >= config.min_score]

    context.log.info(f"Found {len(filtered)} activities for {config.subject}")

    return filtered


class XPRewardConfig(Config):
    """Configuration for XP reward computation."""

    base_xp_per_activity: int = Field(
        default=100,
        description="Base XP for completing an activity"
    )
    score_multiplier: float = Field(
        default=2.0,
        description="Multiplier applied to score (0-1) for bonus XP"
    )
    language_bonus: dict = Field(
        default={
            "ga": 1.5,  # Irish
            "gd": 1.5,  # Scottish Gaelic
            "gv": 2.0,  # Manx (endangered)
            "cy": 1.3,  # Welsh
            "en": 1.0,  # English
        },
        description="Bonus multiplier by language (endangered languages get more)"
    )


@asset(
    group_name="blockchain",
    deps=[user_learning_activity],
    description="Compute XP rewards based on learning activities",
)
def computed_xp_rewards(
    context: AssetExecutionContext,
    config: XPRewardConfig,
    user_learning_activity: list[dict],
) -> list[dict]:
    """
    Calculate XP rewards for each learning activity.

    Formula: base_xp * score * score_multiplier * language_bonus

    Example for Irish quiz with 85% score:
    100 * 0.85 * 2.0 * 1.5 = 255 XP
    """
    rewards = []

    for activity in user_learning_activity:
        lang = activity.get("language", "en")
        lang_bonus = config.language_bonus.get(lang, 1.0)

        xp = int(
            config.base_xp_per_activity
            * activity["score"]
            * config.score_multiplier
            * lang_bonus
        )

        rewards.append({
            "user_id": activity["user_id"],
            "xp_amount": xp,
            "tuath_amount": xp // 10,  # 10 XP = 1 Tuath token
            "activity_type": activity["activity_type"],
            "language": lang,
            "reason": f"{activity['activity_type']} in {lang} ({activity['score']*100:.0f}%)",
        })

        context.log.info(
            f"User {activity['user_id'][:10]}... earns {xp} XP, "
            f"{xp // 10} Tuath for {activity['activity_type']}"
        )

    return rewards


@asset(
    group_name="blockchain",
    deps=[computed_xp_rewards],
    description="Queue of pending token mint operations",
)
def pending_token_mints(
    context: AssetExecutionContext,
    computed_xp_rewards: list[dict],
) -> list[dict]:
    """
    Prepare token minting queue for batch execution.

    Groups rewards by user and prepares mint transactions.
    """
    # Aggregate by user
    user_totals: dict[str, dict] = {}

    for reward in computed_xp_rewards:
        user_id = reward["user_id"]
        if user_id not in user_totals:
            user_totals[user_id] = {
                "user_id": user_id,
                "total_xp": 0,
                "total_tuath": 0,
                "activities": [],
            }

        user_totals[user_id]["total_xp"] += reward["xp_amount"]
        user_totals[user_id]["total_tuath"] += reward["tuath_amount"]
        user_totals[user_id]["activities"].append(reward["reason"])

    mint_queue = list(user_totals.values())

    context.log.info(f"Prepared {len(mint_queue)} mint operations")

    return MaterializeResult(
        asset_key="pending_token_mints",
        metadata={
            "num_mints": MetadataValue.int(len(mint_queue)),
            "total_tuath": MetadataValue.int(
                sum(m["total_tuath"] for m in mint_queue)
            ),
        },
    ), mint_queue


@asset(
    group_name="blockchain",
    deps=[computed_xp_rewards],
    description="Queue of NFT evolution updates",
)
def nft_evolution_queue(
    context: AssetExecutionContext,
    computed_xp_rewards: list[dict],
) -> list[dict]:
    """
    Prepare NFT evolution updates based on XP gains.

    Tracks potential level-ups and warp spasm unlocks.
    """
    # In production, would query current NFT states
    evolutions = []

    for reward in computed_xp_rewards:
        # Check if XP gain triggers level up
        # This would query the blockchain for current level/XP
        evolutions.append({
            "user_id": reward["user_id"],
            "xp_to_grant": reward["xp_amount"],
            "reason": reward["reason"],
            "estimated_new_level": None,  # Would calculate based on current state
        })

    context.log.info(f"Prepared {len(evolutions)} NFT evolution updates")

    return evolutions
