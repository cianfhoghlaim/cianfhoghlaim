"""
The LanceDB-backed storage for the achievement ledger.

The badges are stored in a single LanceDB table
`crypteolas_achievements` with the BGE-M3 embedding (1024-dim)
of the concatenated `evidence + subject + competency` text.
The vector column supports semantic retrieval for
cross-quest relevance.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import lancedb
from lancedb.pydantic import LanceModel, Vector

_DEFAULT_LANCEDB_PATH = Path(
    os.environ.get(
        "TuatHA_CRYpteolas_LANCEDB_PATH",
        str(Path.home() / ".tuatha" / "crypteolas" / "lancedb"),
    ),
)

_EMBEDDING_DIM = 1024


class SkillTreeBadgeRecord(LanceModel):
    """The LanceDB row schema for a skill-tree badge."""

    badge_id: str
    framework: str
    level: str
    subject: str
    competency: str
    learning_outcome_code: str
    date_earned: str
    agent_issuer: str
    evidence: str
    evidence_signature: str = ""
    player_id: str
    realm: str = ""
    xp_awarded: int = 100
    vector: Vector(dim=_EMBEDDING_DIM) = None  # type: ignore[assignment]


class SkillTreeMasteryRecord(LanceModel):
    """The LanceDB row schema for a Cross-British-Isles Achiever mastery."""

    mastery_id: str
    realm: str
    player_id: str
    date_earned: str
    source_badge_ids: list[str]
    vector: Vector(dim=_EMBEDDING_DIM) = None  # type: ignore[assignment]


class AchievementStorage:
    """The LanceDB-backed storage for the achievement ledger.

    Two tables:
    - `crypteolas_achievements` (the badge table)
    - `crypteolas_masteries` (the Cross-British-Isles Achiever mastery table)
    """

    TABLE_BADGES = "crypteolas_achievements"
    TABLE_MASTERIES = "crypteolas_masteries"

    def __init__(self, lancedb_path: Path | str | None = None) -> None:
        self.lancedb_path = Path(lancedb_path) if lancedb_path else _DEFAULT_LANCEDB_PATH
        self.lancedb_path.mkdir(parents=True, exist_ok=True)
        self._db: lancedb.DBConnection | None = None

    @property
    def db(self) -> lancedb.DBConnection:
        if self._db is None:
            self._db = lancedb.connect(str(self.lancedb_path))
        return self._db

    def init_storage(self) -> None:
        """Initialise the 2 tables (idempotent)."""
        if self.TABLE_BADGES not in self.db.table_names():
            self.db.create_table(
                self.TABLE_BADGES,
                schema=SkillTreeBadgeRecord,
                mode="create",
            )
        if self.TABLE_MASTERIES not in self.db.table_names():
            self.db.create_table(
                self.TABLE_MASTERIES,
                schema=SkillTreeMasteryRecord,
                mode="create",
            )

    def insert_badge(self, record: dict[str, Any]) -> None:
        self.init_storage()
        table = self.db.open_table(self.TABLE_BADGES)
        table.add([record])

    def insert_mastery(self, record: dict[str, Any]) -> None:
        self.init_storage()
        table = self.db.open_table(self.TABLE_MASTERIES)
        table.add([record])

    def list_badges(
        self,
        player_id: str,
        framework: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        if self.TABLE_BADGES not in self.db.table_names():
            return []
        table = self.db.open_table(self.TABLE_BADGES)
        filters = [f"player_id = '{player_id}'"]
        if framework:
            filters.append(f"framework = '{framework}'")
        filter_str = " AND ".join(filters)
        df = table.search().where(filter_str).limit(limit).to_pandas()
        return df.to_dict(orient="records")

    def get_badge(self, badge_id: str) -> dict[str, Any] | None:
        if self.TABLE_BADGES not in self.db.table_names():
            return None
        table = self.db.open_table(self.TABLE_BADGES)
        df = table.search().where(f"badge_id = '{badge_id}'").limit(1).to_pandas()
        records = df.to_dict(orient="records")
        return records[0] if records else None

    def search_badges_by_realm(
        self,
        player_id: str,
        realm: str,
        query_embedding: list[float],
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        if self.TABLE_BADGES not in self.db.table_names():
            return []
        table = self.db.open_table(self.TABLE_BADGES)
        df = (
            table.search(query_embedding)
            .where(f"player_id = '{player_id}' AND realm = '{realm}'")
            .limit(limit)
            .to_pandas()
        )
        return df.to_dict(orient="records")

    def list_player_frameworks(self, player_id: str) -> set[str]:
        badges = self.list_badges(player_id=player_id, limit=500)
        return {b["framework"] for b in badges}
