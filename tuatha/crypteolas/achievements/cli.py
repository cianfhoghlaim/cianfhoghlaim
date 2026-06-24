"""The achievement-ledger CLI (the 4 commands from the skill)."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone

from .ledger import AchievementLedger
from .schema import CurriculumFramework, SkillTreeBadge


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="crypteolas-achievements",
        description="The Phase 6 educational-achievement ledger CLI",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    issue = sub.add_parser("issue", help="Issue a new skill-tree badge")
    issue.add_argument("--framework", required=True, choices=[f.value for f in CurriculumFramework])
    issue.add_argument("--level", required=True)
    issue.add_argument("--subject", required=True)
    issue.add_argument("--competency", required=True)
    issue.add_argument("--lo", required=True, help="learning outcome code")
    issue.add_argument("--agent-issuer", required=True)
    issue.add_argument("--player", required=True)
    issue.add_argument("--evidence", required=True)
    issue.add_argument("--xp", type=int, default=100)

    sub.add_parser("list", help="List a player's badges").add_argument(
        "--player", required=True,
    )

    verify = sub.add_parser("verify", help="Verify a badge signature")
    verify.add_argument("--badge-id", required=True)

    mastery = sub.add_parser("mastery", help="Issue a Cross-British-Isles Achiever mastery")
    mastery.add_argument("--player", required=True)
    mastery.add_argument(
        "--realm", required=True,
        choices=["spirit", "water", "fire", "earth", "air"],
    )

    return parser.parse_args()


async def _run() -> int:
    args = _parse_args()
    ledger = AchievementLedger()
    if args.command == "issue":
        badge = SkillTreeBadge(
            framework=CurriculumFramework(args.framework),
            level=args.level,
            subject=args.subject,
            competency=args.competency,
            learning_outcome_code=args.lo,
            date_earned=datetime.now(timezone.utc),
            agent_issuer=args.agent_issuer,
            evidence=args.evidence,
            player_id=args.player,
            xp_awarded=args.xp,
        )
        result = await ledger.issue(badge)
        print(json.dumps(result, indent=2, default=str))
        return 0
    if args.command == "list":
        result = await ledger.list_badges(player_id=args.player)
        print(json.dumps(result, indent=2, default=str))
        return 0
    if args.command == "verify":
        result = await ledger.verify_signature(badge_id=args.badge_id)
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("verified") else 1
    if args.command == "mastery":
        badges = await ledger.list_badges(player_id=args.player, limit=500)
        if not badges:
            print("no badges")
            return 1
        latest = badges[-1]
        badge = SkillTreeBadge.from_dict(latest)
        result = await ledger.issue(badge)
        print(json.dumps(result, indent=2, default=str))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(asyncio.run(_run()))
